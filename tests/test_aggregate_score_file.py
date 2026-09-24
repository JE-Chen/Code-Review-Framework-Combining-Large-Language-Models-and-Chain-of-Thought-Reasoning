"""Tests for the selectable score filename in ``scores.aggregate_rag_quality``.

A group that is re-judged in a later session writes its scores under a second
filename so the original scores stay intact.  ``load_scores`` must be able to
read either set, because pairing two arms judged in the same session is what
removes judge drift from a cross-run comparison.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCORES_DIR = Path(__file__).resolve().parents[1] / "scores"
if str(SCORES_DIR) not in sys.path:
    sys.path.insert(0, str(SCORES_DIR))

pytest.importorskip("scipy", reason="aggregate_rag_quality imports scipy.stats")

from aggregate_rag_quality import SCORE_FILE, load_scores  # noqa: E402


SCORE_LINE = (
    '("readability": {readability}, "constructiveness": {constructiveness}, '
    '"correctness": {correctness}, "coverage": {coverage}, '
    '"comprehensiveness": {comprehensiveness})\n'
)


def _write_case(root: Path, case_id: str, filename: str, **values: int) -> None:
    case_dir = root / "cot" / case_id
    case_dir.mkdir(parents=True, exist_ok=True)
    (case_dir / filename).write_text(SCORE_LINE.format(**values), encoding="utf-8")


def _scores(**overrides: int) -> dict[str, int]:
    values = {
        "readability": 90,
        "constructiveness": 88,
        "correctness": 80,
        "coverage": 82,
        "comprehensiveness": 86,
    }
    values.update(overrides)
    return values


def test_default_filename_unchanged(tmp_path: Path) -> None:
    """Callers that omit the argument still read the original score set."""
    _write_case(tmp_path, "cot_case_1", SCORE_FILE, **_scores())

    rows = load_scores(tmp_path)

    assert rows == {"cot_case_1": _scores()}


def test_alternate_filename_selects_rejudged_set(tmp_path: Path) -> None:
    """A re-judged set is readable without disturbing the original one."""
    _write_case(tmp_path, "cot_case_1", SCORE_FILE, **_scores())
    _write_case(tmp_path, "cot_case_1", "our_score_rejudge.md",
                **_scores(coverage=91))

    original = load_scores(tmp_path)
    rejudged = load_scores(tmp_path, "our_score_rejudge.md")

    assert original["cot_case_1"]["coverage"] == 82
    assert rejudged["cot_case_1"]["coverage"] == 91


def test_missing_filename_yields_no_rows(tmp_path: Path) -> None:
    """An unmatched filename is an empty result, not a crash."""
    _write_case(tmp_path, "cot_case_1", SCORE_FILE, **_scores())

    assert load_scores(tmp_path, "no_such_score.md") == {}


def test_incomplete_score_file_is_rejected(tmp_path: Path) -> None:
    """A truncated score line fails loudly rather than pairing bad data."""
    case_dir = tmp_path / "cot" / "cot_case_1"
    case_dir.mkdir(parents=True)
    (case_dir / "partial.md").write_text('("readability": 90)\n', encoding="utf-8")

    with pytest.raises(ValueError, match="incomplete score file"):
        load_scores(tmp_path, "partial.md")


def test_duplicate_case_id_is_rejected(tmp_path: Path) -> None:
    """The same case id under two condition subtrees is a pairing hazard."""
    _write_case(tmp_path / "a", "cot_case_1", "dup.md", **_scores())
    _write_case(tmp_path / "b", "cot_case_1", "dup.md", **_scores())

    with pytest.raises(ValueError, match="duplicate case id"):
        load_scores(tmp_path, "dup.md")
