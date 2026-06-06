"""Regression: prthinker is self-contained and its prompts mirror stays in sync.

The runner is installed standalone in other repositories
(``pip install "prthinker[runner] @ git+..."``) where the project-specific
``codes`` tree does not exist. The CoT prompt templates must therefore
resolve from the bundled ``prthinker/prompts/`` package, never from
``codes.run.CoT_Prompts``. ``prthinker/prompts/`` is a mirror of the
canonical corpus at ``codes/run/CoT_Prompts/`` (kept in both places on
purpose); the parity test guards against the two drifting apart.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_CANONICAL = _REPO_ROOT / "codes" / "run" / "CoT_Prompts"
_BUNDLED = _REPO_ROOT / "prthinker" / "prompts"

# Run in a fresh interpreter with every ``codes`` import blocked, so the
# only way ``import prthinker`` can succeed is via the bundled prompts.
_STANDALONE_SNIPPET = """
import sys, importlib.abc


class _BlockCodes(importlib.abc.MetaPathFinder):
    def find_spec(self, name, path, target=None):
        if name == "codes" or name.startswith("codes."):
            raise ModuleNotFoundError("blocked for test: " + name)
        return None


sys.meta_path.insert(0, _BlockCodes())

import prthinker  # noqa: F401
from prthinker.steps import registered_steps
from prthinker.prompts.code_smell_detector import CODE_SMELL_DETECTOR_TEMPLATE
from prthinker.prompts.inline_findings import INLINE_FINDINGS_TEMPLATE

assert registered_steps(), "no review steps registered"
assert CODE_SMELL_DETECTOR_TEMPLATE.strip(), "empty code-smell template"
assert INLINE_FINDINGS_TEMPLATE.strip(), "empty inline-findings template"
print("OK")
"""


def test_prthinker_imports_without_codes():
    proc = subprocess.run(  # noqa: S603 — fixed args, no shell, trusted input
        [sys.executable, "-c", _STANDALONE_SNIPPET],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, f"stdout={proc.stdout!r} stderr={proc.stderr!r}"
    assert "OK" in proc.stdout


def test_bundled_prompts_mirror_canonical():
    # Every canonical template module must exist byte-for-byte in the
    # bundled mirror. (The mirror also carries package __init__.py files
    # the namespace-style canonical dir does not; those are not compared.)
    canonical_files = sorted(
        p for p in _CANONICAL.rglob("*.py") if "__pycache__" not in p.parts
    )
    assert canonical_files, "no canonical prompt templates found"
    missing: list[str] = []
    mismatched: list[str] = []
    for src in canonical_files:
        rel = src.relative_to(_CANONICAL)
        dst = _BUNDLED / rel
        if not dst.is_file():
            missing.append(str(rel))
            continue
        if src.read_bytes() != dst.read_bytes():
            mismatched.append(str(rel))
    assert not missing, f"bundled mirror missing: {missing}"
    assert not mismatched, f"bundled mirror out of sync (re-copy): {mismatched}"
