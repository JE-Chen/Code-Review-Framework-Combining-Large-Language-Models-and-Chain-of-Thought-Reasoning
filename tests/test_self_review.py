"""Self-review parser + finding-block renderer.

The parser must be safe in the failure direction: malformed output
returns an empty drop-set, not a "drop everything" set. A wrong drop
loses a real finding; a missed drop just leaves noise the human can
ignore.
"""

from __future__ import annotations


from prthinker.schemas import InlineFinding
from prthinker.self_review import (
    apply_self_review,
    parse_drop_indices,
    render_findings_block,
)


def _f(line: int, severity: str, comment: str) -> InlineFinding:
    return InlineFinding(
        path="x.py", line=line, severity=severity, comment=comment,
    )


# ----- parser -----------------------------------------------------------

def test_parse_drop_indices_clean_json() -> None:
    raw = '{"drop": [1, 3], "reasons": ["dup", "noise"]}'
    assert parse_drop_indices(raw, total=5) == {0, 2}


def test_parse_drop_indices_inside_code_fence() -> None:
    raw = '```json\n{"drop": [2], "reasons": ["nit"]}\n```'
    assert parse_drop_indices(raw, total=3) == {1}


def test_parse_drop_indices_clamps_out_of_range() -> None:
    # 1 is valid (→ 0), 99 is past total → ignored; -3 → ignored.
    raw = '{"drop": [1, 99, -3]}'
    assert parse_drop_indices(raw, total=2) == {0}


def test_parse_drop_indices_garbage_yields_empty() -> None:
    assert parse_drop_indices("not json at all", total=5) == set()
    assert parse_drop_indices('{"unrelated": 1}', total=5) == set()
    assert parse_drop_indices('{"drop": "not a list"}', total=5) == set()


def test_parse_drop_indices_zero_total() -> None:
    assert parse_drop_indices('{"drop": [1, 2]}', total=0) == set()


# ----- application ------------------------------------------------------

def test_apply_self_review_drops_selected() -> None:
    findings = [_f(i, "warning", f"f{i}") for i in range(1, 4)]
    result = apply_self_review(findings, {0, 2})
    assert [f.line for f in result] == [2]


def test_apply_self_review_empty_drop_returns_input_copy() -> None:
    findings = [_f(1, "warning", "a"), _f(2, "warning", "b")]
    result = apply_self_review(findings, set())
    assert result == findings
    # ``apply_self_review`` returns a NEW list — mutating it must not
    # touch the original.
    result.clear()
    assert len(findings) == 2


# ----- renderer ---------------------------------------------------------

def test_render_findings_block_numbers_from_one() -> None:
    findings = [
        _f(7, "warning", "prefer logging"),
        _f(12, "error", "null deref"),
    ]
    rendered = render_findings_block(findings)
    assert rendered.startswith("1. [warning] line 7: prefer logging")
    assert "2. [error] line 12: null deref" in rendered


def test_render_findings_block_empty_input() -> None:
    assert render_findings_block([]) == "(no findings)"


def test_render_findings_block_truncates_long_comment() -> None:
    long = "x" * 300
    findings = [_f(1, "info", long)]
    rendered = render_findings_block(findings)
    # Renderer caps the comment at 200 chars per the source.
    assert "x" * 200 in rendered
    assert "x" * 201 not in rendered
