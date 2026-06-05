"""Tests for the SARIF 2.1.0 exporter."""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Make ``prthinker`` importable when running pytest from the repo root.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from prthinker.pipeline import ReviewResult  # noqa: E402
from prthinker.sarif import (  # noqa: E402
    SARIF_SCHEMA_URI,
    SARIF_VERSION,
    severity_to_level,
    to_sarif,
    write_sarif,
)
from prthinker.schemas import InlineFinding  # noqa: E402


def _finding(
    path: str = "src/app.py",
    line: int = 5,
    severity: str = "warning",
    comment: str = "needs work",
    start_line: int | None = None,
) -> InlineFinding:
    return InlineFinding(
        path=path,
        line=line,
        severity=severity,
        comment=comment,
        start_line=start_line,
    )


def _result(findings: list[InlineFinding] | None = None) -> ReviewResult:
    return ReviewResult(
        code_diff="diff",
        rag_docs=[],
        inline_findings=findings or [],
    )


# ---------- severity -> level mapping ---------------------------------------


def test_severity_to_level_error():
    assert severity_to_level("error") == "error"


def test_severity_to_level_warning():
    assert severity_to_level("warning") == "warning"


def test_severity_to_level_info_is_note():
    assert severity_to_level("info") == "note"


def test_severity_to_level_unknown_is_note():
    assert severity_to_level("totally-unknown") == "note"
    assert severity_to_level("") == "note"


# ---------- required SARIF keys ---------------------------------------------


def test_required_sarif_keys_present():
    sarif = to_sarif(_result())
    assert sarif["$schema"] == SARIF_SCHEMA_URI
    assert sarif["version"] == SARIF_VERSION
    assert isinstance(sarif["runs"], list)
    assert len(sarif["runs"]) == 1


def test_tool_driver_name_and_version():
    sarif = to_sarif(_result(), tool_name="custom", tool_version="9.9")
    driver = sarif["runs"][0]["tool"]["driver"]
    assert driver["name"] == "custom"
    assert driver["version"] == "9.9"


def test_tool_driver_defaults():
    driver = to_sarif(_result())["runs"][0]["tool"]["driver"]
    assert driver["name"] == "prthinker"
    assert driver["version"] == "0"


# ---------- empty result -> empty results array -----------------------------


def test_empty_result_has_empty_results_array():
    sarif = to_sarif(_result())
    run = sarif["runs"][0]
    assert run["results"] == []
    assert run["tool"]["driver"]["rules"] == []


# ---------- findings -> results mapping -------------------------------------


def test_single_finding_maps_to_one_result():
    sarif = to_sarif(_result([_finding(severity="error", comment="boom")]))
    results = sarif["runs"][0]["results"]
    assert len(results) == 1
    res = results[0]
    assert res["level"] == "error"
    assert res["message"]["text"] == "boom"
    assert res["ruleId"] == "prthinker/error"


def test_result_physical_location():
    sarif = to_sarif(_result([_finding(path="a/b.py", line=42)]))
    loc = sarif["runs"][0]["results"][0]["locations"][0]["physicalLocation"]
    assert loc["artifactLocation"]["uri"] == "a/b.py"
    assert loc["region"]["startLine"] == 42


def test_multiline_finding_sets_region_range():
    sarif = to_sarif(_result([_finding(line=10, start_line=7)]))
    region = (
        sarif["runs"][0]["results"][0]["locations"][0]
        ["physicalLocation"]["region"]
    )
    assert region["startLine"] == 7
    assert region["endLine"] == 10


def test_multiple_findings_map_in_order():
    findings = [
        _finding(path="x.py", line=1, severity="info", comment="a"),
        _finding(path="y.py", line=2, severity="warning", comment="b"),
        _finding(path="z.py", line=3, severity="error", comment="c"),
    ]
    results = to_sarif(_result(findings))["runs"][0]["results"]
    assert [r["level"] for r in results] == ["note", "warning", "error"]
    assert [r["message"]["text"] for r in results] == ["a", "b", "c"]


def test_rules_are_deduplicated_by_severity():
    findings = [
        _finding(severity="warning", comment="one"),
        _finding(severity="warning", comment="two"),
        _finding(severity="error", comment="three"),
    ]
    rules = to_sarif(_result(findings))["runs"][0]["tool"]["driver"]["rules"]
    rule_ids = {r["id"] for r in rules}
    assert rule_ids == {"prthinker/warning", "prthinker/error"}
    assert len(rules) == 2


# ---------- json round-trips -----------------------------------------------


def test_json_round_trip_empty():
    sarif = to_sarif(_result())
    assert json.loads(json.dumps(sarif)) == sarif


def test_json_round_trip_with_findings():
    findings = [
        _finding(severity="error", comment="é unicode ✓"),
        _finding(severity="info", line=8, start_line=3),
    ]
    sarif = to_sarif(_result(findings))
    assert json.loads(json.dumps(sarif)) == sarif


# ---------- write_sarif -----------------------------------------------------


def test_write_sarif_creates_valid_json(tmp_path):
    out = tmp_path / "out.sarif"
    write_sarif(_result([_finding(severity="error", comment="x")]), out)
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["version"] == SARIF_VERSION
    assert loaded["runs"][0]["results"][0]["level"] == "error"


def test_write_sarif_accepts_str_path(tmp_path):
    out = tmp_path / "as_str.sarif"
    write_sarif(_result(), str(out))
    assert out.exists()
    assert json.loads(out.read_text(encoding="utf-8"))["runs"][0]["results"] == []


# ---------- orientation signals --------------------------------------------

_CONFLICT_DIFF = (
    "diff --git a/a.py b/a.py\n"
    "--- a/a.py\n"
    "+++ b/a.py\n"
    "@@ -0,0 +1,1 @@\n"
    "+<<<<<<< HEAD\n"
)


def test_signal_emitted_as_result_with_namespaced_rule():
    result = ReviewResult(code_diff=_CONFLICT_DIFF, rag_docs=[], inline_findings=[])
    results = to_sarif(result)["runs"][0]["results"]
    rule_ids = {r["ruleId"] for r in results}
    assert "prthinker/merge-conflict" in rule_ids


def test_signal_result_has_location_and_level():
    result = ReviewResult(code_diff=_CONFLICT_DIFF, rag_docs=[], inline_findings=[])
    res = next(
        r for r in to_sarif(result)["runs"][0]["results"]
        if r["ruleId"] == "prthinker/merge-conflict"
    )
    assert res["level"] == "error"
    loc = res["locations"][0]["physicalLocation"]
    assert loc["artifactLocation"]["uri"] == "a.py"
    assert loc["region"]["startLine"] == 1


def test_signal_rule_registered_in_driver():
    result = ReviewResult(code_diff=_CONFLICT_DIFF, rag_docs=[], inline_findings=[])
    rules = to_sarif(result)["runs"][0]["tool"]["driver"]["rules"]
    assert any(r["id"] == "prthinker/merge-conflict" for r in rules)


def test_findings_and_signals_coexist():
    result = ReviewResult(
        code_diff=_CONFLICT_DIFF, rag_docs=[],
        inline_findings=[_finding(severity="error", comment="boom")],
    )
    rule_ids = [r["ruleId"] for r in to_sarif(result)["runs"][0]["results"]]
    assert "prthinker/error" in rule_ids
    assert "prthinker/merge-conflict" in rule_ids


def test_pathless_navigation_signal_still_a_result():
    diff = (
        "diff --git a/old.py b/new.py\n"
        "similarity index 100%\n"
        "rename from old.py\n"
        "rename to new.py\n"
    )
    result = ReviewResult(code_diff=diff, rag_docs=[], inline_findings=[])
    res = next(
        r for r in to_sarif(result)["runs"][0]["results"]
        if r["ruleId"] == "prthinker/rename"
    )
    assert "locations" in res  # rename carries the new path
    assert res["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] == "new.py"


def test_signal_json_round_trips():
    result = ReviewResult(code_diff=_CONFLICT_DIFF, rag_docs=[], inline_findings=[])
    sarif = to_sarif(result)
    assert json.loads(json.dumps(sarif)) == sarif


# ---------- enrichment: fingerprints + rule help ---------------------------

_FP_KEY = "prthinkerHash/v1"


def test_finding_result_has_partial_fingerprint():
    res = to_sarif(_result([_finding(comment="boom")]))["runs"][0]["results"][0]
    assert len(res["partialFingerprints"][_FP_KEY]) == 64


def test_fingerprint_stable_and_distinct_by_content():
    f1 = to_sarif(_result([_finding(comment="x", line=1)]))["runs"][0]["results"][0]
    f2 = to_sarif(_result([_finding(comment="x", line=1)]))["runs"][0]["results"][0]
    f3 = to_sarif(_result([_finding(comment="y", line=1)]))["runs"][0]["results"][0]
    assert f1["partialFingerprints"][_FP_KEY] == f2["partialFingerprints"][_FP_KEY]
    assert f1["partialFingerprints"][_FP_KEY] != f3["partialFingerprints"][_FP_KEY]


def test_rules_carry_help_uri_and_full_description():
    rule = to_sarif(_result([_finding()]))["runs"][0]["tool"]["driver"]["rules"][0]
    assert rule["helpUri"].startswith("https://")
    assert rule["fullDescription"]["text"]


def test_signal_result_has_fingerprint():
    result = ReviewResult(code_diff=_CONFLICT_DIFF, rag_docs=[], inline_findings=[])
    res = next(
        r for r in to_sarif(result)["runs"][0]["results"]
        if r["ruleId"] == "prthinker/merge-conflict"
    )
    assert len(res["partialFingerprints"][_FP_KEY]) == 64
