"""Tests for the orientation signal composition."""

from __future__ import annotations

from prthinker.orientation import build_static_signal_sections


def test_empty_diff_yields_no_sections():
    assert build_static_signal_sections("", []) == ()


def test_clean_change_yields_no_sections():
    # A docs change with a real edit: no signal fires (coverage-gap only
    # flags production .py files, not Markdown).
    diff = (
        "diff --git a/docs/x.md b/docs/x.md\n"
        "--- a/docs/x.md\n"
        "+++ b/docs/x.md\n"
        "@@ -1 +1 @@\n"
        "-old text\n"
        "+new text\n"
    )
    assert build_static_signal_sections(diff, ["docs/x.md"]) == ()


def test_security_signals_lead_ordering():
    # A diff carrying both a conflict marker and a deferred-work marker:
    # the conflict (security) block must come before the marker block.
    diff = (
        "diff --git a/a.py b/a.py\n"
        "--- a/a.py\n"
        "+++ b/a.py\n"
        "@@ -0,0 +1,2 @@\n"
        "+<<<<<<< HEAD\n"
        "+# TODO: finish\n"
    )
    sections = build_static_signal_sections(diff, ["a.py"])
    blob = "\n".join(sections)
    conflict_at = blob.index("merge-conflict marker(s)")
    todo_at = blob.index("deferred-work marker(s)")
    assert conflict_at < todo_at


def test_path_only_signal_without_diff_lines():
    # noise_files works off the changed-path list alone.
    sections = build_static_signal_sections("", ["poetry.lock"])
    assert any("low-attention file(s)" in s for s in sections)


def test_returns_only_nonempty_blocks():
    diff = (
        "diff --git a/run.sh b/run.sh\n"
        "old mode 100644\n"
        "new mode 100755\n"
    )
    sections = build_static_signal_sections(diff, ["run.sh"])
    assert all(s.strip() for s in sections)
    assert any("file mode change(s)" in s for s in sections)
