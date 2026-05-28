"""Cache + telemetry round-trips."""

from __future__ import annotations

import time

from reviewmind.backends.base import Usage
from reviewmind.backends.wrappers import CachingBackend, InstrumentedBackend
from reviewmind.cache import PromptCache
from reviewmind.telemetry import CallRecord, TelemetrySink
from reviewmind.pricing import estimate_cost

from tests.conftest import FakeBackend


# ----- PromptCache --------------------------------------------------------

def test_cache_miss_returns_none(tmp_cache_path) -> None:
    cache = PromptCache(tmp_cache_path)
    assert cache.get("fake", "fake-1", "p", 100) is None


def test_cache_round_trip(tmp_cache_path) -> None:
    cache = PromptCache(tmp_cache_path)
    cache.put("fake", "fake-1", "p", 100, "the-response")
    assert cache.get("fake", "fake-1", "p", 100) == "the-response"
    # Cache hit counter increments.
    assert cache.stats().total_hits == 1


def test_cache_key_includes_model_and_token_cap(tmp_cache_path) -> None:
    cache = PromptCache(tmp_cache_path)
    cache.put("fake", "model-a", "p", 100, "A")
    # Different model → different key → cache miss.
    assert cache.get("fake", "model-b", "p", 100) is None
    # Different token cap → different key.
    assert cache.get("fake", "model-a", "p", 200) is None


def test_cache_ttl_evicts_old_entries(tmp_cache_path) -> None:
    cache = PromptCache(tmp_cache_path, ttl_seconds=0.01)
    cache.put("fake", "m", "p", 1, "old")
    time.sleep(0.02)
    assert cache.get("fake", "m", "p", 1) is None


# ----- CachingBackend wrapper --------------------------------------------

def test_caching_backend_only_calls_inner_once(tmp_cache_path) -> None:
    backend = FakeBackend(["first call only"])
    wrapped = CachingBackend(backend, PromptCache(tmp_cache_path))
    assert wrapped.generate("p", 100) == "first call only"
    assert wrapped.generate("p", 100) == "first call only"
    assert len(backend.calls) == 1
    # Second call was a hit.
    assert wrapped.last_cache_hit is True


# ----- TelemetrySink + pricing -------------------------------------------

def test_telemetry_records_and_aggregates(tmp_telemetry_path) -> None:
    sink = TelemetrySink(tmp_telemetry_path)
    sink.record(CallRecord(
        backend="openai", model="gpt-4o-mini",
        prompt_tokens=100, completion_tokens=50, tokens_estimated=False,
        latency_ms=200.0, cache_hit=False,
    ))
    sink.record(CallRecord(
        backend="openai", model="gpt-4o-mini",
        prompt_tokens=120, completion_tokens=60, tokens_estimated=False,
        latency_ms=600.0, cache_hit=True,
    ))
    stats = sink.aggregate()
    assert len(stats) == 1
    s = stats[0]
    assert s.backend == "openai"
    assert s.calls == 2
    assert s.cache_hits == 1
    assert s.prompt_tokens == 220
    assert s.completion_tokens == 110
    # ``statistics.median`` averages the two middle values for an even
    # sample, so p50 is (200 + 600) / 2.
    assert s.latency_p50_ms == 400.0
    assert s.latency_p95_ms == 600.0


def test_pricing_is_known_for_listed_models() -> None:
    assert estimate_cost("openai", "gpt-4o-mini", 1_000_000, 1_000_000) is not None
    assert estimate_cost("anthropic", "claude-opus-4-7", 1_000_000, 1_000_000) is not None


def test_pricing_returns_none_for_local_backends() -> None:
    assert estimate_cost("local", "any-model", 100, 50) is None
    assert estimate_cost("remote", "any-model", 100, 50) is None


def test_pricing_returns_none_for_unknown_model() -> None:
    assert estimate_cost("openai", "gpt-5-imaginary", 100, 50) is None


# ----- InstrumentedBackend records into the sink ------------------------

def test_instrumented_backend_records_per_call(
    tmp_telemetry_path, tmp_cache_path
) -> None:
    fake = FakeBackend(
        ["a", "b"],
        kind="openai", model="gpt-4o-mini",
        usage_per_call=[Usage(100, 50), Usage(120, 60)],
    )
    sink = TelemetrySink(tmp_telemetry_path)
    cached = CachingBackend(fake, PromptCache(tmp_cache_path))
    backend = InstrumentedBackend(cached, sink)

    backend.generate("p1", 1000)
    backend.generate("p1", 1000)  # cache hit

    rows = sink.aggregate()
    assert len(rows) == 1
    assert rows[0].calls == 2
    assert rows[0].cache_hits == 1
    # First call had usage 100/50, so cost was recorded.
    assert rows[0].cost_usd > 0
