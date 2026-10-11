"""Prevent runner syntax from exceeding the minimum supported interpreter."""

import ast
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("source", sorted((ROOT / "prthinker").rglob("*.py")))
def test_runner_uses_python310_syntax(source):
    ast.parse(source.read_text(encoding="utf-8"), filename=str(source), feature_version=(3, 10))


def test_cli_help_works_with_legacy_windows_encoding(tmp_path):
    result = subprocess.run([sys.executable, "-m", "prthinker", "--help"], cwd=tmp_path,
                            env={**os.environ, "PYTHONIOENCODING": "cp950", "PYTHONPATH": str(ROOT)},
                            capture_output=True, timeout=30, check=False)
    assert result.returncode == 0, result.stderr.decode("utf-8", "replace")
    assert b"ablation-study" in result.stdout
