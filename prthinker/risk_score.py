"""Per-file risk scoring — churn + complexity + bug history.

Most LLM reviewers treat every file in a diff equally. In practice the
file that breaks production usually has three properties: it has been
churned a lot recently, it is large / complex, and it has appeared in
many past bug-fix commits. This module computes a *risk score* per
file from those three signals so the pipeline can allocate the
findings budget proportional to risk.

Signals (all relative to a configurable lookback window):

* **churn** — number of commits touching the file.
* **complexity** — heuristic line-count proxy (we do not import radon
  here so the runner profile stays thin). Optional: callers may pass a
  pre-computed complexity dict.
* **bug history** — commits whose message starts with ``fix:`` /
  ``bug`` / ``revert`` (case-insensitive substring match).

Score combination is a simple normalised linear combination with
documented default weights. Per ``paper_rule.md`` no-fabrication: the
weights are framework defaults, not a calibrated formula; they should
be tuned per project before publishing any number.
"""

from __future__ import annotations

import logging
import re
import subprocess  # noqa: S404 — only runs git, never shell=True, only on trusted local paths
from dataclasses import dataclass
from pathlib import Path

log = logging.getLogger(__name__)


DEFAULT_CHURN_WEIGHT = 0.4
DEFAULT_COMPLEXITY_WEIGHT = 0.3
DEFAULT_BUG_WEIGHT = 0.3


@dataclass(frozen=True)
class RiskScore:
    """Pure-data per-file risk summary.

    All raw counts are exposed so the formatter can show the breakdown
    instead of an opaque scalar; ``score`` is the normalised
    [0, 1] number used for budget scaling.
    """

    path: str
    churn: int = 0
    complexity_proxy: int = 0
    bug_commits: int = 0
    score: float = 0.0


@dataclass(frozen=True)
class RiskWeights:
    churn: float = DEFAULT_CHURN_WEIGHT
    complexity: float = DEFAULT_COMPLEXITY_WEIGHT
    bug: float = DEFAULT_BUG_WEIGHT


_BUG_RE = re.compile(r"\b(fix|bug|revert)\b", re.IGNORECASE)


def _run_git(args: list[str], *, cwd: Path) -> str:
    """Invoke git with an argv list (no shell). Returns stdout on success
    or ``""`` on any failure — risk scoring is best-effort and must
    never crash the review.
    """
    try:
        proc = subprocess.run(  # noqa: S603 — argv list, no shell, trusted repo
            ["git", *args],  # noqa: S607 — git resolved from PATH
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
    except FileNotFoundError:
        log.warning("risk_score: git not on PATH; returning zero scores")
        return ""
    except subprocess.TimeoutExpired:
        log.warning("risk_score: git command timed out")
        return ""
    if proc.returncode != 0:
        log.debug("risk_score: git args=%s returned %d: %s",
                  args, proc.returncode, proc.stderr[:200])
        return ""
    return proc.stdout


def _churn_and_bug_counts(
    paths: list[str], *, workdir: Path, since: str = "90.days.ago",
) -> dict[str, tuple[int, int]]:
    """Return ``{path: (commit_count, bug_commit_count)}`` over the
    lookback window. One ``git log`` call per file keeps the
    implementation tiny; for very large PRs this is still cheap
    because we only touch files in the diff.
    """
    out: dict[str, tuple[int, int]] = {}
    for path in paths:
        log_text = _run_git(
            ["log", f"--since={since}", "--format=%s", "--", path],
            cwd=workdir,
        )
        if not log_text:
            out[path] = (0, 0)
            continue
        lines = [ln for ln in log_text.splitlines() if ln.strip()]
        churn = len(lines)
        bugs = sum(1 for ln in lines if _BUG_RE.search(ln))
        out[path] = (churn, bugs)
    return out


def _complexity_proxy(path: str, *, workdir: Path) -> int:
    """Cheap complexity proxy: total line count of the file at HEAD.

    Avoids importing radon (heavy) and works for every language; the
    actual cyclomatic complexity could be plugged in later via a
    callback. Returns 0 when the file no longer exists at HEAD (e.g.
    it was added in the PR).
    """
    full = workdir / path
    if not full.exists() or not full.is_file():
        return 0
    try:
        with full.open("rb") as fh:
            return sum(1 for _ in fh)
    except OSError:
        return 0


def _normalise(values: list[int]) -> list[float]:
    if not values:
        return []
    hi = max(values)
    if hi == 0:
        return [0.0 for _ in values]
    return [v / hi for v in values]


def compute_risk_scores(
    paths: list[str], *,
    workdir: Path,
    weights: RiskWeights | None = None,
    since: str = "90.days.ago",
) -> list[RiskScore]:
    """Pure-ish entry point — only side effect is calling git.

    All values are normalised across the input ``paths`` so the highest
    file in the PR scores 1.0 on each axis. The aggregate ``score`` is a
    weighted sum of the three normalised components.
    """
    w = weights or RiskWeights()
    pairs = _churn_and_bug_counts(paths, workdir=workdir, since=since)
    complexity_raw = {p: _complexity_proxy(p, workdir=workdir) for p in paths}

    churn_raw = [pairs[p][0] for p in paths]
    bug_raw = [pairs[p][1] for p in paths]
    cmp_raw = [complexity_raw[p] for p in paths]

    churn_n = _normalise(churn_raw)
    bug_n = _normalise(bug_raw)
    cmp_n = _normalise(cmp_raw)

    out: list[RiskScore] = []
    for i, p in enumerate(paths):
        score = (
            w.churn * churn_n[i]
            + w.complexity * cmp_n[i]
            + w.bug * bug_n[i]
        )
        out.append(RiskScore(
            path=p,
            churn=churn_raw[i],
            complexity_proxy=cmp_raw[i],
            bug_commits=bug_raw[i],
            score=score,
        ))
    return out


def budget_for_file(
    score: float, *,
    base_budget: int,
    floor: int = 2,
    ceiling: int | None = None,
) -> int:
    """Scale ``base_budget`` proportional to the [0, 1] risk score.

    A file with score 0.0 still gets ``floor`` findings worth of
    attention (the model can always say "no issues"); a file with
    score 1.0 gets the full ``ceiling`` (defaults to ``2 * base``).
    """
    if ceiling is None:
        ceiling = base_budget * 2
    span = max(0, ceiling - floor)
    return int(floor + round(span * max(0.0, min(1.0, score))))


__all__ = [
    "DEFAULT_BUG_WEIGHT",
    "DEFAULT_CHURN_WEIGHT",
    "DEFAULT_COMPLEXITY_WEIGHT",
    "RiskScore",
    "RiskWeights",
    "budget_for_file",
    "compute_risk_scores",
]
