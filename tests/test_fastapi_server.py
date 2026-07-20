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
    it resolves the active embedding model's calibrated threshold.
    """
    thresholds: list[float | None] = []

    class _SpyRetriever:
        def __init__(self, threshold: float | None = None) -> None:
            thresholds.append(threshold)

    monkeypatch.setattr(server_module, "FaissRAGRetriever", _SpyRetriever)

    result = server_module._warm_rag_index()

    assert result is None
    assert thresholds == [None]


def test_resolve_lora_path_can_force_base_model(server_module, monkeypatch):
    monkeypatch.setenv("PRTHINKER_DISABLE_LORA", "1")
    monkeypatch.setenv("PRTHINKER_LORA_PATH", "/adapter")
    assert server_module._resolve_lora_path() is None


def test_resolve_rag_mode_rejects_unknown_value(server_module, monkeypatch):
    monkeypatch.setenv("PRTHINKER_RAG_MODE", "typo")
    with pytest.raises(ValueError, match="PRTHINKER_RAG_MODE"):
        server_module._resolve_rag_mode()


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


# ---------------------------------------------------------------------------
# CUDA fail-fast + healthz GPU probe
# ---------------------------------------------------------------------------


class _ExitCalled(Exception):
    """Sentinel raised by the patched os._exit so tests can observe it."""


def _patch_exit(monkeypatch, module) -> list[int]:
    codes: list[int] = []

    def fake_exit(code: int) -> None:
        codes.append(code)
        raise _ExitCalled

    monkeypatch.setattr(module.os, "_exit", fake_exit)
    return codes


class TestIsFatalCudaError:
    def test_cublas_internal_error_is_fatal(self, server_module):
        exc = RuntimeError(
            "CUDA error: CUBLAS_STATUS_INTERNAL_ERROR when calling cublasSgemm")
        assert server_module._is_fatal_cuda_error(exc) is True

    def test_device_side_assert_is_fatal(self, server_module):
        assert server_module._is_fatal_cuda_error(
            RuntimeError("device-side assert triggered")) is True

    def test_plain_oom_is_recoverable(self, server_module):
        exc = torch.cuda.OutOfMemoryError("CUDA error: out of memory")
        assert server_module._is_fatal_cuda_error(exc) is False

    def test_ordinary_exception_is_not_fatal(self, server_module):
        assert server_module._is_fatal_cuda_error(ValueError("bad diff")) is False


class TestExitIfCudaPoisoned:
    def test_fatal_error_exits_1(self, server_module, monkeypatch):
        codes = _patch_exit(monkeypatch, server_module)
        with pytest.raises(_ExitCalled):
            server_module._exit_if_cuda_poisoned(
                RuntimeError("CUDA error: CUBLAS_STATUS_EXECUTION_FAILED"))
        assert codes == [1]

    def test_non_fatal_error_keeps_serving(self, server_module, monkeypatch):
        codes = _patch_exit(monkeypatch, server_module)
        server_module._exit_if_cuda_poisoned(ValueError("bad request"))
        server_module._exit_if_cuda_poisoned(
            torch.cuda.OutOfMemoryError("CUDA error: out of memory"))
        assert codes == []

    def test_env_override_disables_failfast(self, server_module, monkeypatch):
        codes = _patch_exit(monkeypatch, server_module)
        monkeypatch.setenv("PRTHINKER_NO_CUDA_FAILFAST", "1")
        server_module._exit_if_cuda_poisoned(
            RuntimeError("CUDA error: CUBLAS_STATUS_INTERNAL_ERROR"))
        assert codes == []


class TestHealthzGpuProbe:
    # The endpoint function is called directly: the server_module fixture
    # neuters Thread.start for the whole module, which would deadlock
    # TestClient's portal thread; the probe logic is identical either way.

    def test_no_cuda_reports_ok(self, server_module, monkeypatch):
        monkeypatch.setattr(server_module.torch.cuda, "is_available", lambda: False)
        assert server_module.healthz()["gpu"] == "no-cuda"

    def test_healthy_probe_reports_ok(self, server_module, monkeypatch):
        monkeypatch.setattr(server_module.torch.cuda, "is_available", lambda: True)
        monkeypatch.setattr(server_module, "_touch_cuda_devices", lambda: None)
        assert server_module.healthz()["gpu"] == "ok"

    def test_busy_lock_short_circuits_to_ok(self, server_module, monkeypatch):
        from prthinker import gpu_lock

        monkeypatch.setattr(server_module.torch.cuda, "is_available", lambda: True)

        def must_not_run() -> None:
            pytest.fail("probe must not touch the GPU while a generation runs")

        monkeypatch.setattr(server_module, "_touch_cuda_devices", must_not_run)
        with gpu_lock.gpu_serialized():  # simulate an in-flight generation
            assert server_module.healthz()["gpu"] == "busy"

    def test_non_fatal_probe_failure_returns_503(self, server_module, monkeypatch):
        from fastapi import HTTPException

        monkeypatch.setattr(server_module.torch.cuda, "is_available", lambda: True)

        def broken() -> None:
            raise RuntimeError("probe allocation failed")

        monkeypatch.setattr(server_module, "_touch_cuda_devices", broken)
        with pytest.raises(HTTPException) as excinfo:
            server_module.healthz()
        assert excinfo.value.status_code == 503
        assert "probe allocation failed" in excinfo.value.detail

    def test_poisoned_context_exits_for_restart(self, server_module, monkeypatch):
        codes = _patch_exit(monkeypatch, server_module)
        monkeypatch.setattr(server_module.torch.cuda, "is_available", lambda: True)

        def poisoned() -> None:
            raise RuntimeError("CUDA error: CUBLAS_STATUS_INTERNAL_ERROR")

        monkeypatch.setattr(server_module, "_touch_cuda_devices", poisoned)
        with pytest.raises(_ExitCalled):
            server_module.healthz()
        assert codes == [1]


class TestWorkersFailFast:
    def test_review_worker_records_error_then_classifies(
            self, server_module, monkeypatch):
        calls: list[BaseException] = []
        monkeypatch.setattr(
            server_module, "_exit_if_cuda_poisoned", calls.append)
        monkeypatch.setattr(server_module, "_release_gpu_memory", lambda: None)
        boom = RuntimeError("CUDA error: CUBLAS_STATUS_INTERNAL_ERROR")

        def exploding_review(req, cancel_event=None):
            raise boom

        monkeypatch.setattr(server_module, "_execute_review", exploding_review)
        job = server_module._Job()
        with server_module._JOBS_LOCK:
            server_module._JOBS["jid"] = job
        try:
            server_module._run_review_job("jid", object())
        finally:
            with server_module._JOBS_LOCK:
                server_module._JOBS.pop("jid", None)
        assert job.status == "error"  # the job error is recorded first
        assert calls == [boom]  # then the CUDA classification runs

    def test_ask_worker_records_error_then_classifies(
            self, server_module, monkeypatch):
        calls: list[BaseException] = []
        monkeypatch.setattr(
            server_module, "_exit_if_cuda_poisoned", calls.append)
        monkeypatch.setattr(server_module, "_release_gpu_memory", lambda: None)
        boom = RuntimeError("CUDA error: misaligned address")

        class _ExplodingBackend:
            def generate(self, prompt, max_new_tokens=0, cancel_event=None):
                raise boom

        monkeypatch.setattr(server_module, "_backend", _ExplodingBackend())
        job = server_module._AskJob()
        with server_module._ASK_JOBS_LOCK:
            server_module._ASK_JOBS["jid"] = job
        try:
            server_module._run_ask_job(
                "jid", server_module.AskRequest(prompt="p", max_new_tokens=8))
        finally:
            with server_module._ASK_JOBS_LOCK:
                server_module._ASK_JOBS.pop("jid", None)
        assert job.status == "error"
        assert calls == [boom]
