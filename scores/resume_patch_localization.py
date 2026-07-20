"""Finish any ContextBench cases missing from the patch-localisation run.

Runs only the cases absent from ``outcomes_patch_localization.jsonl``, appends
their records, then recomputes the micro-averaged file/line/symbol summary over
all 25 records and writes ``score_patch_localization.json``. Safe to re-run: a
fully populated outcomes file just recomputes the aggregate.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import measure_patch_localization as mpl  # noqa: E402
from prthinker.retrieval_scoring import DimensionScore  # noqa: E402

ROOT = Path(__file__).resolve().parent
OUTCOMES = ROOT / "outcomes_patch_localization.jsonl"
SCORE = ROOT / "score_patch_localization.json"


def _existing() -> dict:
    """Map instance_id -> stored outcome record."""
    if not OUTCOMES.exists():
        return {}
    return {
        (rec := json.loads(line))["instance_id"]: rec
        for line in OUTCOMES.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def _run_missing(rows: list, done: dict) -> dict:
    """Score every case not already present; return the merged record map."""
    proposer = mpl._proposer()
    gold = mpl.scorer.load_gold()
    for row in rows:
        inst = row["original_inst_id"]
        if inst in done:
            continue
        started = time.time()
        _dims, record = mpl._case_result(proposer, row, gold[inst])
        done[inst] = record
        mpl._log(0, len(rows), record, started)
    return done


def _dim_from_record(rec: dict, name: str) -> DimensionScore:
    """Rebuild a DimensionScore from a stored record (honest miss on error)."""
    if "error" in rec:
        return DimensionScore(0.0, 0.0, 0, rec.get("gold", {}).get(name, 0), 0)
    dim = rec.get(name)
    if dim is None:
        return DimensionScore(0.0, 0.0, 0, 0, 0)
    return DimensionScore(dim["coverage"], dim["precision"],
                          dim["intersection"], dim["gold_size"], dim["pred_size"])


def main() -> None:
    """Fill in missing cases, persist the full outcomes file, write the summary."""
    rows = mpl._load_rows()
    order = [r["original_inst_id"] for r in rows]
    done = _run_missing(rows, _existing())
    with OUTCOMES.open("w", encoding="utf-8") as out:
        for inst in order:
            out.write(json.dumps(done[inst], ensure_ascii=False) + "\n")
    file_scores = [_dim_from_record(done[i], "file") for i in order]
    line_scores = [_dim_from_record(done[i], "line") for i in order]
    symbol_scores = [_dim_from_record(done[i], "symbol") for i in order]
    summary = mpl._summary(file_scores, line_scores, symbol_scores)
    SCORE.write_text(json.dumps(summary, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
