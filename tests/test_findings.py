"""Findings parser + suggestion sanitizer.

A bad suggestion is worse than no suggestion — the sanitizer's job is to
drop only the suggestion (not the whole finding) when the model
violated the prompt contract.
"""

from __future__ import annotations

import json

import re

from prthinker.findings import (
    JSON_ARRAY_RE,
    extract_lenient_json,
    parse_inline_findings,
    strip_json_fences,
)

_OBJ_RE = re.compile(r"\{[\s\S]*\}")


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


def test_category_is_parsed_when_present() -> None:
    raw = json.dumps([
        {"line": 2, "severity": "error", "comment": "sqli", "category": "security"},
    ])
    findings = parse_inline_findings(raw, path="x.py", allowed_lines={2})
    assert findings[0].category == "security"


def test_category_defaults_to_none_when_absent() -> None:
    raw = json.dumps([{"line": 2, "severity": "info", "comment": "nit"}])
    findings = parse_inline_findings(raw, path="x.py", allowed_lines={2})
    assert findings[0].category is None


def test_category_round_trips_through_model_dump() -> None:
    from prthinker.schemas import InlineFinding

    original = InlineFinding(
        path="x.py", line=3, severity="warning",
        comment="n+1 query", category="performance",
    )
    restored = InlineFinding.model_validate(original.model_dump())
    assert restored == original
    assert restored.category == "performance"


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


def test_object_fallback_when_array_is_truncated() -> None:
    # A trailing-off array cannot be json.loads'd; the per-object regex
    # fallback must still recover the complete objects.
    raw = (
        '[{"line": 1, "severity": "info", "comment": "ok"}, {"line": 2,'
    )
    findings = parse_inline_findings(raw, path="x.py", allowed_lines={1})
    assert [f.line for f in findings] == [1]


# ----- shared lenient-JSON helpers ---------------------------------------

def test_strip_json_fences_unwraps_fenced_body() -> None:
    assert strip_json_fences("```json\n[1, 2]\n```") == "[1, 2]"


def test_strip_json_fences_plain_fence_without_language() -> None:
    assert strip_json_fences("```\n{}\n```") == "{}"


def test_strip_json_fences_no_fence_strips_whitespace() -> None:
    assert strip_json_fences("  [1]\n") == "[1]"


def test_strip_json_fences_empty_input() -> None:
    assert strip_json_fences("") == ""


def test_extract_lenient_json_array_happy_path() -> None:
    result = extract_lenient_json("noise [1, 2, 3] trailing", pattern=JSON_ARRAY_RE)
    assert result.matched is True
    assert result.decode_error is None
    assert result.data == [1, 2, 3]


def test_extract_lenient_json_object_happy_path() -> None:
    result = extract_lenient_json('```json\n{"a": 1}\n```', pattern=_OBJ_RE)
    assert result.matched is True
    assert result.data == {"a": 1}


def test_extract_lenient_json_no_match() -> None:
    result = extract_lenient_json("no json here", pattern=JSON_ARRAY_RE)
    assert result.matched is False
    assert result.data is None
    assert result.decode_error is None


def test_extract_lenient_json_empty_input() -> None:
    result = extract_lenient_json("", pattern=JSON_ARRAY_RE)
    assert result.matched is False


def test_extract_lenient_json_decode_error_is_reported() -> None:
    result = extract_lenient_json('[{"a": }]', pattern=JSON_ARRAY_RE)
    assert result.matched is True
    assert result.data is None
    assert result.decode_error is not None


def test_split_unified_review_happy_path() -> None:
    from prthinker.findings import split_unified_review

    raw = (
        '{"summary": "Looks fine.", "verdict": "approve", '
        '"findings": [{"line": 2, "severity": "info", "comment": "nit"}]}'
    )
    summary, findings_json = split_unified_review(raw)
    assert "Looks fine." in summary
    assert "Verdict: approve" in summary
    assert json.loads(findings_json) == [
        {"line": 2, "severity": "info", "comment": "nit"}
    ]


def test_split_unified_review_fenced_payload() -> None:
    from prthinker.findings import split_unified_review

    raw = '```json\n{"summary": "ok", "findings": []}\n```'
    summary, findings_json = split_unified_review(raw)
    assert summary == "ok"
    assert findings_json == "[]"


def test_split_unified_review_malformed_degrades_to_raw() -> None:
    from prthinker.findings import split_unified_review

    summary, findings_json = split_unified_review("no json here at all")
    assert summary == "no json here at all"
    assert findings_json == "[]"


def test_split_unified_review_non_list_findings_dropped() -> None:
    from prthinker.findings import split_unified_review

    summary, findings_json = split_unified_review(
        '{"summary": "s", "findings": "oops"}'
    )
    assert summary == "s"
    assert findings_json == "[]"


def test_split_unified_review_missing_fields() -> None:
    from prthinker.findings import split_unified_review

    summary, findings_json = split_unified_review("{}")
    assert summary == ""
    assert findings_json == "[]"
