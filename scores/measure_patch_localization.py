"""Measure patch-derived line/symbol localisation on ContextBench.

Hybrid: a reranking retriever localises files (high recall, few files), then
IssueFixProposer proposes a fix, and the patch's changed lines + enclosing
functions become the line/symbol prediction (precise, from the actual edit
rather than keywords). File score comes from the proposal's localised files
(which now include every file an edit touches); line/symbol from the patch.
Leakage-free: only the problem statement and the repo at its base commit.

Reports both the micro-average (matches the official evaluator; dominated by a
few cases with very large gold spans) and the macro-average (per-case mean, a
fairer per-issue view). A case whose single fix call times out is counted as an
honest miss (its gold enters the denominator with zero intersection).
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
from prthinker.issue_fix import IssueFixProposer, patch_context  # noqa: E402
from prthinker.repo_retrieval import (  # noqa: E402
    LexicalRepoRetriever,
    RepoContext,
    RepoContextRetriever,
    RerankingRepoRetriever,
    enrich_context_spans,
)
from prthinker.retrieval_scoring import (  # noqa: E402
    DimensionScore,
    gold_files,
    gold_lines,
    gold_symbols,
    score_retrieval_case,
    score_symbols,
)

WORKTREES = Path(r"D:\tmp\contextbench_worktrees")
OUTCOMES = ROOT / "outcomes_patch_localization.jsonl"
SCORE = ROOT / "score_patch_localization.json"
_CLI_TIMEOUT_SECONDS = 300.0
_RERANK_CANDIDATES = 20


class _EnrichedRerank(RepoContextRetriever):
    """Rerank localisation whose result carries predicted line spans.

    The reranker selects a small file set; :func:`enrich_context_spans` then
    attaches candidate spans so the proposer can window large files around the
    relevant lines instead of head-truncating them.
    """

    def __init__(self, inner: RepoContextRetriever) -> None:
        self._inner = inner

    def retrieve(self, query: str, workdir: Path) -> RepoContext:
        return enrich_context_spans(self._inner.retrieve(query, workdir), query, workdir)


def _worktree(row: dict) -> Path:
    slug = row["repo"].replace("/", "__")
    return WORKTREES / f"D___tmp_contextbench-repos_github.com__{slug}" / row["base_commit"]


def _micro(scores: list) -> tuple[float, float, float]:
    """Micro-averaged coverage/precision/f1 over dimension scores."""
    inter = sum(s.intersection for s in scores)
    gold = sum(s.gold_size for s in scores)
    pred = sum(s.pred_size for s in scores)
    cov = inter / gold if gold else 0.0
    prec = inter / pred if pred else 0.0
    return cov, prec, (2 * cov * prec / (cov + prec) if cov + prec else 0.0)


def _macro(scores: list) -> float:
    """Per-case mean coverage (recall) — fairer when gold-span sizes vary wildly."""
    return sum(s.coverage for s in scores) / len(scores) if scores else 0.0


def _proposer() -> IssueFixProposer:
    """Reranking localisation feeding the proposer (leakage-free).

    The lexical layer proposes candidates, the backend reranks to the few files
    that must change (high recall, small set), and span enrichment lets the
    proposer focus a large file on its relevant region. One retry recovers an
    invalid first attempt.
    """
    config = ClaudeCliConfig(
        executable="claude", model="", working_dir=".",
        allowed_tools="", timeout_seconds=_CLI_TIMEOUT_SECONDS,
    )
    backend = ClaudeCliBackend(config)
    base = LexicalRepoRetriever(top_k=_RERANK_CANDIDATES)
    retriever = _EnrichedRerank(RerankingRepoRetriever(base, backend, votes=1))
    return IssueFixProposer(retriever, backend, max_retries=1)


def _spans_dict(context) -> dict:
    """ContextBench span records from a RepoContext's (start, end) spans."""
    return {rel: [{"start": s, "end": e} for s, e in v]
            for rel, v in context.spans.items()}


def _miss(gold_size: int) -> DimensionScore:
    """A zero-intersection score that still counts gold — an honest miss."""
    return DimensionScore(0.0, 0.0, 0, gold_size, 0)


def _gold_dims(gold_spans) -> dict:
    """File / line / symbol gold sizes for a case (for miss accounting)."""
    return {
        "file": len(gold_files(gold_spans)),
        "line": len(gold_lines(gold_spans)),
        "symbol": len(gold_symbols(gold_spans)),
    }


def _dim_record(score) -> dict:
    """Flatten a DimensionScore to a JSON-serialisable dict."""
    return {"coverage": score.coverage, "precision": score.precision,
            "intersection": score.intersection, "gold_size": score.gold_size,
            "pred_size": score.pred_size}


def _score_case(proposer, row, gold_spans):
    """Localise + propose a fix; return (file, line, symbol) scores and meta."""
    proposal = proposer.propose(row["problem_statement"], _worktree(row))
    patch = patch_context(proposal, _worktree(row))
    file_s = score_retrieval_case(proposal.localized_files, {}, gold_spans).file
    line_s = score_retrieval_case(patch.files, _spans_dict(patch), gold_spans).line
    symbol_s = score_symbols(patch.symbols, gold_spans)
    return file_s, line_s, symbol_s, {"valid": proposal.valid, "edits": len(proposal.edits)}


def _load_rows() -> list:
    """Load the 25 verified ContextBench cases."""
    return [
        json.loads(line)
        for line in (ROOT / "contextbench_verified_25.jsonl").read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]


def _summary(file_scores: list, line_scores: list, symbol_scores: list) -> dict:
    """Micro- and macro-averaged coverage/precision/f1 per dimension."""
    summary = {}
    for name, scores in (("file", file_scores), ("line", line_scores),
                         ("symbol", symbol_scores)):
        cov, prec, f1 = _micro(scores)
        macro = _macro(scores)
        summary[name] = {"recall": cov, "precision": prec, "f1": f1,
                         "macro_recall": macro}
        print(f"PATCH-LOC {name} micro_recall={cov:.3f} precision={prec:.3f} "
              f"f1={f1:.3f} macro_recall={macro:.3f}", flush=True)
    return summary


def _case_result(proposer: IssueFixProposer, row: dict, gold_spans) -> tuple:
    """(file, line, symbol) scores + a JSON record for one case (miss on error)."""
    inst = row["original_inst_id"]
    try:
        file_s, line_s, symbol_s, meta = _score_case(proposer, row, gold_spans)
    except (RuntimeError, OSError) as exc:
        golds = _gold_dims(gold_spans)
        dims = (_miss(golds["file"]), _miss(golds["line"]), _miss(golds["symbol"]))
        return dims, {"instance_id": inst, "error": str(exc), "gold": golds}
    record = {"instance_id": inst, **meta, "file": _dim_record(file_s),
              "line": _dim_record(line_s), "symbol": _dim_record(symbol_s)}
    return (file_s, line_s, symbol_s), record


def _log(index: int, total: int, record: dict, started: float) -> None:
    """Print a one-line progress report for a completed case."""
    elapsed = time.time() - started
    inst = record["instance_id"]
    if "error" in record:
        print(f"[{index}/{total}] {inst}: ERROR {record['error']} "
              f"({elapsed:.1f}s)", flush=True)
        return
    print(f"[{index}/{total}] {inst}: valid={record['valid']} "
          f"edits={record['edits']} ({elapsed:.1f}s)", flush=True)


def main() -> None:
    """Localise + propose a fix per case; score file + line/symbol; persist both."""
    proposer = _proposer()
    gold = scorer.load_gold()
    rows = _load_rows()
    file_scores, line_scores, symbol_scores = [], [], []
    with OUTCOMES.open("w", encoding="utf-8") as out:
        for index, row in enumerate(rows, 1):
            started = time.time()
            dims, record = _case_result(proposer, row, gold[row["original_inst_id"]])
            file_scores.append(dims[0])
            line_scores.append(dims[1])
            symbol_scores.append(dims[2])
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
            out.flush()
            _log(index, len(rows), record, started)
    summary = _summary(file_scores, line_scores, symbol_scores)
    SCORE.write_text(json.dumps(summary, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
