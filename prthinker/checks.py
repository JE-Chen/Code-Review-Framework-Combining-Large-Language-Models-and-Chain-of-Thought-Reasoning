"""GitHub Checks API helper — pre-merge gate based on review findings.

The flow is two-step: create the check as `in_progress` when the workflow
starts, then PATCH it to `completed` with a conclusion once the pipeline
finishes. The conclusion is derived from the finding count above a
configurable severity floor (`error` by default), so this can be wired
into branch protection as a required status check.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterable, Literal

import httpx

from prthinker.config import GitHubConfig
from prthinker.schemas import InlineFinding, Severity

log = logging.getLogger(__name__)

_API_ROOT = "https://api.github.com"
_USER_AGENT = "prthinker/0.1"

GateFloor = Literal["none", "warning", "error"]
Conclusion = Literal["success", "failure", "neutral"]

_SEVERITY_ORDER: dict[Severity, int] = {"info": 0, "warning": 1, "error": 2}
_GATE_ORDER: dict[str, int] = {"none": 99, "warning": 1, "error": 2}


@dataclass
class CheckResult:
    conclusion: Conclusion
    title: str
    summary: str
    error_count: int
    warning_count: int
    info_count: int


def _client(token: str) -> httpx.Client:
    return httpx.Client(
        base_url=_API_ROOT,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": _USER_AGENT,
        },
        timeout=30.0,
    )


def _supersede_prior_check_runs(
    config: GitHubConfig,
    head_sha: str,
    name: str,
) -> None:
    """Mark every previous ``name`` check run on this SHA as superseded.

    Re-running a workflow (or a matrix shard finishing after a manual
    cancel + restart) leaves stale prthinker check runs attached to
    the same commit, so the PR's Checks tab shows multiple
    same-named entries. GitHub does not allow deleting check runs,
    but PATCHing them to ``status="completed"`` /
    ``conclusion="neutral"`` collapses them into a "superseded" state
    that the UI groups under the live one. The new in-progress run is
    POSTed after this returns.

    Failures here are logged at WARNING but never raised — gate
    opening must not be blocked by a cleanup hiccup.
    """
    with _client(config.token) as client:
        page = 1
        prior_ids: list[int] = []
        while True:
            response = client.get(
                f"/repos/{config.repo}/commits/{head_sha}/check-runs",
                params={"check_name": name, "per_page": 100, "page": page},
            )
            if response.status_code >= 400:
                log.warning(
                    "List prior check runs failed (%d): %s",
                    response.status_code, response.text,
                )
                return
            payload = response.json() or {}
            runs = payload.get("check_runs") or []
            for run in runs:
                if run.get("name") == name:
                    prior_ids.append(int(run["id"]))
            if len(runs) < 100:
                break
            page += 1

        if not prior_ids:
            return

        for check_id in prior_ids:
            patch = client.patch(
                f"/repos/{config.repo}/check-runs/{check_id}",
                json={
                    "status": "completed",
                    "conclusion": "neutral",
                    "output": {
                        "title": f"{name} — superseded",
                        "summary": (
                            "This check run was superseded by a newer "
                            f"{name} run on the same commit."
                        ),
                    },
                },
            )
            if patch.status_code >= 400:
                log.warning(
                    "Supersede check %d failed (%d): %s",
                    check_id, patch.status_code, patch.text,
                )
        log.info(
            "Superseded %d prior %s check run(s) on %s",
            len(prior_ids), name, head_sha[:8],
        )


def create_check_run(
    config: GitHubConfig,
    head_sha: str,
    *,
    name: str = "prthinker",
) -> int:
    """Open an `in_progress` check run on the PR head commit.

    Returns the check_run id so the caller can PATCH it on completion.
    """
    try:
        _supersede_prior_check_runs(config, head_sha, name)
    except Exception as exc:  # noqa: BLE001 — cleanup must never block opening
        log.warning("Prior check-run cleanup failed (%s); continuing", exc)

    with _client(config.token) as client:
        response = client.post(
            f"/repos/{config.repo}/check-runs",
            json={
                "name": name,
                "head_sha": head_sha,
                "status": "in_progress",
            },
        )
        response.raise_for_status()
        check_id = int(response.json()["id"])
        log.info("Opened check run id=%d on %s", check_id, head_sha[:8])
        return check_id


def complete_check_run(
    config: GitHubConfig,
    check_id: int,
    result: CheckResult,
) -> None:
    payload = {
        "status": "completed",
        "conclusion": result.conclusion,
        "output": {
            "title": result.title,
            "summary": result.summary,
        },
    }
    with _client(config.token) as client:
        response = client.patch(
            f"/repos/{config.repo}/check-runs/{check_id}",
            json=payload,
        )
        response.raise_for_status()
        log.info(
            "Completed check run id=%d conclusion=%s",
            check_id, result.conclusion,
        )


def evaluate_gate(
    findings: Iterable[InlineFinding],
    gate_on: GateFloor = "error",
) -> CheckResult:
    """Decide pass/fail from the findings list at the configured floor.

    `gate_on`:
      - "none"    → always pass (success regardless of findings)
      - "warning" → fail if any warning or error finding
      - "error"   → fail only on error-severity findings
    """
    counts: dict[Severity, int] = {"error": 0, "warning": 0, "info": 0}
    for f in findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1

    if gate_on == "none":
        conclusion: Conclusion = "success"
    else:
        floor = _GATE_ORDER[gate_on]
        triggered = any(
            _SEVERITY_ORDER[sev] >= floor and counts[sev] > 0
            for sev in counts
        )
        conclusion = "failure" if triggered else "success"

    title_bits = []
    if counts["error"]:
        title_bits.append(f"{counts['error']} error")
    if counts["warning"]:
        title_bits.append(f"{counts['warning']} warning")
    if counts["info"]:
        title_bits.append(f"{counts['info']} info")
    title = ", ".join(title_bits) if title_bits else "No findings"

    summary_lines = [
        f"Gate: `{gate_on}` (fails on this severity or higher)",
        "",
        f"- 🔴 errors: **{counts['error']}**",
        f"- 🟡 warnings: **{counts['warning']}**",
        f"- 🔵 info: **{counts['info']}**",
    ]
    return CheckResult(
        conclusion=conclusion,
        title=title,
        summary="\n".join(summary_lines),
        error_count=counts["error"],
        warning_count=counts["warning"],
        info_count=counts["info"],
    )


__all__ = [
    "CheckResult",
    "GateFloor",
    "create_check_run",
    "complete_check_run",
    "evaluate_gate",
]
