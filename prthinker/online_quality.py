"""Privacy-safe interaction signals, separate from objective and judged scores."""

from __future__ import annotations

import hashlib
import hmac
import json
import sqlite3
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from prthinker.redaction import redact


class QualityEvent(BaseModel):
    """Only allowlisted operational fields enter the persistent store."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    event_id: str = Field(min_length=1, max_length=200)
    repository: str = Field(min_length=1, max_length=300)
    review_id: str = Field(min_length=1, max_length=200)
    finding_id: str = Field(default="", max_length=200)
    kind: Literal["review", "finding", "accepted", "dismissed", "applied", "converted", "regressed", "reopened"]
    timestamp: float = Field(ge=0, allow_inf_nan=False)
    backend: str = Field(default="", max_length=100)
    model: str = Field(default="", max_length=200)
    latency_ms: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    prompt_tokens: int | None = Field(default=None, ge=0)
    completion_tokens: int | None = Field(default=None, ge=0)
    cost_usd: float | None = Field(default=None, ge=0, allow_inf_nan=False)


class QualityStore:
    """HMAC-link events without storing repository names, user IDs or source."""

    def __init__(self, path: Path, key: bytes):
        if len(key) < 32:
            raise ValueError("quality pseudonymization key must have at least 32 bytes")
        self.path, self.key = path, key
        path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(path) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, timestamp REAL, payload TEXT)")

    def _id(self, value: str) -> str:
        return hmac.new(self.key, value.encode("utf-8"), hashlib.sha256).hexdigest()

    def record(self, event: QualityEvent) -> bool:
        if event.kind not in ("review",) and not event.finding_id:
            raise ValueError("finding interactions require a finding ID")
        payload = event.model_dump()
        for field in ("backend", "model"):
            payload[field] = redact(payload[field])[0]
        for field in ("event_id", "repository", "review_id", "finding_id"):
            payload[field] = self._id(f"{event.repository}/{field}/{payload[field]}")
        with sqlite3.connect(self.path) as conn:
            cursor = conn.execute("INSERT OR IGNORE INTO events VALUES (?,?,?)",
                                  (payload["event_id"], event.timestamp, json.dumps(payload)))
        return cursor.rowcount == 1

    def read(self, start: float = 0, end: float = float("inf")) -> list[dict]:
        if start >= end:
            raise ValueError("quality window start must precede end")
        with sqlite3.connect(self.path) as conn:
            rows = conn.execute("SELECT payload FROM events WHERE timestamp>=? AND timestamp<? ORDER BY timestamp,id",
                                (start, end)).fetchall()
        return [json.loads(row[0]) for row in rows]

    def report(self, start=0, end=float("inf")) -> dict:
        rows = self.read(start, end)
        reviews = [row for row in rows if row["kind"] == "review"]
        findings = {(row["review_id"], row["finding_id"]) for row in rows if row["kind"] == "finding"}
        dispositions = {}
        counts = {key: 0 for key in ("accepted", "dismissed", "applied", "converted", "regressed", "reopened")}
        for row in rows:
            if row["kind"] in counts:
                counts[row["kind"]] += 1
            if row["kind"] in ("accepted", "dismissed"):
                dispositions[(row["review_id"], row["finding_id"])] = row["kind"]
        decided = len(dispositions)
        accepted = sum(value == "accepted" for value in dispositions.values())
        return {
            "measurement": "user_interaction_signals", "events": len(rows), "reviews": len(reviews),
            "findings": len(findings), "dispositions": decided, "signals": counts,
            "acceptance_rate_among_decided": accepted / decided if decided else None,
            "unanswered_findings": len(findings - dispositions.keys()),
            "mean_latency_ms": _mean_known(reviews, "latency_ms"),
            "prompt_tokens": _sum_known(reviews, "prompt_tokens"),
            "completion_tokens": _sum_known(reviews, "completion_tokens"),
            "cost_usd": _sum_known(reviews, "cost_usd"),
            "missing_latency_reviews": sum(row["latency_ms"] is None for row in reviews),
            "groups": sorted({(row["backend"], row["model"]) for row in reviews}),
        }


def _mean_known(rows, key):
    values = [row[key] for row in rows if row[key] is not None]
    return sum(values) / len(values) if values else None


def _sum_known(rows, key):
    values = [row[key] for row in rows if row[key] is not None]
    return sum(values) if values and len(values) == len(rows) else None


def drift(previous: dict, current: dict) -> dict:
    """Descriptive signal drift; never assert causal or objective quality."""
    before, after = previous["acceptance_rate_among_decided"], current["acceptance_rate_among_decided"]
    return {"measurement": "interaction_drift",
            "acceptance_rate_delta": after - before if before is not None and after is not None else None,
            "previous_dispositions": previous["dispositions"], "current_dispositions": current["dispositions"],
            "configuration_changed": previous["groups"] != current["groups"]}


def add_parser(sub):
    root = sub.add_parser("quality")
    actions = root.add_subparsers(dest="action", required=True)
    record = actions.add_parser("record")
    record.add_argument("event_file", type=Path)
    report = actions.add_parser("report")
    report.add_argument("--since", type=float, default=0)
    report.add_argument("--until", type=float, default=float("inf"))
    report.add_argument("--split-at", type=float)
    for parser in (record, report):
        parser.add_argument("--store", type=Path, required=True)


def command(args):
    import os

    from prthinker.cli_io import emit_text

    key = os.environ.get("PRTHINKER_QUALITY_KEY", "").encode("utf-8")
    store = QualityStore(args.store, key)
    if args.action == "record":
        event = QualityEvent.model_validate_json(args.event_file.read_text(encoding="utf-8"))
        result = {"recorded": store.record(event)}
    else:
        result = store.report(args.since, args.until)
        if args.split_at is not None:
            result["drift"] = drift(store.report(args.since, args.split_at), store.report(args.split_at, args.until))
    emit_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", None)
    return 0
