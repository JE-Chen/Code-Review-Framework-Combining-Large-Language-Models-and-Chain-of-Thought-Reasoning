"""Findings parser + suggestion sanitizer.

A bad suggestion is worse than no suggestion — the sanitizer's job is to
drop only the suggestion (not the whole finding) when the model
violated the prompt contract.
"""

from __future__ import annotations

import json

from reviewmind.findings import parse_inline_findings


def test_empty_array_returns_no_findings() -> None:
    assert parse_inline_findings("[]", path="x.py") == []


def test_plain_array_round_trips() -> None:
    raw = json.dumps([
        {"line": 2, "severity": "warning", "comment": "use logging"},
        {"line": 5, "severity": "error", "comment": "null deref"},
    ])
    findings = parse_inline_findings(raw, path="x.py", allowed_lines={2, 5})
    assert [f.line for f in findings] == [2, 5]
    assert [f.severity for f in findings] == ["warning", "error"]
    assert all(f.path == "x.py" for f in findings)


def test_json_fences_are_stripped() -> None:
    raw = (
        "Here are my findings:\n\n"
        "```json\n"
        '[{"line": 1, "severity": "info", "comment": "nit"}]\n'
        "```\n"
    )
    findings = parse_inline_findings(raw, path="x.py", allowed_lines={1})
    assert len(findings) == 1
    assert findings[0].comment == "nit"


def test_lines_outside_diff_are_dropped() -> None:
    raw = json.dumps([
        {"line": 1, "severity": "info", "comment": "ok"},
        {"line": 999, "severity": "error", "comment": "imaginary"},
    ])
    findings = parse_inline_findings(raw, path="x.py", allowed_lines={1, 2})
    assert [f.line for f in findings] == [1]


def test_path_is_always_pinned_to_caller() -> None:
    # The model is asked to omit ``path``; we shouldn't trust whatever it
    # puts there. The parser must overwrite to the caller's path.
    raw = json.dumps([
        {"path": "wrong.py", "line": 1, "severity": "info", "comment": "x"},
    ])
    findings = parse_inline_findings(raw, path="x.py", allowed_lines={1})
    assert findings[0].path == "x.py"


def test_sanitizer_drops_suggestion_on_info_severity() -> None:
    raw = json.dumps([
        {"line": 1, "severity": "info", "comment": "nit", "suggestion": "fix"},
    ])
    findings = parse_inline_findings(raw, path="x.py", allowed_lines={1})
    assert findings[0].suggestion is None
    # The textual comment survives so the reviewer still sees the advice.
    assert findings[0].comment == "nit"


def test_sanitizer_keeps_single_line_suggestion_on_error() -> None:
    raw = json.dumps([
        {
            "line": 2, "severity": "error",
            "comment": "logger >> print",
            "suggestion": "    logger.info('hi')",
            "original": "    print('hi')",
        },
    ])
    findings = parse_inline_findings(raw, path="x.py", allowed_lines={1, 2})
    assert findings[0].suggestion == "    logger.info('hi')"


def test_sanitizer_keeps_valid_multiline_suggestion() -> None:
    raw = json.dumps([
        {
            "line": 5, "start_line": 3, "severity": "warning",
            "comment": "swap order",
            "suggestion": "a\nb\nc",
        },
    ])
    findings = parse_inline_findings(raw, path="x.py", allowed_lines={3, 4, 5})
    f = findings[0]
    assert f.start_line == 3
    assert f.line == 5
    assert f.suggestion == "a\nb\nc"


def test_sanitizer_drops_suggestion_when_line_count_mismatches() -> None:
    raw = json.dumps([
        {
            "line": 5, "start_line": 3, "severity": "warning",
            "comment": "wrong count",
            "suggestion": "x",  # 1 line, but range is 3 lines
        },
    ])
    findings = parse_inline_findings(raw, path="x.py", allowed_lines={3, 4, 5})
    assert findings[0].suggestion is None
    assert findings[0].start_line is None
    assert findings[0].comment == "wrong count"


def test_sanitizer_drops_suggestion_when_start_line_exceeds_line() -> None:
    raw = json.dumps([
        {
            "line": 3, "start_line": 5, "severity": "warning",
            "comment": "swap", "suggestion": "x",
        },
    ])
    findings = parse_inline_findings(raw, path="x.py", allowed_lines={3, 5})
    assert findings[0].suggestion is None


def test_malformed_entries_are_skipped() -> None:
    raw = json.dumps([
        {"line": 1, "severity": "warning", "comment": "good"},
        {"line": "not-a-number", "severity": "warning", "comment": "bad"},
        {"line": 2, "severity": "warning", "comment": "good2"},
    ])
    findings = parse_inline_findings(raw, path="x.py", allowed_lines={1, 2})
    assert [f.line for f in findings] == [1, 2]
