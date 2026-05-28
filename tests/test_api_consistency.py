"""Cross-language API drift detector — schema + parser tests."""

from __future__ import annotations

import json

import pytest

from reviewmind.api_consistency import (
    build_prompt,
    classify_side,
    is_mixed_language,
    parse_drift_findings,
)
from reviewmind.diff import FileDiff
from reviewmind.schemas import ApiDriftFinding


def _fd(path: str, raw: str = "diff", is_binary: bool = False,
        is_deleted: bool = False) -> FileDiff:
    return FileDiff(path=path, raw=raw, is_binary=is_binary, is_deleted=is_deleted)


# ----- classification ---------------------------------------------------

@pytest.mark.parametrize(
    "path, expected",
    [
        ("api/routes.py",          "backend"),
        ("web/src/api.ts",         "frontend"),
        ("web/src/api.tsx",        "frontend"),
        ("web/main.js",            "frontend"),
        ("web/main.jsx",           "frontend"),
        ("scripts/setup.sh",       None),
        ("docs/README.md",         None),
        ("data.json",              None),
    ],
)
def test_classify_side(path: str, expected: str | None) -> None:
    assert classify_side(path) == expected


# ----- mixed-language detection -----------------------------------------

def test_is_mixed_language_yes() -> None:
    assert is_mixed_language([_fd("backend/app.py"), _fd("ui/api.ts")])


def test_is_mixed_language_no_only_backend() -> None:
    assert not is_mixed_language([_fd("a.py"), _fd("b.py")])


def test_is_mixed_language_no_only_frontend() -> None:
    assert not is_mixed_language([_fd("a.ts"), _fd("b.tsx")])


def test_is_mixed_language_ignores_binary_and_deleted() -> None:
    diffs = [
        _fd("ignored.ts", is_binary=True),
        _fd("dropped.py", is_deleted=True),
        _fd("a.py"),
    ]
    assert not is_mixed_language(diffs)


# ----- prompt builder ---------------------------------------------------

def test_build_prompt_empty_when_not_mixed() -> None:
    assert build_prompt([_fd("a.py")]) == ""


def test_build_prompt_lists_both_sides() -> None:
    diffs = [
        _fd("backend/routes.py", raw="@@ +1 @@\n+def x(): pass\n"),
        _fd("web/api.ts",        raw="@@ +1 @@\n+function x() {}\n"),
    ]
    prompt = build_prompt(diffs)
    assert "## Backend (Python) files" in prompt
    assert "## Frontend (TypeScript / JavaScript) files" in prompt
    assert "`backend/routes.py`" in prompt
    assert "`web/api.ts`" in prompt


# ----- parser -----------------------------------------------------------

def _allowed() -> set[str]:
    return {"backend/r.py", "web/api.ts"}


def test_parse_clean_payload() -> None:
    raw = json.dumps([{
        "backend_path":  "backend/r.py",
        "frontend_path": "web/api.ts",
        "kind":          "field_renamed",
        "summary":       "user_id → userId",
        "evidence":      "diff snippet",
    }])
    out = parse_drift_findings(raw, allowed_paths=_allowed())
    assert len(out) == 1
    assert out[0].kind == "field_renamed"
    assert out[0].backend_path == "backend/r.py"


def test_parse_inside_fenced_block() -> None:
    raw = (
        "Here is the result:\n```json\n"
        + json.dumps([{
            "backend_path":  "backend/r.py",
            "frontend_path": "web/api.ts",
            "kind":          "other",
            "summary":       "x",
        }])
        + "\n```"
    )
    out = parse_drift_findings(raw, allowed_paths=_allowed())
    assert len(out) == 1


def test_parser_drops_unknown_paths() -> None:
    raw = json.dumps([
        {
            "backend_path":  "fake/x.py", "frontend_path": "web/api.ts",
            "kind": "other", "summary": "x",
        },
        {
            "backend_path":  "backend/r.py", "frontend_path": "fake/y.ts",
            "kind": "other", "summary": "y",
        },
        {
            "backend_path":  "backend/r.py", "frontend_path": "web/api.ts",
            "kind": "other", "summary": "ok",
        },
    ])
    out = parse_drift_findings(raw, allowed_paths=_allowed())
    assert [df.summary for df in out] == ["ok"]


def test_parser_returns_empty_on_garbage() -> None:
    assert parse_drift_findings("not json", allowed_paths=_allowed()) == []
    assert parse_drift_findings("[]", allowed_paths=_allowed()) == []


def test_parser_drops_malformed_entries() -> None:
    raw = json.dumps([
        "not a dict",
        {"backend_path": "backend/r.py"},  # missing required summary
        {
            "backend_path":  "backend/r.py", "frontend_path": "web/api.ts",
            "kind": "field_renamed", "summary": "keep me",
        },
    ])
    out = parse_drift_findings(raw, allowed_paths=_allowed())
    assert [df.summary for df in out] == ["keep me"]


# ----- ApiDriftFinding schema -------------------------------------------

def test_api_drift_finding_default_kind() -> None:
    df = ApiDriftFinding(
        backend_path="b.py", frontend_path="f.ts", summary="s",
    )
    assert df.kind == "other"
    assert df.evidence == ""


def test_api_drift_rejects_unknown_kind() -> None:
    with pytest.raises(Exception):
        ApiDriftFinding(
            backend_path="b.py", frontend_path="f.ts",
            summary="s", kind="not_a_kind",  # type: ignore[arg-type]
        )
