"""Remote HTTP backends.

Two thin clients of the FastAPI server:

- RemoteHttpBackend       - proxies a single prompt to /ask.
                            Plugs into CoTPipeline like LocalQwen3Backend,
                            so the pipeline orchestration stays on the runner.

- RemotePipelineClient    - calls /review once and gets the full structured
                            result. Saves N-1 HTTP round-trips per review
                            and lets the server own RAG + step orchestration.
                            Not an InferenceBackend (it returns ReviewResponse,
                            not a raw string).
"""

from __future__ import annotations

import logging
import time

import httpx

from prthinker.backends.base import InferenceBackend
from prthinker.config import RemoteBackendConfig
from prthinker.schemas import ReviewRequest, ReviewResponse

log = logging.getLogger("prthinker.backends.remote")


# Each individual HTTP call must complete inside any upstream proxy's
# idle timeout. Cloudflare's free/pro/business plans cap that at ~100s,
# so keep per-call timeout well below.
_PER_CALL_TIMEOUT_SECONDS = 30.0
_POLL_INTERVAL_SECONDS = 5.0
# A poll occasionally trips the per-call timeout (backend GIL pause
# during a heavy generate step, Cloudflare edge hiccup, runner network
# blip). One slow poll should not crash a multi-minute review; retry
# transient failures and only surface a persistent stall.
_MAX_CONSECUTIVE_POLL_FAILURES = 5


def _build_client(config: RemoteBackendConfig) -> httpx.Client:
    headers: dict[str, str] = {}
    if config.api_key:
        headers["Authorization"] = f"Bearer {config.api_key}"
    return httpx.Client(
        base_url=config.url.rstrip("/"),
        timeout=config.timeout_seconds,
        headers=headers,
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


class RemoteHttpBackend(InferenceBackend):
    """POSTs prompts to `/ask` (plain text out)."""

    def __init__(self, config: RemoteBackendConfig) -> None:
        self._config = config
        self._client = _build_client(config)

    def backend_kind(self) -> str:
        return "remote"

    def model_name(self) -> str:
        # The server picks the model at boot time; the runner does not know it.
        return "remote"

    def generate(self, prompt: str, max_new_tokens: int) -> str:
        response = self._client.post(
            "/ask",
            json={"prompt": prompt, "max_new_tokens": max_new_tokens},
        )
        response.raise_for_status()
        return response.text

    def close(self) -> None:
        self._client.close()


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
        self._client = _build_poll_client(config)

    def review(self, request: ReviewRequest) -> ReviewResponse:
        submit_resp = self._client.post(
            "/review/submit",
            json=request.model_dump(),
        )
        submit_resp.raise_for_status()
        job_id = submit_resp.json()["job_id"]
        completed_cleanly = False
        try:
            result = self._poll_until_done(job_id)
            completed_cleanly = True
            return result
        finally:
            if not completed_cleanly:
                # Client is exiting before the job reached a terminal
                # state — tell the server so it stops burning GPU on a
                # review nobody will read. Best-effort: a failure here
                # must not mask the original exception.
                self._send_cancel(job_id)

    def _poll_until_done(self, job_id: str) -> ReviewResponse:
        deadline = time.monotonic() + self._config.timeout_seconds
        consecutive_failures = 0
        while True:
            if time.monotonic() >= deadline:
                raise TimeoutError(
                    f"Remote review job {job_id} did not finish within "
                    f"{self._config.timeout_seconds}s"
                )
            time.sleep(_POLL_INTERVAL_SECONDS)
            try:
                poll_resp = self._client.get(f"/review/result/{job_id}")
                poll_resp.raise_for_status()
            except (
                httpx.ReadTimeout,
                httpx.ConnectTimeout,
                httpx.ConnectError,
                httpx.RemoteProtocolError,
                httpx.HTTPStatusError,
            ) as exc:
                consecutive_failures += 1
                if consecutive_failures > _MAX_CONSECUTIVE_POLL_FAILURES:
                    raise
                log.warning(
                    "Poll %d/%d for job %s failed transiently: %s",
                    consecutive_failures,
                    _MAX_CONSECUTIVE_POLL_FAILURES,
                    job_id,
                    exc,
                )
                continue
            consecutive_failures = 0
            payload = poll_resp.json()
            status = payload.get("status")
            if status == "done":
                return ReviewResponse.model_validate(payload["result"])
            if status == "error":
                raise RuntimeError(
                    f"Remote review job {job_id} failed: {payload.get('error')}"
                )
            if status == "cancelled":
                raise RuntimeError(
                    f"Remote review job {job_id} was cancelled server-side"
                )

    def _send_cancel(self, job_id: str) -> None:
        try:
            self._client.post(f"/review/cancel/{job_id}")
        except Exception as exc:  # noqa: BLE001 — cleanup must never raise
            log.warning("Cancel for job %s failed (ignored): %s", job_id, exc)

    def close(self) -> None:
        self._client.close()
