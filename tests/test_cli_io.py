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


def test_write_stdout_plain(capsys) -> None:
    from prthinker.cli_io import write_stdout

    write_stdout("hello")
    assert capsys.readouterr().out == "hello"


def test_write_stdout_falls_back_on_encode_error(monkeypatch) -> None:
    import io
    import sys

    from prthinker.cli_io import write_stdout

    captured: list[bytes] = []

    class _Buffer:
        def write(self, data: bytes) -> None:
            captured.append(data)

        def flush(self) -> None:
            pass

    class _Cp950Stdout(io.StringIO):
        encoding = "cp950"
        buffer = _Buffer()

        def write(self, text: str) -> int:
            # Mirror a Windows cp950 console choking on an emoji.
            text.encode("cp950")
            return len(text)

    monkeypatch.setattr(sys, "stdout", _Cp950Stdout())
    write_stdout("alert \U0001f6a8 done")
    assert captured, "fallback buffer never received bytes"
    assert b"alert " in captured[0] and b"done" in captured[0]


def test_write_stdout_fallback_without_buffer(monkeypatch) -> None:
    import io
    import sys

    from prthinker.cli_io import write_stdout

    written: list[str] = []

    class _NoBufferStdout(io.StringIO):
        encoding = "ascii"
        buffer = None

        def write(self, text: str) -> int:
            text.encode("ascii")  # raises on non-ascii
            written.append(text)
            return len(text)

    monkeypatch.setattr(sys, "stdout", _NoBufferStdout())
    write_stdout("café")  # non-ascii → replaced, not crashed
    assert written and "caf" in written[-1]
