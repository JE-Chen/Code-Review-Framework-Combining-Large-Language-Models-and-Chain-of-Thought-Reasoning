"""Pure-logic tests for the provenance / audit-trail extension.

Two concerns:

* the Pydantic schemas reject obviously invalid inputs;
* the inline-findings parser is *defensive* — a malformed provenance
  block never drops the underlying finding (safe-failure direction).
"""

from __future__ import annotations

import json

import pytest

from reviewmind.findings import build_provenance_block, parse_inline_findings
from reviewmind.schemas import (
    InlineFinding,
    Provenance,
    ProvenanceCitation,
)


# ----- schema validation -----------------------------------------------

def test_citation_default_lines_is_empty_list() -> None:
    c = ProvenanceCitation(kind="diff_evidence")
    assert c.lines == []
    assert c.index is None
    assert c.note == ""


def test_citation_rejects_zero_index() -> None:
    with pytest.raises(Exception):
        ProvenanceCitation(kind="rag_rule", index=0)


def test_citation_rejects_unknown_kind() -> None:
    with pytest.raises(Exception):
        ProvenanceCitation(kind="not_a_kind")  # type: ignore[arg-type]


def test_provenance_confidence_range() -> None:
    Provenance(confidence=0.0)
    Provenance(confidence=1.0)
    with pytest.raises(Exception):
        Provenance(confidence=-0.1)
    with pytest.raises(Exception):
        Provenance(confidence=1.5)


def test_inlinefinding_provenance_default_none() -> None:
    f = InlineFinding(path="x.py", line=1, severity="info", comment="x")
    assert f.provenance is None


# ----- parser: provenance round-trip -----------------------------------

def _finding_payload(**extras) -> dict:
    base = {
        "line": 4,
        "severity": "warning",
        "comment": "noisy log statement",
    }
    base.update(extras)
    return base


def test_parser_keeps_valid_provenance() -> None:
    raw = json.dumps([_finding_payload(provenance={
        "confidence": 0.7,
        "citations": [
            {"kind": "rag_rule", "index": 2, "note": "matches rule on logging"},
            {"kind": "diff_evidence", "lines": [4], "note": "the print call"},
        ],
    })])
    findings = parse_inline_findings(
        raw, path="a.py", allowed_lines={4},
        n_rag_rules=3, n_accepted_examples=0,
    )
    assert len(findings) == 1
    p = findings[0].provenance
    assert p is not None
    assert p.confidence == 0.7
    assert [c.kind for c in p.citations] == ["rag_rule", "diff_evidence"]


def test_parser_drops_out_of_range_rag_index() -> None:
    raw = json.dumps([_finding_payload(provenance={
        "citations": [
            {"kind": "rag_rule", "index": 99},
            {"kind": "rag_rule", "index": 1, "note": "ok"},
        ],
    })])
    findings = parse_inline_findings(
        raw, path="a.py", allowed_lines={4},
        n_rag_rules=2,
    )
    assert len(findings) == 1
    citations = findings[0].provenance.citations  # type: ignore[union-attr]
    assert [c.index for c in citations] == [1]


def test_parser_drops_out_of_range_accepted_example_index() -> None:
    raw = json.dumps([_finding_payload(provenance={
        "citations": [
            {"kind": "accepted_example", "index": 5},
        ],
    })])
    findings = parse_inline_findings(
        raw, path="a.py", allowed_lines={4},
        n_accepted_examples=2,
    )
    # Citation gone, but the finding survives.
    assert len(findings) == 1
    assert findings[0].provenance is None  # no citations and no confidence


def test_parser_keeps_finding_when_provenance_is_garbage() -> None:
    # Pydantic would reject ``provenance=123`` outright; the parser
    # strips it and keeps the finding.
    raw = json.dumps([_finding_payload(provenance=123)])
    findings = parse_inline_findings(raw, path="a.py", allowed_lines={4})
    assert len(findings) == 1
    assert findings[0].provenance is None


def test_parser_drops_diff_evidence_lines_outside_diff() -> None:
    raw = json.dumps([_finding_payload(provenance={
        "citations": [
            {"kind": "diff_evidence", "lines": [4, 999]},
        ],
    })])
    findings = parse_inline_findings(
        raw, path="a.py", allowed_lines={4},
    )
    p = findings[0].provenance
    assert p is not None
    assert p.citations[0].lines == [4]


def test_parser_back_compat_no_provenance_field() -> None:
    raw = json.dumps([_finding_payload()])
    findings = parse_inline_findings(raw, path="a.py", allowed_lines={4})
    assert findings[0].provenance is None


# ----- prompt block builder --------------------------------------------

def test_build_provenance_block_empty_when_nothing_to_cite() -> None:
    assert build_provenance_block(rag_docs=[], n_accepted_examples=0) == ""


def test_build_provenance_block_numbers_rag_docs() -> None:
    block = build_provenance_block(
        rag_docs=["always handle None", "prefer logging over print"],
        n_accepted_examples=0,
    )
    assert "1. always handle None" in block
    assert "2. prefer logging over print" in block
    assert "Audit trail (provenance)" in block


def test_build_provenance_block_mentions_accepted_examples_count() -> None:
    block = build_provenance_block(rag_docs=[], n_accepted_examples=3)
    assert "3 accepted-example" in block


def test_build_provenance_block_truncates_long_rules() -> None:
    long = "x" * 500
    block = build_provenance_block(
        rag_docs=[long], n_accepted_examples=0, max_doc_chars=80,
    )
    # Truncated to 80 chars including ellipsis.
    assert "x" * 79 in block
    assert "x" * 500 not in block
