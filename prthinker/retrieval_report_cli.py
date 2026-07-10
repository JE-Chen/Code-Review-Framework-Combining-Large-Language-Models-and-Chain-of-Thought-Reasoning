"""Render retrieval trajectory JSONL into an audit report."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from prthinker.cli_io import emit_text


def add_parser(sub) -> None:
    """Register the ``retrieval-report`` subcommand."""
    parser = sub.add_parser(
        "retrieval-report",
        help="Summarize content-safe retrieval trajectory JSONL",
    )
    parser.add_argument("input", type=Path)
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--out", type=Path)


def _read_events(path: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                events.append(json.loads(line))
    return events


def _event_path(event: dict[str, Any]) -> str:
    return str(event.get("path", "") or "<diff>")


def _tally_retrievals(
    by_path: dict[str, dict[str, int]], retrievals: list[dict[str, Any]]
) -> None:
    for event in retrievals:
        metadata = event.get("metadata") or {}
        by_path[_event_path(event)]["retrieved"] += len(metadata.get("retrieved", []))


def _tally_uses(
    by_path: dict[str, dict[str, int]], uses: list[dict[str, Any]]
) -> None:
    for event in uses:
        metadata = event.get("metadata") or {}
        row = by_path[_event_path(event)]
        row["used"] += len(metadata.get("used", []))
        row["citations"] += len(metadata.get("cited_indices", []))


def _totals(by_path: dict[str, dict[str, int]]) -> tuple[int, int, float]:
    """Retrieved/used totals plus the derived utilization ratio."""
    retrieved_total = sum(row["retrieved"] for row in by_path.values())
    used_total = sum(row["used"] for row in by_path.values())
    utilization = used_total / retrieved_total if retrieved_total else 0.0
    return retrieved_total, used_total, utilization


def summarize(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate trajectory events without exposing prompt/code content."""
    by_event = Counter(str(event.get("event", "")) for event in events)
    retrievals = [event for event in events if event.get("event") == "retrieve"]
    uses = [event for event in events if event.get("event") == "retrieval_use"]
    by_path: dict[str, dict[str, int]] = defaultdict(
        lambda: {"retrieved": 0, "used": 0, "citations": 0}
    )
    _tally_retrievals(by_path, retrievals)
    _tally_uses(by_path, uses)
    retrieved_total, used_total, utilization = _totals(by_path)
    return {
        "events": len(events),
        "by_event": dict(by_event),
        "retrievals": len(retrievals),
        "retrieval_use_events": len(uses),
        "retrieved_total": retrieved_total,
        "used_total": used_total,
        "utilization": utilization,
        "by_path": dict(sorted(by_path.items())),
    }


def render_markdown(summary: dict[str, Any]) -> str:
    """Render the retrieval audit summary as Markdown."""
    lines = [
        "# Retrieval report",
        "",
        f"- Events: {summary['events']}",
        f"- Retrieval events: {summary['retrievals']}",
        f"- Retrieval-use events: {summary['retrieval_use_events']}",
        f"- Retrieved docs: {summary['retrieved_total']}",
        f"- Used/cited docs: {summary['used_total']}",
        f"- Utilization: {summary['utilization']:.2f}",
        "",
        "## By path",
        "",
    ]
    by_path = summary.get("by_path", {})
    if not by_path:
        lines.append("_No retrieval events._")
    else:
        for path, row in by_path.items():
            lines.append(
                f"- `{path}`: {row['retrieved']} retrieved · "
                f"{row['used']} used · {row['citations']} citation(s)"
            )
    return "\n".join(lines).rstrip() + "\n"


def command(args: argparse.Namespace) -> int:
    """CLI entry point for ``retrieval-report``."""
    summary = summarize(_read_events(args.input))
    if args.format == "json":
        text = json.dumps(summary, indent=2) + "\n"
    else:
        text = render_markdown(summary)
    emit_text(text, args.out)
    return 0


__all__ = ["add_parser", "command", "render_markdown", "summarize"]
