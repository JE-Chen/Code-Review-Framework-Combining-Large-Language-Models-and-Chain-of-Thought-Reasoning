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

import logging
import re
from dataclasses import dataclass
from pathlib import PurePosixPath

from pydantic import ValidationError

from prthinker.diff import FileDiff
from prthinker.lenient_json import extract_json_array
from prthinker.schemas import DependencyUpgradeFinding

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


def _is_diff_header(line: str) -> bool:
    return line.startswith(("+++", "---", "@@"))


_PY_REQ_RE = re.compile(
    r"^([+-])\s*(?P<name>[A-Za-z0-9._-]+)\s*"
    r"(?:==|~=|>=|<=|>)\s*"
    r"(?P<ver>[0-9A-Za-z.\-]+)"
)


def _scan_python_requirements(file_diff: str) -> dict[str, dict[str, str]]:
    """Pair up '-' / '+' lines by package name."""
    pairs: dict[str, dict[str, str]] = {}
    for line in file_diff.splitlines():
        if _is_diff_header(line):
            continue
        m = _PY_REQ_RE.match(line)
        if m is None:
            continue
        slot_key = "new" if m.group(1) == "+" else "old"
        pairs.setdefault(m.group("name"), {})[slot_key] = m.group("ver")
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


_NPM_SPEC_RE = re.compile(r"^[\^~>=<0-9.]")


def _is_likely_dep_key(name: str, spec: str) -> bool:
    """Skip well-known metadata keys + non-semver-shaped values."""
    if name in _NPM_METADATA_KEYS:
        return False
    return bool(_NPM_SPEC_RE.match(spec))


def _scan_package_json(file_diff: str) -> dict[str, dict[str, str]]:
    pairs: dict[str, dict[str, str]] = {}
    for line in file_diff.splitlines():
        if _is_diff_header(line):
            continue
        m = _NPM_RE.match(line)
        if m is None:
            continue
        name = m.group("name")
        spec = m.group("spec")
        if not _is_likely_dep_key(name, spec):
            continue
        slot_key = "new" if m.group(1) == "+" else "old"
        pairs.setdefault(name, {})[slot_key] = spec
    return pairs


_PYPROJECT_DEP_RE = re.compile(
    r'^([+-])\s*"(?P<name>[A-Za-z0-9._-]+)\s*'
    r'(?:==|~=|>=|<=|>)\s*'
    r'(?P<ver>[0-9A-Za-z.\-]+)'
)


def _scan_pyproject(file_diff: str) -> dict[str, dict[str, str]]:
    pairs: dict[str, dict[str, str]] = {}
    for line in file_diff.splitlines():
        if _is_diff_header(line):
            continue
        m = _PYPROJECT_DEP_RE.match(line)
        if m is None:
            continue
        slot_key = "new" if m.group(1) == "+" else "old"
        pairs.setdefault(m.group("name"), {})[slot_key] = m.group("ver")
    return pairs


_PY_REQ_BASENAMES = frozenset({
    "requirements.txt",
    "requirements-dev.txt",
    "requirements_dev.txt",
    "constraints.txt",
})


def _dispatch_scanner(
    basename: str,
) -> tuple[str, callable] | None:
    """Map a lock-file basename to ``(ecosystem, scanner)`` or ``None``
    when the file is one we deliberately don't scan (e.g. auto-generated
    poetry.lock / Cargo.lock).
    """
    if basename in _PY_REQ_BASENAMES:
        return ("python", _scan_python_requirements)
    if basename == "pyproject.toml":
        return ("python", _scan_pyproject)
    if basename == "package.json":
        return ("node", _scan_package_json)
    return None


def _collect_upgrades(
    file_path: str,
    ecosystem: str,
    pairs: dict[str, dict[str, str]],
) -> list[PackageUpgrade]:
    """Turn the ``{name: {old, new}}`` map produced by a scanner into a
    list of :class:`PackageUpgrade`, dropping rows that didn't actually
    change.
    """
    out: list[PackageUpgrade] = []
    for pkg, versions in pairs.items():
        old = versions.get("old", "")
        new = versions.get("new", "")
        if not old or not new or old == new:
            continue
        out.append(PackageUpgrade(
            file_path=file_path,
            package=pkg,
            old_version=old,
            new_version=new,
            ecosystem=ecosystem,
        ))
    return out


def detect_upgrades(file_diffs: list[FileDiff]) -> list[PackageUpgrade]:
    """Find every package whose version line changed in the diff."""
    out: list[PackageUpgrade] = []
    for fd in file_diffs:
        if fd.is_binary or fd.is_deleted or not _is_lockfile(fd.path):
            continue
        dispatch = _dispatch_scanner(PurePosixPath(fd.path).name)
        if dispatch is None:
            continue
        ecosystem, scanner = dispatch
        out.extend(_collect_upgrades(fd.path, ecosystem, scanner(fd.raw)))
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


def _coerce_impact_entry(
    entry, upgrade: PackageUpgrade,
) -> DependencyUpgradeFinding | None:
    """Validate one raw entry; ``None`` if it must be dropped."""
    if not isinstance(entry, dict):
        return None
    payload = dict(entry)
    payload.setdefault("package", upgrade.package)
    payload.setdefault("old_version", upgrade.old_version)
    payload.setdefault("new_version", upgrade.new_version)
    payload.setdefault("ecosystem", upgrade.ecosystem)
    payload.setdefault("file_path", upgrade.file_path)
    try:
        return DependencyUpgradeFinding.model_validate(payload)
    except ValidationError as exc:
        log.debug("Dropped malformed dep-upgrade finding %r: %s", entry, exc)
        return None


def parse_impact(
    raw_output: str, *, upgrade: PackageUpgrade,
) -> list[DependencyUpgradeFinding]:
    """Parse the model's JSON-array reply into structured findings."""
    data = extract_json_array(raw_output, parser_name="dep_upgrade parser")
    if not data:
        return []
    out: list[DependencyUpgradeFinding] = []
    for entry in data:
        finding = _coerce_impact_entry(entry, upgrade)
        if finding is not None:
            out.append(finding)
    return out


__all__ = [
    "PROMPT_TEMPLATE",
    "PackageUpgrade",
    "build_prompt",
    "detect_upgrades",
    "parse_impact",
]
