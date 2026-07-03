"""Adapters from public PR-review datasets to prthinker's canonical JSONL.

The adapter is deliberately offline: users download a pinned dataset revision,
then this module converts JSON or JSONL without hidden network calls.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable


def _first(row: dict[str, Any], names: tuple[str, ...], default: Any = "") -> Any:
    for name in names:
        value: Any = row
        for part in name.split("."):
            if not isinstance(value, dict) or part not in value:
                value = None
                break
            value = value[part]
        if value not in (None, "", []):
            return value
    return default


def _rows(path: Path) -> Iterable[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".jsonl":
        for line in text.splitlines():
            if line.strip():
                yield json.loads(line)
        return
    payload = json.loads(text)
    if isinstance(payload, dict):
        payload = payload.get("data", payload.get("instances", payload.get("rows")))
    if not isinstance(payload, list):
        raise ValueError("JSON dataset must be a list or contain data/instances/rows")
    yield from payload


def canonicalize(row: dict[str, Any], *, index: int, dataset: str) -> dict[str, Any]:
    """Convert common CodeFuse-CR-Bench/SWE-PRBench exports to one schema."""
    case_id = str(_first(row, ("case_id", "instance_id", "id", "pr_id"), index))
    repository = str(_first(row, ("repository", "repo", "repo_name", "project")))
    issue = str(_first(row, ("issue.body", "issue", "issue_text", "description")))
    title = str(_first(row, ("title", "pr_title", "issue.title")))
    diff = str(_first(row, ("diff", "patch", "pr_diff", "code_change")))
    if not diff:
        raise ValueError(f"case {case_id!r} has no diff/patch field")
    prompt = (
        "Review the pull-request change below. Report only actionable findings "
        "introduced by the change, with file and line evidence.\n\n"
        f"Repository: {repository or 'unknown'}\n"
        f"Title: {title or 'unknown'}\n"
        f"Issue context:\n{issue or 'not provided'}\n\n"
        f"Pull-request diff:\n{diff}"
    )
    ground_truth = _first(
        row,
        ("ground_truth", "review_comments", "human_comments", "comments", "labels"),
        [],
    )
    return {
        "case_id": f"{dataset}:{case_id}",
        "prompt": prompt,
        "metadata": {
            "dataset": dataset,
            "source_case_id": case_id,
            "repository": repository,
            "ground_truth": ground_truth,
        },
    }


def convert_dataset(source: str | Path, target: str | Path, *, dataset: str) -> int:
    """Convert ``source`` into canonical JSONL and return the case count."""
    output = Path(target)
    output.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with output.open("w", encoding="utf-8") as handle:
        for index, row in enumerate(_rows(Path(source)), start=1):
            converted = canonicalize(row, index=index, dataset=dataset)
            handle.write(json.dumps(converted, ensure_ascii=False) + "\n")
            count += 1
    return count


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Convert a PR-review benchmark")
    parser.add_argument("source", help="Pinned local JSON or JSONL dataset")
    parser.add_argument("target", help="Canonical output JSONL")
    parser.add_argument(
        "--dataset",
        required=True,
        choices=("codefuse-cr-bench", "swe-prbench"),
    )
    args = parser.parse_args(argv)
    count = convert_dataset(args.source, args.target, dataset=args.dataset)
    print(f"converted {count} cases to {args.target}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
