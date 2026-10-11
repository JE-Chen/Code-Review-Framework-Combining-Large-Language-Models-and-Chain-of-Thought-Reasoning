"""Interaction tracking preserves privacy and does not manufacture quality scores."""

import json

import pytest
from pydantic import ValidationError

from prthinker.online_quality import QualityEvent, QualityStore, drift


def event(kind, identifier, timestamp=1):
    return QualityEvent(event_id=identifier, repository="private/repo", review_id="pr1",
                        finding_id="finding1", kind=kind, timestamp=timestamp)


def test_events_are_pseudonymous_and_idempotent(tmp_path):
    store = QualityStore(tmp_path / "quality.sqlite", b"k" * 32)
    assert store.record(event("finding", "1"))
    assert not store.record(event("finding", "1"))
    assert store.record(event("accepted", "2", 2))
    raw = json.dumps(store.read())
    assert "private/repo" not in raw and "finding1" not in raw and "pr1" not in raw
    report = store.report()
    assert report["acceptance_rate_among_decided"] == 1
    assert report["cost_usd"] is None
    assert report["measurement"] == "user_interaction_signals"


def test_latest_disposition_and_window_drift(tmp_path):
    store = QualityStore(tmp_path / "quality.sqlite", b"k" * 32)
    store.record(event("accepted", "1", 1))
    store.record(event("dismissed", "2", 3))
    assert store.report()["acceptance_rate_among_decided"] == 0
    assert drift(store.report(0, 2), store.report(2, 4))["acceptance_rate_delta"] == -1


def test_unknown_metrics_and_input_allowlist(tmp_path):
    with pytest.raises(ValueError):
        QualityStore(tmp_path / "bad.sqlite", b"short")
    with pytest.raises(ValidationError):
        QualityEvent(**event("review", "1").model_dump(), source="secret")
    store = QualityStore(tmp_path / "empty.sqlite", b"k" * 32)
    assert store.report()["acceptance_rate_among_decided"] is None
    with pytest.raises(ValueError):
        store.report(3, 2)
    assert QualityEvent.model_validate(event("review", "1").model_dump()) == event("review", "1")


def test_partial_usage_is_not_reported_as_complete_and_metadata_is_redacted(tmp_path):
    store = QualityStore(tmp_path / "quality.sqlite", b"k" * 32)
    known = event("review", "known").model_copy(update={"prompt_tokens": 10, "cost_usd": 1.0,
                                                        "model": "ghp_" + "x" * 30})
    store.record(known)
    store.record(event("review", "unknown"))
    assert store.report()["prompt_tokens"] is None
    assert store.report()["cost_usd"] is None
    assert "ghp_" not in json.dumps(store.read())
