"""Tests for the JUnit XML exporter."""

from __future__ import annotations

from xml.etree import ElementTree as ET  # noqa: S405 — parsing our own output  # nosec B405

from prthinker.junit_report import to_junit_xml, write_junit
from prthinker.pipeline import ReviewResult
from prthinker.schemas import InlineFinding


def _finding(path="a.py", line=5, severity="warning", comment="needs work"):
    return InlineFinding(path=path, line=line, severity=severity, comment=comment)


def _result(findings=None, code_diff="diff") -> ReviewResult:
    return ReviewResult(
        code_diff=code_diff, rag_docs=[], inline_findings=findings or []
    )


def _root(xml: str):
    return ET.fromstring(xml)  # noqa: S314 — input is our own generated XML  # nosec B314


def test_empty_result_is_well_formed_zero_tests():
    root = _root(to_junit_xml(_result()))
    assert root.tag == "testsuites"
    assert root.attrib["tests"] == "0"
    assert root.attrib["failures"] == "0"
    assert root.attrib["errors"] == "0"


def test_warning_becomes_failure():
    root = _root(to_junit_xml(_result([_finding(severity="warning")])))
    assert root.attrib["tests"] == "1"
    assert root.attrib["failures"] == "1"
    assert root.attrib["errors"] == "0"
    assert root.find("./testsuite/testcase/failure") is not None


def test_error_becomes_error_element():
    root = _root(to_junit_xml(_result([_finding(severity="error")])))
    assert root.attrib["errors"] == "1"
    assert root.find("./testsuite/testcase/error") is not None


def test_one_suite_per_file():
    findings = [_finding(path="a.py"), _finding(path="b.py"), _finding(path="a.py")]
    root = _root(to_junit_xml(_result(findings)))
    suites = {s.attrib["name"] for s in root.findall("./testsuite")}
    assert suites == {"a.py", "b.py"}


def test_testcase_carries_location_and_classname():
    root = _root(to_junit_xml(_result([_finding(path="x.py", line=9)])))
    case = root.find("./testsuite/testcase")
    assert case.attrib["classname"] == "x.py"
    assert "x.py:9" in case.attrib["name"]


def test_signals_included_as_cases():
    diff = (
        "diff --git a/a.py b/a.py\n"
        "--- a/a.py\n"
        "+++ b/a.py\n"
        "@@ -0,0 +1,1 @@\n"
        "+<<<<<<< HEAD\n"
    )
    root = _root(to_junit_xml(_result(code_diff=diff)))
    names = [c.attrib["name"] for c in root.findall(".//testcase")]
    assert any("Leftover merge-conflict marker" in n for n in names)


def test_xss_payload_is_escaped_and_parses():
    payload = "<script>alert(1)</script>"
    xml = to_junit_xml(_result([_finding(comment=payload)]))
    assert "<script>" not in xml
    # Still well-formed and the text round-trips through the parser.
    root = _root(xml)
    failure = root.find("./testsuite/testcase/failure")
    assert payload in failure.text


def test_write_junit_roundtrips(tmp_path):
    out = tmp_path / "junit.xml"
    write_junit(_result([_finding(comment="boom")]), out)
    root = _root(out.read_text(encoding="utf-8"))
    assert root.tag == "testsuites"
    assert "boom" in (root.find(".//failure").text or "")
