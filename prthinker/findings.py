"""Parse free-form model output into structured ``InlineFinding`` items.

The model is *asked* to emit a JSON array, but realistically may add a
preamble, wrap in fenced code blocks, or trail off. We:

1. Scan for bracket-balanced ``[ ... ]`` spans (:mod:`prthinker.lenient_json`),
   tolerant of reasoning prose, non-JSON code fences, and trailing text.
2. Parse with ``json.loads``; if that fails, fall back to per-object regex.
3. Validate against the Pydantic schema (drops malformed entries).
4. Filter against ``allowed_lines`` so we never post a comment on a line
   GitHub will reject.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from typing import Iterable

from pydantic import ValidationError

from prthinker.lenient_json import iter_json_arrays, iter_json_objects
from prthinker.schemas import InlineFinding, ProvenanceCitation

log = logging.getLogger(__name__)

_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)
JSON_ARRAY_RE = re.compile(r"\[[\s\S]*\]")
_OBJECT_RE = re.compile(r"\{[^{}]*\}")


@dataclass(frozen=True)
class LenientJson:
    """Outcome of :func:`extract_lenient_json`.

    ``matched`` says whether ``pattern`` found a candidate payload;
    ``decode_error`` carries the ``json.JSONDecodeError`` message when
    the matched text failed to parse; ``data`` is the parsed JSON on
    success and ``None`` otherwise.
    """

    data: object | None = None
    matched: bool = False
    decode_error: str | None = None


def strip_json_fences(raw: str) -> str:
    """Return the ``` fence body when ``raw`` wraps one, else ``raw``, stripped."""
    match = _FENCE_RE.search(raw)
    if match:
        return match.group(1).strip()
    return raw.strip()


def _lenient_from_spans(spans: Iterable[str], expected: type) -> LenientJson:
    """Fold balanced JSON spans into a :class:`LenientJson`.

    ``matched`` is set once any span is seen; the last span decoding to
    ``expected`` wins (a valid span clears an earlier decode error), and a
    decode error is reported only when no span parsed to the wanted type.
    """
    data = None
    matched = False
    decode_error: str | None = None
    for span in spans:
        matched = True
        try:
            parsed = json.loads(span)
        except json.JSONDecodeError as exc:
            decode_error = str(exc)
            continue
        if isinstance(parsed, expected):
            data, decode_error = parsed, None
    if not matched:
        return LenientJson()
    if data is not None:
        return LenientJson(data=data, matched=True)
    return LenientJson(matched=True, decode_error=decode_error)


def extract_lenient_json(raw: str, *, pattern: re.Pattern[str]) -> LenientJson:
    """Scan ``raw`` for the container ``pattern`` targets and JSON-parse it.

    Shared by the findings / judge / lessons parsers. The balanced scanner
    (:mod:`prthinker.lenient_json`) tolerates reasoning prose, non-JSON code
    fences, and trailing text around the payload; ``pattern`` only selects
    array (``\\[``) vs object, so every caller keeps its existing call. Each
    caller still keeps its own logging and fallback via ``matched`` /
    ``decode_error``.
    """
    if pattern.pattern.startswith("\\["):
        return _lenient_from_spans(iter_json_arrays(raw), list)
    return _lenient_from_spans(iter_json_objects(raw), dict)


_JSON_OBJECT_RE = re.compile(r"\{[\s\S]*\}")


def split_unified_review(raw: str) -> tuple[str, str]:
    """Split a unified-review payload into (summary text, findings JSON).

    The unified step returns one JSON object carrying ``summary``,
    ``verdict`` and ``findings``; the pipeline stores the pieces under the
    historical ``compact_review`` / ``inline_findings`` result keys so
    every downstream consumer stays unchanged. Malformed payloads degrade
    to (raw text, "[]"): the reviewer still sees the model's output in the
    summary block and the findings parse safely to nothing.
    """
    parsed = extract_lenient_json(raw, pattern=_JSON_OBJECT_RE)
    if not isinstance(parsed.data, dict):
        log.warning("Unified review payload was not a JSON object; degrading")
        return raw.strip(), "[]"
    summary = str(parsed.data.get("summary", "") or "").strip()
    verdict = str(parsed.data.get("verdict", "") or "").strip()
    if verdict:
        summary = f"{summary}\n\nVerdict: {verdict}".strip()
    findings = parsed.data.get("findings", [])
    if not isinstance(findings, list):
        findings = []
    return summary, json.dumps(findings, ensure_ascii=False)


def build_provenance_block(
    *,
    rag_docs: list[str],
    n_accepted_examples: int,
    max_doc_chars: int = 200,
) -> str:
    """Render the provenance-instructions block for the prompt.

    Numbers the RAG docs (1-based) so the model has stable indices to
    cite. Accepted examples are already numbered by their formatter; we
    only tell the model how many exist so it does not invent indices.

    Returns ``""`` when there is nothing the model can cite, which
    silently disables the audit-trail request.
    """
    from prthinker.prompts.inline_findings import (
        PROVENANCE_INSTRUCTIONS_TEMPLATE,
    )

    if not rag_docs and n_accepted_examples == 0:
        return ""

    if rag_docs:
        rag_lines = ["### Available RAG rules (cite by 1-based index)", ""]
        for i, doc in enumerate(rag_docs, start=1):
            snippet = doc.strip().replace("\n", " ")
            if len(snippet) > max_doc_chars:
                snippet = snippet[: max_doc_chars - 1].rstrip() + "…"
            rag_lines.append(f"{i}. {snippet}")
        rag_lines.append("")
        rag_block = "\n".join(rag_lines)
    else:
        rag_block = ""

    if n_accepted_examples:
        ex_block = (
            f"### Available accepted examples\n\n"
            f"{n_accepted_examples} accepted-example(s) are listed above "
            f"under \"Examples of past advice that was accepted\". Cite "
            f"them by the same 1-based index they use there.\n"
        )
    else:
        ex_block = ""

    return PROVENANCE_INSTRUCTIONS_TEMPLATE.format(
        rag_rules_list=rag_block,
        accepted_examples_list=ex_block,
    )


def _coerce_objects(text: str) -> list[dict]:
    items: list[dict] = []
    for raw in _OBJECT_RE.findall(text):
        try:
            items.append(json.loads(raw))
        except json.JSONDecodeError:
            continue
    return items


def _extract_findings_objects(body: str) -> list[dict]:
    """Parse the model body into a list of finding dicts (best effort)."""
    result = extract_lenient_json(body, pattern=JSON_ARRAY_RE)
    if result.matched and isinstance(result.data, list):
        return [item for item in result.data if isinstance(item, dict)]
    return _coerce_objects(body)


def _validate_finding(item: dict, path: str) -> "InlineFinding | None":
    """Validate one finding dict, retrying once without a bad provenance block.

    A malformed ``provenance`` citation must never lose a real finding, so
    on validation failure we strip it and retry before giving up.
    """
    item["path"] = path  # Always pin to the file we're reviewing.
    if "provenance" in item and not isinstance(item["provenance"], dict):
        item.pop("provenance")
    try:
        return InlineFinding.model_validate(item)
    except ValidationError as exc:
        if "provenance" not in item:
            log.debug("Dropped malformed finding %r: %s", item, exc)
            return None
    stripped = {k: v for k, v in item.items() if k != "provenance"}
    try:
        finding = InlineFinding.model_validate(stripped)
    except ValidationError as exc2:
        log.debug("Dropped malformed finding %r: %s", item, exc2)
        return None
    log.debug("Stripped bad provenance from finding on %s:%s",
              path, item.get("line"))
    return finding


def parse_inline_findings(
    raw_output: str,
    *,
    path: str,
    allowed_lines: Iterable[int] | None = None,
    n_rag_rules: int = 0,
    n_accepted_examples: int = 0,
) -> list[InlineFinding]:
    """Best-effort parse of a model's findings output for a single file.

    ``n_rag_rules`` / ``n_accepted_examples`` describe how many entries
    the prompt actually surfaced. Provenance citations referencing an
    index outside that range are silently dropped (the *citation*,
    never the whole finding — safe-failure direction).
    """
    body = strip_json_fences(raw_output)
    if not body or body == "[]":
        return []

    parsed = _extract_findings_objects(body)
    if not parsed:
        log.warning("No JSON findings could be extracted for %s", path)
        return []

    allowed = set(allowed_lines) if allowed_lines is not None else None

    findings: list[InlineFinding] = []
    for item in parsed:
        finding = _process_finding_item(
            item,
            path=path,
            allowed=allowed,
            n_rag_rules=n_rag_rules,
            n_accepted_examples=n_accepted_examples,
        )
        if finding is not None:
            findings.append(finding)

    return findings


def _process_finding_item(
    item: dict,
    *,
    path: str,
    allowed: set[int] | None,
    n_rag_rules: int,
    n_accepted_examples: int,
) -> "InlineFinding | None":
    """Validate, line-filter, and sanitize one finding dict; ``None`` drops it."""
    finding = _validate_finding(item, path)
    if finding is None:
        return None
    if allowed is not None and finding.line not in allowed:
        log.debug(
            "Dropping finding on %s:%d — line not in diff",
            finding.path, finding.line,
        )
        return None
    finding = _sanitize_suggestion(finding, allowed)
    return _sanitize_provenance(
        finding,
        allowed=allowed,
        n_rag_rules=n_rag_rules,
        n_accepted_examples=n_accepted_examples,
    )


def _index_in_range(index: int | None, available: int) -> bool:
    """Return whether a 1-based citation index falls within the available count."""
    return index is not None and 1 <= index <= available


def _sanitize_citation(
    cite: ProvenanceCitation,
    *,
    allowed: set[int] | None,
    n_rag_rules: int,
    n_accepted_examples: int,
) -> "ProvenanceCitation | None":
    """Return the (possibly trimmed) citation, or ``None`` to drop it."""
    if cite.kind == "rag_rule":
        if not _index_in_range(cite.index, n_rag_rules):
            log.debug("Dropping rag_rule citation index=%s (have %d)",
                      cite.index, n_rag_rules)
            return None
    elif cite.kind == "accepted_example":
        if not _index_in_range(cite.index, n_accepted_examples):
            log.debug("Dropping accepted_example citation index=%s (have %d)",
                      cite.index, n_accepted_examples)
            return None
    elif cite.kind == "diff_evidence":
        return _sanitize_diff_evidence(cite, allowed)
    return cite


def _sanitize_diff_evidence(
    cite: ProvenanceCitation, allowed: set[int] | None
) -> "ProvenanceCitation | None":
    """Filter diff-evidence lines to those in the diff, or drop if none remain."""
    # Same constraint we use for the finding's anchor line.
    if allowed is None or not cite.lines:
        return cite
    cite_lines = [ln for ln in cite.lines if ln in allowed]
    if not cite_lines:
        log.debug("Dropping diff_evidence citation; no lines in diff")
        return None
    return cite.model_copy(update={"lines": cite_lines})


def _sanitize_provenance(
    finding: InlineFinding,
    *,
    allowed: set[int] | None,
    n_rag_rules: int,
    n_accepted_examples: int,
) -> InlineFinding:
    """Drop out-of-range citations; never drop the finding itself."""
    if finding.provenance is None:
        return finding

    kept = []
    for cite in finding.provenance.citations:
        sanitized = _sanitize_citation(
            cite,
            allowed=allowed,
            n_rag_rules=n_rag_rules,
            n_accepted_examples=n_accepted_examples,
        )
        if sanitized is not None:
            kept.append(sanitized)

    if not kept and finding.provenance.confidence is None:
        return finding.model_copy(update={"provenance": None})
    return finding.model_copy(update={
        "provenance": finding.provenance.model_copy(update={"citations": kept})
    })


def _suggestion_range_reason(
    finding: InlineFinding, allowed: set[int] | None
) -> str | None:
    """Return why the suggestion's line range is invalid, or ``None`` if valid."""
    if finding.start_line is not None and finding.start_line > finding.line:
        return "start_line > line"
    if (
        finding.start_line is not None
        and allowed is not None
        and finding.start_line not in allowed
    ):
        return f"start_line {finding.start_line} not in diff"
    return _multiline_length_reason(finding)


def _multiline_length_reason(finding: InlineFinding) -> str | None:
    """Return why a multiline suggestion's line count is wrong, or ``None``."""
    if not finding.is_multiline:
        return None
    expected = finding.line - (finding.start_line or finding.line) + 1
    actual = len(finding.suggestion.splitlines())
    if actual != expected:
        return f"suggestion has {actual} lines, expected {expected}"
    return None


def _suggestion_drop_reasons(
    finding: InlineFinding, allowed: set[int] | None
) -> list[str]:
    """Collect every reason the suggestion violates the prompt contract."""
    reasons: list[str] = []
    if finding.severity == "info":
        reasons.append("severity=info forbids suggestion")
    range_reason = _suggestion_range_reason(finding, allowed)
    if range_reason is not None:
        reasons.append(range_reason)
    return reasons


def _sanitize_suggestion(
    finding: InlineFinding, allowed: set[int] | None
) -> InlineFinding:
    """Drop the suggestion if the model violated the prompt contract.

    Mutating via model_copy keeps the rest of the finding intact — a bad
    suggestion shouldn't lose the textual comment.
    """
    if finding.suggestion is None:
        return finding

    reasons = _suggestion_drop_reasons(finding, allowed)
    if reasons:
        log.warning(
            "Dropping suggestion on %s:%d (%s)",
            finding.path, finding.line, "; ".join(reasons),
        )
        return finding.model_copy(update={
            "suggestion": None,
            "start_line": None,
            "original": None,
        })

    return finding


__all__ = [
    "JSON_ARRAY_RE",
    "LenientJson",
    "build_provenance_block",
    "extract_lenient_json",
    "parse_inline_findings",
    "strip_json_fences",
]
