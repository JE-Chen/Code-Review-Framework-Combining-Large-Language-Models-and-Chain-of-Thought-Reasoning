"""Sweep the focus-window size over stored block-rerank predictions (no LLM).

The uncapped block-rerank run selected whole def/class blocks (high line recall,
low precision). This re-scores those same selections after narrowing each block
to its densest ``focus_lines``-line query window — the ContextBench
"balance-point granularity" lever — to find the window size that maximises
line-level f1 without another model run.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
sys.path.insert(0, str(ROOT))

import contextbench_local_scorer as scorer  # noqa: E402
from prthinker.repo_retrieval import (  # noqa: E402
    _compute_idf,
    _index_document,
    _iter_code_files,
    expand_query,
    focus_window,
)
from prthinker.retrieval_scoring import score_retrieval_case  # noqa: E402

WORKTREES = Path(r"D:\tmp\contextbench_worktrees")
BLOCKS = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "outcomes_block_rerank_uncapped.jsonl")
WINDOWS = (20, 30, 40, 60, 80, 100, None)


def _worktree(repo: str, base_commit: str) -> Path:
    slug = repo.replace("/", "__")
    return WORKTREES / f"D___tmp_contextbench-repos_github.com__{slug}" / base_commit


def _problem_index() -> dict:
    """Map instance_id -> (problem_statement, worktree path)."""
    index = {}
    for line in (ROOT / "contextbench_verified_25.jsonl").read_text(
        encoding="utf-8"
    ).splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        index[row["original_inst_id"]] = (
            row["problem_statement"], _worktree(row["repo"], row["base_commit"]))
    return index


def _case_context(files: list, workdir: Path, problem: str) -> tuple:
    """Return (idf, query terms, {rel: lines}) for a case's retrieved files."""
    wanted = set(files)
    texts = {rel: text for rel, text in _iter_code_files(workdir) if rel in wanted}
    idf = _compute_idf([_index_document(rel, text) for rel, text in texts.items()])
    terms = expand_query(problem).terms
    return idf, terms, {rel: text.splitlines() for rel, text in texts.items()}


def _narrowed_spans(record: dict, idf, terms, lines_by: dict, window) -> dict:
    """Apply the focus window to every stored block span of one case."""
    spans = {}
    for rel, blocks in record["blocks"].items():
        lines = lines_by.get(rel)
        if lines is None:
            continue
        narrowed = []
        for block in blocks:
            span = (block["start"], block["end"])
            if window is not None:
                span = focus_window(lines, span, terms, idf, window)
            narrowed.append({"start": span[0], "end": span[1]})
        spans[rel] = narrowed
    return spans


def _line_scores(records: list, index: dict, window) -> list:
    """Line DimensionScores for every case at one window size."""
    gold = scorer.load_gold()
    scores = []
    for record in records:
        inst = record["instance_id"]
        if "error" in record:
            continue
        problem, workdir = index[inst]
        idf, terms, lines_by = _case_context(record["files"], workdir, problem)
        spans = _narrowed_spans(record, idf, terms, lines_by, window)
        scores.append(score_retrieval_case(record["files"], spans, gold[inst]).line)
    return scores


def _micro(scores: list) -> tuple[float, float, float]:
    """Micro coverage/precision/f1."""
    inter = sum(s.intersection for s in scores)
    gold = sum(s.gold_size for s in scores)
    pred = sum(s.pred_size for s in scores)
    cov = inter / gold if gold else 0.0
    prec = inter / pred if pred else 0.0
    return cov, prec, (2 * cov * prec / (cov + prec) if cov + prec else 0.0)


def main() -> None:
    """Print line recall/precision/f1 for each focus-window size."""
    records = [json.loads(line) for line in BLOCKS.read_text(
        encoding="utf-8").splitlines() if line.strip()]
    index = _problem_index()
    print(f"{'focus_lines':>12}  recall  precision   f1")
    for window in WINDOWS:
        cov, prec, f1 = _micro(_line_scores(records, index, window))
        label = "whole-block" if window is None else str(window)
        print(f"{label:>12}  {cov:.3f}   {prec:.3f}     {f1:.3f}", flush=True)


if __name__ == "__main__":
    main()
