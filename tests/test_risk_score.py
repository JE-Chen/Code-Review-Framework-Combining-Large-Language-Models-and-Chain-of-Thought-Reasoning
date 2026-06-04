"""Risk-score module — pure-logic tests + a fast end-to-end run against
a temporary git repository.

The git-history part of the scorer shells out to ``git``; we set up a
tiny throwaway repo per test using subprocess so the test is fully
self-contained and offline.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from prthinker.risk_score import (
    RiskScore,
    RiskWeights,
    budget_for_file,
    compute_risk_scores,
    format_risk_note,
)


# ----- format_risk_note -------------------------------------------------

def test_risk_note_lists_high_risk_files() -> None:
    scores = [
        RiskScore(path="hot.py", churn=20, complexity_proxy=400,
                  bug_commits=5, score=0.82),
        RiskScore(path="cold.py", churn=1, complexity_proxy=10,
                  bug_commits=0, score=0.05),
    ]
    note = format_risk_note(scores)
    assert "1 high-risk file(s)" in note
    assert "`hot.py` — risk 0.82" in note
    assert "20 commits · 5 bug-fix · 400 lines" in note
    assert "cold.py" not in note  # below the high-risk floor


def test_risk_note_empty_when_all_low() -> None:
    scores = [RiskScore(path="a.py", score=0.1)]
    assert format_risk_note(scores) == ""


def test_risk_note_orders_by_score_desc() -> None:
    scores = [
        RiskScore(path="mid.py", score=0.6),
        RiskScore(path="top.py", score=0.9),
    ]
    note = format_risk_note(scores)
    assert note.index("top.py") < note.index("mid.py")


# ----- budget mapping ---------------------------------------------------

def test_budget_floor_for_zero_score() -> None:
    assert budget_for_file(0.0, base_budget=10, floor=2) == 2


def test_budget_ceiling_for_top_score() -> None:
    # default ceiling = base * 2
    assert budget_for_file(1.0, base_budget=10, floor=2) == 20


def test_budget_explicit_ceiling() -> None:
    assert budget_for_file(1.0, base_budget=10, floor=2, ceiling=12) == 12


def test_budget_clamps_out_of_range() -> None:
    assert budget_for_file(-1.0, base_budget=10) == 2  # default floor
    assert budget_for_file(2.0, base_budget=10) == 20


def test_budget_proportional_in_middle() -> None:
    # base=10 floor=2 ceiling=20 span=18 -> 0.5 score = 2 + 9 = 11
    assert budget_for_file(0.5, base_budget=10, floor=2) == 11


# ----- compute_risk_scores against a real git repo ----------------------

def _has_git() -> bool:
    return shutil.which("git") is not None


pytestmark = pytest.mark.skipif(
    not _has_git(), reason="git not available on PATH",
)


def _git(*args: str, cwd: Path) -> None:
    subprocess.run(
        ["git", *args], cwd=cwd, check=True,
        capture_output=True,
    )


def _setup_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git("init", "-q", cwd=repo)
    _git("config", "user.email", "t@example.com", cwd=repo)
    _git("config", "user.name", "test", cwd=repo)
    return repo


def _commit(repo: Path, path: str, content: str, message: str) -> None:
    full = repo / path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content, encoding="utf-8")
    _git("add", path, cwd=repo)
    _git("commit", "-q", "-m", message, cwd=repo)


def test_compute_returns_zero_when_no_history(tmp_path: Path) -> None:
    repo = _setup_repo(tmp_path)
    # Repo exists but has no commits; we still expect [].
    scores = compute_risk_scores([], workdir=repo)
    assert scores == []


def test_compute_normalises_across_paths(tmp_path: Path) -> None:
    repo = _setup_repo(tmp_path)
    # quiet.py: 1 commit, 1 line
    _commit(repo, "quiet.py", "x=1\n", "feat: quiet file")
    # hot.py: 5 commits, larger file, 2 bug-fix commits
    for i in range(5):
        msg = "fix: hot bug" if i % 2 == 0 else f"feat: hot {i}"
        _commit(repo, "hot.py", f"line{i}\n" * (i + 5), msg)

    scores = compute_risk_scores(
        ["quiet.py", "hot.py"], workdir=repo,
    )
    by_path = {s.path: s for s in scores}
    # hot has more churn, more lines, and more bug commits → higher score.
    assert by_path["hot.py"].score > by_path["quiet.py"].score
    assert by_path["hot.py"].churn >= 5
    assert by_path["hot.py"].bug_commits >= 1


def test_weights_are_documented_defaults() -> None:
    w = RiskWeights()
    # The three weights sum to 1.0 in the default mapping (documented).
    assert abs((w.churn + w.complexity + w.bug) - 1.0) < 1e-6


def test_missing_file_at_head_is_handled(tmp_path: Path) -> None:
    repo = _setup_repo(tmp_path)
    _commit(repo, "a.py", "x\n", "feat: a")
    # Compute risk for a path that doesn't exist on disk — should not crash.
    scores = compute_risk_scores(["nonexistent.py"], workdir=repo)
    assert len(scores) == 1
    assert scores[0].complexity_proxy == 0
    assert scores[0].score == 0.0


def test_no_git_repo_returns_zero_scores(tmp_path: Path) -> None:
    workdir = tmp_path / "not_a_repo"
    workdir.mkdir()
    scores = compute_risk_scores(["a.py"], workdir=workdir)
    assert len(scores) == 1
    assert scores[0].churn == 0
    assert scores[0].score == 0.0
