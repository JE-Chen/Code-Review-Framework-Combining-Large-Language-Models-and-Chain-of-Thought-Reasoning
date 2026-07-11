"""Tests for prthinker.stack_trace — failure text to ranked frames."""

from __future__ import annotations

from prthinker.stack_trace import TraceFrame, parse_traceback

_PY_TRACEBACK = """\
Traceback (most recent call last):
  File "/repo/app/main.py", line 10, in run
    helper()
  File "/usr/lib/python3.11/site-packages/pkg/mod.py", line 5, in helper
    inner()
  File "/repo/app/util.py", line 42, in inner
    raise ValueError("boom")
ValueError: boom
"""


class TestPythonTracebacks:
    def test_deepest_user_frame_first_with_workdir(self):
        frames = parse_traceback(_PY_TRACEBACK, workdir="/repo")
        assert frames == [
            TraceFrame(path="app/util.py", line=42, symbol="inner", rank=0),
            TraceFrame(path="app/main.py", line=10, symbol="run", rank=1),
        ]

    def test_site_packages_frames_filtered(self):
        frames = parse_traceback(_PY_TRACEBACK)
        assert all("site-packages" not in frame.path for frame in frames)

    def test_without_workdir_paths_stay_absolute_posix(self):
        frames = parse_traceback(_PY_TRACEBACK)
        assert frames[0].path == "/repo/app/util.py"

    def test_frame_without_symbol(self):
        text = '  File "pkg/mod.py", line 3\n    x = 1\n'
        frames = parse_traceback(text)
        assert frames == [TraceFrame(path="pkg/mod.py", line=3, symbol="", rank=0)]

    def test_all_noise_traceback_yields_empty(self):
        text = (
            '  File "/usr/lib/python3.11/site-packages/a.py", line 1, in f\n'
            '  File "<frozen importlib._bootstrap>", line 2, in g\n'
            '  File "<string>", line 1, in <module>\n'
        )
        assert parse_traceback(text) == []

    def test_windows_paths_normalised_against_workdir(self):
        text = '  File "C:\\proj\\pkg\\mod.py", line 7, in f\n'
        frames = parse_traceback(text, workdir="C:/proj")
        assert frames == [TraceFrame(path="pkg/mod.py", line=7, symbol="f", rank=0)]

    def test_stdlib_lib_python_frames_filtered(self):
        text = (
            '  File "/usr/lib/python3.11/json/decoder.py", line 5, in decode\n'
            '  File "/repo/app.py", line 2, in main\n'
        )
        frames = parse_traceback(text, workdir="/repo")
        assert [frame.path for frame in frames] == ["app.py"]


class TestGenericStacks:
    def test_node_stack_with_symbols_and_internals_filtered(self):
        text = (
            "Error: boom\n"
            "    at Object.<anonymous> (/app/src/index.js:10:5)\n"
            "    at helper (/app/node_modules/dep/lib.js:3:1)\n"
            "    at Module._compile (node:internal/modules/cjs/loader:1234:14)\n"
        )
        frames = parse_traceback(text, workdir="/app")
        assert frames == [
            TraceFrame(path="src/index.js", line=10, symbol="Object.<anonymous>", rank=0),
        ]

    def test_go_panic_frames_in_appearance_order(self):
        text = (
            "panic: runtime error: index out of range\n\n"
            "goroutine 1 [running]:\n"
            "main.doWork(...)\n"
            "\t/home/u/proj/main.go:12 +0x1b\n"
            "main.main()\n"
            "\t/home/u/proj/main.go:25 +0x2c\n"
        )
        frames = parse_traceback(text, workdir="/home/u/proj")
        assert [(frame.path, frame.line) for frame in frames] == [
            ("main.go", 12), ("main.go", 25),
        ]

    def test_rust_backtrace_filters_toolchain_frames(self):
        text = (
            "   0: std::panicking::begin_panic\n"
            "             at /rustc/abc123/library/std/src/panicking.rs:616:12\n"
            "   1: my_crate::do_thing\n"
            "             at ./src/lib.rs:12:9\n"
        )
        frames = parse_traceback(text)
        assert frames == [TraceFrame(path="src/lib.rs", line=12, symbol="", rank=0)]

    def test_generic_path_line_fallback(self):
        frames = parse_traceback("compile error in pkg/handler.py:88 (bad token)")
        assert frames == [TraceFrame(path="pkg/handler.py", line=88, symbol="", rank=0)]


class TestEdgeCases:
    def test_garbage_input_yields_empty(self):
        assert parse_traceback("nothing to see here, version 1.2.3, ok") == []

    def test_empty_input_yields_empty(self):
        assert parse_traceback("") == []

    def test_dedupe_preserves_best_rank(self):
        text = "boom at a/b.go:7\nagain a/b.go:7 and then a/c.go:9\n"
        frames = parse_traceback(text)
        assert frames == [
            TraceFrame(path="a/b.go", line=7, symbol="", rank=0),
            TraceFrame(path="a/c.go", line=9, symbol="", rank=1),
        ]

    def test_same_file_different_lines_kept(self):
        text = "x at a/b.go:7\ny at a/b.go:8\n"
        frames = parse_traceback(text)
        assert [(frame.path, frame.line) for frame in frames] == [
            ("a/b.go", 7), ("a/b.go", 8),
        ]

    def test_relative_dot_slash_prefix_stripped(self):
        frames = parse_traceback("failed at ./pkg/x.rs:3")
        assert frames[0].path == "pkg/x.rs"
