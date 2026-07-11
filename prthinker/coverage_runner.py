"""Collect a per-test coverage matrix by running tests as subprocesses.

For a handful of failing + passing tests (never a whole suite — the cap
is :data:`MAX_TESTS_PER_RUN`), each test id is executed under
``python -m coverage run -m pytest <id>`` in its own temp data file,
exported with ``coverage json``, and parsed into the
:class:`~prthinker.fault_localization.CoverageMatrix` that SBFL scores.

Fail-open by design: a missing coverage tool, a timeout, or a nonzero
exit with no coverage data skips that test with a warning — collection
never raises into the caller, it just yields a smaller matrix.

Runner-safe: the coverage tool is invoked as a subprocess (arg lists,
``shell=False``); this module never imports ``coverage``.
"""

from __future__ import annotations

import json
import logging
import subprocess  # noqa: S404 — coverage/pytest run via arg lists, never shell=True
import sys
import tempfile
from pathlib import Path
from typing import Sequence

from prthinker.fault_localization import CoverageMatrix, LineKey

log = logging.getLogger(__name__)

# SBFL needs only a few failing + passing tests; running more burns
# minutes for marginal signal, so the id list is hard-capped.
MAX_TESTS_PER_RUN = 8
DEFAULT_TEST_TIMEOUT = 120.0
DEFAULT_TEST_CMD: tuple[str, ...] = ("pytest", "-x", "-q")
_JSON_EXPORT_TIMEOUT = 60.0
_COVERAGE_MODULE = "coverage"


def _is_test_file(rel: str) -> bool:
    """True for test modules, which SBFL excludes from the suspect set."""
    name = rel.rsplit("/", 1)[-1]
    stem = name.rsplit(".", 1)[0]
    return name.startswith("test_") or stem.endswith("_test") or name == "conftest.py"


def executed_lines(report: dict) -> set[LineKey]:
    """The ``(path, line)`` pairs a ``coverage json`` report marks executed.

    Paths are normalised to posix separators; test modules themselves
    are dropped so the matrix only implicates production code.
    """
    lines: set[LineKey] = set()
    files = report.get("files", {}) if isinstance(report, dict) else {}
    for raw_path, info in files.items():
        rel = str(raw_path).replace("\\", "/")
        if _is_test_file(rel):
            continue
        for lineno in info.get("executed_lines", []):
            lines.add((rel, int(lineno)))
    return lines


def _export_lines(
    workdir: Path, data_file: Path, json_file: Path, test_id: str
) -> set[LineKey] | None:
    """Run ``coverage json`` on ``data_file`` and parse the executed lines."""
    argv = [
        sys.executable, "-m", _COVERAGE_MODULE, "json",
        f"--data-file={data_file}", "-o", str(json_file),
    ]
    try:
        proc = subprocess.run(  # noqa: S603 — argv list, never shell=True
            argv, cwd=workdir, capture_output=True, text=True,
            timeout=_JSON_EXPORT_TIMEOUT, check=False,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        log.warning("coverage json export for %s skipped: %s", test_id, exc)
        return None
    if proc.returncode != 0 or not json_file.exists():
        log.warning(
            "coverage json export for %s failed (exit=%s); test skipped",
            test_id, proc.returncode,
        )
        return None
    try:
        report = json.loads(json_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        log.warning("coverage report for %s unreadable: %s", test_id, exc)
        return None
    return executed_lines(report)


def _run_one_test(
    workdir: Path, test_cmd: tuple[str, ...], test_id: str, timeout: float
) -> tuple[set[LineKey], bool] | None:
    """Run one test under coverage; return (executed lines, passed) or None."""
    with tempfile.TemporaryDirectory(prefix="prthinker-cov-") as tmp:
        data_file = Path(tmp) / "coverage.data"
        json_file = Path(tmp) / "coverage.json"
        argv = [
            sys.executable, "-m", _COVERAGE_MODULE, "run",
            f"--data-file={data_file}", "-m", *test_cmd, test_id,
        ]
        try:
            proc = subprocess.run(  # noqa: S603 — argv list, never shell=True
                argv, cwd=workdir, capture_output=True, text=True,
                timeout=timeout, check=False,
            )
        except (subprocess.TimeoutExpired, OSError) as exc:
            log.warning("coverage run for %s skipped: %s", test_id, exc)
            return None
        if not data_file.exists():
            log.warning(
                "coverage run for %s produced no data (exit=%s); test skipped",
                test_id, proc.returncode,
            )
            return None
        lines = _export_lines(workdir, data_file, json_file, test_id)
        if lines is None:
            return None
        return lines, proc.returncode == 0


def collect_coverage(
    workdir: Path | str,
    test_cmd: Sequence[str] = DEFAULT_TEST_CMD,
    test_ids: Sequence[str] = (),
    timeout: float = DEFAULT_TEST_TIMEOUT,
) -> CoverageMatrix:
    """Run each test id under coverage and assemble the SBFL matrix.

    ``test_cmd`` is the runner module and its options (default
    ``pytest -x -q``), invoked as ``python -m coverage run -m
    <test_cmd> <test_id>`` inside ``workdir``. A test whose collection
    fails (tool absent, timeout, nonzero exit with no coverage data) is
    skipped with a warning; the returned matrix simply omits it.
    """
    workdir = Path(workdir)
    ids = list(test_ids)
    if len(ids) > MAX_TESTS_PER_RUN:
        log.warning(
            "coverage collection capped at %d tests (%d requested)",
            MAX_TESTS_PER_RUN, len(ids),
        )
        ids = ids[:MAX_TESTS_PER_RUN]
    coverage: dict[str, set[LineKey]] = {}
    outcomes: dict[str, bool] = {}
    for test_id in ids:
        result = _run_one_test(workdir, tuple(test_cmd), test_id, timeout)
        if result is None:
            continue
        coverage[test_id], outcomes[test_id] = result
    return CoverageMatrix(coverage=coverage, outcomes=outcomes)


__all__ = [
    "DEFAULT_TEST_CMD",
    "DEFAULT_TEST_TIMEOUT",
    "MAX_TESTS_PER_RUN",
    "collect_coverage",
    "executed_lines",
]
