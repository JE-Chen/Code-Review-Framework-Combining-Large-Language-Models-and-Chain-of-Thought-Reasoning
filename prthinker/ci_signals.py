"""Fetch CI failure signals for a PR head SHA via the GitHub Actions API.

The reviewer prepends these signals to the diff so the model can correlate
a flagged change with an observed test/lint failure. We deliberately fetch
only *failed* jobs and truncate each log to the tail — the goal is to give
the model a smoking gun, not the entire build output.
"""

from __future__ import annotations

import logging
import zipfile
from dataclasses import dataclass
from io import BytesIO

import httpx

log = logging.getLogger(__name__)

_API_ROOT = "https://api.github.com"
_USER_AGENT = "prthinker/0.1"


@dataclass
class FailureSignal:
    workflow_name: str
    job_name: str
    conclusion: str
    log_tail: str


def fetch_ci_failure_signals(
    repo: str,
    head_sha: str,
    token: str,
    *,
    max_jobs: int = 5,
    log_tail_chars: int = 4000,
    base_url: str = _API_ROOT,
) -> list[FailureSignal]:
    """Return up to `max_jobs` failed jobs' tail logs for the commit.

    Workflow runs that are still in progress, or that completed successfully,
    are skipped. Jobs without logs (e.g. cancelled) yield an empty tail.
    ``base_url`` points the client at a GitHub Enterprise API root; the
    default keeps the public cloud.
    """
    signals: list[FailureSignal] = []
    with _client(token, base_url) as client:
        for run in _list_failed_runs(client, repo, head_sha):
            if len(signals) >= max_jobs:
                break
            for job in _list_failed_jobs(client, repo, int(run["id"])):
                if len(signals) >= max_jobs:
                    break
                tail = _fetch_job_log_tail(
                    client, repo, int(job["id"]), log_tail_chars
                )
                signals.append(_build_signal(run, job, tail))
    log.info("Collected %d failure signal(s) for %s", len(signals), head_sha[:8])
    return signals


def _build_signal(run: dict, job: dict, log_tail: str) -> FailureSignal:
    """Assemble a FailureSignal, falling back through the run/job name fields."""
    return FailureSignal(
        workflow_name=str(run.get("name") or run.get("path") or ""),
        job_name=str(job.get("name") or ""),
        conclusion=str(job.get("conclusion") or "failure"),
        log_tail=log_tail,
    )


def format_signals_block(signals: list[FailureSignal]) -> str:
    """Render signals as a fenced markdown block prepended to the diff.

    Empty list → empty string (no header emitted, so prompts aren't polluted
    with an empty section).
    """
    if not signals:
        return ""

    lines = [
        "<!-- CI Failure Signals -->",
        "# CI Failure Signals",
        "",
        "These are failed jobs from the latest CI run on this PR head.",
        "Correlate findings with the failures below when applicable; do NOT",
        "invent failures not present here.",
        "",
    ]
    for s in signals:
        lines += [
            f"## {s.workflow_name} / {s.job_name} ({s.conclusion})",
            "",
            "```",
            s.log_tail.strip() or "(no log captured)",
            "```",
            "",
        ]
    lines += ["<!-- End CI Failure Signals -->", "", ""]
    return "\n".join(lines)


def _client(token: str, base_url: str = _API_ROOT) -> httpx.Client:
    return httpx.Client(
        base_url=base_url.rstrip("/"),
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": _USER_AGENT,
        },
        timeout=60.0,
    )


def _list_failed_runs(
    client: httpx.Client, repo: str, head_sha: str
) -> list[dict]:
    response = client.get(
        f"/repos/{repo}/actions/runs",
        params={
            "head_sha": head_sha,
            "status": "completed",
            "per_page": 20,
        },
    )
    response.raise_for_status()
    runs = response.json().get("workflow_runs", [])
    return [r for r in runs if r.get("conclusion") == "failure"]


def _list_failed_jobs(client: httpx.Client, repo: str, run_id: int) -> list[dict]:
    out: list[dict] = []
    page = 1
    while True:
        response = client.get(
            f"/repos/{repo}/actions/runs/{run_id}/jobs",
            params={"per_page": 100, "page": page, "filter": "latest"},
        )
        response.raise_for_status()
        batch = response.json().get("jobs", [])
        if not batch:
            break
        out.extend(j for j in batch if j.get("conclusion") == "failure")
        if len(batch) < 100:
            break
        page += 1
    return out


def _fetch_job_log_tail(
    client: httpx.Client, repo: str, job_id: int, tail_chars: int
) -> str:
    """The Actions logs endpoint returns either gzipped text or a zip of step logs.

    We accept both: try as zip first, fall through to plain text.
    """
    response = client.get(
        f"/repos/{repo}/actions/jobs/{job_id}/logs",
        follow_redirects=True,
    )
    if response.status_code == 404:
        return ""
    response.raise_for_status()
    blob = response.content
    text = _extract_log_text(blob)
    if len(text) > tail_chars:
        return text[-tail_chars:]
    return text


def _extract_log_text(blob: bytes) -> str:
    # Some endpoints stream a zip of per-step .txt files. Concatenate them
    # so we have a single chronological log.
    try:
        with zipfile.ZipFile(BytesIO(blob)) as zf:
            parts = []
            for name in sorted(zf.namelist()):
                if name.endswith(".txt"):
                    with zf.open(name) as fh:
                        parts.append(fh.read().decode("utf-8", errors="replace"))
            if parts:
                return "\n".join(parts)
    except zipfile.BadZipFile:
        pass

    return blob.decode("utf-8", errors="replace")


__all__ = [
    "FailureSignal",
    "fetch_ci_failure_signals",
    "format_signals_block",
]
