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

CREATE TABLE IF NOT EXISTS imports (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    workdir     TEXT    NOT NULL,
    from_file   TEXT    NOT NULL,
    target      TEXT    NOT NULL,
    kind        TEXT    NOT NULL,
    ts          REAL    NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_imports_from
    ON imports (workdir, from_file);
"""


@dataclass(frozen=True)
class Symbol:
    """One canonical symbol exported by the repo."""

    symbol: str
    kind: str  # "function" / "class" / "method" / "ts_export" / "const"
    file_path: str
    line: int
    parent: str = ""  # enclosing class for methods, else ""


@dataclass(frozen=True)
class Import:
    """One file→target relationship parsed from the source.

    ``target`` is a raw module / path string as it appeared in the
    source. The resolver in :mod:`prthinker.kg_visualize` maps it back
    to a known file node when possible so the KG graph becomes
    connected across files; external / unresolvable targets are
    dropped from the visualization (no orphan boxes).
    """

    from_file: str
    target: str
    kind: str  # "py_absolute" / "py_relative" / "tsjs"


# ---------------------------------------------------------------------------
# Python AST scanner
# ---------------------------------------------------------------------------


def _extract_python_imports(tree: ast.AST, rel: str) -> list[Import]:
    """Collect every Import / ImportFrom row from a parsed Python tree.

    Relative imports keep their leading dots in ``target`` so the
    resolver can walk up from ``rel``'s directory.
    """
    imports: list[Import] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name:
                    imports.append(Import(
                        from_file=rel, target=alias.name,
                        kind="py_absolute",
                    ))
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if node.level > 0:
                imports.append(Import(
                    from_file=rel,
                    target=("." * node.level) + module,
                    kind="py_relative",
                ))
            elif module:
                imports.append(Import(
                    from_file=rel, target=module,
                    kind="py_absolute",
                ))
    return imports


def _class_member_symbols(cls: ast.ClassDef, rel: str) -> list[Symbol]:
    """Methods defined directly inside a class body."""
    out: list[Symbol] = []
    for inner in cls.body:
        if isinstance(inner, ast.FunctionDef | ast.AsyncFunctionDef):
            out.append(Symbol(
                symbol=inner.name, kind="method",
                file_path=rel, line=inner.lineno,
                parent=cls.name,
            ))
    return out


def _const_targets_in(assign: ast.Assign) -> list[str]:
    """ALL_CAPS top-level assignment targets, heuristic for constants."""
    names: list[str] = []
    for target in assign.targets:
        if (
            isinstance(target, ast.Name)
            and target.id.isupper()
            and target.id.replace("_", "").isalnum()
        ):
            names.append(target.id)
    return names


def _extract_python_symbols(tree: ast.Module, rel: str) -> list[Symbol]:
    """Top-level functions / classes (+ methods) / ALL_CAPS constants."""
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
            out.extend(_class_member_symbols(node, rel))
        elif isinstance(node, ast.Assign):
            for name in _const_targets_in(node):
                out.append(Symbol(
                    symbol=name, kind="const",
                    file_path=rel, line=node.lineno,
                ))
    return out


def _scan_python(
    file_path: Path, rel: str
) -> tuple[list[Symbol], list[Import]]:
    """Walk a Python file's AST and yield top-level + class-method symbols
    plus the file's import edges.

    Private names (``_x``) are kept — they're still canonical and the
    reviewer should still treat them as real. We skip generated /
    obviously-broken files via try/except around the parse.

    Imports are emitted as :class:`Import` rows so the visualization
    layer can resolve them back to file nodes and turn what used to
    be a forest of disconnected per-file stars into a connected graph.
    """
    try:
        tree = ast.parse(file_path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, SyntaxError):
        return [], []
    return _extract_python_symbols(tree, rel), _extract_python_imports(tree, rel)


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

_TS_IMPORT_PATTERNS: tuple[re.Pattern[str], ...] = (
    # `import X from "..."` / `import { x } from "..."`
    re.compile(r"""^\s*import\s+[^'"]+from\s+['"]([^'"]+)['"]""", re.MULTILINE),
    # `import "..."` (side-effect imports)
    re.compile(r"""^\s*import\s+['"]([^'"]+)['"]""", re.MULTILINE),
    # `export { x } from "..."` (re-exports)
    re.compile(r"""^\s*export\s+[^'"]+from\s+['"]([^'"]+)['"]""", re.MULTILINE),
)


def _scan_jsts(
    file_path: Path, rel: str
) -> tuple[list[Symbol], list[Import]]:
    try:
        body = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [], []
    out: list[Symbol] = []
    for kind, pat in _TS_PATTERNS:
        for m in pat.finditer(body):
            out.append(Symbol(
                symbol=m.group(1), kind=kind, file_path=rel,
                line=body.count("\n", 0, m.start()) + 1,
            ))
    imports: list[Import] = []
    seen: set[str] = set()
    for pat in _TS_IMPORT_PATTERNS:
        for m in pat.finditer(body):
            target = m.group(1)
            if target in seen:
                continue
            seen.add(target)
            imports.append(Import(
                from_file=rel, target=target, kind="tsjs",
            ))
    return out, imports


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
    """Walk ``workdir`` and extract every Symbol in supported languages.

    Back-compat shim that ignores import edges. New callers should
    prefer :func:`scan_workdir_full`, which also returns import edges
    so the visualization can render a connected cross-file graph.
    """
    syms, _ = scan_workdir_full(workdir)
    return syms


def scan_workdir_full(
    workdir: Path,
) -> tuple[list[Symbol], list[Import]]:
    """Walk ``workdir`` and extract every Symbol and Import edge.

    Imports are how the visualization wires per-file stars into a
    single connected graph. The resolver in :mod:`kg_visualize`
    handles the module-string → file-path mapping; this scanner just
    captures what the source actually wrote.
    """
    syms: list[Symbol] = []
    imps: list[Import] = []
    for file in workdir.rglob("*"):
        if not file.is_file():
            continue
        if any(part in _IGNORED_DIRS for part in file.parts):
            continue
        scanner = _LANG_DISPATCH.get(file.suffix.lower())
        if scanner is None:
            continue
        rel = file.relative_to(workdir).as_posix()
        file_syms, file_imps = scanner(file, rel)
        syms.extend(file_syms)
        imps.extend(file_imps)
    return syms, imps


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

    def rebuild(
        self,
        workdir: Path,
        symbols: Iterable[Symbol],
        imports: Iterable[Import] | None = None,
    ) -> int:
        """Drop every symbol + import for ``workdir`` and re-insert.

        Wholesale-rebuild semantics so the store always reflects HEAD;
        partial updates are deferred to future work. ``imports`` is
        optional to keep older callers (that pass symbols only)
        working — the visualization will fall back to file-stars-only
        when no imports are stored.
        """
        wd = str(workdir.resolve())
        now = time.time()
        sym_rows = [
            (wd, s.file_path, s.symbol, s.kind, s.line, s.parent, now)
            for s in symbols
        ]
        imp_rows = [
            (wd, i.from_file, i.target, i.kind, now)
            for i in (imports or ())
        ]
        with self._connect() as conn:
            conn.execute("DELETE FROM symbols WHERE workdir = ?", (wd,))
            conn.execute("DELETE FROM imports WHERE workdir = ?", (wd,))
            conn.executemany(
                "INSERT INTO symbols (workdir, file_path, symbol, kind, "
                "line, parent, ts) VALUES (?, ?, ?, ?, ?, ?, ?)",
                sym_rows,
            )
            if imp_rows:
                conn.executemany(
                    "INSERT INTO imports (workdir, from_file, target, "
                    "kind, ts) VALUES (?, ?, ?, ?, ?)",
                    imp_rows,
                )
        return len(sym_rows)

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

    def all_imports(self, workdir: Path) -> list[Import]:
        wd = str(workdir.resolve())
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT from_file, target, kind "
                "FROM imports WHERE workdir = ? ORDER BY from_file, target",
                (wd,),
            ).fetchall()
        return [
            Import(from_file=str(r[0]), target=str(r[1]), kind=str(r[2]))
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
    "Import",
    "KnowledgeGraphStore",
    "Symbol",
    "format_kg_block",
    "scan_workdir",
    "scan_workdir_full",
]
