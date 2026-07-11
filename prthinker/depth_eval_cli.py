"""CLI subcommand comparing full vs adaptive review depth on a diff corpus.

``depth-eval`` runs every diff in a local corpus twice — full step plan,
then adaptive — through two independently built pipelines, and renders the
:mod:`prthinker.depth_eval` comparison as a markdown report. Backend and
review flags come from the shared common parser, like every review
subcommand.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from collections.abc import Callable
from pathlib import Path

from prthinker.backends import create_backend
from prthinker.cli_io import emit_text
from prthinker.cli_review import _build_config, _build_retriever
from prthinker.depth_eval import (
    CountingBackend,
    PipelineProbe,
    format_markdown,
    run_depth_comparison,
)
from prthinker.pipeline import CoTPipeline, PerFileReviewOptions
from prthinker.rag import RemoteRAGRetriever
from prthinker.rules import load_rules_dir
from prthinker.step_planner import STEP_PLAN_ADAPTIVE, STEP_PLAN_FULL

log = logging.getLogger("prthinker")

_DIFF_SUFFIXES = frozenset({".diff", ".patch"})


def add_parser(sub, common: argparse.ArgumentParser) -> None:
    """Register the ``depth-eval`` subcommand on the shared parser."""
    parser = sub.add_parser(
        "depth-eval",
        parents=[common],
        help="Run a diff corpus at full and adaptive review depth and "
        "report the finding-quality delta next to the model-call and "
        "token savings.",
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--diffs-dir",
        type=Path,
        default=None,
        help="Directory of *.diff / *.patch files (one unified diff each).",
    )
    source.add_argument(
        "--diffs-jsonl",
        type=Path,
        default=None,
        help='JSONL corpus with one {"diff": ...} object per line.',
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Write the markdown report here (default: stdout).",
    )
    parser.add_argument(
        "--max-diffs",
        type=int,
        default=0,
        help="Cap the number of diffs compared (0 = no cap).",
    )


def _load_diffs_dir(diffs_dir: Path) -> list[str]:
    """Read every *.diff / *.patch file in the directory, sorted by name."""
    if not diffs_dir.is_dir():
        raise FileNotFoundError(f"--diffs-dir {diffs_dir} is not a directory")
    paths = sorted(
        path
        for path in diffs_dir.iterdir()
        if path.is_file() and path.suffix.lower() in _DIFF_SUFFIXES
    )
    return [path.read_text(encoding="utf-8") for path in paths]


def _load_diffs_jsonl(path: Path) -> list[str]:
    """Read one diff per JSONL line; reject rows without a 'diff' string."""
    diffs: list[str] = []
    with path.open(encoding="utf-8") as handle:
        for number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            record = json.loads(line)
            diff = record.get("diff") if isinstance(record, dict) else None
            if not isinstance(diff, str) or not diff:
                raise ValueError(
                    f"{path}:{number}: expected a non-empty 'diff' string field"
                )
            diffs.append(diff)
    return diffs


def load_diffs(
    diffs_dir: Path | None,
    diffs_jsonl: Path | None,
    max_diffs: int = 0,
) -> list[str]:
    """Load the diff corpus from whichever source was given, capped."""
    if diffs_dir is not None:
        diffs = _load_diffs_dir(diffs_dir)
    elif diffs_jsonl is not None:
        diffs = _load_diffs_jsonl(diffs_jsonl)
    else:
        raise ValueError("one of --diffs-dir / --diffs-jsonl is required")
    if max_diffs > 0:
        return diffs[:max_diffs]
    return diffs


def _pipeline_factory(
    args: argparse.Namespace,
) -> Callable[[str], PipelineProbe]:
    """Build the per-mode pipeline factory from the parsed backend flags."""
    config = _build_config(args)
    extra_rules = tuple(load_rules_dir(args.rules_dir))

    def build(_mode: str) -> PipelineProbe:
        backend = CountingBackend(create_backend(config))
        retriever = _build_retriever(args, config)

        def close() -> None:
            backend.close()
            if isinstance(retriever, RemoteRAGRetriever):
                retriever.close()

        pipeline = CoTPipeline(
            backend=backend,
            retriever=retriever,
            steps=config.steps,
            max_new_tokens=config.max_new_tokens,
            extra_rules=extra_rules,
        )
        return PipelineProbe(
            pipeline=pipeline, usage_snapshot=backend.snapshot, close=close
        )

    return build


def command(
    args: argparse.Namespace,
    pipeline_factory: Callable[[str], PipelineProbe] | None = None,
) -> int:
    """CLI entry point for ``depth-eval``.

    ``pipeline_factory`` is injectable for tests; when omitted it is built
    from the parsed backend flags.
    """
    try:
        diffs = load_diffs(args.diffs_dir, args.diffs_jsonl, max_diffs=args.max_diffs)
    except (FileNotFoundError, ValueError) as exc:
        sys.stderr.write(f"depth-eval: {exc}\n")
        return 2
    if not diffs:
        sys.stderr.write("depth-eval: no diffs found in the given source\n")
        return 2
    log.info("depth-eval: comparing %d diff(s)", len(diffs))
    factory = (
        pipeline_factory if pipeline_factory is not None else _pipeline_factory(args)
    )
    report = run_depth_comparison(
        factory,
        diffs,
        PerFileReviewOptions(inline_review=True, step_plan=STEP_PLAN_FULL),
        PerFileReviewOptions(inline_review=True, step_plan=STEP_PLAN_ADAPTIVE),
    )
    emit_text(format_markdown(report), args.out)
    return 0


__all__ = ["add_parser", "command", "load_diffs"]
