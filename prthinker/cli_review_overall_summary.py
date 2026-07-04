"""PR-wide overall-summary synthesis for the matrix aggregate job.

Split out of :mod:`prthinker.cli_review` to keep that module under the
file-length bar. The aggregate step rolls the per-shard ``total_summary``
blocks up into one PR-wide paragraph by asking the remote backend's
``/ask`` endpoint; this module owns the submit / poll / cancel loop.

Best-effort throughout: a missing backend URL, a timeout, or any HTTP
failure logs a warning and returns an empty string so the formatter falls
back to the per-file blocks alone. The module imports only leaf helpers
(``httpx``, ``config``); it never imports :mod:`prthinker.cli_review`, so the
dependency edge runs one way (``cli_review`` -> ``cli_review_overall_summary``).
"""

from __future__ import annotations

import logging
import time

import httpx

from prthinker.config import env_str

log = logging.getLogger("prthinker")

_OVERALL_SUMMARY_PER_CALL_TIMEOUT = 30.0
_OVERALL_SUMMARY_POLL_INTERVAL = 5.0
_OVERALL_SUMMARY_DEADLINE_SECONDS = 1800.0
_OVERALL_SUMMARY_MAX_NEW_TOKENS = 16784


def _collect_overall_summary_inputs(per_file: list) -> list[str]:
    """Return the non-empty per-file total summaries, ready for the prompt."""
    summaries: list[str] = []
    for fr in per_file:
        text = (fr.total_summary or "").strip()
        if text:
            summaries.append(f"### {fr.path}\n{text}")
    return summaries


def _build_overall_summary_prompt(summaries: list[str]) -> str:
    return (
        "You are summarising a code-review run. Below are per-file "
        "summaries from a single pull request. Write ONE concise PR-wide "
        "summary in 3-5 sentences. Capture the common themes, the most "
        "important findings, and the residual risk. Do not enumerate the "
        "per-file blocks verbatim.\n\n" + "\n\n".join(summaries)
    )


def _best_effort_cancel_ask_job(client: httpx.Client, job_id: str) -> None:
    """Tell the backend to release the GPU; ignore failures by design."""
    try:
        client.post(f"/ask/cancel/{job_id}")
    except httpx.HTTPError as exc:
        log.debug("Cancel for ask job %s failed (ignored): %s", job_id, exc)


def _poll_overall_summary(client: httpx.Client, job_id: str, deadline: float) -> str:
    while True:
        if time.monotonic() >= deadline:
            _best_effort_cancel_ask_job(client, job_id)
            log.warning(
                "Overall summary synthesis exceeded deadline; skipping",
            )
            return ""
        time.sleep(_OVERALL_SUMMARY_POLL_INTERVAL)
        poll = client.get(f"/ask/result/{job_id}")
        poll.raise_for_status()
        payload = poll.json()
        status = payload.get("status")
        if status == "done":
            return (payload.get("result") or "").strip()
        if status == "error":
            log.warning(
                "Overall summary synthesis failed server-side: %s",
                payload.get("error"),
            )
            return ""
        if status == "cancelled":
            log.warning("Overall summary synthesis cancelled server-side")
            return ""


def _synthesize_overall_summary(per_file: list) -> str:
    """Ask the remote backend for a single PR-wide summary.

    Each matrix shard already produced its own per-file
    ``total_summary``; the aggregate needs to roll them up into one
    paragraph that captures the PR's overall shape — common themes,
    the heaviest findings, residual risk — without restating every
    file. Best-effort: a missing backend, a timeout, or any other
    failure logs a warning and returns an empty string so the
    formatter falls back to the per-file blocks alone.
    """
    summaries = _collect_overall_summary_inputs(per_file)
    if len(summaries) < 2:
        return ""

    remote_url = (env_str("PRTHINKER_REMOTE_URL", "") or "").strip()
    if not remote_url:
        return ""

    api_key = (env_str("PRTHINKER_REMOTE_API_KEY", "") or "").strip()
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    deadline = time.monotonic() + _OVERALL_SUMMARY_DEADLINE_SECONDS
    prompt = _build_overall_summary_prompt(summaries)
    try:
        with httpx.Client(
            base_url=remote_url.rstrip("/"),
            timeout=_OVERALL_SUMMARY_PER_CALL_TIMEOUT,
            headers=headers,
        ) as client:
            submit = client.post(
                "/ask/submit",
                json={
                    "prompt": prompt,
                    "max_new_tokens": _OVERALL_SUMMARY_MAX_NEW_TOKENS,
                },
            )
            submit.raise_for_status()
            job_id = submit.json()["job_id"]
            return _poll_overall_summary(client, job_id, deadline)
    except (httpx.HTTPError, KeyError, ValueError) as exc:
        log.warning("Overall summary synthesis failed (%s); skipping", exc)
        return ""
