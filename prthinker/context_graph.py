"""Optional Tree-sitter context extraction with a dependency-free fallback."""

from __future__ import annotations
from dataclasses import dataclass
import re
from pathlib import Path
from typing import Iterable

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


def parse_tree_sitter(path: Path, language: str) -> list[ContextNode]:
    try:
        from tree_sitter_language_pack import get_parser
    except ImportError as exc:
        raise RuntimeError(
            "install prthinker[tree-sitter] for multi-language AST context"
        ) from exc
    source = path.read_bytes()
    tree = get_parser(language).parse(source)
    out = []
    wanted = {
        "function_definition",
        "class_definition",
        "method_definition",
        "function_declaration",
        "class_declaration",
        "method_declaration",
    }
    stack = [tree.root_node]
    while stack:
        node = stack.pop()
        stack.extend(reversed(node.children))
        if node.type not in wanted:
            continue
        name_node = node.child_by_field_name("name")
        name = (
            source[name_node.start_byte : name_node.end_byte].decode("utf-8", "replace")
            if name_node
            else ""
        )
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


def scan_workdir(
    workdir: Path, *, max_file_bytes: int = 1_000_000
) -> list[ContextNode]:
    """Scan supported source languages, skipping generated/private trees."""
    nodes: list[ContextNode] = []
    ignored = {".git", ".venv", "node_modules", "dist", "build", "vendor"}
    for path in workdir.rglob("*"):
        if not path.is_file() or any(part in ignored for part in path.parts):
            continue
        language = LANGUAGE_BY_SUFFIX.get(path.suffix.lower())
        if language is None or path.stat().st_size > max_file_bytes:
            continue
        try:
            parsed = parse_tree_sitter(path, language)
        except (OSError, RuntimeError, ValueError):
            continue
        relative = path.relative_to(workdir).as_posix()
        nodes.extend(
            ContextNode(relative, n.kind, n.name, n.start_line, n.end_line)
            for n in parsed
        )
    return nodes


def scan_import_edges(workdir: Path) -> list[tuple[str, str]]:
    """Extract conservative cross-file import/include targets for polyglot KG."""
    patterns = {
        ".java": re.compile(r"^\s*import\s+(?:static\s+)?([\w.]+)", re.M),
        ".kt": re.compile(r"^\s*import\s+([\w.]+)", re.M),
        ".go": re.compile(r'^\s*(?:import\s+)?["`]([^"`]+)["`]', re.M),
        ".rs": re.compile(r"^\s*use\s+([\w:]+)", re.M),
        ".c": re.compile(r'^\s*#include\s+["<]([^">]+)', re.M),
        ".h": re.compile(r'^\s*#include\s+["<]([^">]+)', re.M),
        ".cpp": re.compile(r'^\s*#include\s+["<]([^">]+)', re.M),
        ".cs": re.compile(r"^\s*using\s+([\w.]+)", re.M),
    }
    edges: list[tuple[str, str]] = []
    for path in workdir.rglob("*"):
        pattern = patterns.get(path.suffix.lower())
        if pattern is None or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        rel = path.relative_to(workdir).as_posix()
        edges.extend((rel, target) for target in pattern.findall(text))
    return edges
