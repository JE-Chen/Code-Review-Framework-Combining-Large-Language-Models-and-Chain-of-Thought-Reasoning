"""Measure iterative (agentic) multi-round retrieval on ContextBench.

Mirrors the ContextBench SOTA mechanism: over several rounds the backend selects
relevant blocks from the current pool and proposes the next search query, which
surfaces new files; selections accumulate. Blocks are held at balance-point
granularity via ``focus_lines``. Scores file / line / symbol (AST-based) with
micro + macro + bootstrap 95% CIs. Leakage-free: only problem statement + repo.
"""

from __future__ import annotations

import json
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
sys.path.insert(0, str(ROOT))

import contextbench_local_scorer as scorer  # noqa: E402
from prthinker.backends.claude_cli import ClaudeCliBackend  # noqa: E402
from prthinker.config import ClaudeCliConfig  # noqa: E402
from prthinker.repo_retrieval import IterativeRetriever, LexicalRepoRetriever  # noqa: E402
from prthinker.retrieval_scoring import (  # noqa: E402
    DimensionScore,
    gold_files,
    gold_lines,
    gold_symbols,
    score_retrieval_case,
    score_symbols,
)

WORKTREES = Path(r"D:\tmp\contextbench_worktrees")
OUTCOMES = ROOT / "outcomes_iterative.jsonl"
SCORE = ROOT / "score_iterative.json"
_CLI_TIMEOUT_SECONDS = 300.0
_CANDIDATES = 20
_ROUNDS = 3
_FOCUS_LINES = 60
_BOOTSTRAP_SAMPLES = 2000
_BOOTSTRAP_SEED = 12345
_CI_LOW = 0.025
_CI_HIGH = 0.975


def _worktree(row: dict) -> Path:
    slug = row["repo"].replace("/", "__")
    return WORKTREES / f"D___tmp_contextbench-repos_github.com__{slug}" / row["base_commit"]


def _retriever() -> IterativeRetriever:
    """Iterative retriever: lexical base, backend explore-and-select each round."""
    config = ClaudeCliConfig(
        executable="claude", model="", working_dir=".",
        allowed_tools="", timeout_seconds=_CLI_TIMEOUT_SECONDS,
    )
    backend = ClaudeCliBackend(config)
    return IterativeRetriever(
        LexicalRepoRetriever(top_k=_CANDIDATES), backend,
        rounds=_ROUNDS, focus_lines=_FOCUS_LINES,
    )


def _spans_dict(context) -> dict:
    """ContextBench span records from a RepoContext's (start, end) spans."""
    return {rel: [{"start": s, "end": e} for s, e in v]
            for rel, v in context.spans.items()}


def _load_rows() -> list:
    """Load the 25 verified ContextBench cases."""
    return [
        json.loads(line)
        for line in (ROOT / "contextbench_verified_25.jsonl").read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]


def _metric(scores: list) -> tuple[float, float, float]:
    """Micro coverage/precision/f1 over dimension scores."""
    inter = sum(s.intersection for s in scores)
    gold = sum(s.gold_size for s in scores)
    pred = sum(s.pred_size for s in scores)
    cov = inter / gold if gold else 0.0
    prec = inter / pred if pred else 0.0
    return cov, prec, (2 * cov * prec / (cov + prec) if cov + prec else 0.0)


def _macro(scores: list) -> float:
    """Per-case mean coverage (recall)."""
    return sum(s.coverage for s in scores) / len(scores) if scores else 0.0


def _bootstrap_ci(scores: list, index: int) -> tuple[float, float]:
    """Percentile 95% CI for one metric (0=recall, 1=precision, 2=f1)."""
    rng = random.Random(_BOOTSTRAP_SEED)  # noqa: S311 — CI resampling, not security
    size = len(scores)
    draws = []
    for _ in range(_BOOTSTRAP_SAMPLES):
        sample = [scores[rng.randrange(size)] for _ in range(size)]
        draws.append(_metric(sample)[index])
    draws.sort()
    return draws[int(_CI_LOW * _BOOTSTRAP_SAMPLES)], draws[int(_CI_HIGH * _BOOTSTRAP_SAMPLES)]


def _dimension_summary(name: str, scores: list) -> dict:
    """Micro + macro + bootstrap CIs for one dimension, and print a line."""
    cov, prec, f1 = _metric(scores)
    recall_ci = _bootstrap_ci(scores, 0)
    f1_ci = _bootstrap_ci(scores, 2)
    print(f"ITERATIVE {name} micro_recall={cov:.3f} CI[{recall_ci[0]:.3f},"
          f"{recall_ci[1]:.3f}] precision={prec:.3f} f1={f1:.3f} "
          f"CI[{f1_ci[0]:.3f},{f1_ci[1]:.3f}] macro_recall={_macro(scores):.3f}",
          flush=True)
    return {"recall": cov, "precision": prec, "f1": f1, "macro_recall": _macro(scores),
            "recall_ci": recall_ci, "f1_ci": f1_ci}


def _miss(gold_size: int) -> DimensionScore:
    """A zero-intersection score that still counts gold — an honest miss."""
    return DimensionScore(0.0, 0.0, 0, gold_size, 0)


def _score_case(retriever, row: dict, gold_spans) -> tuple:
    """Retrieve context for a case; return (file, line, symbol) scores + pred."""
    context = retriever.retrieve(row["problem_statement"], _worktree(row))
    case = score_retrieval_case(context.files, _spans_dict(context), gold_spans)
    symbol = score_symbols(context.symbols, gold_spans)
    pred = {"instance_id": row["original_inst_id"],
            "files": list(context.files), "blocks": _spans_dict(context)}
    return case.file, case.line, symbol, pred


def _case_result(retriever, row: dict, gold_spans) -> tuple:
    """(file, line, symbol) scores + record for one case (honest miss on error)."""
    inst = row["original_inst_id"]
    try:
        return _score_case(retriever, row, gold_spans)
    except (RuntimeError, OSError) as exc:
        dims = (_miss(len(gold_files(gold_spans))), _miss(len(gold_lines(gold_spans))),
                _miss(len(gold_symbols(gold_spans))))
        return (*dims, {"instance_id": inst, "error": str(exc)})


def main() -> None:
    """Run the iterative retriever over every case, score, and persist with CIs."""
    retriever = _retriever()
    gold = scorer.load_gold()
    rows = _load_rows()
    file_scores, line_scores, symbol_scores = [], [], []
    with OUTCOMES.open("w", encoding="utf-8") as out:
        for index, row in enumerate(rows, 1):
            started = time.time()
            inst = row["original_inst_id"]
            file_s, line_s, symbol_s, pred = _case_result(retriever, row, gold[inst])
            file_scores.append(file_s)
            line_scores.append(line_s)
            symbol_scores.append(symbol_s)
            out.write(json.dumps(pred, ensure_ascii=False) + "\n")
            out.flush()
            note = "ERROR" if "error" in pred else (
                f"files={len(pred['files'])} file_cov={file_s.coverage:.2f} "
                f"line_cov={line_s.coverage:.2f}")
            print(f"[{index}/{len(rows)}] {inst}: {note} "
                  f"({time.time() - started:.1f}s)", flush=True)
    summary = {
        "file": _dimension_summary("file", file_scores),
        "line": _dimension_summary("line", line_scores),
        "symbol": _dimension_summary("symbol", symbol_scores),
    }
    SCORE.write_text(json.dumps(summary, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
