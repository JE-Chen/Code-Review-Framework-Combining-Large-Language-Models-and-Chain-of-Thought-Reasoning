"""Parse free-form model output into structured ``InlineFinding`` items.

The model is *asked* to emit a JSON array, but realistically may add a
preamble, wrap in fenced code blocks, or trail off. We:

1. Strip code fences.
2. Find the outermost ``[ ... ]`` block.
3. Parse with ``json.loads``; if that fails, fall back to per-object regex.
4. Validate against the Pydantic schema (drops malformed entries).
5. Filter against ``allowed_lines`` so we never post a comment on a line
   GitHub will reject.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Iterable

from pydantic import ValidationError

from reviewmind.schemas import InlineFinding

log = logging.getLogger(__name__)

_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)
_ARRAY_RE = re.compile(r"\[[\s\S]*\]")
_OBJECT_RE = re.compile(r"\{[^{}]*\}")


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
    from codes.run.CoT_Prompts.inline_findings import (
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


def _strip_fences(text: str) -> str:
    match = _FENCE_RE.search(text)
    if match:
        return match.group(1)
    return text


def _extract_array(text: str) -> str | None:
    match = _ARRAY_RE.search(text)
    return match.group(0) if match else None


def _coerce_objects(text: str) -> list[dict]:
    items: list[dict] = []
    for raw in _OBJECT_RE.findall(text):
        try:
            items.append(json.loads(raw))
        except json.JSONDecodeError:
            continue
    return items


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
    body = _strip_fences(raw_output).strip()
    if not body or body == "[]":
        return []

    parsed: list[dict] | None = None

    array_text = _extract_array(body)
    if array_text is not None:
        try:
            data = json.loads(array_text)
            if isinstance(data, list):
                parsed = [item for item in data if isinstance(item, dict)]
        except json.JSONDecodeError:
            parsed = None

    if parsed is None:
        parsed = _coerce_objects(body)

    if not parsed:
        log.warning("No JSON findings could be extracted for %s", path)
        return []

    allowed = set(allowed_lines) if allowed_lines is not None else None

    findings: list[InlineFinding] = []
    for item in parsed:
        item.setdefault("path", path)
        item["path"] = path  # Always pin to the file we're reviewing.
        # Pre-clean a malformed provenance block so it does not blow up
        # the whole finding. ``provenance`` is optional; on any parse
        # failure we strip it and keep the finding.
        if "provenance" in item and not isinstance(item["provenance"], dict):
            item.pop("provenance")
        try:
            finding = InlineFinding.model_validate(item)
        except ValidationError as exc:
            # One more try without provenance, on the principle that a
            # bad citation should never lose a real finding.
            if "provenance" in item:
                stripped = {k: v for k, v in item.items() if k != "provenance"}
                try:
                    finding = InlineFinding.model_validate(stripped)
                except ValidationError as exc2:
                    log.debug("Dropped malformed finding %r: %s", item, exc2)
                    continue
                log.debug("Stripped bad provenance from finding on %s:%s (%s)",
                          path, item.get("line"), exc)
            else:
                log.debug("Dropped malformed finding %r: %s", item, exc)
                continue

        if allowed is not None and finding.line not in allowed:
            log.debug(
                "Dropping finding on %s:%d — line not in diff",
                finding.path, finding.line,
            )
            continue

        finding = _sanitize_suggestion(finding, allowed)
        finding = _sanitize_provenance(
            finding,
            allowed=allowed,
            n_rag_rules=n_rag_rules,
            n_accepted_examples=n_accepted_examples,
        )
        findings.append(finding)

    return findings


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
        if cite.kind == "rag_rule":
            if cite.index is None or not (1 <= cite.index <= n_rag_rules):
                log.debug("Dropping rag_rule citation index=%s (have %d)",
                          cite.index, n_rag_rules)
                continue
        elif cite.kind == "accepted_example":
            if cite.index is None or not (1 <= cite.index <= n_accepted_examples):
                log.debug("Dropping accepted_example citation index=%s (have %d)",
                          cite.index, n_accepted_examples)
                continue
        elif cite.kind == "diff_evidence":
            # Filter evidence lines to only those that appear in the diff
            # — same constraint we use for the finding's anchor line.
            if allowed is not None and cite.lines:
                cite_lines = [ln for ln in cite.lines if ln in allowed]
                if not cite_lines:
                    log.debug("Dropping diff_evidence citation; no lines in diff")
                    continue
                cite = cite.model_copy(update={"lines": cite_lines})
        kept.append(cite)

    if not kept and finding.provenance.confidence is None:
        return finding.model_copy(update={"provenance": None})
    return finding.model_copy(update={
        "provenance": finding.provenance.model_copy(update={"citations": kept})
    })


def _sanitize_suggestion(
    finding: InlineFinding, allowed: set[int] | None
) -> InlineFinding:
    """Drop the suggestion if the model violated the prompt contract.

    Mutating via model_copy keeps the rest of the finding intact — a bad
    suggestion shouldn't lose the textual comment.
    """
    if finding.suggestion is None:
        return finding

    reasons: list[str] = []
    if finding.severity == "info":
        reasons.append("severity=info forbids suggestion")

    range_invalid = (
        finding.start_line is not None and finding.start_line > finding.line
    )
    if range_invalid:
        reasons.append("start_line > line")
    elif (
        finding.start_line is not None
        and allowed is not None
        and finding.start_line not in allowed
    ):
        reasons.append(f"start_line {finding.start_line} not in diff")
    elif finding.is_multiline:
        expected = finding.line - (finding.start_line or finding.line) + 1
        actual = len(finding.suggestion.splitlines())
        if actual != expected:
            reasons.append(
                f"suggestion has {actual} lines, expected {expected}"
            )

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


__all__ = ["parse_inline_findings", "build_provenance_block"]
