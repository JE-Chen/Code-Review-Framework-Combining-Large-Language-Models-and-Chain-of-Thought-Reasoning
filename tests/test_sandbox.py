"""Sandbox verifier — tests target the pure-data application logic
plus the verify command runner using a tiny shell-free workdir.

We intentionally use a non-shell verify command (``python -c "..."``)
so the subprocess call works on every CI platform and never depends
on bash being available.
"""

from __future__ import annotations

import sys
from pathlib import Path

from reviewmind.sandbox import VerificationResult, verify_suggestion
from reviewmind.schemas import InlineFinding


def _make_workdir(tmp_path: Path, body: str) -> Path:
    workdir = tmp_path / "src"
    workdir.mkdir()
    (workdir / "a.py").write_text(body, encoding="utf-8")
    return workdir


# ----- skip cases (no side effects) --------------------------------------

def test_no_suggestion_returns_skip(tmp_path: Path) -> None:
    workdir = _make_workdir(tmp_path, "x = 1\n")
    f = InlineFinding(path="a.py", line=1, severity="info", comment="ok")
    result = verify_suggestion(f, workdir=workdir, verify_cmd="echo")
    assert result.status == "skip"
    assert "no suggestion" in result.reason


def test_missing_file_returns_skip(tmp_path: Path) -> None:
    workdir = _make_workdir(tmp_path, "x = 1\n")
    f = InlineFinding(
        path="does_not_exist.py", line=1, severity="warning",
        comment="x", suggestion="y = 2",
    )
    result = verify_suggestion(f, workdir=workdir, verify_cmd="echo")
    assert result.status == "skip"
    assert "not present" in result.reason


def test_original_mismatch_returns_skip(tmp_path: Path) -> None:
    workdir = _make_workdir(tmp_path, "x = 1\n")
    f = InlineFinding(
        path="a.py", line=1, severity="warning", comment="x",
        original="something_else = 9",
        suggestion="x = 99",
    )
    result = verify_suggestion(f, workdir=workdir, verify_cmd="echo")
    assert result.status == "skip"
    assert "original text does not match" in result.reason


def test_line_range_out_of_bounds_returns_skip(tmp_path: Path) -> None:
    workdir = _make_workdir(tmp_path, "x = 1\n")
    f = InlineFinding(
        path="a.py", line=99, severity="warning", comment="x",
        suggestion="x = 2",
    )
    result = verify_suggestion(f, workdir=workdir, verify_cmd="echo")
    assert result.status == "skip"
    assert "out of file" in result.reason


# ----- pass / fail (apply + run verify_cmd) ------------------------------

def test_pass_when_verify_cmd_exits_zero(tmp_path: Path) -> None:
    workdir = _make_workdir(tmp_path, "x = 1\n")
    f = InlineFinding(
        path="a.py", line=1, severity="warning", comment="x",
        suggestion="x = 2",
    )
    py = sys.executable
    result = verify_suggestion(
        f, workdir=workdir,
        verify_cmd=f'{py} -c exit(0)',
    )
    assert result.status == "pass"
    assert result.duration_ms >= 0


def test_fail_when_verify_cmd_exits_nonzero(tmp_path: Path) -> None:
    workdir = _make_workdir(tmp_path, "x = 1\n")
    f = InlineFinding(
        path="a.py", line=1, severity="warning", comment="x",
        suggestion="x = 2",
    )
    py = sys.executable
    result = verify_suggestion(
        f, workdir=workdir,
        verify_cmd=f'{py} -c exit(7)',
    )
    assert result.status == "fail"
    assert "exit=7" in result.reason


def test_verify_cmd_not_runnable_returns_error(tmp_path: Path) -> None:
    workdir = _make_workdir(tmp_path, "x = 1\n")
    f = InlineFinding(
        path="a.py", line=1, severity="warning", comment="x",
        suggestion="x = 2",
    )
    result = verify_suggestion(
        f, workdir=workdir, verify_cmd="this-binary-does-not-exist-xyz",
    )
    assert result.status == "error"
    assert "not runnable" in result.reason


def test_sandbox_does_not_modify_original_workdir(tmp_path: Path) -> None:
    original = "x = 1\n"
    workdir = _make_workdir(tmp_path, original)
    f = InlineFinding(
        path="a.py", line=1, severity="warning", comment="x",
        suggestion="x = 999",
    )
    py = sys.executable
    verify_suggestion(
        f, workdir=workdir, verify_cmd=f'{py} -c exit(0)',
    )
    # The original file in workdir must remain untouched.
    assert (workdir / "a.py").read_text(encoding="utf-8") == original


# ----- VerificationResult is frozen --------------------------------------

def test_verification_result_is_frozen() -> None:
    r = VerificationResult(status="pass", verify_cmd="x")
    try:
        r.status = "fail"  # type: ignore[misc]
    except Exception:
        return
    raise AssertionError("VerificationResult should be frozen")
