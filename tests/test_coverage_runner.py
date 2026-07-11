"""Tests for prthinker.coverage_runner — subprocess coverage collection.

The happy-path test runs the REAL ``coverage`` + ``pytest`` tools as
subprocesses against a tiny temp project; it skips (clearly marked)
only when neither tool is runnable via ``python -m``. Every failure
mode is covered fail-open with scripted ``subprocess.run`` stand-ins.
"""

from __future__ import annotations

import subprocess
import sys

import pytest

from prthinker import coverage_runner
from prthinker.coverage_runner import (
    MAX_TESTS_PER_RUN,
    collect_coverage,
    executed_lines,
)

_CALC_SRC = """\
def add(a, b):
    return a + b

def sub(a, b):
    return a - a
"""

_CALC_TESTS = """\
from calc import add, sub

def test_add():
    assert add(1, 2) == 3

def test_sub():
    assert sub(5, 2) == 3
"""


def _tool_runnable(module: str) -> bool:
    try:
        proc = subprocess.run(
            [sys.executable, "-m", module, "--version"],
            capture_output=True, text=True, timeout=60, check=False,
        )
    except OSError:
        return False
    return proc.returncode == 0


class TestRealSubprocessCollection:
    def test_collects_matrix_from_tiny_project(self, tmp_path):
        # REAL-SUBPROCESS TEST: exercises the actual coverage + pytest
        # tools; skipped only where they are not installed.
        if not (_tool_runnable("coverage") and _tool_runnable("pytest")):
            pytest.skip("coverage/pytest not runnable via 'python -m'")
        (tmp_path / "calc.py").write_text(_CALC_SRC, encoding="utf-8")
        (tmp_path / "test_calc.py").write_text(_CALC_TESTS, encoding="utf-8")

        matrix = collect_coverage(
            tmp_path,
            test_ids=["test_calc.py::test_add", "test_calc.py::test_sub"],
        )

        assert matrix.outcomes == {
            "test_calc.py::test_add": True,
            "test_calc.py::test_sub": False,
        }
        add_cov = matrix.coverage["test_calc.py::test_add"]
        sub_cov = matrix.coverage["test_calc.py::test_sub"]
        assert ("calc.py", 2) in add_cov  # body of add
        assert ("calc.py", 5) not in add_cov  # body of sub not executed
        assert ("calc.py", 5) in sub_cov  # the faulty line
        # Test modules themselves are excluded from the suspect set.
        assert all(not path.startswith("test_") for path, _ in add_cov | sub_cov)


class TestFailOpenBehaviour:
    def test_missing_tool_skips_all_tests(self, tmp_path, monkeypatch):
        def raise_missing(*_args, **_kwargs):
            raise FileNotFoundError("no python")

        monkeypatch.setattr(coverage_runner.subprocess, "run", raise_missing)
        matrix = collect_coverage(tmp_path, test_ids=["t::one"])
        assert matrix.coverage == {}
        assert matrix.outcomes == {}

    def test_timeout_skips_the_test(self, tmp_path, monkeypatch):
        def raise_timeout(argv, **_kwargs):
            raise subprocess.TimeoutExpired(cmd=argv, timeout=1)

        monkeypatch.setattr(coverage_runner.subprocess, "run", raise_timeout)
        matrix = collect_coverage(tmp_path, test_ids=["t::one"], timeout=1)
        assert matrix.coverage == {}

    def test_nonzero_rc_without_data_skips_the_test(self, tmp_path, monkeypatch):
        def fake_run(argv, **_kwargs):
            return subprocess.CompletedProcess(argv, returncode=2, stdout="", stderr="")

        monkeypatch.setattr(coverage_runner.subprocess, "run", fake_run)
        matrix = collect_coverage(tmp_path, test_ids=["t::one"])
        assert matrix.coverage == {}

    def test_json_export_failure_skips_the_test(self, tmp_path, monkeypatch):
        def fake_run(argv, **_kwargs):
            command = argv[3]  # [python, -m, coverage, <command>, ...]
            if command == "run":
                data_file = next(a for a in argv if str(a).startswith("--data-file="))
                with open(str(data_file).split("=", 1)[1], "w", encoding="utf-8") as fh:
                    fh.write("stub")
                return subprocess.CompletedProcess(argv, 0, stdout="", stderr="")
            return subprocess.CompletedProcess(argv, 1, stdout="", stderr="")

        monkeypatch.setattr(coverage_runner.subprocess, "run", fake_run)
        matrix = collect_coverage(tmp_path, test_ids=["t::one"])
        assert matrix.coverage == {}

    def test_test_ids_capped_at_module_constant(self, tmp_path, monkeypatch):
        calls: list[str] = []

        def fake_run_one(_workdir, _cmd, test_id, _timeout):
            calls.append(test_id)
            return {("m.py", 1)}, True

        monkeypatch.setattr(coverage_runner, "_run_one_test", fake_run_one)
        matrix = collect_coverage(tmp_path, test_ids=[f"t::{i}" for i in range(20)])
        assert len(calls) == MAX_TESTS_PER_RUN
        assert len(matrix.outcomes) == MAX_TESTS_PER_RUN

    def test_empty_test_ids_yield_empty_matrix(self, tmp_path):
        matrix = collect_coverage(tmp_path, test_ids=[])
        assert matrix.coverage == {}
        assert matrix.outcomes == {}


class TestExecutedLinesParsing:
    def test_parses_and_normalises_paths(self):
        report = {
            "files": {
                "pkg\\mod.py": {"executed_lines": [1, 3]},
                "app.py": {"executed_lines": [2]},
            }
        }
        assert executed_lines(report) == {
            ("pkg/mod.py", 1), ("pkg/mod.py", 3), ("app.py", 2),
        }

    def test_filters_test_modules(self):
        report = {
            "files": {
                "tests/test_mod.py": {"executed_lines": [1]},
                "tests/conftest.py": {"executed_lines": [2]},
                "pkg/mod_test.py": {"executed_lines": [3]},
                "pkg/real.py": {"executed_lines": [4]},
            }
        }
        assert executed_lines(report) == {("pkg/real.py", 4)}

    def test_missing_or_malformed_sections_yield_empty(self):
        assert executed_lines({}) == set()
        assert executed_lines({"files": {}}) == set()
        assert executed_lines({"files": {"a.py": {}}}) == set()
