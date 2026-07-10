"""Tests for the depth-eval CLI subcommand (prthinker.depth_eval_cli)."""

from __future__ import annotations

from pathlib import Path

import pytest

from prthinker.cli_parser import _build_parser
from prthinker.depth_eval import CountingBackend, PipelineProbe
from prthinker.depth_eval_cli import command, load_diffs
from prthinker.pipeline import CoTPipeline
from tests.conftest import FakeBackend


class _NoOpRetriever:
    def retrieve(self, _text: str) -> list[str]:
        return []


_DIFF = "\n".join(
    ["diff --git a/mod.py b/mod.py", "--- a/mod.py", "+++ b/mod.py",
     "@@ -1,60 +1,60 @@"]
    + [f"+line {i}" for i in range(50)]
)


def _fake_factory(_mode: str) -> PipelineProbe:
    backend = CountingBackend(FakeBackend())
    pipeline = CoTPipeline(backend=backend, retriever=_NoOpRetriever())
    return PipelineProbe(pipeline=pipeline, usage_snapshot=backend.snapshot)


def _parse(argv: list[str]):
    return _build_parser().parse_args(argv)


# ---------------------------------------------------------------------------
# Parser registration
# ---------------------------------------------------------------------------


def test_parser_accepts_depth_eval_subcommand(tmp_path: Path):
    args = _parse(["depth-eval", "--diffs-dir", str(tmp_path)])
    assert args.command == "depth-eval"
    assert args.diffs_dir == tmp_path
    assert args.diffs_jsonl is None
    assert args.out is None
    assert args.max_diffs == 0
    # The shared backend flags ride along from the common parser.
    assert hasattr(args, "backend")
    assert hasattr(args, "step_plan")


def test_parser_requires_a_diff_source():
    with pytest.raises(SystemExit):
        _parse(["depth-eval"])


def test_parser_rejects_both_diff_sources(tmp_path: Path):
    with pytest.raises(SystemExit):
        _parse(
            ["depth-eval", "--diffs-dir", str(tmp_path),
             "--diffs-jsonl", str(tmp_path / "x.jsonl")]
        )


def test_parser_reads_out_and_max_diffs(tmp_path: Path):
    args = _parse(
        ["depth-eval", "--diffs-dir", str(tmp_path),
         "--out", str(tmp_path / "r.md"), "--max-diffs", "3"]
    )
    assert args.out == tmp_path / "r.md"
    assert args.max_diffs == 3


# ---------------------------------------------------------------------------
# load_diffs
# ---------------------------------------------------------------------------


def test_load_diffs_dir_reads_diff_and_patch_files(tmp_path: Path):
    (tmp_path / "b.diff").write_text("diff b", encoding="utf-8")
    (tmp_path / "a.patch").write_text("diff a", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("ignored", encoding="utf-8")
    assert load_diffs(tmp_path, None) == ["diff a", "diff b"]


def test_load_diffs_dir_missing_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_diffs(tmp_path / "absent", None)


def test_load_diffs_jsonl(tmp_path: Path):
    corpus = tmp_path / "c.jsonl"
    corpus.write_text('{"diff": "one"}\n\n{"diff": "two"}\n', encoding="utf-8")
    assert load_diffs(None, corpus) == ["one", "two"]


def test_load_diffs_jsonl_rejects_row_without_diff(tmp_path: Path):
    corpus = tmp_path / "c.jsonl"
    corpus.write_text('{"diff": "one"}\n{"nope": 1}\n', encoding="utf-8")
    with pytest.raises(ValueError, match="c.jsonl:2"):
        load_diffs(None, corpus)


def test_load_diffs_max_diffs_cap(tmp_path: Path):
    for name in ("a.diff", "b.diff", "c.diff"):
        (tmp_path / name).write_text(name, encoding="utf-8")
    assert load_diffs(tmp_path, None, max_diffs=2) == ["a.diff", "b.diff"]
    assert len(load_diffs(tmp_path, None, max_diffs=0)) == 3


# ---------------------------------------------------------------------------
# command
# ---------------------------------------------------------------------------


def test_command_empty_dir_is_clean_error(tmp_path: Path, capsys):
    args = _parse(["depth-eval", "--diffs-dir", str(tmp_path)])
    assert command(args, pipeline_factory=_fake_factory) == 2
    assert "no diffs found" in capsys.readouterr().err


def test_command_missing_dir_is_clean_error(tmp_path: Path, capsys):
    args = _parse(["depth-eval", "--diffs-dir", str(tmp_path / "absent")])
    assert command(args, pipeline_factory=_fake_factory) == 2
    assert "not a directory" in capsys.readouterr().err


def test_command_bad_jsonl_is_clean_error(tmp_path: Path, capsys):
    corpus = tmp_path / "c.jsonl"
    corpus.write_text('{"nope": 1}\n', encoding="utf-8")
    args = _parse(["depth-eval", "--diffs-jsonl", str(corpus)])
    assert command(args, pipeline_factory=_fake_factory) == 2
    assert "'diff'" in capsys.readouterr().err


def test_command_writes_report_to_out_file(tmp_path: Path):
    (tmp_path / "one.diff").write_text(_DIFF, encoding="utf-8")
    out = tmp_path / "report" / "depth.md"
    args = _parse(
        ["depth-eval", "--diffs-dir", str(tmp_path), "--out", str(out)]
    )
    assert command(args, pipeline_factory=_fake_factory) == 0
    text = out.read_text(encoding="utf-8")
    assert text.startswith("# Review depth evaluation")
    assert "Diffs compared: 1" in text


def test_command_defaults_to_stdout(tmp_path: Path, capsys):
    (tmp_path / "one.diff").write_text(_DIFF, encoding="utf-8")
    args = _parse(["depth-eval", "--diffs-dir", str(tmp_path)])
    assert command(args, pipeline_factory=_fake_factory) == 0
    assert "# Review depth evaluation" in capsys.readouterr().out


def test_command_max_diffs_caps_comparison(tmp_path: Path):
    for name in ("a.diff", "b.diff", "c.diff"):
        (tmp_path / name).write_text(_DIFF, encoding="utf-8")
    out = tmp_path / "depth.md"
    args = _parse(
        ["depth-eval", "--diffs-dir", str(tmp_path),
         "--max-diffs", "2", "--out", str(out)]
    )
    assert command(args, pipeline_factory=_fake_factory) == 0
    assert "Diffs compared: 2" in out.read_text(encoding="utf-8")
