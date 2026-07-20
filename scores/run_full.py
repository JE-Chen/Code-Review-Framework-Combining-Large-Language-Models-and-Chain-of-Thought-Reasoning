"""Run the iterative retriever over the full 266-case Python ContextBench set.

Resumable, per-case checkpointed. For each case it lazily ensures the base repo
is cloned and a work-tree exists at the base commit, runs
``prthinker.repo_retrieval.IterativeRetriever``, scores file/line/symbol against
the case's gold context, and appends the result to ``outcomes_full.jsonl``. A
clone / work-tree / retrieval failure is recorded as an honest miss and the run
continues. Prints a running micro-average so progress can be checked every N.
"""

from __future__ import annotations

import json
import subprocess  # nosec B404 — git via arg lists, shell=False
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
sys.path.insert(0, str(ROOT))

import measure_iterative as mi  # noqa: E402
from prthinker.backends.claude_cli import ClaudeCliBackend  # noqa: E402
from prthinker.config import ClaudeCliConfig  # noqa: E402
from prthinker.repo_retrieval import IterativeRetriever, LexicalRepoRetriever  # noqa: E402
from prthinker.retrieval_scoring import (  # noqa: E402
    score_retrieval_case,
    score_symbols,
)

BASE_REPOS = Path(r"D:\tmp\contextbench-repos")
WORKTREES = Path(r"D:\tmp\contextbench_worktrees")
CASES = ROOT / "cases_full.jsonl"
OUTCOMES = ROOT / "outcomes_full.jsonl"
_CLONE_TIMEOUT = 2400.0
_GIT_TIMEOUT = 600.0
_CLI_TIMEOUT = 300.0
_RETRY_ATTEMPTS = 2
_RETRY_BASE_SLEEP = 20.0
_RATE_LIMIT_PACE = 30.0
_BREAKER = 5


class _RetryingBackend:
    """Wrap a backend, retrying transient CLI failures with linear backoff.

    The claude CLI exits non-zero under a transient rate limit; a short backoff
    usually clears it. Persistent failure (quota genuinely exhausted) still
    propagates after the attempts are spent, so the caller can stop cleanly.
    """

    def __init__(self, inner, attempts: int = _RETRY_ATTEMPTS,
                 base_sleep: float = _RETRY_BASE_SLEEP) -> None:
        self._inner = inner
        self._attempts = attempts
        self._base = base_sleep

    def generate(self, prompt: str, max_new_tokens: int) -> str:
        for attempt in range(self._attempts + 1):
            try:
                return self._inner.generate(prompt, max_new_tokens)
            except RuntimeError:
                if attempt == self._attempts:
                    raise
                time.sleep(self._base * (attempt + 1))
        return ""  # unreachable — the final attempt returns or raises


def _retriever() -> IterativeRetriever:
    """Iterative retriever whose backend retries transient CLI rate limits."""
    config = ClaudeCliConfig(
        executable="claude", model="", working_dir=".",
        allowed_tools="", timeout_seconds=_CLI_TIMEOUT,
    )
    backend = _RetryingBackend(ClaudeCliBackend(config))
    return IterativeRetriever(
        LexicalRepoRetriever(top_k=20), backend, rounds=3, focus_lines=60)


def _slug(repo: str) -> str:
    return repo.replace("/", "__")


def _base_path(repo: str) -> Path:
    return BASE_REPOS / f"github.com__{_slug(repo)}"


def _worktree_path(repo: str, base_commit: str) -> Path:
    folder = f"D___tmp_contextbench-repos_github.com__{_slug(repo)}"
    return WORKTREES / folder / base_commit


def _git(args: list, cwd: Path | None, timeout: float) -> subprocess.CompletedProcess:
    """Run a git command with an arg list (never shell), capturing output."""
    return subprocess.run(  # nosec B603 B607 — fixed git exe, arg list, no shell
        ["git", *args], cwd=str(cwd) if cwd else None, capture_output=True,
        text=True, timeout=timeout, check=False,
    )


def _ensure_repo(repo: str, repo_url: str) -> Path:
    """Clone the base repository if it is not present; return its path."""
    base = _base_path(repo)
    if (base / ".git").exists():
        return base
    base.parent.mkdir(parents=True, exist_ok=True)
    result = _git(["clone", repo_url, str(base)], None, _CLONE_TIMEOUT)
    if not (base / ".git").exists():
        raise RuntimeError(f"clone failed for {repo}: {result.stderr[-300:]}")
    return base


def _ensure_worktree(repo: str, base_commit: str, base: Path) -> Path:
    """Add a work-tree at ``base_commit`` if absent; return its path."""
    worktree = _worktree_path(repo, base_commit)
    if worktree.exists():
        return worktree
    if _git(["cat-file", "-e", base_commit], base, _GIT_TIMEOUT).returncode != 0:
        _git(["fetch", "origin", base_commit], base, _CLONE_TIMEOUT)
    worktree.parent.mkdir(parents=True, exist_ok=True)
    result = _git(["worktree", "add", "--detach", str(worktree), base_commit],
                  base, _GIT_TIMEOUT)
    if not worktree.exists():
        raise RuntimeError(f"worktree failed for {repo}@{base_commit[:10]}: "
                           f"{result.stderr[-300:]}")
    return worktree


def _gold_of(record: dict) -> list:
    """Parse a case's gold_context JSON string into span records."""
    gold = record["gold_context"]
    return json.loads(gold) if isinstance(gold, str) else gold


def _score(context, gold_spans) -> tuple:
    """(file, line, symbol) DimensionScores for a retrieved context."""
    case = score_retrieval_case(context.files, mi._spans_dict(context), gold_spans)
    return case.file, case.line, score_symbols(context.symbols, gold_spans)


def _run_case(retriever, record: dict) -> tuple:
    """Prepare, retrieve, score one case.

    Returns ``(status, dims, payload)`` where status is ``"ok"`` (write result),
    ``"setup_fail"`` (permanent clone/work-tree failure — write an honest miss),
    or ``"cli_fail"`` (transient CLI/quota failure — do not write, retry on a
    later resume). Separating the two keeps a rate limit from poisoning the
    outcomes with misses that resume would then skip.
    """
    gold_spans = _gold_of(record)
    inst = record["original_inst_id"]
    try:
        base = _ensure_repo(record["repo"], record["repo_url"])
        workdir = _ensure_worktree(record["repo"], record["base_commit"], base)
    except (RuntimeError, OSError, subprocess.TimeoutExpired) as exc:
        return "setup_fail", _miss_dims(gold_spans), {
            "instance_id": inst, "repo": record["repo"], "error": str(exc)[:300]}
    try:
        context = retriever.retrieve(record["problem_statement"], workdir)
    except (RuntimeError, OSError, subprocess.TimeoutExpired) as exc:
        return "cli_fail", None, str(exc)[:150]
    file_s, line_s, symbol_s = _score(context, gold_spans)
    record_out = {"instance_id": inst, "repo": record["repo"],
                  "files": list(context.files), "blocks": mi._spans_dict(context)}
    return "ok", (file_s, line_s, symbol_s), record_out


def _miss_dims(gold_spans) -> tuple:
    """Honest-miss DimensionScores (gold counted, zero intersection)."""
    from prthinker.retrieval_scoring import gold_files, gold_lines, gold_symbols
    return (mi._miss(len(gold_files(gold_spans))), mi._miss(len(gold_lines(gold_spans))),
            mi._miss(len(gold_symbols(gold_spans))))


def _load_done() -> set:
    """Instance ids already scored (for resume)."""
    if not OUTCOMES.exists():
        return set()
    return {json.loads(line)["instance_id"]
            for line in OUTCOMES.read_text(encoding="utf-8").splitlines() if line.strip()}


def _progress(index: int, total: int, record: dict, dims: tuple, started: float) -> None:
    """Print a per-case line with the running micro-average of each dimension."""
    file_s, line_s, _ = dims
    tag = "ERROR" if "error" in record else (
        f"file={file_s.coverage:.2f} line={line_s.coverage:.2f}")
    print(f"[{index}/{total}] {record['instance_id']}: {tag} "
          f"({time.time() - started:.1f}s)", flush=True)


def _handle_cli_fail(index: int, total: int, record: dict, detail: str,
                     consecutive: int, started: float) -> bool:
    """Log a transient CLI failure; return True if the breaker should trip."""
    print(f"[{index}/{total}] {record['original_inst_id']}: CLI-FAIL {detail} "
          f"(consecutive={consecutive}) ({time.time() - started:.1f}s)", flush=True)
    if consecutive >= _BREAKER:
        print(f"QUOTA STOP: {consecutive} consecutive CLI failures — the claude "
              "CLI quota is exhausted; resume later to continue.", flush=True)
        return True
    time.sleep(_RATE_LIMIT_PACE)
    return False


def main() -> None:
    """Run every not-yet-scored case, checkpointing; stop cleanly on quota."""
    retriever = _retriever()
    records = [json.loads(line) for line in CASES.read_text(
        encoding="utf-8").splitlines() if line.strip()]
    done = _load_done()
    file_scores, line_scores, symbol_scores = [], [], []
    consecutive_cli = 0
    with OUTCOMES.open("a", encoding="utf-8") as out:
        for index, record in enumerate(records, 1):
            if record["original_inst_id"] in done:
                continue
            started = time.time()
            status, dims, payload = _run_case(retriever, record)
            if status == "cli_fail":
                consecutive_cli += 1
                if _handle_cli_fail(index, len(records), record, payload,
                                    consecutive_cli, started):
                    break
                continue
            consecutive_cli = 0
            file_scores.append(dims[0])
            line_scores.append(dims[1])
            symbol_scores.append(dims[2])
            out.write(json.dumps(payload, ensure_ascii=False) + "\n")
            out.flush()
            _progress(index, len(records), payload, dims, started)
            if len(file_scores) % 50 == 0:
                _checkpoint(file_scores, line_scores, symbol_scores)
    _checkpoint(file_scores, line_scores, symbol_scores)


def _checkpoint(file_scores: list, line_scores: list, symbol_scores: list) -> None:
    """Print the micro-average over cases scored so far this session."""
    for name, scores in (("file", file_scores), ("line", line_scores),
                         ("symbol", symbol_scores)):
        cov, prec, f1 = mi._metric(scores)
        print(f"CHECKPOINT {name} n={len(scores)} recall={cov:.3f} "
              f"precision={prec:.3f} f1={f1:.3f}", flush=True)


if __name__ == "__main__":
    main()
