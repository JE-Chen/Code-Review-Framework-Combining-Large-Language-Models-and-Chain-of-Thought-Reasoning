"""Deterministic, auditable scoring for structured review findings."""

from __future__ import annotations
import json
import random
import re
from dataclasses import dataclass
from typing import Any, Sequence
from pathlib import Path


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


def normalize(value: Any) -> list[FindingLabel]:
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            return []
    if isinstance(value, dict):
        value = value.get("findings", value.get("comments", []))
    out = []
    for x in value if isinstance(value, list) else []:
        if not isinstance(x, dict):
            continue
        raw = x.get("line", x.get("line_number"))
        line = None
        try:
            line = int(raw) if raw is not None else None
        except (ValueError, TypeError):
            pass
        out.append(
            FindingLabel(
                str(x.get("path", x.get("file", ""))),
                line,
                str(x.get("message", x.get("body", x.get("comment", "")))),
                str(x.get("kind", x.get("type", ""))),
            )
        )
    return out


def _tokens(s):
    return set(re.findall(r"[a-z_][a-z0-9_]+", s.lower()))


def matches(a, b, tolerance=2):
    if a.path and b.path and a.path.replace("\\", "/") != b.path.replace("\\", "/"):
        return False
    if a.line is not None and b.line is not None and abs(a.line - b.line) > tolerance:
        return False
    if a.kind and b.kind and a.kind != b.kind:
        return False
    x, y = _tokens(a.message), _tokens(b.message)
    return (
        (len(x & y) / len(x | y) >= 0.35)
        if x and y
        else a.line is not None and b.line is not None
    )


def score_case(case_id, predicted, expected):
    left = set(range(len(expected)))
    tp = 0
    for p in predicted:
        i = next((i for i in left if matches(p, expected[i])), None)
        if i is not None:
            left.remove(i)
            tp += 1
    return CaseScore(case_id, tp, len(predicted) - tp, len(left))


def aggregate(scores: Sequence[CaseScore], samples=1000, seed=0):
    if not scores:
        return {"cases": 0, "precision": 0, "recall": 0, "f1": 0, "f1_ci95": [0, 0]}
    tp = sum(x.tp for x in scores)
    fp = sum(x.fp for x in scores)
    fn = sum(x.fn for x in scores)
    p = tp / (tp + fp) if tp + fp else 1
    r = tp / (tp + fn) if tp + fn else 1
    f = 2 * p * r / (p + r) if p + r else 0
    rng = random.Random(seed)  # nosec B311 — deterministic bootstrap resampling, not security
    boot = sorted(
        sum(rng.choice(scores).f1 for _ in scores) / len(scores) for _ in range(samples)
    )
    return {
        "cases": len(scores),
        "precision": p,
        "recall": r,
        "f1": f,
        "f1_ci95": [boot[int(0.025 * (samples - 1))], boot[int(0.975 * (samples - 1))]],
    }


def score_files(cases_path: str | Path, outcomes_path: str | Path) -> list[CaseScore]:
    """Score canonical cases against raw structured benchmark outcomes."""
    cases: dict[str, Any] = {}
    with Path(cases_path).open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                row = json.loads(line)
                cases[str(row["case_id"])] = row
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
            dataset = metadata.get("dataset", "")
            raw = row.get("raw_output", "")
            if dataset == "codereviewqa":
                predicted = str(raw).strip().strip('"').lower()
                expected_answer = str(metadata.get("answer", "")).strip().lower()
                scores.append(CaseScore(case_id, 1, 0, 0) if predicted == expected_answer else CaseScore(case_id, 0, 1, 1))
            elif dataset in {"contextbench", "core-bench"}:
                try:
                    payload = json.loads(raw) if isinstance(raw, str) else raw
                except json.JSONDecodeError:
                    payload = {}
                predicted = set(payload.get("retrieved", [])) if isinstance(payload, dict) else set()
                expected_context = set(metadata.get("gold_context", []))
                hits = len(predicted & expected_context)
                scores.append(CaseScore(case_id, hits, len(predicted)-hits, len(expected_context)-hits))
            else:
                expected = metadata.get("ground_truth", [])
                scores.append(score_case(case_id, normalize(raw), normalize(expected)))
    return scores
