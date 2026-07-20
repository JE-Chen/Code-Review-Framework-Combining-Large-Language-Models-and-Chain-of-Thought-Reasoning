"""Leakage-free lexical ContextBench baseline for the selected 25 cases."""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "contextbench_verified_25.jsonl"
OUTPUT = ROOT / "contextbench_official_lexical_baseline.jsonl"
WORKTREES = Path(r"D:\tmp\contextbench_worktrees")
TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{2,}")
CODE_SUFFIXES = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".go", ".rs",
    ".c", ".cc", ".cpp", ".h", ".hpp", ".rb", ".php",
}
STOP = {
    "the", "and", "for", "that", "this", "with", "from", "have", "has",
    "are", "was", "were", "not", "but", "can", "should", "would", "when",
    "where", "which", "into", "return", "using", "use", "used", "code",
    "file", "issue", "test", "tests", "class", "function", "true", "false",
}


def tokens(text: str) -> list[str]:
    return [x.lower() for x in TOKEN_RE.findall(text) if x.lower() not in STOP]


def repo_worktree(row: dict) -> Path:
    slug = row["repo"].replace("/", "__")
    # Official evaluator names the worktree root from its local cache path.
    root = WORKTREES / f"D___tmp_contextbench-repos_github.com__{slug}"
    return root / row["base_commit"]


def retrieve(row: dict, top_k: int = 10) -> tuple[list[str], dict[str, list[dict]]]:
    repo = repo_worktree(row)
    if not repo.is_dir():
        raise FileNotFoundError(repo)
    query = Counter(tokens(row["problem_statement"]))
    candidates: list[tuple[float, str, list[str]]] = []
    for path in repo.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in CODE_SUFFIXES:
            continue
        try:
            if path.stat().st_size > 1_000_000:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        rel = path.relative_to(repo).as_posix()
        path_tokens = Counter(tokens(rel.replace("/", " ")))
        body_tokens = Counter(tokens(text))
        score = 0.0
        for term, qtf in query.items():
            score += qtf * (8.0 * path_tokens[term] + min(body_tokens[term], 8))
        if score:
            candidates.append((score / math.sqrt(max(len(body_tokens), 1)), rel, text.splitlines()))
    candidates.sort(key=lambda x: (-x[0], x[1]))
    files = [rel for _, rel, _ in candidates[:top_k]]
    spans: dict[str, list[dict]] = {}
    query_terms = set(query)
    for _, rel, lines in candidates[:top_k]:
        ranked = sorted(
            ((len(query_terms & set(tokens(line))), i) for i, line in enumerate(lines, 1)),
            reverse=True,
        )
        best = [i for overlap, i in ranked[:3] if overlap]
        spans[rel] = [
            {"type": "line", "start": max(1, i - 3), "end": min(len(lines), i + 3)}
            for i in sorted(best)
        ]
    return files, spans


source_rows = [
    json.loads(line)
    for line in SOURCE.read_text(encoding="utf-8").splitlines()
    if line.strip()
]
with OUTPUT.open("w", encoding="utf-8") as output:
    for index, row in enumerate(source_rows, 1):
        files, spans = retrieve(row)
        step = {"files": files, "spans": spans, "symbols": {}}
        record = {
            "instance_id": row["original_inst_id"],
            "repo_url": row["repo_url"],
            "commit": row["base_commit"],
            "traj_data": {
                "pred_steps": [step],
                "pred_files": files,
                "pred_spans": spans,
                "pred_symbols": {},
            },
            "model_patch": "",
            "baseline": "lexical-v1-problem-statement-only",
        }
        output.write(json.dumps(record, ensure_ascii=False) + "\n")
        output.flush()
        print(f"[{index}/{len(source_rows)}] {row['original_inst_id']}: {len(files)} files", flush=True)
print(f"wrote {len(source_rows)} trajectories to {OUTPUT}")
