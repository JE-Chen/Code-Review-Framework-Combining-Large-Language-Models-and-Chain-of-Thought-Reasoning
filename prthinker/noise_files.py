"""Flag low-attention changed files a reviewer can safely skim.

Not every changed file deserves the same scrutiny. A regenerated lock
file, a minified bundle, a committed snapshot, or a vendored dependency
is machine-produced — reading it line by line is wasted effort and
distracts from the hand-written changes that actually need review. This
module classifies the changed-file list into those low-attention
categories and renders a compact, self-omitting note so the reviewer
knows up front which files to skim rather than scrutinise.

It is purely advisory: it never drops a file from the review and never
gates the verdict — a poisoned lock file is still a real risk, so the
note says "skim", not "ignore".

Runner-safe: pure path inspection over the changed-file list.
"""

from __future__ import annotations

import posixpath

_NOISE_LIMIT = 12

_REASON_LOCKFILE = "lockfile"
_REASON_GENERATED = "minified/generated"
_REASON_VENDORED = "vendored"
_REASON_SNAPSHOT = "snapshot"

_LOCKFILES = frozenset(
    {
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "poetry.lock",
        "pipfile.lock",
        "cargo.lock",
        "composer.lock",
        "gemfile.lock",
        "go.sum",
    }
)
_GENERATED_SUFFIXES = (".min.js", ".min.css", ".map", ".lock")
_VENDOR_DIRS = frozenset({"vendor", "node_modules", "third_party", "dist"})
_SNAPSHOT_MARKERS = ("__snapshots__",)
_SNAPSHOT_SUFFIXES = (".snap",)


def _is_lockfile(base: str) -> bool:
    """True when the file's base name is a known dependency lock file."""
    return base in _LOCKFILES


def _is_generated(base: str) -> bool:
    """True for minified bundles / source maps / generic lock artifacts."""
    return base.endswith(_GENERATED_SUFFIXES)


def _is_vendored(parts: list[str]) -> bool:
    """True when any path segment is a known vendored-dependency dir."""
    return any(part in _VENDOR_DIRS for part in parts)


def _is_snapshot(base: str, parts: list[str]) -> bool:
    """True for committed test snapshots (``__snapshots__`` / ``*.snap``)."""
    return base.endswith(_SNAPSHOT_SUFFIXES) or any(
        marker in parts for marker in _SNAPSHOT_MARKERS
    )


def _classify(path: str) -> str | None:
    """Return the noise reason for one path, or None when it needs review."""
    base = posixpath.basename(path).lower()
    parts = [p.lower() for p in path.split("/") if p]
    if _is_lockfile(base):
        return _REASON_LOCKFILE
    if _is_snapshot(base, parts):
        return _REASON_SNAPSHOT
    if _is_vendored(parts):
        return _REASON_VENDORED
    if _is_generated(base):
        return _REASON_GENERATED
    return None


def noise_files(changed_paths: list[str]) -> list[tuple[str, str]]:
    """Return ``(path, reason)`` for low-attention files, sorted by path."""
    classified = [
        (path, reason)
        for path in changed_paths
        if (reason := _classify(path)) is not None
    ]
    return sorted(classified, key=lambda item: item[0])


def format_noise_note(noise: list[tuple[str, str]]) -> str:
    """Collapsible 'safe to skim' block, or ``""`` when there is nothing."""
    if not noise:
        return ""
    shown = noise[:_NOISE_LIMIT]
    lines = [
        f"<details><summary>🗂 {len(noise)} low-attention file(s) — "
        "safe to skim</summary>",
        "",
    ]
    lines += [f"- `{path}` — {reason}" for path, reason in shown]
    extra = len(noise) - len(shown)
    if extra > 0:
        lines.append(f"- … and {extra} more")
    lines += [
        "",
        "_Machine-generated or vendored — skim for surprises, but the "
        "verdict never hinges on these._",
        "",
        "</details>",
    ]
    return "\n".join(lines)


__all__ = ["format_noise_note", "noise_files"]
