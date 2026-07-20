"""Run ContextBench through the framework's repository context retriever.

This is a thin driver: all retrieval logic lives in the framework component
``prthinker.repo_retrieval.LexicalRepoRetriever`` (BM25 + issue-aware query
expansion + span/symbol prediction). The eval only locates each case's
checked-out work-tree and serialises the framework's ``RepoContext`` into the
ContextBench trajectory schema. It remains leakage-free: the retriever reads
only the ``problem_statement`` and the repository at ``base_commit``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
SOURCE = ROOT / "contextbench_verified_25.jsonl"
OUTPUT = ROOT / "contextbench_improved_baseline.jsonl"
WORKTREES = Path(r"D:\tmp\contextbench_worktrees")

sys.path.insert(0, str(REPO_ROOT))
from prthinker.repo_retrieval import LexicalRepoRetriever  # noqa: E402


def _worktree(row: dict) -> Path:
    """Locate the checked-out repository work-tree for one case."""
    slug = row["repo"].replace("/", "__")
    root = WORKTREES / f"D___tmp_contextbench-repos_github.com__{slug}"
    return root / row["base_commit"]


def _spans_payload(spans: dict[str, list[tuple[int, int]]]) -> dict:
    """Convert framework ``(start, end)`` spans to ContextBench span records."""
    return {
        path: [{"type": "line", "start": start, "end": end} for start, end in file_spans]
        for path, file_spans in spans.items()
    }


def _record(row: dict, context) -> dict:
    """Assemble a ContextBench trajectory record from a RepoContext."""
    files = list(context.files)
    spans = _spans_payload(context.spans)
    step = {"files": files, "spans": spans, "symbols": context.symbols}
    return {
        "instance_id": row["original_inst_id"],
        "repo_url": row["repo_url"],
        "commit": row["base_commit"],
        "traj_data": {
            "pred_steps": [step],
            "pred_files": files,
            "pred_spans": spans,
            "pred_symbols": context.symbols,
        },
        "model_patch": "",
        "baseline": "framework-repo-retriever-v1-problem-statement-only",
    }


def main() -> None:
    """Retrieve context for every source case via the framework component."""
    retriever = LexicalRepoRetriever()
    rows = [
        json.loads(line)
        for line in SOURCE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    with OUTPUT.open("w", encoding="utf-8") as out:
        for index, row in enumerate(rows, 1):
            context = retriever.retrieve(row["problem_statement"], _worktree(row))
            out.write(json.dumps(_record(row, context), ensure_ascii=False) + "\n")
            out.flush()
            print(f"[{index}/{len(rows)}] {row['original_inst_id']}: "
                  f"{len(context.files)} files", flush=True)
    print(f"wrote {len(rows)} trajectories to {OUTPUT}")


if __name__ == "__main__":
    main()
