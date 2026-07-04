"""Deterministic, auditable scoring for structured review findings."""

from __future__ import annotations
import json
import random
import re
from dataclasses import dataclass
from typing import Any, Sequence
from pathlib import Path

_MESSAGE_JACCARD_FLOOR = 0.35
_CI_LOW = 0.025
_CI_HIGH = 0.975
_QA_DATASET = "codereviewqa"
_RETRIEVAL_DATASETS = {"contextbench", "core-bench"}


@dataclass(frozen=True)
class FindingLabel:
    path: str = ""
    line: int | None = None
    message: str = ""
    kind: str = ""


@dataclass(frozen=True)
class CaseScore:
    case_id: str
    tp: int
    fp: int
    fn: int

    @property
    def precision(self):
        return self.tp / (self.tp + self.fp) if self.tp + self.fp else 1.0

    @property
    def recall(self):
        return self.tp / (self.tp + self.fn) if self.tp + self.fn else 1.0

    @property
    def f1(self):
        return (
            2 * self.precision * self.recall / (self.precision + self.recall)
            if self.precision + self.recall
            else 0.0
        )


def _coerce_line(raw: Any) -> int | None:
    """Coerce a raw line value to an int, or None when unparseable."""
    try:
        return int(raw) if raw is not None else None
    except (ValueError, TypeError):
        return None


def _finding_from_dict(row: dict[str, Any]) -> FindingLabel:
    """Build a FindingLabel from one raw finding dict."""
    return FindingLabel(
        str(row.get("path", row.get("file", ""))),
        _coerce_line(row.get("line", row.get("line_number"))),
        str(row.get("message", row.get("body", row.get("comment", "")))),
        str(row.get("kind", row.get("type", ""))),
    )


def _as_finding_list(value: Any) -> list[Any]:
    """Decode strings and unwrap dict envelopes to a list of raw findings."""
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            return []
    if isinstance(value, dict):
        value = value.get("findings", value.get("comments", []))
    return value if isinstance(value, list) else []


def normalize(value: Any) -> list[FindingLabel]:
    """Normalize an arbitrary finding payload to a list of FindingLabel."""
    return [
        _finding_from_dict(row)
        for row in _as_finding_list(value)
        if isinstance(row, dict)
    ]


def _tokens(s):
    return set(re.findall(r"[a-z_][a-z0-9_]+", s.lower()))


def _path_conflict(a, b) -> bool:
    """True when both findings name a different file."""
    return bool(a.path and b.path and a.path.replace("\\", "/") != b.path.replace("\\", "/"))


def _line_conflict(a, b, tolerance) -> bool:
    """True when both line numbers exist and differ beyond the tolerance."""
    return a.line is not None and b.line is not None and abs(a.line - b.line) > tolerance


def _kind_conflict(a, b) -> bool:
    """True when both kinds exist and differ."""
    return bool(a.kind and b.kind and a.kind != b.kind)


def _message_match(a, b) -> bool:
    """True when message tokens clear the Jaccard floor, else fall back to lines."""
    x, y = _tokens(a.message), _tokens(b.message)
    if x and y:
        return len(x & y) / len(x | y) >= _MESSAGE_JACCARD_FLOOR
    return a.line is not None and b.line is not None


def matches(a, b, tolerance=2):
    """True when two findings describe the same issue within the tolerance."""
    if _path_conflict(a, b) or _line_conflict(a, b, tolerance) or _kind_conflict(a, b):
        return False
    return _message_match(a, b)


def score_case(case_id, predicted, expected):
    left = set(range(len(expected)))
    tp = 0
    for p in predicted:
        i = next((i for i in left if matches(p, expected[i])), None)
        if i is not None:
            left.remove(i)
            tp += 1
    return CaseScore(case_id, tp, len(predicted) - tp, len(left))


def _prf(tp, fp, fn):
    """Return (precision, recall, f1) for aggregate confusion counts."""
    p = tp / (tp + fp) if tp + fp else 1
    r = tp / (tp + fn) if tp + fn else 1
    f = 2 * p * r / (p + r) if p + r else 0
    return p, r, f


def _bootstrap_f1_ci(scores, samples, seed):
    """Return the 95% bootstrap CI for mean F1 across the cases."""
    rng = random.Random(seed)  # nosec B311 — deterministic bootstrap resampling, not security
    boot = sorted(
        sum(rng.choice(scores).f1 for _ in scores) / len(scores) for _ in range(samples)
    )
    return [boot[int(_CI_LOW * (samples - 1))], boot[int(_CI_HIGH * (samples - 1))]]


def aggregate(scores: Sequence[CaseScore], samples=1000, seed=0):
    """Aggregate case scores into precision/recall/F1 with a bootstrap CI."""
    if not scores:
        return {"cases": 0, "precision": 0, "recall": 0, "f1": 0, "f1_ci95": [0, 0]}
    p, r, f = _prf(
        sum(x.tp for x in scores), sum(x.fp for x in scores), sum(x.fn for x in scores)
    )
    return {
        "cases": len(scores),
        "precision": p,
        "recall": r,
        "f1": f,
        "f1_ci95": _bootstrap_f1_ci(scores, samples, seed),
    }


def _load_cases(cases_path: str | Path) -> dict[str, Any]:
    """Load canonical benchmark cases indexed by case ID."""
    cases: dict[str, Any] = {}
    with Path(cases_path).open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                row = json.loads(line)
                cases[str(row["case_id"])] = row
    return cases


def _score_choice(case_id, raw, metadata) -> CaseScore:
    """Score an exact-match code-review comprehension answer."""
    predicted = str(raw).strip().strip('"').lower()
    expected_answer = str(metadata.get("answer", "")).strip().lower()
    if predicted == expected_answer:
        return CaseScore(case_id, 1, 0, 0)
    return CaseScore(case_id, 0, 1, 1)


def _score_retrieval(case_id, raw, metadata) -> CaseScore:
    """Score a context-retrieval case by set overlap of retrieved IDs."""
    try:
        payload = json.loads(raw) if isinstance(raw, str) else raw
    except json.JSONDecodeError:
        payload = {}
    predicted = set(payload.get("retrieved", [])) if isinstance(payload, dict) else set()
    expected_context = set(metadata.get("gold_context", []))
    hits = len(predicted & expected_context)
    return CaseScore(case_id, hits, len(predicted) - hits, len(expected_context) - hits)


def _score_outcome(case_id, raw, metadata) -> CaseScore:
    """Dispatch one outcome to the evaluator for its dataset family."""
    dataset = metadata.get("dataset", "")
    if dataset == _QA_DATASET:
        return _score_choice(case_id, raw, metadata)
    if dataset in _RETRIEVAL_DATASETS:
        return _score_retrieval(case_id, raw, metadata)
    return score_case(
        case_id, normalize(raw), normalize(metadata.get("ground_truth", []))
    )


def score_files(cases_path: str | Path, outcomes_path: str | Path) -> list[CaseScore]:
    """Score canonical cases against raw structured benchmark outcomes."""
    cases = _load_cases(cases_path)
    scores: list[CaseScore] = []
    with Path(outcomes_path).open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            case_id = str(row["case_id"])
            if case_id not in cases:
                raise ValueError(f"outcome references unknown case {case_id!r}")
            metadata = cases[case_id].get("metadata", {})
            scores.append(_score_outcome(case_id, row.get("raw_output", ""), metadata))
    return scores
