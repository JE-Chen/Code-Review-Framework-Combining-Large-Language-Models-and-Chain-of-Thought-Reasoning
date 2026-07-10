"""GitHub Checks API helper — pre-merge gate based on review findings.

The flow is two-step: create the check as `in_progress` when the workflow
starts, then PATCH it to `completed` with a conclusion once the pipeline
finishes. The conclusion is derived from the finding count above a
configurable severity floor (`error` by default), so this can be wired
into branch protection as a required status check.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Iterable, Literal

import httpx

from prthinker.config import GitHubConfig
from prthinker.github_api import client_for
from prthinker.schemas import InlineFinding, Severity

log = logging.getLogger(__name__)

GateFloor = Literal["none", "warning", "error"]
Conclusion = Literal["success", "failure", "neutral"]

_SEVERITY_ORDER: dict[Severity, int] = {"info": 0, "warning": 1, "error": 2}
# "none" is absent on purpose: _derive_conclusion early-returns before the
# lookup, so only the gating floors need an order value.
_GATE_ORDER: dict[str, int] = {"warning": 1, "error": 2}


@dataclass
class CheckResult:
    conclusion: Conclusion
    title: str
    summary: str
    error_count: int
    warning_count: int
    info_count: int
    annotations: list[dict] = field(default_factory=list)


# Check Run annotations render per-line on the Files-changed and Checks
# tabs. Unlike review comments, a bad line does not 422 the batch, so this
# is a robust parallel channel. GitHub accepts at most 50 per request.
_ANNOTATION_BATCH = 50
_LEVEL_BY_SEVERITY: dict[Severity, str] = {
    "error": "failure",
    "warning": "warning",
    "info": "notice",
}


def _build_annotations(findings: list[InlineFinding]) -> list[dict]:
    """Map findings to GitHub Check Run annotation payloads."""
    annotations: list[dict] = []
    for finding in findings:
        start = finding.line
        if finding.start_line is not None and finding.start_line <= finding.line:
            start = finding.start_line
        annotations.append({
            "path": finding.path,
            "start_line": start,
            "end_line": finding.line,
            "annotation_level": _LEVEL_BY_SEVERITY.get(finding.severity, "notice"),
            "message": finding.comment,
        })
    return annotations


def _list_prior_check_run_ids(
    client: httpx.Client,
    config: GitHubConfig,
    head_sha: str,
    name: str,
) -> list[int] | None:
    """Page through check-runs on head_sha; return matching ids or None on error."""
    prior_ids: list[int] = []
    page = 1
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
            return None
        payload = response.json() or {}
        runs = payload.get("check_runs") or []
        for run in runs:
            if run.get("name") == name:
                prior_ids.append(int(run["id"]))
        if len(runs) < 100:
            return prior_ids
        page += 1


def _patch_check_to_superseded(
    client: httpx.Client,
    config: GitHubConfig,
    check_id: int,
    name: str,
) -> None:
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
    with client_for(config) as client:
        prior_ids = _list_prior_check_run_ids(client, config, head_sha, name)
        if not prior_ids:
            return
        for check_id in prior_ids:
            _patch_check_to_superseded(client, config, check_id, name)
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

    with client_for(config) as client:
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


def _annotation_batches(annotations: list[dict]) -> list[list[dict]]:
    """Split annotations into GitHub-sized batches (≥1 batch, possibly empty)."""
    if not annotations:
        return [[]]
    return [
        annotations[i:i + _ANNOTATION_BATCH]
        for i in range(0, len(annotations), _ANNOTATION_BATCH)
    ]


def complete_check_run(
    config: GitHubConfig,
    check_id: int,
    result: CheckResult,
) -> None:
    # GitHub appends annotations across successive updates and caps each
    # request at 50, so a >50-finding review is sent over several PATCHes.
    batches = _annotation_batches(result.annotations)
    with client_for(config) as client:
        for batch in batches:
            output: dict[str, object] = {
                "title": result.title,
                "summary": result.summary,
            }
            if batch:
                output["annotations"] = batch
            response = client.patch(
                f"/repos/{config.repo}/check-runs/{check_id}",
                json={
                    "status": "completed",
                    "conclusion": result.conclusion,
                    "output": output,
                },
            )
            response.raise_for_status()
    log.info(
        "Completed check run id=%d conclusion=%s (%d annotation(s))",
        check_id, result.conclusion, len(result.annotations),
    )


def _count_by_severity(findings: Iterable[InlineFinding]) -> dict[Severity, int]:
    """Tally findings into per-severity counts seeded at zero."""
    counts: dict[Severity, int] = {"error": 0, "warning": 0, "info": 0}
    for f in findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1
    return counts


def _derive_conclusion(counts: dict[Severity, int], gate_on: GateFloor) -> Conclusion:
    """Map severity counts and the gate floor to a pass/fail conclusion."""
    if gate_on == "none":
        return "success"
    floor = _GATE_ORDER[gate_on]
    triggered = any(
        _SEVERITY_ORDER[sev] >= floor and counts[sev] > 0
        for sev in counts
    )
    return "failure" if triggered else "success"


def _build_title(counts: dict[Severity, int]) -> str:
    """Render the non-zero severity counts as a compact one-line title."""
    title_bits = []
    if counts["error"]:
        title_bits.append(f"{counts['error']} error")
    if counts["warning"]:
        title_bits.append(f"{counts['warning']} warning")
    if counts["info"]:
        title_bits.append(f"{counts['info']} info")
    return ", ".join(title_bits) if title_bits else "No findings"


def _build_summary(counts: dict[Severity, int], gate_on: GateFloor) -> str:
    """Render the markdown gate summary block for the check output."""
    summary_lines = [
        f"Gate: `{gate_on}` (fails on this severity or higher)",
        "",
        f"- 🔴 errors: **{counts['error']}**",
        f"- 🟡 warnings: **{counts['warning']}**",
        f"- 🔵 info: **{counts['info']}**",
    ]
    return "\n".join(summary_lines)


def evaluate_gate(
    findings: Iterable[InlineFinding],
    gate_on: GateFloor = "error",
    *,
    with_annotations: bool = False,
) -> CheckResult:
    """Decide pass/fail from the findings list at the configured floor.

    `gate_on`:
      - "none"    → always pass (success regardless of findings)
      - "warning" → fail if any warning or error finding
      - "error"   → fail only on error-severity findings

    When ``with_annotations`` is set, the result also carries per-line
    Check Run annotations built from the findings.
    """
    items = list(findings)
    counts = _count_by_severity(items)
    return CheckResult(
        conclusion=_derive_conclusion(counts, gate_on),
        title=_build_title(counts),
        summary=_build_summary(counts, gate_on),
        error_count=counts["error"],
        warning_count=counts["warning"],
        info_count=counts["info"],
        annotations=_build_annotations(items) if with_annotations else [],
    )


__all__ = [
    "CheckResult",
    "GateFloor",
    "create_check_run",
    "complete_check_run",
    "evaluate_gate",
]
