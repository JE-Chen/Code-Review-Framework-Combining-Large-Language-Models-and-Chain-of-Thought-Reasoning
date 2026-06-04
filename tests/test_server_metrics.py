"""Unit tests for the review-domain Prometheus metrics decorator.

The metrics dependency ships only in the ``[server]`` extra, so the whole
module skips when ``prometheus_client`` is absent (e.g. the CI runner
profile). No model is loaded — the decorator wraps a fake review callable.
"""

import pytest

prometheus_client = pytest.importorskip("prometheus_client")

from codes.util.server_metrics import METRICS_ENABLED, observe_review  # noqa: E402  # after importorskip guard
from prthinker.pipeline import ReviewCancelledError  # noqa: E402  # after importorskip guard

REGISTRY = prometheus_client.REGISTRY


class _Req:
    def __init__(self, file_path=None):
        self.file_path = file_path


class _Resp:
    def __init__(self, findings):
        self.inline_findings = list(findings)


def _val(name, labels=None):
    return REGISTRY.get_sample_value(name, labels or {}) or 0.0


def test_metrics_enabled_when_dependency_present():
    assert METRICS_ENABLED is True


def test_successful_review_records_count_duration_and_findings():
    labels = {"mode": "full", "outcome": "ok"}
    before_total = _val("prthinker_reviews_total", labels)
    before_dur = _val("prthinker_review_duration_seconds_count", {"mode": "full"})
    before_find = _val("prthinker_review_findings_count")

    wrapped = observe_review(lambda req, cancel_event=None: _Resp(["a", "b"]))
    resp = wrapped(_Req())

    assert resp.inline_findings == ["a", "b"]
    assert _val("prthinker_reviews_total", labels) == before_total + 1
    assert _val("prthinker_review_duration_seconds_count", {"mode": "full"}) == before_dur + 1
    assert _val("prthinker_review_findings_count") == before_find + 1
    assert _val("prthinker_review_findings_sum") >= 2.0


def test_per_file_mode_label_distinct_from_full():
    labels = {"mode": "per_file", "outcome": "ok"}
    before = _val("prthinker_reviews_total", labels)

    wrapped = observe_review(lambda req, cancel_event=None: _Resp([]))
    wrapped(_Req(file_path="foo.py"))

    assert _val("prthinker_reviews_total", labels) == before + 1


def test_cancelled_review_uses_cancelled_outcome_and_reraises():
    labels = {"mode": "full", "outcome": "cancelled"}
    before = _val("prthinker_reviews_total", labels)

    def _cancel(req, cancel_event=None):
        raise ReviewCancelledError("stopped")

    with pytest.raises(ReviewCancelledError):
        observe_review(_cancel)(_Req())

    assert _val("prthinker_reviews_total", labels) == before + 1


def test_failed_review_uses_error_outcome_and_reraises():
    labels = {"mode": "full", "outcome": "error"}
    before = _val("prthinker_reviews_total", labels)

    def _boom(req, cancel_event=None):
        raise ValueError("kaboom")

    with pytest.raises(ValueError):
        observe_review(_boom)(_Req())

    assert _val("prthinker_reviews_total", labels) == before + 1


def test_in_progress_gauge_returns_to_baseline_after_each_path():
    baseline = _val("prthinker_reviews_in_progress")

    observe_review(lambda req, cancel_event=None: _Resp([]))(_Req())
    assert _val("prthinker_reviews_in_progress") == baseline

    def _boom(req, cancel_event=None):
        raise ValueError("x")

    with pytest.raises(ValueError):
        observe_review(_boom)(_Req())
    assert _val("prthinker_reviews_in_progress") == baseline
