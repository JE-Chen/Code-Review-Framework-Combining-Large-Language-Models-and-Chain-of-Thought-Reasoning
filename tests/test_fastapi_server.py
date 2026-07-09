"""Unit tests for the idle-job sweeper helpers in ``codes.run.fastapi_server``.

The server module constructs a real ``LocalHFBackend`` (which loads the 30B
model) and a FAISS retriever (which builds an embedding index) at import time,
and spawns a daemon sweeper thread. None of that is needed to exercise the pure
idle-cancel logic, so we inject lightweight fakes into ``sys.modules`` for the
heavy ``codes.util`` dependencies and neuter the thread start *before*
importing the module under test.
"""

from __future__ import annotations

import importlib
from contextlib import contextmanager
import sys
import threading
import time
import types
from dataclasses import dataclass, field

import pytest

torch = pytest.importorskip("torch")  # module under test imports torch at top


@dataclass
class _FakeJob:
    """Minimal stand-in matching the job protocol the sweeper relies on."""

    status: str = "running"
    created_at: float = field(default_factory=time.time)
    last_polled_at: float = field(default_factory=time.time)
    cancel_event: threading.Event = field(default_factory=threading.Event)


class _FakeModel:
    """Eval-able placeholder so ``LocalHFBackend.__init__`` succeeds."""

    def eval(self) -> "_FakeModel":
        return self


def _install_fake_module(name: str, **attrs: object) -> tuple[str, object]:
    """Insert a stub module into sys.modules, returning a restore record."""
    prev = sys.modules.get(name)
    stub = types.ModuleType(name)
    for key, value in attrs.items():
        setattr(stub, key, value)
    sys.modules[name] = stub
    return name, prev


@pytest.fixture(scope="module")
def server_module():
    """Import the server module with heavy ``codes.util`` deps stubbed out."""
    records = [
        _install_fake_module(
            "codes.util.hf_model_util",
            load_hf_model=lambda *a, **k: (_FakeModel(), object()),
            hf_generate=lambda *a, **k: ("", ""),
        ),
        _install_fake_module(
            "codes.util.faiss_util",
            search_docs=lambda *a, **k: [],
            # rag.py resolves threshold=None to this calibrated default;
            # the server passes an explicit 0.7 so the value is inert here.
            RECOMMENDED_THRESHOLD=0.7,
        ),
    ]
    orig_thread_start = threading.Thread.start
    threading.Thread.start = lambda self: None  # type: ignore[method-assign]
    sys.modules.pop("codes.run.fastapi_server", None)
    try:
        module = importlib.import_module("codes.run.fastapi_server")
        yield module
    finally:
        threading.Thread.start = orig_thread_start  # type: ignore[method-assign]
        sys.modules.pop("codes.run.fastapi_server", None)
        for name, prev in records:
            if prev is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = prev


def test_warm_rag_index_constructs_default_retriever(server_module, monkeypatch):
    """_warm_rag_index warms the FAISS index by building a default retriever.

    The helper exists only for its import-time side effect (loading the
    embedding stack + building the index once); it returns nothing and the
    retriever it constructs is discarded. We spy on the constructor to assert
    it is built at the legacy 0.7 threshold without touching a real model.
    """
    thresholds: list[float | None] = []

    class _SpyRetriever:
        def __init__(self, threshold: float | None = None) -> None:
            thresholds.append(threshold)

    monkeypatch.setattr(server_module, "FaissRAGRetriever", _SpyRetriever)

    result = server_module._warm_rag_index()

    assert result is None
    assert thresholds == [0.7]


def test_cancel_if_idle_sets_event_when_idle(server_module):
    """An idle running job gets its cancel_event set."""
    now = time.time()
    job = _FakeJob(status="running", last_polled_at=now - 10_000)
    server_module._cancel_if_idle("jid", job, now, "Review")
    assert job.cancel_event.is_set()


def test_cancel_if_idle_skips_recent_job(server_module):
    """A recently polled running job is left untouched."""
    now = time.time()
    job = _FakeJob(status="running", last_polled_at=now)
    server_module._cancel_if_idle("jid", job, now, "Ask")
    assert not job.cancel_event.is_set()


def test_cancel_if_idle_skips_non_running(server_module):
    """A non-running job is never cancelled even if old."""
    now = time.time()
    job = _FakeJob(status="pending", last_polled_at=now - 10_000)
    server_module._cancel_if_idle("jid", job, now, "Review")
    assert not job.cancel_event.is_set()


def test_cancel_if_idle_skips_already_cancelled(server_module):
    """An already-cancelled job is a no-op (no error, stays set)."""
    now = time.time()
    job = _FakeJob(status="running", last_polled_at=now - 10_000)
    job.cancel_event.set()
    server_module._cancel_if_idle("jid", job, now, "Review")
    assert job.cancel_event.is_set()


def test_cancel_if_idle_boundary(server_module):
    """At exactly the timeout the job is NOT cancelled (strict >)."""
    now = time.time()
    timeout = server_module._IDLE_TIMEOUT_SECONDS
    job = _FakeJob(status="running", last_polled_at=now - timeout)
    server_module._cancel_if_idle("jid", job, now, "Review")
    assert not job.cancel_event.is_set()

    just_over = _FakeJob(status="running", last_polled_at=now - timeout - 1)
    server_module._cancel_if_idle("jid", just_over, now, "Review")
    assert just_over.cancel_event.is_set()


def test_sweep_table_once_cancels_idle_only(server_module):
    """Sweeping a table cancels only the idle running jobs under its lock."""
    now = time.time()
    idle = _FakeJob(status="running", last_polled_at=now - 10_000)
    recent = _FakeJob(status="running", last_polled_at=now)
    done = _FakeJob(status="completed", last_polled_at=now - 10_000)
    table = {"a": idle, "b": recent, "c": done}
    lock = threading.Lock()

    server_module._sweep_table_once(lock, table, "Ask", now)

    assert idle.cancel_event.is_set()
    assert not recent.cancel_event.is_set()
    assert not done.cancel_event.is_set()
    assert not lock.locked()


def test_sweep_table_once_logs_label(server_module, caplog):
    """The warning message embeds the provided label verbatim."""
    import logging

    now = time.time()
    idle = _FakeJob(status="running", last_polled_at=now - 10_000)
    with caplog.at_level(logging.WARNING, logger="prthinker.server"):
        server_module._sweep_table_once(threading.Lock(), {"x": idle}, "Review", now)
    assert any("Review job x idle" in r.getMessage() for r in caplog.records)


def test_make_job_slot_cancels_and_evicts_expired_active_job(
    server_module,
):
    now = time.time()
    expired = _FakeJob(created_at=now - server_module._JOB_TTL_SECONDS - 1)
    table = {"expired": expired}

    assert server_module._make_job_slot_locked(table, now)
    assert expired.cancel_event.is_set()
    assert table == {}


def test_make_job_slot_evicts_terminal_before_rejecting(
    server_module, monkeypatch,
):
    monkeypatch.setattr(server_module, "_MAX_JOBS_PER_KIND", 2)
    table = {
        "done": _FakeJob(status="done"),
        "active": _FakeJob(status="running"),
    }

    assert server_module._make_job_slot_locked(table, time.time())
    assert set(table) == {"active"}


def test_make_job_slot_rejects_when_all_slots_are_active(
    server_module, monkeypatch,
):
    monkeypatch.setattr(server_module, "_MAX_JOBS_PER_KIND", 2)
    table = {
        "a": _FakeJob(status="running"),
        "b": _FakeJob(status="pending"),
    }

    assert not server_module._make_job_slot_locked(table, time.time())
    assert set(table) == {"a", "b"}


def test_start_job_worker_rolls_back_failed_start(server_module):
    table = {"job": _FakeJob(status="pending")}

    class _BrokenThread:
        def start(self):
            raise RuntimeError("cannot start")

    with pytest.raises(RuntimeError, match="cannot start"):
        server_module._start_job_worker(
            _BrokenThread(), threading.Lock(), table, "job",
        )
    assert table == {}


def test_release_gpu_memory_serializes_cuda_empty_cache(
    server_module, monkeypatch,
):
    events: list[str] = []

    @contextmanager
    def _lock():
        events.append("lock-enter")
        yield
        events.append("lock-exit")

    monkeypatch.setattr(server_module, "gpu_serialized", _lock)
    monkeypatch.setattr(server_module.gc, "collect", lambda: events.append("gc"))
    monkeypatch.setattr(server_module.torch.cuda, "is_available", lambda: True)
    monkeypatch.setattr(
        server_module.torch.cuda,
        "empty_cache",
        lambda: events.append("empty-cache"),
    )

    server_module._release_gpu_memory()

    assert events == ["gc", "lock-enter", "empty-cache", "lock-exit"]
