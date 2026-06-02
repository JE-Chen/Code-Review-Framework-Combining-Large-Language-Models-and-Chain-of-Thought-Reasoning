"""Prometheus review-domain metrics for the inference server.

Kept separate from ``fastapi_server`` so the metric definitions and the
``observe_review`` decorator are unit-testable without loading the model.
The metrics register on the default ``prometheus_client`` registry, which
is the same registry the FastAPI instrumentator exposes at ``/metrics`` —
so every completed review leaves a data point in Prometheus (and Grafana)
independent of the HTTP-transport metrics.
"""

from __future__ import annotations

import functools
import time
from typing import Callable, TypeVar

from prthinker.pipeline import ReviewCancelledError

_MODE_PER_FILE = "per_file"
_MODE_FULL = "full"
_OUTCOME_OK = "ok"
_OUTCOME_CANCELLED = "cancelled"
_OUTCOME_ERROR = "error"

try:
    from prometheus_client import Counter, Gauge, Histogram

    _REVIEWS_TOTAL = Counter(
        "prthinker_reviews_total",
        "CoT reviews executed, by mode and outcome.",
        ("mode", "outcome"),
    )
    _REVIEW_DURATION = Histogram(
        "prthinker_review_duration_seconds",
        "Wall-clock duration of a CoT review, by mode.",
        ("mode",),
        buckets=(1, 5, 15, 30, 60, 120, 300, 600, 1200),
    )
    _REVIEW_FINDINGS = Histogram(
        "prthinker_review_findings",
        "Inline findings produced per review.",
        buckets=(0, 1, 2, 3, 5, 8, 13, 21),
    )
    _REVIEWS_IN_PROGRESS = Gauge(
        "prthinker_reviews_in_progress",
        "CoT reviews currently executing.",
    )
    METRICS_ENABLED = True
except ImportError:  # pragma: no cover - the server profile always ships the dep
    METRICS_ENABLED = False


_ReviewFn = TypeVar("_ReviewFn", bound=Callable[..., object])


def _review_mode(req: object) -> str:
    """Return the metric ``mode`` label for a review request."""
    return _MODE_PER_FILE if getattr(req, "file_path", None) is not None else _MODE_FULL


def observe_review(fn: _ReviewFn) -> _ReviewFn:
    """Record review-domain Prometheus metrics around a review execution.

    Wraps a ``(req, cancel_event=None) -> ReviewResponse`` callable so every
    completed review — success, cancellation, or error — increments the
    review counter, observes its duration, and (on success) records the
    inline-finding count. A no-op passthrough when the metrics dependency
    is absent.
    """
    if not METRICS_ENABLED:
        return fn

    @functools.wraps(fn)
    def wrapper(req: object, cancel_event: object | None = None) -> object:
        mode = _review_mode(req)
        outcome = _OUTCOME_OK
        started = time.monotonic()
        _REVIEWS_IN_PROGRESS.inc()
        try:
            resp = fn(req, cancel_event)
            _REVIEW_FINDINGS.observe(len(resp.inline_findings))
            return resp
        except ReviewCancelledError:
            outcome = _OUTCOME_CANCELLED
            raise
        except Exception:
            outcome = _OUTCOME_ERROR
            raise
        finally:
            _REVIEWS_IN_PROGRESS.dec()
            _REVIEW_DURATION.labels(mode=mode).observe(time.monotonic() - started)
            _REVIEWS_TOTAL.labels(mode=mode, outcome=outcome).inc()

    return wrapper  # type: ignore[return-value]
