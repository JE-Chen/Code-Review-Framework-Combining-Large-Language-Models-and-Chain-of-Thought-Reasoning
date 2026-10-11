"""Optional Tree-sitter context extraction with a dependency-free fallback."""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

LANGUAGE_BY_SUFFIX = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".java": "java",
    ".go": "go",
    ".rs": "rust",
    ".c": "c",
    ".h": "c",
    ".cc": "cpp",
    ".cpp": "cpp",
    ".cs": "c_sharp",
    ".kt": "kotlin",
    ".rb": "ruby",
    ".php": "php",
}


@dataclass(frozen=True)
class ContextNode:
    path: str
    kind: str
    name: str
    start_line: int
    end_line: int
    parent: str = ""


def _node_name(node, source: bytes) -> str:
    """C-family declarators nest identifiers; declarations may lack a name field."""
    named = node.child_by_field_name("name")
    if named is not None:
        return source[named.start_byte:named.end_byte].decode("utf-8", "replace")
    declarator = node.child_by_field_name("declarator")
    candidates = list(declarator.children if declarator is not None else node.children)
    while candidates:
        child = candidates.pop(0)
        if child.type in ("identifier", "type_identifier", "field_identifier", "simple_identifier"):
            return source[child.start_byte:child.end_byte].decode("utf-8", "replace")
        if "declarator" in child.type:
            candidates[0:0] = child.children
    return ""


def parse_tree_sitter(path: Path, language: str) -> list[ContextNode]:
    try:
        from tree_sitter_language_pack import get_parser
    except ImportError as exc:
        raise RuntimeError(
            "install prthinker[tree-sitter] for multi-language AST context"
        ) from exc
    source = path.read_bytes()
    parser_language = "csharp" if language == "c_sharp" else language
    tree = get_parser(parser_language).parse(source)
    out = []
    wanted = {
        "function_definition",
        "class_definition",
        "method_definition",
        "function_declaration",
        "class_declaration",
        "method_declaration",
        "function_item",
        "struct_item",
        "enum_item",
        "trait_item",
        "interface_declaration",
        "type_spec",
        "module",
    }
    stack = [tree.root_node]
    while stack:
        node = stack.pop()
        stack.extend(reversed(node.children))
        if node.type not in wanted:
            continue
        name = _node_name(node, source)
        out.append(
            ContextNode(
                path.as_posix(),
                node.type,
                name,
                node.start_point[0] + 1,
                node.end_point[0] + 1,
            )
        )
    return out


def impact_slice(changed: Iterable[str], edges: Iterable[tuple[str, str]]) -> set[str]:
    impacted = set(changed)
    reverse = {}
    for source, target in edges:
        reverse.setdefault(target, set()).add(source)
    queue = list(impacted)
    while queue:
        for item in reverse.get(queue.pop(), ()):
            if item not in impacted:
                impacted.add(item)
                queue.append(item)
    return impacted


_IGNORED_DIRS = {".git", ".venv", "venv", "node_modules", "dist", "build", "vendor",
                 "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "_build"}


def _language_for_scan(path: Path, max_file_bytes: int) -> str | None:
    """Return the Tree-sitter language for a scannable file, else None."""
    if not path.is_file():
        return None
    if any(part in _IGNORED_DIRS for part in path.parts):
        return None
    language = LANGUAGE_BY_SUFFIX.get(path.suffix.lower())
    if language is None:
        return None
    if path.stat().st_size > max_file_bytes:
        return None
    return language


def _scan_one_file(
    path: Path, workdir: Path, language: str
) -> list[ContextNode]:
    """Parse one file into workdir-relative context nodes, [] on failure."""
    try:
        parsed = parse_tree_sitter(path, language)
    except (OSError, RuntimeError, ValueError, LookupError):
        return []
    relative = path.relative_to(workdir).as_posix()
    return [
        ContextNode(relative, n.kind, n.name, n.start_line, n.end_line, n.parent)
        for n in parsed
    ]


def scan_workdir(
    workdir: Path, *, max_file_bytes: int = 1_000_000
) -> list[ContextNode]:
    """Scan supported source languages, skipping generated/private trees."""
    nodes: list[ContextNode] = []
    for path in workdir.rglob("*"):
        language = _language_for_scan(path, max_file_bytes)
        if language is None:
            continue
        nodes.extend(_scan_one_file(path, workdir, language))
    return nodes


_C_INCLUDE_RE = re.compile(r'^\s*#include\s+["<]([^">]+)', re.MULTILINE)
_IMPORT_PATTERNS = {
    ".java": re.compile(r"^\s*import\s+(?:static\s+)?([\w.]+)", re.MULTILINE),
    ".kt": re.compile(r"^\s*import\s+([\w.]+)", re.MULTILINE),
    ".go": re.compile(r'^\s*(?:import\s+)?["`]([^"`]+)["`]', re.MULTILINE),
    ".rs": re.compile(r"^\s*use\s+([\w:]+)", re.MULTILINE),
    ".c": _C_INCLUDE_RE,
    ".h": _C_INCLUDE_RE,
    ".cpp": _C_INCLUDE_RE,
    ".cs": re.compile(r"^\s*using\s+([\w.]+)", re.MULTILINE),
}


def scan_import_edges(workdir: Path) -> list[tuple[str, str]]:
    """Extract conservative cross-file import/include targets for polyglot KG."""
    edges: list[tuple[str, str]] = []
    for path in workdir.rglob("*"):
        pattern = _IMPORT_PATTERNS.get(path.suffix.lower())
        if pattern is None or _language_for_scan(path, 1_000_000) is None:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        rel = path.relative_to(workdir).as_posix()
        edges.extend((rel, target) for target in pattern.findall(text))
    return edges
