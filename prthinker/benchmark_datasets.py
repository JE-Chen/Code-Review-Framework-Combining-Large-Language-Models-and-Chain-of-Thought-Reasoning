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


def _context_ids(value: Any) -> list[str]:
    """Normalize ContextBench's serialized context records to file/symbol IDs."""
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            return [value] if value else []
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in value:
        identifier = item.get("file") or item.get("symbol") if isinstance(item, dict) else item
        if identifier and str(identifier) not in result:
            result.append(str(identifier))
    return result


def canonicalize(row: dict[str, Any], *, index: int, dataset: str) -> dict[str, Any]:
    """Convert supported public code-review datasets to one schema."""
    case_id = str(_first(row, ("case_id", "instance_id", "id", "pr_id"), index))
    repository = str(_first(row, ("repository", "repo", "repo_name", "project")))
    issue = str(_first(row, ("issue.body", "issue", "issue_text", "description")))
    title = str(_first(row, ("title", "pr_title", "issue.title")))
    diff = str(_first(row, ("diff", "patch", "pr_diff", "code_change")))
    task = str(
        _first(
            row,
            ("task", "question", "query", "review_question", "problem_statement"),
        )
    )
    choices = _first(row, ("choices", "options", "answers"), [])
    answer = _first(row, ("answer", "label", "correct_answer"), None)
    gold_context = _first(
        row, ("gold_context", "gold_contexts", "relevant_context", "gold_files"), []
    )
    retrieval_dataset = dataset in {"contextbench", "core-bench"}
    if retrieval_dataset:
        gold_context = _context_ids(gold_context)
    if not diff and not (retrieval_dataset and task):
        raise ValueError(f"case {case_id!r} has no diff/patch field")
    if dataset == "codereviewqa":
        prompt = f"Answer this code-review comprehension question with only the selected choice identifier.\n\n{task}\n\nChoices:\n{json.dumps(choices, ensure_ascii=False)}\n\nChange:\n{diff}"
    elif retrieval_dataset:
        prompt = f"Locate the minimal repository context needed to address this task. Return JSON with a retrieved array of file or symbol IDs.\n\nRepository: {repository}\nTask: {task}"
    else:
        prompt = (
            "Review the pull-request change below. Report only actionable findings "
            "introduced by the change, with file and line evidence.\n\n"
            f"Repository: {repository or 'unknown'}\nTitle: {title or 'unknown'}\n"
            f"Issue context:\n{issue or 'not provided'}\n\nPull-request diff:\n{diff}"
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
            "answer": answer,
            "gold_context": gold_context,
            "task": task,
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
        choices=(
            "codefuse-cr-bench",
            "swe-prbench",
            "contextcrbench",
            "swrbench",
            "c-crab",
            "codereviewqa",
            "contextbench",
            "core-bench",
        ),
    )
    args = parser.parse_args(argv)
    count = convert_dataset(args.source, args.target, dataset=args.dataset)
    print(f"converted {count} cases to {args.target}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
