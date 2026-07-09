"""Remote HTTP backends.

Two thin clients of the FastAPI server:

- RemoteHttpBackend       - runs a single prompt through the async /ask job
                            (submit + poll). Plugs into CoTPipeline like
                            LocalHFBackend, so the pipeline orchestration
                            stays on the runner.

- RemotePipelineClient    - calls /review once and gets the full structured
                            result. Saves N-1 HTTP round-trips per review
                            and lets the server own RAG + step orchestration.
                            Not an InferenceBackend (it returns ReviewResponse,
                            not a raw string).

Both go through the async job pattern (``/{kind}/submit`` for a job id, then
poll ``/{kind}/result/{id}``). A 30B MoE generation runs for minutes, far
longer than Cloudflare's ~100s edge timeout that a synchronous call cannot
survive (the 504 the synchronous /ask returned on slow PR summaries). Each
individual call fits inside the proxy timeout; the overall wait is bounded by
``config.timeout_seconds``.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from typing import TypeVar

import httpx

from prthinker.backends.base import InferenceBackend
from prthinker.config import RemoteBackendConfig
from prthinker.schemas import ReviewRequest, ReviewResponse

log = logging.getLogger("prthinker.backends.remote")

T = TypeVar("T")

_STATUS_DONE = "done"
_STATUS_ERROR = "error"
_STATUS_CANCELLED = "cancelled"

# Each individual HTTP call must complete inside any upstream proxy's
# idle timeout. Cloudflare's free/pro/business plans cap that at ~100s,
# so keep per-call timeout well below.
_PER_CALL_TIMEOUT_SECONDS = 30.0
_POLL_INTERVAL_SECONDS = 5.0
# A poll occasionally trips the per-call timeout (backend GIL pause
# during a heavy generate step, Cloudflare edge hiccup, runner network
# blip). One slow poll should not crash a multi-minute review; retry
# transient failures and only surface a persistent stall. A 30B MoE
# backend restart or GPU reload can produce 502s for >1 min, so the
# budget must comfortably cover that.
_MAX_CONSECUTIVE_POLL_FAILURES = 60
_POLL_BACKOFF_AFTER_FAILURES = 5
_POLL_MAX_INTERVAL_SECONDS = 30.0

_TRANSIENT_POLL_ERRORS = (
    httpx.ReadTimeout,
    httpx.ConnectTimeout,
    httpx.ConnectError,
    httpx.RemoteProtocolError,
    httpx.HTTPStatusError,
)


def _build_poll_client(config: RemoteBackendConfig) -> httpx.Client:
    headers: dict[str, str] = {}
    if config.api_key:
        headers["Authorization"] = f"Bearer {config.api_key}"
    return httpx.Client(
        base_url=config.url.rstrip("/"),
        timeout=_PER_CALL_TIMEOUT_SECONDS,
        headers=headers,
    )


class _AsyncJobClient:
    """Submit→poll→cancel machinery shared by the /ask and /review jobs.

    ``kind`` selects the endpoint family (``"ask"`` or ``"review"``); the
    caller supplies the submit body and a ``parse_done`` callback that maps
    a terminal ``done`` payload to the result type it wants back.
    """

    def __init__(self, client: httpx.Client, kind: str, timeout_seconds: float) -> None:
        self._client = client
        self._kind = kind
        self._timeout_seconds = timeout_seconds

    def run(self, submit_body: dict, parse_done: Callable[[dict], T]) -> T:
        submit_resp = self._client.post(f"/{self._kind}/submit", json=submit_body)
        submit_resp.raise_for_status()
        job_id = submit_resp.json()["job_id"]
        completed_cleanly = False
        try:
            result = self._poll_until_done(job_id, parse_done)
            completed_cleanly = True
            return result
        finally:
            if not completed_cleanly:
                # Client is exiting before the job reached a terminal state —
                # tell the server so it stops burning GPU on work nobody will
                # read. Best-effort: a failure here must not mask the original
                # exception.
                self._send_cancel(job_id)

    @staticmethod
    def _poll_sleep_seconds(consecutive_failures: int) -> float:
        """Compute the back-off sleep before the next poll attempt."""
        if consecutive_failures <= _POLL_BACKOFF_AFTER_FAILURES:
            return _POLL_INTERVAL_SECONDS
        return min(
            _POLL_INTERVAL_SECONDS
            * 2 ** (consecutive_failures - _POLL_BACKOFF_AFTER_FAILURES),
            _POLL_MAX_INTERVAL_SECONDS,
        )

    def _terminal_result_or_none(
        self, job_id: str, payload: dict, parse_done: Callable[[dict], T]
    ) -> "T | None":
        """Map a poll payload to a result, raise on terminal errors, else None."""
        status = payload.get("status")
        if status == _STATUS_DONE:
            return parse_done(payload)
        if status == _STATUS_ERROR:
            raise RuntimeError(
                f"Remote {self._kind} job {job_id} failed: {payload.get('error')}"
            )
        if status == _STATUS_CANCELLED:
            raise RuntimeError(
                f"Remote {self._kind} job {job_id} was cancelled server-side"
            )
        return None

    def _poll_until_done(self, job_id: str, parse_done: Callable[[dict], T]) -> T:
        deadline = time.monotonic() + self._timeout_seconds
        consecutive_failures = 0
        while True:
            if time.monotonic() >= deadline:
                raise TimeoutError(
                    f"Remote {self._kind} job {job_id} did not finish within "
                    f"{self._timeout_seconds}s"
                )
            time.sleep(self._poll_sleep_seconds(consecutive_failures))
            try:
                poll_resp = self._client.get(f"/{self._kind}/result/{job_id}")
                poll_resp.raise_for_status()
            except _TRANSIENT_POLL_ERRORS as exc:
                consecutive_failures += 1
                self._note_poll_failure(job_id, consecutive_failures, exc)
                continue
            consecutive_failures = 0
            result = self._terminal_result_or_none(job_id, poll_resp.json(), parse_done)
            if result is not None:
                return result

    def _note_poll_failure(
        self, job_id: str, consecutive_failures: int, exc: Exception
    ) -> None:
        """Log a transient poll failure; re-raise once the budget is exhausted."""
        if consecutive_failures > _MAX_CONSECUTIVE_POLL_FAILURES:
            raise exc
        log.warning(
            "Poll %d/%d for %s job %s failed transiently: %s",
            consecutive_failures,
            _MAX_CONSECUTIVE_POLL_FAILURES,
            self._kind,
            job_id,
            exc,
        )

    def _send_cancel(self, job_id: str) -> None:
        try:
            self._client.post(f"/{self._kind}/cancel/{job_id}")
        except Exception as exc:  # noqa: BLE001 — cleanup must never raise
            log.warning(
                "Cancel for %s job %s failed (ignored): %s",
                self._kind,
                job_id,
                exc,
            )

    def close(self) -> None:
        self._client.close()


def _parse_ask_done(payload: dict) -> str:
    """Extract the generated text from a terminal /ask poll payload."""
    return payload.get("result") or ""


def _parse_review_done(payload: dict) -> ReviewResponse:
    """Validate the structured review from a terminal /review poll payload."""
    return ReviewResponse.model_validate(payload["result"])


class RemoteHttpBackend(InferenceBackend):
    concurrency_limit = 4
    """Runs prompts through the async /ask job (submit + poll)."""

    def __init__(self, config: RemoteBackendConfig) -> None:
        self._config = config
        self._job = _AsyncJobClient(
            _build_poll_client(config), "ask", config.timeout_seconds
        )

    def backend_kind(self) -> str:
        return "remote"

    def model_name(self) -> str:
        # The server picks the model at boot time; the runner does not know it.
        return "remote"

    def generate(
        self,
        prompt: str,
        max_new_tokens: int,
        *,
        cancel_event: "object | None" = None,
    ) -> str:
        # The async job owns cancellation server-side (it cancels on an
        # abnormal exit); the runner does not stream tokens, so the local
        # cancel_event is not wired into the poll loop.
        del cancel_event
        return self._job.run(
            {"prompt": prompt, "max_new_tokens": max_new_tokens},
            _parse_ask_done,
        )

    def close(self) -> None:
        self._job.close()


class RemotePipelineClient:
    """Submits a review job and polls for the result.

    A single CoT review on a 30B MoE backend runs for minutes, longer
    than Cloudflare's 100s edge timeout. The client submits to
    `/review/submit` for a job id, then polls `/review/result/{id}`
    until status moves to ``done`` / ``error``. Each individual call
    fits well inside any reverse-proxy timeout; the overall wait is
    bounded by ``config.timeout_seconds``.
    """

    def __init__(self, config: RemoteBackendConfig) -> None:
        self._config = config
        self._job = _AsyncJobClient(
            _build_poll_client(config), "review", config.timeout_seconds
        )

    def review(self, request: ReviewRequest) -> ReviewResponse:
        return self._job.run(request.model_dump(), _parse_review_done)

    def close(self) -> None:
        self._job.close()
