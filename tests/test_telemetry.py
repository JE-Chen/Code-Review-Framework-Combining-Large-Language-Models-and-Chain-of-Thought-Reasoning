"""Aggregation branch coverage for :mod:`prthinker.telemetry`."""

from __future__ import annotations

import time

import pytest

from prthinker.telemetry import CallRecord, TelemetrySink, _stats_from_rows


@pytest.fixture
def sink(tmp_path):
    return TelemetrySink(tmp_path / "telemetry.sqlite")


def _rec(backend="openai", model="gpt-4o-mini", latency=100.0, cache_hit=False):
    return CallRecord(
        backend=backend,
        model=model,
        prompt_tokens=10,
        completion_tokens=5,
        tokens_estimated=False,
        latency_ms=latency,
        cache_hit=cache_hit,
    )


def test_aggregate_empty_returns_empty_list(sink) -> None:
    assert sink.aggregate() == []


def test_aggregate_groups_by_backend_and_model(sink) -> None:
    sink.record(_rec(backend="openai", model="a"))
    sink.record(_rec(backend="openai", model="b"))
    sink.record(_rec(backend="anthropic", model="a"))
    stats = sink.aggregate()
    assert {(s.backend, s.model) for s in stats} == {
        ("openai", "a"),
        ("openai", "b"),
        ("anthropic", "a"),
    }


def test_aggregate_folds_all_calls_for_one_key(sink) -> None:
    sink.record(_rec(latency=100.0, cache_hit=True))
    sink.record(_rec(latency=300.0))
    stats = sink.aggregate()
    assert len(stats) == 1
    only = stats[0]
    assert only.calls == 2
    assert only.cache_hits == 1
    assert only.prompt_tokens == 20
    assert only.completion_tokens == 10
    assert only.latency_p50_ms == 200.0


def test_aggregate_orders_by_backend_then_model(sink) -> None:
    sink.record(_rec(backend="openai", model="b"))
    sink.record(_rec(backend="anthropic", model="z"))
    sink.record(_rec(backend="openai", model="a"))
    stats = sink.aggregate()
    assert [(s.backend, s.model) for s in stats] == [
        ("anthropic", "z"),
        ("openai", "a"),
        ("openai", "b"),
    ]


def test_aggregate_interleaved_inserts_still_group_once_per_key(sink) -> None:
    # Insertion order alternates keys; the single ordered query + groupby
    # must still yield exactly one stats row per (backend, model).
    sink.record(_rec(backend="x", model="m", latency=100.0))
    sink.record(_rec(backend="y", model="m", latency=50.0))
    sink.record(_rec(backend="x", model="m", latency=200.0))
    stats = sink.aggregate()
    by_key = {(s.backend, s.model): s for s in stats}
    assert by_key[("x", "m")].calls == 2
    assert by_key[("y", "m")].calls == 1
    assert len(stats) == 2


def test_aggregate_since_seconds_filters_old_rows(sink) -> None:
    # An old row that the since-filter should exclude.
    with sink._connect() as conn:
        conn.execute(
            "INSERT INTO calls (timestamp, backend, model, prompt_tokens, "
            "completion_tokens, tokens_estimated, latency_ms, cost_usd, "
            "cache_hit, error) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (time.time() - 10_000, "old", "m", 1, 1, 0, 1.0, None, 0, None),
        )
    sink.record(_rec(backend="fresh", model="m"))
    stats = sink.aggregate(since_seconds=60)
    assert [s.backend for s in stats] == ["fresh"]


def test_time_filter_none_yields_no_clause() -> None:
    clause, params = TelemetrySink._time_filter(None)
    assert clause == ""
    assert params == ()


def test_time_filter_since_yields_clause_and_param() -> None:
    clause, params = TelemetrySink._time_filter(60)
    assert clause == "WHERE timestamp >= ?"
    assert len(params) == 1


def test_stats_from_rows_handles_none_token_columns() -> None:
    # rows: (prompt_tokens, completion_tokens, latency_ms, cost_usd, cache_hit)
    rows = [
        (None, None, 200.0, None, 1),
        (5, 3, 100.0, 0.5, 0),
    ]
    stats = _stats_from_rows("openai", "m", rows)
    assert stats.calls == 2
    assert stats.cache_hits == 1
    assert stats.prompt_tokens == 5
    assert stats.completion_tokens == 3
    assert stats.cost_usd == 0.5
    assert stats.latency_p50_ms == 150.0
    assert stats.latency_p95_ms == 200.0
