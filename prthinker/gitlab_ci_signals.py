"""Fetch CI failure signals for an MR head SHA via the GitLab pipelines API.

GitLab counterpart of :mod:`prthinker.ci_signals`: same
:class:`~prthinker.ci_signals.FailureSignal` shape and the same
"smoking gun, not the whole build log" posture — only *failed* jobs of
*failed* pipelines are fetched, and each trace is truncated to its tail.
The rendered block reuses :func:`prthinker.ci_signals.format_signals_block`.
"""

from __future__ import annotations

import logging
import urllib.parse

import httpx

from prthinker.ci_signals import FailureSignal

log = logging.getLogger(__name__)

_DEFAULT_BASE_URL = "https://gitlab.com/api/v4"
_USER_AGENT = "prthinker/0.1"
_PIPELINES_PER_SHA = 20
_JOBS_PER_PAGE = 100


def fetch_gitlab_ci_failure_signals(
    project: str,
    head_sha: str,
    token: str,
    *,
    base_url: str | None = None,
    max_jobs: int = 5,
    log_tail_chars: int = 4000,
) -> list[FailureSignal]:
    """Return up to ``max_jobs`` failed jobs' trace tails for the commit.

    Pipelines still running (or green) are skipped. Jobs whose trace is
    missing (e.g. canceled before start) yield an empty tail.
    """
    project_quoted = urllib.parse.quote(str(project), safe="")
    signals: list[FailureSignal] = []
    with _client(token, base_url or _DEFAULT_BASE_URL) as client:
        for pipeline in _list_failed_pipelines(client, project_quoted, head_sha):
            if len(signals) >= max_jobs:
                break
            for job in _list_failed_jobs(
                client, project_quoted, int(pipeline["id"])
            ):
                if len(signals) >= max_jobs:
                    break
                tail = _fetch_job_trace_tail(
                    client, project_quoted, int(job["id"]), log_tail_chars
                )
                signals.append(_build_signal(pipeline, job, tail))
    log.info(
        "Collected %d GitLab failure signal(s) for %s",
        len(signals), head_sha[:8],
    )
    return signals


def _build_signal(pipeline: dict, job: dict, log_tail: str) -> FailureSignal:
    """Assemble a FailureSignal from a pipeline / job pair."""
    return FailureSignal(
        workflow_name=str(pipeline.get("ref") or pipeline.get("name") or ""),
        job_name=str(job.get("name") or ""),
        conclusion=str(job.get("status") or "failed"),
        log_tail=log_tail,
    )


def _client(token: str, base_url: str) -> httpx.Client:
    return httpx.Client(
        base_url=base_url.rstrip("/"),
        headers={
            "PRIVATE-TOKEN": token,
            "User-Agent": _USER_AGENT,
        },
        timeout=60.0,
    )


def _list_failed_pipelines(
    client: httpx.Client, project_quoted: str, head_sha: str
) -> list[dict]:
    response = client.get(
        f"/projects/{project_quoted}/pipelines",
        params={
            "sha": head_sha,
            "status": "failed",
            "per_page": _PIPELINES_PER_SHA,
        },
    )
    response.raise_for_status()
    pipelines = response.json()
    return pipelines if isinstance(pipelines, list) else []


def _list_failed_jobs(
    client: httpx.Client, project_quoted: str, pipeline_id: int
) -> list[dict]:
    out: list[dict] = []
    page = 1
    while True:
        response = client.get(
            f"/projects/{project_quoted}/pipelines/{pipeline_id}/jobs",
            params={
                "scope[]": "failed",
                "per_page": _JOBS_PER_PAGE,
                "page": page,
            },
        )
        response.raise_for_status()
        batch = response.json()
        if not batch:
            break
        out.extend(batch)
        if len(batch) < _JOBS_PER_PAGE:
            break
        page += 1
    return out


def _fetch_job_trace_tail(
    client: httpx.Client, project_quoted: str, job_id: int, tail_chars: int
) -> str:
    """Fetch one job's plain-text trace, truncated to the tail."""
    response = client.get(f"/projects/{project_quoted}/jobs/{job_id}/trace")
    if response.status_code == 404:
        return ""
    response.raise_for_status()
    text = response.text
    if len(text) > tail_chars:
        return text[-tail_chars:]
    return text


__all__ = ["fetch_gitlab_ci_failure_signals"]
