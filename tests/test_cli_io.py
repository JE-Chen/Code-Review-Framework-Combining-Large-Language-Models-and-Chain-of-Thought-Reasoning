"""``prthinker.cli_io.emit_text`` — the shared file-or-stdout emit helper."""

from __future__ import annotations

from pathlib import Path

from prthinker.cli_io import emit_text


def test_emit_text_writes_file(tmp_path: Path) -> None:
    out = tmp_path / "report.json"
    emit_text("{}\n", out)
    assert out.read_text(encoding="utf-8") == "{}\n"


def test_emit_text_creates_parent_dirs(tmp_path: Path) -> None:
    out = tmp_path / "deep" / "nested" / "report.md"
    emit_text("# hi\n", out)
    assert out.read_text(encoding="utf-8") == "# hi\n"


def test_emit_text_stdout_when_out_is_none(capsys) -> None:
    emit_text("to stdout\n", None)
    assert capsys.readouterr().out == "to stdout\n"


def test_emit_text_empty_string_writes_empty_file(tmp_path: Path) -> None:
    out = tmp_path / "empty.txt"
    emit_text("", out)
    assert out.exists() and out.read_text(encoding="utf-8") == ""


def test_emit_text_utf8_content(tmp_path: Path) -> None:
    out = tmp_path / "utf8.md"
    emit_text("報告 · résumé\n", out)
    assert out.read_text(encoding="utf-8") == "報告 · résumé\n"


def test_emit_text_overwrites_existing_file(tmp_path: Path) -> None:
    out = tmp_path / "r.txt"
    out.write_text("old", encoding="utf-8")
    emit_text("new", out)
    assert out.read_text(encoding="utf-8") == "new"
