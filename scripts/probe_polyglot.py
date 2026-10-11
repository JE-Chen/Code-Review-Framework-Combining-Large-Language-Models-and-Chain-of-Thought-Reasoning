"""Offline parser probe for the optional multi-language grammar dependency."""

import json
import tempfile
from pathlib import Path

from prthinker.context_graph import parse_tree_sitter

SAMPLES = {
    "java": ("A.java", "class Alpha {}", "Alpha"),
    "go": ("a.go", "package main\nfunc Alpha() {}", "Alpha"),
    "rust": ("a.rs", "fn alpha() {}", "alpha"),
    "c": ("a.c", "int alpha() {return 1;}", "alpha"),
    "cpp": ("a.cpp", "int alpha() {return 1;}", "alpha"),
    "c_sharp": ("A.cs", "class Alpha {}", "Alpha"),
    "kotlin": ("a.kt", "class Alpha {}", "Alpha"),
}


def main():
    results = {}
    with tempfile.TemporaryDirectory(prefix="prthinker-parser-") as temporary:
        root = Path(temporary)
        for language, (name, code, expected) in SAMPLES.items():
            path = root / name
            path.write_text(code, encoding="utf-8")
            symbols = [node.name for node in parse_tree_sitter(path, language)]
            if expected not in symbols:
                raise RuntimeError(f"{language} failed to extract the fixture symbol")
            results[language] = symbols
    print(json.dumps({"measurement": "offline_parser_probe", "status": "passed", "checks": results}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
