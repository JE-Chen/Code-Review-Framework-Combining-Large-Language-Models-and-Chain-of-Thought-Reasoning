"""Suppress phantom "undefined name / missing import" findings.

A diff-only reviewer sees only the changed lines plus a few lines of
context, so a symbol imported at the top of a file (outside the hunk
window) looks undefined and the model reports a non-existent
``NameError``. This guard re-grounds that one finding class against the
file's own source — reconstructed from the diff, including the text git
places after the second ``@@`` on a hunk header (the section line, which
for a top-of-file edit is the very import the model missed) — and drops a
finding only when the named symbol is provably bound. The direction is
safe: when the binding cannot be proven, the finding is kept, so a real
missing import is never hidden.

Runner-safe: depends only on the standard library and the pydantic
schemas.
"""

from __future__ import annotations

import ast
import builtins
import keyword
import logging
import re
from typing import Sequence

from prthinker.schemas import InlineFinding

log = logging.getLogger(__name__)

_PY_SUFFIXES = (".py", ".pyi")
_BUILTIN_NAMES = frozenset(dir(builtins))

# The finding must read like an "undefined symbol" claim before we act.
_UNDEFINED_CLAIM_RE = re.compile(
    r"not\s+imported|not\s+defined|undefined|name\s*error|"
    r"missing\s+import|unresolved",
    re.IGNORECASE,
)

# Capture the *specific* symbol the finding says is missing. Ordered most
# specific first; the first match wins so we never act on a loose guess.
_SUBJECT_RES = (
    re.compile(r"\bname\s+['\"`]?(\w+)['\"`]?\s+is\s+not\s+defined", re.IGNORECASE),
    re.compile(r"\bundefined\s+name\s+['\"`]?(\w+)", re.IGNORECASE),
    re.compile(r"\bmissing\s+import\s+(?:for\s+)?['\"`]?(\w+)", re.IGNORECASE),
    re.compile(
        r"['\"`]?(\w+)['\"`]?\s+is\s+(?:being\s+)?used\b[^.]*?\bnot\s+imported",
        re.IGNORECASE,
    ),
    re.compile(
        r"['\"`]?(\w+)['\"`]?\s+is\s+(?:not\s+(?:imported|defined)|undefined)",
        re.IGNORECASE,
    ),
)

_HUNK_RE = re.compile(r"^@@\s+-\d+(?:,\d+)?\s+\+\d+(?:,\d+)?\s+@@\s?(.*)$")
_IMPORT_RE = re.compile(r"^\s*import\s+(.+)$")
_FROM_IMPORT_RE = re.compile(r"^\s*from\s+\S+\s+import\s+(.+)$")
_DEF_RE = re.compile(r"^\s*(?:async\s+)?def\s+(\w+)")
_CLASS_RE = re.compile(r"^\s*class\s+(\w+)")
_ASSIGN_RE = re.compile(r"^\s*(\w+)\s*(?::[^=]+)?=(?!=)")
_FOR_RE = re.compile(r"^\s*for\s+(\w+)\s+in\b")
_AS_RE = re.compile(r"\bas\s+(\w+)")


def _is_bindable_name(token: str) -> bool:
    """Return whether ``token`` can name a binding.

    ``str.isidentifier`` alone accepts Python keywords (``class``,
    ``for``), which can never be a bound symbol; excluding them stops a
    keyword from being mistaken for a defined name.
    """
    return token.isidentifier() and not keyword.iskeyword(token)


def _hunk_heading(line: str) -> str:
    """Return the section text after the second ``@@`` of a hunk header."""
    match = _HUNK_RE.match(line)
    return match.group(1).strip() if match else ""


def reconstruct_source_from_diff(diff_text: str) -> str:
    """Rebuild best-effort new-side source from a unified diff.

    Includes added lines, context lines, and each hunk header's section
    text — exactly the out-of-window context a diff-only reviewer misses.
    """
    out: list[str] = []
    for line in diff_text.splitlines():
        if line.startswith("@@"):
            heading = _hunk_heading(line)
            if heading:
                out.append(heading)
        elif line.startswith("+") and not line.startswith("+++"):
            out.append(line[1:])
        elif line.startswith(" "):
            out.append(line[1:])
    return "\n".join(out)


def _import_alias_names(aliases: list[ast.alias]) -> set[str]:
    """Return the names an ``import`` / ``from ... import`` binds."""
    out: set[str] = set()
    for alias in aliases:
        out.add(alias.asname or alias.name.split(".", 1)[0])
    return out


def _names_from_node(node: ast.AST) -> set[str]:
    """Return the names a single AST node binds (empty for non-binders)."""
    if isinstance(node, (ast.Import, ast.ImportFrom)):
        return _import_alias_names(node.names)
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return {node.name}
    if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
        return {node.id}
    if isinstance(node, ast.arg):
        return {node.arg}
    return set()


def _ast_bound_names(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        names |= _names_from_node(node)
    return names


def _bound_name_of_import_token(token: str, *, dotted_head: bool) -> str | None:
    """Return the name a single import clause token binds, or ``None``."""
    token = token.strip()
    if not token:
        return None
    if " as " in token:
        return token.split(" as ", 1)[1].strip() or None
    return token.split(".", 1)[0] if dotted_head else token


def _split_import_clause(clause: str, *, dotted_head: bool) -> set[str]:
    cleaned = clause.strip().strip("()").replace("\\", " ")
    out: set[str] = set()
    for part in cleaned.split(","):
        name = _bound_name_of_import_token(part, dotted_head=dotted_head)
        if name is not None and _is_bindable_name(name):
            out.add(name)
    return out


def _import_names_in_line(line: str) -> set[str]:
    match = _FROM_IMPORT_RE.match(line)
    if match:
        return _split_import_clause(match.group(1), dotted_head=False)
    match = _IMPORT_RE.match(line)
    if match:
        return _split_import_clause(match.group(1), dotted_head=True)
    return set()


def _bound_names_in_line(line: str) -> set[str]:
    names = _import_names_in_line(line)
    for pattern in (_DEF_RE, _CLASS_RE, _ASSIGN_RE, _FOR_RE):
        match = pattern.match(line)
        if match:
            names.add(match.group(1))
    names.update(_AS_RE.findall(line))
    return {name for name in names if _is_bindable_name(name)}


def _regex_bound_names(source: str) -> set[str]:
    names: set[str] = set()
    for line in source.splitlines():
        names |= _bound_names_in_line(line)
    return names


def collect_bound_names(source: str) -> set[str]:
    """Return every name bound anywhere in ``source`` (plus builtins).

    Parses with :mod:`ast` when the source is syntactically valid and
    falls back to a line-based regex scan when it is not — the
    diff-reconstructed source is often a partial, unparseable fragment.
    """
    names = set(_BUILTIN_NAMES)
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return names | _regex_bound_names(source)
    return names | _ast_bound_names(tree)


def claimed_missing_name(comment: str) -> str | None:
    """Return the symbol a finding claims is undefined, or ``None``.

    Yields a name only when the comment reads like an "undefined symbol /
    missing import" claim *and* names a specific identifier; otherwise
    ``None``, so the finding is left untouched.
    """
    if not _UNDEFINED_CLAIM_RE.search(comment):
        return None
    for pattern in _SUBJECT_RES:
        match = pattern.search(comment)
        if match and _is_bindable_name(match.group(1)):
            return match.group(1)
    return None


def suppress_phantom_undefined(
    findings: Sequence[InlineFinding],
    *,
    diff_text: str,
    path: str,
) -> list[InlineFinding]:
    """Drop findings that wrongly claim a bound symbol is undefined.

    Only Python files are inspected. A finding is dropped solely when the
    symbol it names is provably bound in the file's reconstructed source —
    the safe direction, so a genuinely missing import is never hidden.
    """
    if not path.endswith(_PY_SUFFIXES):
        return list(findings)
    claims = [(finding, claimed_missing_name(finding.comment)) for finding in findings]
    if not any(name for _, name in claims):
        return list(findings)
    bound = collect_bound_names(reconstruct_source_from_diff(diff_text))
    kept: list[InlineFinding] = []
    for finding, name in claims:
        if name is not None and name in bound:
            log.debug(
                "Dropping phantom undefined-name finding on %s:%d for %r",
                path, finding.line, name,
            )
            continue
        kept.append(finding)
    return kept


__all__ = [
    "claimed_missing_name",
    "collect_bound_names",
    "reconstruct_source_from_diff",
    "suppress_phantom_undefined",
]
