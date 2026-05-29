"""Per-repo knowledge graph — ground the reviewer in real symbols.

LLM reviewers on large repos routinely hallucinate symbol names — they
write "the ``get_user`` function in ``auth.py``" when ``get_user``
actually lives in ``core/users.py``, or invent class methods that
never existed. This module scans the working tree once, extracts the
canonical ``{symbol: (file, line, kind)}`` mapping using Python ``ast``
and lightweight regex for JS/TS, and persists it to SQLite. The
inline-findings prompt then carries a "Known symbols" block that the
model is told to treat as the authoritative truth.

Per ``paper_rule.md``'s no-fabrication rule, this module ships the
mechanism only. Whether symbol-grounding reduces hallucination rate on
real PRs is future work.
"""

from __future__ import annotations

import ast
import contextlib
import logging
import re
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

log = logging.getLogger(__name__)


_SCHEMA = """
CREATE TABLE IF NOT EXISTS symbols (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    workdir     TEXT    NOT NULL,
    file_path   TEXT    NOT NULL,
    symbol      TEXT    NOT NULL,
    kind        TEXT    NOT NULL,
    line        INTEGER NOT NULL,
    parent      TEXT    NOT NULL DEFAULT '',
    ts          REAL    NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_symbols_name
    ON symbols (workdir, symbol);
CREATE INDEX IF NOT EXISTS idx_symbols_file
    ON symbols (workdir, file_path);
"""


@dataclass(frozen=True)
class Symbol:
    """One canonical symbol exported by the repo."""

    symbol: str
    kind: str  # "function" / "class" / "method" / "ts_export" / "const"
    file_path: str
    line: int
    parent: str = ""  # enclosing class for methods, else ""


# ---------------------------------------------------------------------------
# Python AST scanner
# ---------------------------------------------------------------------------


def _scan_python(file_path: Path, rel: str) -> list[Symbol]:
    """Walk a Python file's AST and yield top-level + class-method symbols.

    Private names (``_x``) are kept — they're still canonical and the
    reviewer should still treat them as real. We skip generated /
    obviously-broken files via try/except around the parse.
    """
    try:
        tree = ast.parse(file_path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, SyntaxError):
        return []

    out: list[Symbol] = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            out.append(Symbol(
                symbol=node.name, kind="function",
                file_path=rel, line=node.lineno,
            ))
        elif isinstance(node, ast.ClassDef):
            out.append(Symbol(
                symbol=node.name, kind="class",
                file_path=rel, line=node.lineno,
            ))
            for inner in node.body:
                if isinstance(inner, ast.FunctionDef | ast.AsyncFunctionDef):
                    out.append(Symbol(
                        symbol=inner.name, kind="method",
                        file_path=rel, line=inner.lineno,
                        parent=node.name,
                    ))
        elif isinstance(node, ast.Assign):
            # Top-level constants — heuristic: ALL_CAPS names.
            for target in node.targets:
                if (
                    isinstance(target, ast.Name)
                    and target.id.isupper()
                    and target.id.replace("_", "").isalnum()
                ):
                    out.append(Symbol(
                        symbol=target.id, kind="const",
                        file_path=rel, line=node.lineno,
                    ))
    return out


# ---------------------------------------------------------------------------
# JS / TS regex scanner — intentionally simple; we want zero parser deps in
# the runner profile. Catches the most common export forms; misses esoteric
# ones, which is fine — the model gets fewer symbols, not wrong ones.
# ---------------------------------------------------------------------------

_TS_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("function", re.compile(r"^export\s+(?:async\s+)?function\s+(\w+)", re.MULTILINE)),
    ("class",    re.compile(r"^export\s+(?:abstract\s+)?class\s+(\w+)", re.MULTILINE)),
    ("ts_type",  re.compile(r"^export\s+(?:type|interface|enum)\s+(\w+)", re.MULTILINE)),
    ("const",    re.compile(r"^export\s+const\s+(\w+)", re.MULTILINE)),
    ("default",  re.compile(r"^export\s+default\s+(?:function\s+)?(\w+)", re.MULTILINE)),
)


def _scan_jsts(file_path: Path, rel: str) -> list[Symbol]:
    try:
        body = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []
    out: list[Symbol] = []
    for kind, pat in _TS_PATTERNS:
        for m in pat.finditer(body):
            out.append(Symbol(
                symbol=m.group(1), kind=kind, file_path=rel,
                line=body.count("\n", 0, m.start()) + 1,
            ))
    return out


_LANG_DISPATCH: dict[str, callable] = {
    ".py":   _scan_python,
    ".ts":   _scan_jsts,
    ".tsx":  _scan_jsts,
    ".js":   _scan_jsts,
    ".jsx":  _scan_jsts,
    ".mjs":  _scan_jsts,
    ".cjs":  _scan_jsts,
}

_IGNORED_DIRS = frozenset({
    ".git", "node_modules", "__pycache__", ".venv", "venv", "dist",
    "build", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "_build",
})


def scan_workdir(workdir: Path) -> list[Symbol]:
    """Walk ``workdir`` and extract every Symbol in supported languages."""
    out: list[Symbol] = []
    for file in workdir.rglob("*"):
        if not file.is_file():
            continue
        if any(part in _IGNORED_DIRS for part in file.parts):
            continue
        scanner = _LANG_DISPATCH.get(file.suffix.lower())
        if scanner is None:
            continue
        rel = file.relative_to(workdir).as_posix()
        out.extend(scanner(file, rel))
    return out


# ---------------------------------------------------------------------------
# Persistent store
# ---------------------------------------------------------------------------


class KnowledgeGraphStore:
    """SQLite-backed store of ``Symbol``s scoped by ``workdir`` path."""

    def __init__(self, path: Path) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript(_SCHEMA)

    @contextlib.contextmanager
    def _connect(self):
        conn = sqlite3.connect(str(self._path), isolation_level=None)
        try:
            yield conn
        finally:
            conn.close()

    def rebuild(self, workdir: Path, symbols: Iterable[Symbol]) -> int:
        """Drop every symbol for ``workdir`` and insert ``symbols``.

        Wholesale-rebuild semantics so the store always reflects HEAD;
        partial updates are deferred to future work.
        """
        wd = str(workdir.resolve())
        now = time.time()
        rows = [
            (wd, s.file_path, s.symbol, s.kind, s.line, s.parent, now)
            for s in symbols
        ]
        with self._connect() as conn:
            conn.execute("DELETE FROM symbols WHERE workdir = ?", (wd,))
            conn.executemany(
                "INSERT INTO symbols (workdir, file_path, symbol, kind, "
                "line, parent, ts) VALUES (?, ?, ?, ?, ?, ?, ?)",
                rows,
            )
        return len(rows)

    def all_symbols(self, workdir: Path) -> list[Symbol]:
        wd = str(workdir.resolve())
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT symbol, kind, file_path, line, parent "
                "FROM symbols WHERE workdir = ? ORDER BY symbol",
                (wd,),
            ).fetchall()
        return [
            Symbol(
                symbol=str(r[0]), kind=str(r[1]),
                file_path=str(r[2]), line=int(r[3]), parent=str(r[4]),
            )
            for r in rows
        ]

    def __len__(self) -> int:
        with self._connect() as conn:
            return int(conn.execute(
                "SELECT COUNT(*) FROM symbols"
            ).fetchone()[0])


def format_kg_block(symbols: Iterable[Symbol], *, max_symbols: int = 200) -> str:
    """Render top-N symbols as a prompt-ready truth block.

    Capped at ``max_symbols`` so the prompt doesn't grow unbounded on
    monorepos; the cap is per-file at the call site.
    """
    items = list(symbols)[:max_symbols]
    if not items:
        return ""
    lines = [
        "## Known symbols (treat as canonical, do not hallucinate)",
        "",
        "Any symbol you reference in a finding MUST appear below. If a",
        "symbol you want to flag is not listed, frame the finding around",
        "the actual line of code visible in the diff instead.",
        "",
    ]
    for s in items:
        loc = f"{s.file_path}:{s.line}"
        parent = f" (in `{s.parent}`)" if s.parent else ""
        lines.append(f"- `{s.symbol}` ({s.kind}) — `{loc}`{parent}")
    return "\n".join(lines) + "\n"


__all__ = [
    "KnowledgeGraphStore",
    "Symbol",
    "format_kg_block",
    "scan_workdir",
]
