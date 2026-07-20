"""Measure the RAG rerank retriever (lexical recall + LLM localisation).

Runs prthinker.repo_retrieval.RerankingRepoRetriever over the 25 verified
cases: the lexical layer proposes candidate files, the claude-cli backend
selects the relevant subset. Scores the selection with the validated local
scorer. Leakage-free: only problem_statement + the repo at base_commit.
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
    LexicalRepoRetriever,
    RerankingRepoRetriever,
)

WORKTREES = Path(r"D:\tmp\contextbench_worktrees")
CANDIDATE_K = 20
OUTPUT = ROOT / "contextbench_rerank.jsonl"


def _worktree(row: dict) -> Path:
    slug = row["repo"].replace("/", "__")
    return WORKTREES / f"D___tmp_contextbench-repos_github.com__{slug}" / row["base_commit"]


def main() -> None:
    """Run the reranking retriever over every case and score the selections."""
    config = ClaudeCliConfig(
        executable="claude", model="", working_dir=".",
        allowed_tools="", timeout_seconds=180.0,
    )
    retriever = RerankingRepoRetriever(
        LexicalRepoRetriever(top_k=CANDIDATE_K), ClaudeCliBackend(config),
    )
    rows = [
        json.loads(line)
        for line in (ROOT / "contextbench_verified_25.jsonl").read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]
    preds = []
    with OUTPUT.open("w", encoding="utf-8") as out:
        for index, row in enumerate(rows, 1):
            started = time.time()
            context = retriever.retrieve(row["problem_statement"], _worktree(row))
            preds.append({
                "instance_id": row["original_inst_id"],
                "traj_data": {"pred_files": list(context.files), "pred_spans": {}},
            })
            out.write(json.dumps(preds[-1], ensure_ascii=False) + "\n")
            out.flush()
            print(f"[{index}/{len(rows)}] {row['original_inst_id']}: "
                  f"{len(context.files)} files ({time.time() - started:.1f}s)", flush=True)
    report = scorer.score_file(preds, scorer.load_gold())
    agg = report["aggregate"]["file"]
    cov, prec = agg["coverage"], agg["precision"]
    f1 = 2 * cov * prec / (cov + prec) if cov + prec else 0.0
    print(f"RERANK file recall={cov:.3f} precision={prec:.3f} f1={f1:.3f}")


if __name__ == "__main__":
    main()
