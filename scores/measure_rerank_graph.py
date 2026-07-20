"""Measure graph-expanded RAG rerank (LocAgent-style recall + LLM localisation).

Pipeline: lexical BM25 -> import-graph neighbour expansion (high recall pool)
-> claude-cli backend selects the relevant files. Scores the selection with
the validated local scorer. Leakage-free: only problem_statement + repo.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
sys.path.insert(0, str(ROOT))

import contextbench_local_scorer as scorer  # noqa: E402
from prthinker.backends.claude_cli import ClaudeCliBackend  # noqa: E402
from prthinker.config import ClaudeCliConfig  # noqa: E402
from prthinker.repo_retrieval import (  # noqa: E402
    GraphExpandedRetriever,
    LexicalRepoRetriever,
    RerankingRepoRetriever,
    enrich_context_spans,
)
from prthinker.retrieval_scoring import score_symbols  # noqa: E402

WORKTREES = Path(r"D:\tmp\contextbench_worktrees")
OUTPUT = ROOT / "contextbench_rerank_graph.jsonl"


def _worktree(row: dict) -> Path:
    slug = row["repo"].replace("/", "__")
    return WORKTREES / f"D___tmp_contextbench-repos_github.com__{slug}" / row["base_commit"]


def main() -> None:
    """Run the graph-expanded reranking retriever over every case and score it."""
    config = ClaudeCliConfig(
        executable="claude", model="", working_dir=".",
        allowed_tools="", timeout_seconds=240.0,
    )
    base = GraphExpandedRetriever(
        LexicalRepoRetriever(top_k=20), neighbour_budget=15,
    )
    retriever = RerankingRepoRetriever(base, ClaudeCliBackend(config), votes=3)
    rows = [
        json.loads(line)
        for line in (ROOT / "contextbench_verified_25.jsonl").read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]
    gold = scorer.load_gold()
    preds, symbol_scores = [], []
    with OUTPUT.open("w", encoding="utf-8") as out:
        for index, row in enumerate(rows, 1):
            started = time.time()
            workdir = _worktree(row)
            context = enrich_context_spans(
                retriever.retrieve(row["problem_statement"], workdir),
                row["problem_statement"], workdir,
            )
            spans = {rel: [{"start": s, "end": e} for s, e in v]
                     for rel, v in context.spans.items()}
            preds.append({
                "instance_id": row["original_inst_id"],
                "traj_data": {"pred_files": list(context.files), "pred_spans": spans},
            })
            symbol_scores.append(score_symbols(context.symbols, gold[row["original_inst_id"]]))
            out.write(json.dumps(preds[-1], ensure_ascii=False) + "\n")
            out.flush()
            print(f"[{index}/{len(rows)}] {row['original_inst_id']}: "
                  f"{len(context.files)} files ({time.time() - started:.1f}s)", flush=True)
    agg = scorer.score_file(preds, gold)["aggregate"]
    _print_dim("file", agg["file"])
    _print_dim("line", agg["line"])
    _print_symbol(symbol_scores)


def _print_dim(name: str, dim: dict) -> None:
    """Print one micro-averaged dimension result."""
    print(f"GRAPH+RERANK {name} recall={dim['coverage']:.3f} "
          f"precision={dim['precision']:.3f} f1={dim['f1']:.3f}")


def _print_symbol(scores: list) -> None:
    """Print the best-effort (non-official) symbol dimension."""
    inter = sum(s.intersection for s in scores)
    gold_total = sum(s.gold_size for s in scores)
    pred_total = sum(s.pred_size for s in scores)
    cov = inter / gold_total if gold_total else 0.0
    prec = inter / pred_total if pred_total else 0.0
    f1 = 2 * cov * prec / (cov + prec) if cov + prec else 0.0
    print(f"GRAPH+RERANK symbol(non-official) recall={cov:.3f} "
          f"precision={prec:.3f} f1={f1:.3f}")


if __name__ == "__main__":
    main()
