"""Process-wide GPU serialization for the inference server.

The FastAPI server answers requests on many threads (one per ``/review``
or ``/ask`` job) but drives a single GPU. Two ``model.generate`` calls in
flight at once OOM the card — see CLAUDE.md "no concurrent GPU". Every
generate acquires this one lock, so forward passes run strictly one at a
time and extra callers queue instead of contending for VRAM.

The lock lives in a runner-safe module (stdlib ``threading`` only) so its
behaviour is unit-testable without importing torch; the local backend
imports and applies it. The lock is process-global on purpose: a single
GPU is a single resource regardless of how many backend instances exist.

It is a plain (non-reentrant) lock. The pipeline issues its per-step
``generate`` calls sequentially, never nested, so re-entrancy is not
needed; a reentrant lock would silently permit the very overlap this
guards against if a future caller nested two generates on one thread.
"""

from __future__ import annotations

import threading
from collections.abc import Iterator
from contextlib import contextmanager

_GPU_LOCK = threading.Lock()


@contextmanager
def gpu_serialized() -> Iterator[None]:
    """Hold the process-wide GPU lock for the duration of the block.

    The lock is always released on exit, including when the body raises,
    so a failed or cancelled generation never wedges the GPU for every
    later request.
    """
    with _GPU_LOCK:
        yield


__all__ = ["gpu_serialized"]
