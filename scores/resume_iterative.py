"""Finish any missing iterative-retrieval cases and recompute the summary.

Runs only the cases absent from ``outcomes_iterative.jsonl``, then re-scores all
25 stored predictions (file/line from the blocks, symbol re-derived from each
span's innermost enclosing def/class) and writes ``score_iterative.json`` with
bootstrap CIs. Safe to re-run: a full outcomes file just recomputes the summary.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import measure_iterative as mi
from prthinker.repo_retrieval import enclosing_blocks
from prthinker.retrieval_scoring import (
    gold_files,
    gold_lines,
    gold_symbols,
    score_retrieval_case,
    score_symbols,
)

ROOT = Path(__file__).resolve().parent
OUTCOMES = mi.OUTCOMES


def _existing() -> dict:
    """Map instance_id -> stored prediction record."""
    if not OUTCOMES.exists():
        return {}
    return {
        (rec := json.loads(line))["instance_id"]: rec
        for line in OUTCOMES.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def _symbols_for(pred: dict, workdir: Path) -> dict:
    """Innermost enclosing def/class name for each predicted span (per file)."""
    names: dict[str, list[str]] = {}
    for rel, blocks in pred.get("blocks", {}).items():
        try:
            lines = (workdir / rel).read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        enclosing = enclosing_blocks(lines)
        picked = []
        for block in blocks:
            covering = [(end - start, name) for start, end, name in enclosing
                        if start <= block["start"] <= end]
            if covering:
                picked.append(min(covering)[1])
        names[rel] = picked
    return names


def _score_pred(pred: dict, row: dict, gold_spans) -> tuple:
    """(file, line, symbol) DimensionScores for one stored prediction."""
    if "error" in pred:
        return (mi._miss(len(gold_files(gold_spans))),
                mi._miss(len(gold_lines(gold_spans))),
                mi._miss(len(gold_symbols(gold_spans))))
    case = score_retrieval_case(pred["files"], pred.get("blocks", {}), gold_spans)
    symbol = score_symbols(_symbols_for(pred, mi._worktree(row)), gold_spans)
    return case.file, case.line, symbol


def _run_missing(rows: list, preds: dict, gold: dict) -> None:
    """Run the retriever only for cases missing from ``preds``."""
    retriever = mi._retriever()
    for row in rows:
        inst = row["original_inst_id"]
        if inst in preds:
            continue
        started = time.time()
        *_, pred = mi._case_result(retriever, row, gold[inst])
        preds[inst] = pred
        note = "ERROR" if "error" in pred else f"files={len(pred['files'])}"
        print(f"{inst}: {note} ({time.time() - started:.1f}s)", flush=True)


def main() -> None:
    """Fill missing cases, persist all 25 predictions, write the summary."""
    gold = mi.scorer.load_gold()
    rows = mi._load_rows()
    order = [row["original_inst_id"] for row in rows]
    rowmap = {row["original_inst_id"]: row for row in rows}
    preds = _existing()
    _run_missing(rows, preds, gold)
    with OUTCOMES.open("w", encoding="utf-8") as out:
        for inst in order:
            out.write(json.dumps(preds[inst], ensure_ascii=False) + "\n")
    file_scores, line_scores, symbol_scores = [], [], []
    for inst in order:
        file_s, line_s, symbol_s = _score_pred(preds[inst], rowmap[inst], gold[inst])
        file_scores.append(file_s)
        line_scores.append(line_s)
        symbol_scores.append(symbol_s)
    summary = {
        "file": mi._dimension_summary("file", file_scores),
        "line": mi._dimension_summary("line", line_scores),
        "symbol": mi._dimension_summary("symbol", symbol_scores),
    }
    mi.SCORE.write_text(json.dumps(summary, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
