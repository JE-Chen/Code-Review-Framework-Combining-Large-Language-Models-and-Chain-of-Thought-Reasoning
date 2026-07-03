"""Append-only, content-safe trajectory events."""

from __future__ import annotations
import hashlib
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class TrajectoryEvent:
    run_id: str
    event: str
    timestamp: float
    duration_ms: float = 0
    path: str = ""
    tool: str = ""
    status: str = ""
    input_sha256: str = ""
    metadata: dict | None = None


class TrajectorySink:
    def __init__(self, path: Path, run_id: str):
        self.path = path
        self.run_id = run_id
        path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, event: str, *, content: str = "", **fields):
        row = TrajectoryEvent(
            self.run_id,
            event,
            time.time(),
            input_sha256=hashlib.sha256(content.encode()).hexdigest()
            if content
            else "",
            **fields,
        )
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(row), ensure_ascii=False) + "\n")
