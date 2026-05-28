"""``reviewmind report`` — cross-store longitudinal summary.

Reads what the framework has already written:

- ``telemetry.sqlite`` — per-call (timestamp, backend, model, tokens,
  latency, cost, cache_hit)
- ``cache.sqlite`` — entry count + lifetime hit count
- ``dismissed.jsonl`` — author-rejected comments
- ``accepted.jsonl`` — author-applied suggestions

Renders into markdown, HTML, or JSON.  Sections:

1. Time window header
2. Per-(backend, model) totals: calls, hits, tokens, cost, p50 / p95
3. Cache fill + lifetime hit rate
4. Dismissed: total + by reason
5. Accepted: total + by file
6. Daily cost sparkline (ASCII, last 14 days)

No external deps — pure stdlib + the project's existing modules.
"""

from __future__ import annotations

import json
import logging
import sqlite3
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from reviewmind.accepted import AcceptedExamplesStore
from reviewmind.cache import PromptCache
from reviewmind.dismissed import DismissedExamplesStore
from reviewmind.telemetry import TelemetrySink

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class ReportInputs:
    telemetry_path: Path
    cache_path: Path
    dismissed_path: Path
    accepted_path: Path
    since_seconds: float | None  # None = all-time


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def _daily_cost_series(telemetry: Path, days: int) -> list[tuple[str, float]]:
    """Last `days` days of (YYYY-MM-DD, cost_usd) — zero-filled for empties."""
    if not telemetry.exists():
        return []
    now = time.time()
    cutoff = now - days * 86400.0
    with sqlite3.connect(str(telemetry)) as conn:
        rows = conn.execute(
            "SELECT timestamp, COALESCE(cost_usd, 0) FROM calls "
            "WHERE timestamp >= ?",
            (cutoff,),
        ).fetchall()

    buckets: dict[str, float] = {}
    for ts, cost in rows:
        day = time.strftime("%Y-%m-%d", time.gmtime(ts))
        buckets[day] = buckets.get(day, 0.0) + float(cost)

    # Zero-fill for the trailing 14 days.
    series: list[tuple[str, float]] = []
    for i in range(days - 1, -1, -1):
        day = time.strftime(
            "%Y-%m-%d", time.gmtime(now - i * 86400.0)
        )
        series.append((day, buckets.get(day, 0.0)))
    return series


def _dismissed_by_reason(store: DismissedExamplesStore) -> Counter[str]:
    counter: Counter[str] = Counter()
    for example in store:
        counter[example.reason or "(unspecified)"] += 1
    return counter


def _accepted_by_file(store: AcceptedExamplesStore) -> Counter[str]:
    counter: Counter[str] = Counter()
    for example in store:
        counter[example.path or "(unknown)"] += 1
    return counter


# ---------------------------------------------------------------------------
# Renderers
# ---------------------------------------------------------------------------

_SPARK_TICKS = "▁▂▃▄▅▆▇█"


def _spark(values: list[float]) -> str:
    if not values or max(values) == 0:
        return _SPARK_TICKS[0] * len(values)
    peak = max(values)
    out = []
    for v in values:
        idx = int(round((v / peak) * (len(_SPARK_TICKS) - 1)))
        out.append(_SPARK_TICKS[idx])
    return "".join(out)


def _gather(inputs: ReportInputs) -> dict[str, object]:
    """Run every read; return a plain dict for the renderer to format."""
    data: dict[str, object] = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "window": (
            "all-time" if inputs.since_seconds is None
            else f"last {inputs.since_seconds / 86400.0:g} day(s)"
        ),
    }

    if inputs.telemetry_path.exists():
        sink = TelemetrySink(inputs.telemetry_path)
        stats = sink.aggregate(since_seconds=inputs.since_seconds)
        data["telemetry"] = [
            {
                "backend": s.backend,
                "model": s.model,
                "calls": s.calls,
                "cache_hits": s.cache_hits,
                "prompt_tokens": s.prompt_tokens,
                "completion_tokens": s.completion_tokens,
                "cost_usd": round(s.cost_usd, 4),
                "p50_ms": round(s.latency_p50_ms, 0),
                "p95_ms": round(s.latency_p95_ms, 0),
            }
            for s in stats
        ]
        data["daily_cost"] = _daily_cost_series(inputs.telemetry_path, days=14)
    else:
        data["telemetry"] = []
        data["daily_cost"] = []

    if inputs.cache_path.exists():
        cache = PromptCache(inputs.cache_path)
        cstats = cache.stats()
        data["cache"] = {
            "entries": cstats.total_entries,
            "hits": cstats.total_hits,
        }
    else:
        data["cache"] = {"entries": 0, "hits": 0}

    if inputs.dismissed_path.exists():
        d_store = DismissedExamplesStore(inputs.dismissed_path)
        by_reason = _dismissed_by_reason(d_store)
        data["dismissed"] = {
            "total": len(d_store),
            "by_reason": dict(by_reason.most_common()),
        }
    else:
        data["dismissed"] = {"total": 0, "by_reason": {}}

    if inputs.accepted_path.exists():
        a_store = AcceptedExamplesStore(inputs.accepted_path)
        by_file = _accepted_by_file(a_store)
        data["accepted"] = {
            "total": len(a_store),
            "top_files": dict(by_file.most_common(5)),
        }
    else:
        data["accepted"] = {"total": 0, "top_files": {}}

    return data


def render_json(inputs: ReportInputs) -> str:
    return json.dumps(_gather(inputs), indent=2, ensure_ascii=False) + "\n"


def render_markdown(inputs: ReportInputs) -> str:
    data = _gather(inputs)
    out: list[str] = [
        f"# reviewmind report — {data['window']}",
        "",
        f"*Generated {data['generated_at']}*",
        "",
    ]

    # ----- usage table ----------------------------------------------------
    telemetry = data["telemetry"]
    out.append("## Usage by backend & model")
    out.append("")
    if telemetry:
        out.append("| backend | model | calls | hits | in-tok | out-tok | USD | p50 ms | p95 ms |")
        out.append("|---|---|---:|---:|---:|---:|---:|---:|---:|")
        total_cost = 0.0
        for row in telemetry:
            total_cost += float(row["cost_usd"])
            out.append(
                f"| {row['backend']} | {row['model']} | "
                f"{row['calls']} | {row['cache_hits']} | "
                f"{row['prompt_tokens']} | {row['completion_tokens']} | "
                f"${row['cost_usd']:.4f} | {row['p50_ms']:.0f} | {row['p95_ms']:.0f} |"
            )
        out.append("")
        out.append(f"**Total cost in window:** ${total_cost:.4f}")
    else:
        out.append("_No telemetry recorded in window._")
    out.append("")

    # ----- cache ----------------------------------------------------------
    cache = data["cache"]
    out.append("## Cache")
    out.append("")
    out.append(
        f"- entries: **{cache['entries']}**\n"
        f"- lifetime hits: **{cache['hits']}**"
    )
    out.append("")

    # ----- daily cost sparkline -------------------------------------------
    series = data["daily_cost"]
    if series:
        out.append("## Daily cost (last 14 days)")
        out.append("")
        values = [v for _d, v in series]
        out.append(f"```\n{_spark(values)}\n```")
        peak = max(values) if values else 0.0
        out.append(f"_peak: ${peak:.4f}_")
        out.append("")

    # ----- dismissed -------------------------------------------------------
    dismissed = data["dismissed"]
    out.append("## Dismissed corpus")
    out.append("")
    out.append(f"Total entries: **{dismissed['total']}**")
    out.append("")
    if dismissed["by_reason"]:
        out.append("| reason | count |")
        out.append("|---|---:|")
        for reason, n in dismissed["by_reason"].items():
            out.append(f"| {reason} | {n} |")
        out.append("")

    # ----- accepted --------------------------------------------------------
    accepted = data["accepted"]
    out.append("## Accepted corpus")
    out.append("")
    out.append(f"Total entries: **{accepted['total']}**")
    out.append("")
    if accepted["top_files"]:
        out.append("Top 5 files by accepted-suggestion count:")
        out.append("")
        out.append("| path | count |")
        out.append("|---|---:|")
        for path, n in accepted["top_files"].items():
            out.append(f"| `{path}` | {n} |")
        out.append("")

    return "\n".join(out).rstrip() + "\n"


def render_html(inputs: ReportInputs) -> str:
    """Wrap the markdown output in a minimal self-contained HTML shell.

    No JS, no external CSS — just enough styling to print cleanly.
    Markdown rendering is intentionally not done here; the consumer can
    pipe the markdown output through their renderer of choice. We just
    embed it inside a ``<pre>`` so the rendered HTML is still readable.
    """
    md = render_markdown(inputs)
    return (
        "<!doctype html>\n<meta charset='utf-8'>\n"
        "<title>reviewmind report</title>\n"
        "<style>"
        "body{font:14px/1.5 -apple-system,'Segoe UI',sans-serif;"
        "max-width:960px;margin:2em auto;padding:0 1em;color:#222;}"
        "pre{background:#f6f8fa;padding:1em;border-radius:6px;"
        "white-space:pre-wrap;font-family:'SFMono-Regular',Consolas,monospace;}"
        "</style>\n"
        f"<pre>{md.replace('<', '&lt;')}</pre>\n"
    )


__all__ = [
    "ReportInputs",
    "render_markdown",
    "render_html",
    "render_json",
]
