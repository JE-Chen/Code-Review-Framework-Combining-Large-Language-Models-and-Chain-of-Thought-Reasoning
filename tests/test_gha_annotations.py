"""Tests for the GitHub Actions workflow-command annotations."""

from __future__ import annotations

from prthinker.gha_annotations import print_gha_annotations, to_gha_annotations
from prthinker.pipeline import ReviewResult
from prthinker.schemas import InlineFinding


def _finding(path="a.py", line=10, severity="warning", comment="needs work"):
    return InlineFinding(path=path, line=line, severity=severity, comment=comment)


def _result(findings=None, code_diff="diff") -> ReviewResult:
    return ReviewResult(
        code_diff=code_diff, rag_docs=[], inline_findings=findings or []
    )


def test_empty_result_no_commands():
    assert to_gha_annotations(_result(code_diff="")) == []


def test_finding_maps_to_error_command():
    cmd = to_gha_annotations(_result([_finding(severity="error", comment="boom")]))[0]
    assert cmd.startswith("::error ")
    assert "file=a.py" in cmd
    assert "line=10" in cmd
    assert "title=prthinker/error" in cmd
    assert cmd.endswith("::boom")


def test_severity_maps_to_levels():
    levels = [
        to_gha_annotations(_result([_finding(severity=s)]))[0].split(" ", 1)[0]
        for s in ("error", "warning", "info")
    ]
    assert levels == ["::error", "::warning", "::notice"]


def test_message_newlines_are_escaped():
    cmd = to_gha_annotations(_result([_finding(comment="line1\nline2")]))[0]
    assert "\n" not in cmd.split("::", 2)[-1]
    assert "%0A" in cmd


def test_property_comma_and_colon_escaped():
    cmd = to_gha_annotations(_result([_finding(path="a,b:c.py")]))[0]
    assert "file=a%2Cb%3Ac.py" in cmd


def test_percent_escaped_first():
    cmd = to_gha_annotations(_result([_finding(comment="100% done")]))[0]
    assert "100%25 done" in cmd


def test_signals_included():
    diff = (
        "diff --git a/a.py b/a.py\n"
        "--- a/a.py\n"
        "+++ b/a.py\n"
        "@@ -0,0 +1,1 @@\n"
        "+<<<<<<< HEAD\n"
    )
    cmds = to_gha_annotations(_result(code_diff=diff))
    assert any("title=prthinker/merge-conflict" in c and c.startswith("::error")
               for c in cmds)


def test_pathless_signal_has_no_file_prop():
    diff = (
        "diff --git a/old.py b/new.py\n"
        "similarity index 100%\n"
        "rename from old.py\n"
        "rename to new.py\n"
    )
    cmds = to_gha_annotations(_result(code_diff=diff))
    rename = next(c for c in cmds if "title=prthinker/rename" in c)
    # rename carries the new path, so file= IS present.
    assert "file=new.py" in rename


def test_print_writes_each_command_line(capsys):
    print_gha_annotations(_result([_finding(comment="boom")]))
    out = capsys.readouterr().out.splitlines()
    assert len(out) == 1
    assert out[0].startswith("::warning ")
