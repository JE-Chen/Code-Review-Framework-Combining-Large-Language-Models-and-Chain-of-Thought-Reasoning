"""Tests for the process-wide GPU serialization lock.

The lock is what makes the single-GPU server safe under concurrent
requests, so it is exercised directly (mutual exclusion, exception
release) without needing torch, plus a torch-free check that the local
backend actually wraps its generate in it.
"""

from __future__ import annotations

import contextlib
import threading
import time
import types

from prthinker.gpu_lock import gpu_serialized


def test_gpu_serialized_is_mutually_exclusive() -> None:
    # Five threads race into the guarded region; record the peak number
    # inside it at once. A correct lock keeps that peak at exactly 1.
    active = 0
    peak = 0
    state_lock = threading.Lock()

    def worker() -> None:
        nonlocal active, peak
        with gpu_serialized():
            with state_lock:
                active += 1
                peak = max(peak, active)
            time.sleep(0.02)
            with state_lock:
                active -= 1

    threads = [threading.Thread(target=worker) for _ in range(5)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert peak == 1


def test_gpu_serialized_releases_on_exception() -> None:
    with contextlib.suppress(ValueError):
        with gpu_serialized():
            raise ValueError("boom")
    # If the lock leaked on the raise, this second acquire would deadlock.
    acquired = []

    def worker() -> None:
        with gpu_serialized():
            acquired.append(True)

    thread = threading.Thread(target=worker)
    thread.start()
    thread.join(timeout=2.0)
    assert acquired == [True]
    assert not thread.is_alive()


def test_local_backend_generate_runs_under_the_lock(monkeypatch) -> None:
    # Construct the backend without loading a model (object.__new__) and
    # stub the lazy hf_generate import, so generate() needs no torch/GPU.
    import sys

    from prthinker.backends import local as local_mod
    from prthinker.backends.local import LocalHFBackend

    fake_qwen3 = types.ModuleType("codes.util.hf_model_util")
    fake_qwen3.hf_generate = lambda *a, **k: ("hello", None)
    monkeypatch.setitem(sys.modules, "codes.util.hf_model_util", fake_qwen3)

    entered: list[bool] = []

    @contextlib.contextmanager
    def _tracking_cm():
        entered.append(True)
        yield

    monkeypatch.setattr(local_mod, "gpu_serialized", _tracking_cm)

    backend = object.__new__(LocalHFBackend)
    backend._model = object()
    backend._tokenizer = object()
    assert backend.generate("prompt", 8) == "hello"
    assert entered == [True]  # the forward pass ran inside the lock
