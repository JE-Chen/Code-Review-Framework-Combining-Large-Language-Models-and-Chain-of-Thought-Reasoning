"""``reviewmind report`` rendering — markdown, html, json.

We use real temporary SQLite + JSONL stores so the renderers see live
data via the same code path that production uses.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from reviewmind.accepted import AcceptedExample, AcceptedExamplesStore
from reviewmind.cache import PromptCache
from reviewmind.dismissed import DismissedExample, DismissedExamplesStore
from reviewmind.report import (
    ReportInputs,
    render_html,
    render_json,
    render_markdown,
)
from reviewmind.telemetry import CallRecord, TelemetrySink


@pytest.fixture
def populated_inputs(tmp_path: Path) -> ReportInputs:
    # Telemetry: two calls, one with cost, one cache hit.
    tel = TelemetrySink(tmp_path / "telemetry.sqlite")
    tel.record(CallRecord(
        backend="openai", model="gpt-4o-mini",
        prompt_tokens=100, completion_tokens=50, tokens_estimated=False,
        latency_ms=300.0, cache_hit=False,
    ))
    tel.record(CallRecord(
        backend="openai", model="gpt-4o-mini",
        prompt_tokens=120, completion_tokens=60, tokens_estimated=False,
        latency_ms=200.0, cache_hit=True,
    ))

    # Cache: one entry, one hit.
    cache = PromptCache(tmp_path / "cache.sqlite")
    cache.put("openai", "gpt-4o-mini", "p", 1024, "response")
    cache.get("openai", "gpt-4o-mini", "p", 1024)

    # Dismissed store with two reasons.
    d = DismissedExamplesStore(tmp_path / "dismissed.jsonl")
    d.append(DismissedExample(
        path="a.py", comment="x", reason="thumbs-down reaction"
    ))
    d.append(DismissedExample(
        path="b.py", comment="y", reason="reply matched: 'false positive'"
    ))

    # Accepted store with two entries on same file.
    a = AcceptedExamplesStore(tmp_path / "accepted.jsonl")
    a.append(AcceptedExample(
        path="auth.py", comment="x", suggestion="y", pr_number=1
    ))
    a.append(AcceptedExample(
        path="auth.py", comment="z", suggestion="w", pr_number=2
    ))

    return ReportInputs(
        telemetry_path=tmp_path / "telemetry.sqlite",
        cache_path=tmp_path / "cache.sqlite",
        dismissed_path=tmp_path / "dismissed.jsonl",
        accepted_path=tmp_path / "accepted.jsonl",
        since_seconds=None,
    )


def test_markdown_includes_every_section(populated_inputs: ReportInputs) -> None:
    body = render_markdown(populated_inputs)
    assert "# reviewmind report" in body
    assert "## Usage by backend & model" in body
    assert "## Cache" in body
    assert "## Daily cost (last 14 days)" in body
    assert "## Dismissed corpus" in body
    assert "## Accepted corpus" in body


def test_markdown_renders_telemetry_row(populated_inputs: ReportInputs) -> None:
    body = render_markdown(populated_inputs)
    assert "openai" in body
    assert "gpt-4o-mini" in body
    # 2 calls, 1 cache hit aggregated.
    assert "| 2 | 1 |" in body or "| 2 |" in body


def test_markdown_dismissed_section_lists_reasons(
    populated_inputs: ReportInputs,
) -> None:
    body = render_markdown(populated_inputs)
    assert "thumbs-down reaction" in body
    assert "false positive" in body


def test_markdown_accepted_top_files(populated_inputs: ReportInputs) -> None:
    body = render_markdown(populated_inputs)
    assert "auth.py" in body
    # Both accepted entries are on auth.py → count of 2.
    assert "| 2 |" in body


def test_json_renders_as_parseable_object(populated_inputs: ReportInputs) -> None:
    body = render_json(populated_inputs)
    data = json.loads(body)
    assert data["window"] == "all-time"
    assert data["telemetry"][0]["backend"] == "openai"
    assert data["dismissed"]["total"] == 2
    assert data["accepted"]["total"] == 2
    assert data["cache"]["entries"] == 1
    assert data["cache"]["hits"] == 1


def test_html_wraps_markdown(populated_inputs: ReportInputs) -> None:
    body = render_html(populated_inputs)
    assert body.startswith("<!doctype html>")
    assert "<pre>" in body
    assert "reviewmind report" in body


def test_renderers_handle_missing_files(tmp_path: Path) -> None:
    # Everything optional — no store files exist on disk.
    inputs = ReportInputs(
        telemetry_path=tmp_path / "nope.sqlite",
        cache_path=tmp_path / "nope.sqlite",
        dismissed_path=tmp_path / "nope.jsonl",
        accepted_path=tmp_path / "nope.jsonl",
        since_seconds=None,
    )
    body = render_markdown(inputs)
    # Doesn't crash; reports zeros where data is missing.
    assert "No telemetry recorded" in body
    data = json.loads(render_json(inputs))
    assert data["telemetry"] == []
    assert data["cache"]["entries"] == 0


def test_since_window_label(populated_inputs: ReportInputs) -> None:
    populated_inputs = ReportInputs(
        telemetry_path=populated_inputs.telemetry_path,
        cache_path=populated_inputs.cache_path,
        dismissed_path=populated_inputs.dismissed_path,
        accepted_path=populated_inputs.accepted_path,
        since_seconds=7 * 86400.0,
    )
    body = render_markdown(populated_inputs)
    assert "last 7 day(s)" in body
