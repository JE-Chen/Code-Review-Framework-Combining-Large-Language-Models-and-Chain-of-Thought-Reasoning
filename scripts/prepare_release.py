"""Synchronize package metadata only after final-release evidence passes."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from prthinker.release_gate import check_release

ROOT = Path(__file__).resolve().parents[1]


def prepare(root: Path, tag: str, checker=check_release):
    """Validate the exact requested version before writing build metadata."""
    if not re.fullmatch(r"v[1-9]\d*\.\d+\.\d+", tag):
        raise ValueError("final release requires a vMAJOR.MINOR.PATCH tag")
    version = tag[1:]
    evidence = root / "release/evidence.json"
    if json.loads(evidence.read_text(encoding="utf-8")).get("target_version") != version:
        raise ValueError("tag does not match evidence target version")
    if not checker(evidence)["ready"]:
        raise ValueError("final release evidence gates have not passed")
    replacements = []
    for relative, expression in (("pyproject.toml", r'(?m)^version = "[^"]+"$'),
                                 ("prthinker/__init__.py", r'(?m)^__version__ = "[^"]+"$'),
                                 ("CITATION.cff", r'(?m)^version: .+$')):
        path = root / relative
        text = path.read_text(encoding="utf-8")
        prefix = "__version__" if relative.endswith(".py") else "version"
        replacement = f'version: {version}' if relative.endswith(".cff") else f'{prefix} = "{version}"'
        updated, count = re.subn(expression, replacement, text)
        if count != 1:
            raise ValueError(f"ambiguous version metadata: {relative}")
        replacements.append((path, updated))
    for path, updated in replacements:
        path.write_text(updated, encoding="utf-8")
    return version


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tag")
    args = parser.parse_args()
    print(prepare(ROOT, args.tag))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
