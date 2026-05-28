"""Dependency-upgrade detector + impact-parser tests."""

from __future__ import annotations

import json

from prthinker.dep_upgrade import (
    PackageUpgrade,
    build_prompt,
    detect_upgrades,
    parse_impact,
)
from prthinker.diff import FileDiff


def _fd(path: str, raw: str) -> FileDiff:
    return FileDiff(path=path, raw=raw)


# ----- requirements.txt -------------------------------------------------

_REQ_DIFF = """\
diff --git a/requirements.txt b/requirements.txt
--- a/requirements.txt
+++ b/requirements.txt
@@ -1,3 +1,3 @@
-requests==2.28.1
+requests==2.32.0
 pydantic==2.0
-numpy==1.24.0
+numpy==1.26.4
"""


def test_detect_python_requirements_upgrades() -> None:
    upgrades = detect_upgrades([_fd("requirements.txt", _REQ_DIFF)])
    by_pkg = {u.package: u for u in upgrades}
    assert "requests" in by_pkg
    assert by_pkg["requests"].old_version == "2.28.1"
    assert by_pkg["requests"].new_version == "2.32.0"
    assert by_pkg["requests"].ecosystem == "python"
    assert "numpy" in by_pkg
    assert "pydantic" not in by_pkg  # unchanged


def test_detect_in_dev_requirements_too() -> None:
    upgrades = detect_upgrades([_fd("requirements-dev.txt", _REQ_DIFF)])
    assert {u.package for u in upgrades} == {"requests", "numpy"}


# ----- pyproject.toml ---------------------------------------------------

_PYPROJECT_DIFF = """\
diff --git a/pyproject.toml b/pyproject.toml
--- a/pyproject.toml
+++ b/pyproject.toml
@@
 dependencies = [
-    "httpx==0.25.0",
+    "httpx==0.27.0",
     "pydantic==2.0",
 ]
"""


def test_detect_pyproject_upgrades() -> None:
    upgrades = detect_upgrades([_fd("pyproject.toml", _PYPROJECT_DIFF)])
    assert len(upgrades) == 1
    assert upgrades[0].package == "httpx"
    assert upgrades[0].old_version == "0.25.0"
    assert upgrades[0].new_version == "0.27.0"


# ----- package.json -----------------------------------------------------

_NPM_DIFF = """\
diff --git a/package.json b/package.json
--- a/package.json
+++ b/package.json
@@
   "dependencies": {
-    "react": "^18.2.0",
+    "react": "^18.3.1",
     "lodash": "^4.17.21"
   }
"""


def test_detect_package_json_upgrades() -> None:
    upgrades = detect_upgrades([_fd("package.json", _NPM_DIFF)])
    by_pkg = {u.package: u for u in upgrades}
    assert by_pkg["react"].old_version == "^18.2.0"
    assert by_pkg["react"].new_version == "^18.3.1"
    assert by_pkg["react"].ecosystem == "node"
    assert "lodash" not in by_pkg


def test_package_json_skips_metadata_keys() -> None:
    raw = """\
diff --git a/package.json b/package.json
--- a/package.json
+++ b/package.json
@@
-  "name": "old-name",
+  "name": "new-name",
-  "version": "1.0.0",
+  "version": "1.1.0",
"""
    # "name" / "version" don't have semver-shaped specs → not picked up.
    upgrades = detect_upgrades([_fd("package.json", raw)])
    assert upgrades == []


# ----- non-lockfile / no-op cases ---------------------------------------

def test_random_file_skipped() -> None:
    raw = "diff --git a/src/foo.py b/src/foo.py\n+x = 1\n"
    assert detect_upgrades([_fd("src/foo.py", raw)]) == []


def test_unchanged_version_not_reported() -> None:
    raw = """\
diff --git a/requirements.txt b/requirements.txt
--- a/requirements.txt
+++ b/requirements.txt
@@
 requests==2.28.0
"""
    assert detect_upgrades([_fd("requirements.txt", raw)]) == []


# ----- prompt builder ---------------------------------------------------

def test_build_prompt_excludes_the_lock_file_itself() -> None:
    up = PackageUpgrade(
        file_path="requirements.txt",
        package="requests", old_version="2.28.0", new_version="2.32.0",
        ecosystem="python",
    )
    diffs = [
        _fd("requirements.txt", "UNIQUE_LOCK_FILE_MARKER"),
        _fd("src/api.py", "diff --git a/src/api.py b/src/api.py\n+requests.get(...)\n"),
    ]
    prompt = build_prompt(up, diffs)
    assert "requests" in prompt
    assert "2.28.0" in prompt
    assert "2.32.0" in prompt
    assert "src/api.py" in prompt
    # The lock file's own diff text should not be in the prompt body —
    # the impact prompt asks about call-sites elsewhere, not the bump
    # line we already know about.
    assert "UNIQUE_LOCK_FILE_MARKER" not in prompt


# ----- parser -----------------------------------------------------------

def _upgrade() -> PackageUpgrade:
    return PackageUpgrade(
        file_path="requirements.txt",
        package="requests", old_version="2.28.0", new_version="2.32.0",
        ecosystem="python",
    )


def test_parser_round_trip() -> None:
    raw = json.dumps([{
        "severity": "warning",
        "summary":  "stream API changed",
        "evidence": "release-notes link",
    }])
    out = parse_impact(raw, upgrade=_upgrade())
    assert len(out) == 1
    assert out[0].package == "requests"
    assert out[0].severity == "warning"
    assert out[0].summary == "stream API changed"


def test_parser_drops_malformed_entries() -> None:
    raw = json.dumps([
        "not a dict",
        {},  # missing required summary
        {"severity": "info", "summary": "no known impact"},
    ])
    out = parse_impact(raw, upgrade=_upgrade())
    assert len(out) == 1
    assert out[0].summary == "no known impact"


def test_parser_returns_empty_on_garbage() -> None:
    assert parse_impact("not json", upgrade=_upgrade()) == []
    assert parse_impact("[]", upgrade=_upgrade()) == []


def test_parser_inside_fenced_block() -> None:
    raw = (
        "Sure, here is the analysis:\n```json\n"
        + json.dumps([{"severity": "info", "summary": "no breaking changes"}])
        + "\n```"
    )
    out = parse_impact(raw, upgrade=_upgrade())
    assert len(out) == 1


def test_PackageUpgrade_is_frozen() -> None:
    up = _upgrade()
    try:
        up.package = "x"  # type: ignore[misc]
    except Exception:
        return
    raise AssertionError("PackageUpgrade should be frozen")
