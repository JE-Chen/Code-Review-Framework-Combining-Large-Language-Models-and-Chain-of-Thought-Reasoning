"""Extract the 266 Python ContextBench-verified cases from the official parquet.

Writes ``cases_full.jsonl`` — one record per case with the fields the full run
needs (id, repo, base_commit, problem_statement, gold_context) — ordered so the
repositories already cloned locally come first, letting the run validate on
available cases before any new clone.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

PARQUET = Path(r"D:\tmp\ContextBench-official\data\contextbench_verified.parquet")
OUT = Path(__file__).resolve().parent / "cases_full.jsonl"
_PRIORITY = ("django/django", "astropy/astropy")  # already cloned locally


def _order_key(repo: str, counts: dict) -> tuple:
    """Cloned repos first, then smaller repos before larger ones."""
    if repo in _PRIORITY:
        return (0, _PRIORITY.index(repo), 0)
    return (1, counts[repo], repo)


def main() -> None:
    """Write the ordered Python case records to cases_full.jsonl."""
    frame = pd.read_parquet(PARQUET)
    python = frame[frame["language"] == "python"]
    counts = python["repo"].value_counts().to_dict()
    records = [
        {
            "original_inst_id": row["original_inst_id"],
            "repo": row["repo"],
            "repo_url": row["repo_url"],
            "base_commit": row["base_commit"],
            "problem_statement": row["problem_statement"],
            "gold_context": row["gold_context"],
        }
        for _, row in python.iterrows()
    ]
    records.sort(key=lambda rec: _order_key(rec["repo"], counts))
    with OUT.open("w", encoding="utf-8") as out:
        for record in records:
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
    by_repo: dict = {}
    for record in records:
        by_repo[record["repo"]] = by_repo.get(record["repo"], 0) + 1
    print(f"wrote {len(records)} python cases across {len(by_repo)} repos to {OUT.name}")
    print("first repos:", list(by_repo)[:6])


if __name__ == "__main__":
    main()
