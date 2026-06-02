"""Tests for the benchmark evaluation-harness skeleton."""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

from prthinker.benchmark import (
    BenchmarkCase,
    BenchmarkOutcome,
    run_cases,
    write_outcomes,
)

from .conftest import FakeBackend


def test_run_cases_records_raw_outputs_in_order() -> None:
    backend = FakeBackend(["out-a", "out-b", "out-c"])
    cases = [
        BenchmarkCase(case_id="a", prompt="prompt-a"),
        BenchmarkCase(case_id="b", prompt="prompt-b"),
        BenchmarkCase(case_id="c", prompt="prompt-c"),
    ]

    outcomes = run_cases(backend, cases)

    assert [o.case_id for o in outcomes] == ["a", "b", "c"]
    assert [o.raw_output for o in outcomes] == ["out-a", "out-b", "out-c"]
    # Backend was driven once per case, prompts preserved in order.
    assert [prompt for prompt, _ in backend.calls] == [
        "prompt-a",
        "prompt-b",
        "prompt-c",
    ]


def test_run_cases_empty_returns_empty_list() -> None:
    backend = FakeBackend(["unused"])
    assert run_cases(backend, []) == []
    assert backend.calls == []


def test_run_cases_single_case() -> None:
    backend = FakeBackend(["only"])
    outcomes = run_cases(backend, [BenchmarkCase(case_id="x", prompt="p")])
    assert outcomes == [BenchmarkOutcome(case_id="x", raw_output="only")]


def test_run_cases_passes_max_new_tokens() -> None:
    backend = FakeBackend(["r"])
    run_cases(
        backend,
        [BenchmarkCase(case_id="x", prompt="p")],
        max_new_tokens=7,
    )
    assert backend.calls == [("p", 7)]


def test_run_cases_default_max_new_tokens() -> None:
    backend = FakeBackend(["r"])
    run_cases(backend, [BenchmarkCase(case_id="x", prompt="p")])
    _prompt, max_new_tokens = backend.calls[0]
    assert max_new_tokens == 1024


def test_write_outcomes_round_trips_to_jsonl(tmp_path: Path) -> None:
    outcomes = [
        BenchmarkOutcome(case_id="a", raw_output="line one\nstill a"),
        BenchmarkOutcome(case_id="b", raw_output="行 unicode"),
    ]
    path = tmp_path / "outcomes.jsonl"

    write_outcomes(outcomes, path)

    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
    ]
    reloaded = [BenchmarkOutcome.from_dict(row) for row in rows]
    assert reloaded == outcomes


def test_write_outcomes_empty_creates_empty_file(tmp_path: Path) -> None:
    path = tmp_path / "empty.jsonl"
    write_outcomes([], path)
    assert path.read_text(encoding="utf-8") == ""


def test_write_outcomes_accepts_str_path(tmp_path: Path) -> None:
    path = tmp_path / "str.jsonl"
    write_outcomes(
        [BenchmarkOutcome(case_id="a", raw_output="x")], str(path)
    )
    assert path.exists()


def test_outcome_to_dict_from_dict_round_trip() -> None:
    outcome = BenchmarkOutcome(case_id="a", raw_output="payload")
    assert BenchmarkOutcome.from_dict(outcome.to_dict()) == outcome


def test_outcome_has_no_numeric_score_field() -> None:
    field_names = {f.name for f in dataclasses.fields(BenchmarkOutcome)}
    # Skeleton emits raw output only — no scoring / metric fields.
    assert field_names == {"case_id", "raw_output"}
    for forbidden in ("score", "metric", "rating", "accuracy", "value"):
        assert forbidden not in field_names
    outcome = BenchmarkOutcome(case_id="a", raw_output="x")
    for _name, field_value in vars(outcome).items():
        assert not isinstance(field_value, (int, float))


def test_dataclasses_are_frozen() -> None:
    case = BenchmarkCase(case_id="a", prompt="p")
    outcome = BenchmarkOutcome(case_id="a", raw_output="x")
    for frozen in (case, outcome):
        try:
            frozen.case_id = "mutated"  # type: ignore[misc]
        except dataclasses.FrozenInstanceError:
            continue
        raise AssertionError("dataclass should be frozen")
