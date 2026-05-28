"""Dependency-upgrade detector + impact-analysis prompt builder.

Detects when a PR's diff touches a lock-file (``requirements.txt`` /
``pyproject.toml`` / ``package.json`` / ``Cargo.toml`` / ``go.mod``)
and extracts per-package version deltas. Builds a prompt per
upgraded package asking the model whether breaking changes between
the two versions are likely to affect this codebase's usage, given
the package's actual call-sites in the rest of the diff.

Design:

* :func:`detect_upgrades` — pure-data scan over a unified diff,
  returns a list of :class:`PackageUpgrade`.
* :func:`build_prompt` — render the impact-analysis prompt for one
  upgrade. The prompt instructs the model to base its answer only on
  what it sees in the diff + its own knowledge of the package; the
  framework does NOT fetch remote changelogs at this level (CI-fragile
  + privacy-implicating; left to future work).
* :func:`parse_impact` — safe-failure JSON parser. Bad output yields
  an empty list.

Per ``paper_rule.md`` no-fabrication: this module reports what the
model says, not a calibrated "definitely affects you" verdict.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from pathlib import PurePosixPath

from pydantic import ValidationError

from reviewmind.diff import FileDiff
from reviewmind.schemas import DependencyUpgradeFinding

log = logging.getLogger(__name__)


_LOCK_FILES = {
    "requirements.txt",
    "requirements-dev.txt",
    "requirements_dev.txt",
    "constraints.txt",
    "pyproject.toml",
    "Pipfile",
    "poetry.lock",
    "uv.lock",
    "package.json",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "Cargo.toml",
    "Cargo.lock",
    "go.mod",
    "go.sum",
    "Gemfile",
    "Gemfile.lock",
    "composer.json",
    "composer.lock",
}


def _is_lockfile(path: str) -> bool:
    name = PurePosixPath(path).name
    return name in _LOCK_FILES


@dataclass(frozen=True)
class PackageUpgrade:
    """One package whose version changed in the diff."""

    file_path: str
    package: str
    old_version: str
    new_version: str
    ecosystem: str  # "python" | "node" | "rust" | "go" | "ruby" | "php" | "unknown"


# ---------------------------------------------------------------------------
# Per-ecosystem extractors. Each one takes the unified diff text for a
# single file and yields PackageUpgrade items.
# ---------------------------------------------------------------------------

_PY_REQ_RE = re.compile(
    r"^([+-])\s*(?P<name>[A-Za-z0-9._-]+)\s*"
    r"(?:==|~=|>=|<=|>)\s*"
    r"(?P<ver>[0-9A-Za-z.\-]+)"
)


def _scan_python_requirements(file_diff: str) -> dict[str, dict[str, str]]:
    """Pair up '-' / '+' lines by package name."""
    pairs: dict[str, dict[str, str]] = {}
    for line in file_diff.splitlines():
        if line.startswith("+++") or line.startswith("---") or line.startswith("@@"):
            continue
        m = _PY_REQ_RE.match(line)
        if m is None:
            continue
        sign = m.group(1)
        name = m.group("name")
        ver = m.group("ver")
        slot = pairs.setdefault(name, {})
        if sign == "+":
            slot["new"] = ver
        else:
            slot["old"] = ver
    return pairs


_NPM_RE = re.compile(
    r'^([+-])\s*"(?P<name>[^"]+)"\s*:\s*"(?P<spec>[^"]+)"'
)

# Known top-level package.json keys whose values look semver-ish but
# are not dependencies. Anything else is treated as a candidate dep.
_NPM_METADATA_KEYS = frozenset({
    "name", "version", "description", "main", "module", "type",
    "license", "homepage", "private", "engines",
    "author", "bin", "browser", "files", "scripts",
})


def _scan_package_json(file_diff: str) -> dict[str, dict[str, str]]:
    pairs: dict[str, dict[str, str]] = {}
    for line in file_diff.splitlines():
        if line.startswith("+++") or line.startswith("---") or line.startswith("@@"):
            continue
        m = _NPM_RE.match(line)
        if m is None:
            continue
        sign = m.group(1)
        name = m.group("name")
        spec = m.group("spec")
        if name in _NPM_METADATA_KEYS:
            continue
        # Demand a semver-ish spec to avoid script entries etc.
        if not re.match(r"^[\^~>=<0-9.]", spec):
            continue
        slot = pairs.setdefault(name, {})
        if sign == "+":
            slot["new"] = spec
        else:
            slot["old"] = spec
    return pairs


_PYPROJECT_DEP_RE = re.compile(
    r'^([+-])\s*"(?P<name>[A-Za-z0-9._-]+)\s*'
    r'(?:==|~=|>=|<=|>)\s*'
    r'(?P<ver>[0-9A-Za-z.\-]+)'
)


def _scan_pyproject(file_diff: str) -> dict[str, dict[str, str]]:
    pairs: dict[str, dict[str, str]] = {}
    for line in file_diff.splitlines():
        if line.startswith("+++") or line.startswith("---") or line.startswith("@@"):
            continue
        m = _PYPROJECT_DEP_RE.match(line)
        if m is None:
            continue
        sign = m.group(1)
        name = m.group("name")
        ver = m.group("ver")
        slot = pairs.setdefault(name, {})
        if sign == "+":
            slot["new"] = ver
        else:
            slot["old"] = ver
    return pairs


def detect_upgrades(file_diffs: list[FileDiff]) -> list[PackageUpgrade]:
    """Find every package whose version line changed in the diff."""
    out: list[PackageUpgrade] = []
    for fd in file_diffs:
        if fd.is_binary or fd.is_deleted or not _is_lockfile(fd.path):
            continue
        name = PurePosixPath(fd.path).name
        if name in {"requirements.txt", "requirements-dev.txt",
                    "requirements_dev.txt", "constraints.txt"}:
            ecosystem = "python"
            pairs = _scan_python_requirements(fd.raw)
        elif name == "pyproject.toml":
            ecosystem = "python"
            pairs = _scan_pyproject(fd.raw)
        elif name in {"package.json"}:
            ecosystem = "node"
            pairs = _scan_package_json(fd.raw)
        else:
            # Other lock files (poetry.lock, Cargo.lock, yarn.lock, …)
            # are deliberately skipped at this level — they are
            # auto-generated, noisy, and the human-curated file in the
            # same PR already names the package + version pair.
            continue

        for pkg, versions in pairs.items():
            old = versions.get("old", "")
            new = versions.get("new", "")
            if not old or not new or old == new:
                continue
            out.append(PackageUpgrade(
                file_path=fd.path,
                package=pkg,
                old_version=old,
                new_version=new,
                ecosystem=ecosystem,
            ))
    return out


# ---------------------------------------------------------------------------
# Prompt + parser
# ---------------------------------------------------------------------------

PROMPT_TEMPLATE = """\
# Dependency upgrade impact analysis

The PR upgrades ``{package}`` ({ecosystem}) from
``{old_version}`` to ``{new_version}``.

Based on (a) your knowledge of this package's release history and (b)
the call-sites of ``{package}`` visible in the rest of the diff below,
report any breaking changes between these versions that are likely to
affect this codebase.

You MUST output ONLY a JSON array, no surrounding prose, no markdown
fences. Each element must conform to:

  {{
    "severity": "info" | "warning" | "error",
    "summary":  "<one sentence: what change, what to do>",
    "evidence": "<short justification — release-note quote, doc
                  pointer, or 'no breaking change in this range'>"
  }}

Rules:

- If you don't know the package's release notes for these versions,
  emit one entry with severity ``info`` and summary "no known impact"
  rather than guessing.
- Do not invent call-sites that aren't in the diff.

## Diff (other than the lock file)
{usage_excerpt}
"""


def build_prompt(
    upgrade: PackageUpgrade,
    file_diffs: list[FileDiff],
    *,
    excerpt_chars: int = 6000,
) -> str:
    """Render the impact-analysis prompt for one upgrade.

    Excludes the lock file itself; the model already knows the version
    delta from ``old_version`` / ``new_version``.
    """
    parts: list[str] = []
    used = 0
    for fd in file_diffs:
        if fd.path == upgrade.file_path:
            continue
        if fd.is_binary or fd.is_deleted:
            continue
        section = f"### `{fd.path}`\n\n```diff\n{fd.raw.rstrip()}\n```\n"
        if used + len(section) > excerpt_chars:
            parts.append("\n*(diff truncated to fit prompt)*")
            break
        parts.append(section)
        used += len(section)

    return PROMPT_TEMPLATE.format(
        package=upgrade.package,
        ecosystem=upgrade.ecosystem,
        old_version=upgrade.old_version,
        new_version=upgrade.new_version,
        usage_excerpt="\n".join(parts) or "(no other diff content)",
    )


_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)
_ARRAY_RE = re.compile(r"\[[\s\S]*\]")


def parse_impact(
    raw_output: str, *, upgrade: PackageUpgrade,
) -> list[DependencyUpgradeFinding]:
    """Parse the model's JSON-array reply into structured findings."""
    body = raw_output.strip()
    fence = _FENCE_RE.search(body)
    if fence:
        body = fence.group(1).strip()
    if not body or body == "[]":
        return []
    match = _ARRAY_RE.search(body)
    if match is None:
        log.warning("dep_upgrade parser: no JSON array found")
        return []
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        log.warning("dep_upgrade parser: JSON decode failed (%s)", exc)
        return []
    if not isinstance(data, list):
        return []
    out: list[DependencyUpgradeFinding] = []
    for entry in data:
        if not isinstance(entry, dict):
            continue
        payload = dict(entry)
        payload.setdefault("package", upgrade.package)
        payload.setdefault("old_version", upgrade.old_version)
        payload.setdefault("new_version", upgrade.new_version)
        payload.setdefault("ecosystem", upgrade.ecosystem)
        payload.setdefault("file_path", upgrade.file_path)
        try:
            out.append(DependencyUpgradeFinding.model_validate(payload))
        except ValidationError as exc:
            log.debug("Dropped malformed dep-upgrade finding %r: %s", entry, exc)
    return out


__all__ = [
    "PROMPT_TEMPLATE",
    "PackageUpgrade",
    "build_prompt",
    "detect_upgrades",
    "parse_impact",
]
