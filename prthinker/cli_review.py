"""Review-file / review-pr command handlers and review execution."""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from prthinker.backends import create_backend
from prthinker.backends.remote import RemotePipelineClient
from prthinker.config import (
    SUMMARY_MARKER,
    BackendKind,
    Config,
)
from prthinker.cli_review_helpers import (
    BACKEND_CONFIG_BUILDERS,
    apply_arbitration,
    build_cache_telemetry,
    build_dialogue_block,
    build_platform_adapter,
)

# The publish flow below calls these helpers; importing them here also
# keeps them reachable as ``prthinker.cli_review.<name>``.
from prthinker.cli_review_emit import (
    _append_api_impact,
    _append_report_links,
    _append_review_footer,
    _build_preliminary_overview,
    _close_review_gate,
    _emit_review_artifacts,
    _extra_sections,
    _gate_inputs,
    _gate_line,
    _impact_note,
    _inline_post_breakdown,
    _join_overview,
    _maybe_set_labels,
    _maybe_update_pr_body,
    _maybe_write_job_summary,
    _postprocess_findings,
    _pr_files_url,
    _review_progress,
    _submit_inline_review,
)

# Not called in this module — re-exported on its own statement (so the
# suppressions sit on the reported line) because the test-suite imports it
# via ``prthinker.cli_review``.
from prthinker.cli_review_emit import _report_links_footer  # noqa: F401  # pylint: disable=unused-import

# ``_maybe_autofix`` / ``_maybe_file_issues`` are dispatched from
# ``_publish_review_result`` below; importing them here also keeps them
# reachable as ``prthinker.cli_review.<name>``.
from prthinker.cli_review_autofix import _maybe_autofix
from prthinker.cli_review_issues import _maybe_file_issues

# Re-exported for the test-suite, which drives them via
# ``prthinker.cli_review``; not called directly in this module.
from prthinker.cli_review_autofix import (  # noqa: F401  # pylint: disable=unused-import
    _collect_auto_fix_findings,
    _maybe_open_auto_fix_mr,
    _maybe_open_auto_fix_pr,
    _open_auto_fix_pr_and_report,
    _report_auto_fix_outcome,
    _resolve_auto_fix_base_branch,
    _resolve_mr_base_branch,
)

# ``_synthesize_overall_summary`` is imported by ``cli_commands`` (the
# aggregate job) via ``prthinker.cli_review``; the helpers ride along so the
# ``prthinker.cli_review.<name>`` path keeps resolving for every moved symbol.
from prthinker.cli_review_overall_summary import (  # noqa: F401  # pylint: disable=unused-import
    _best_effort_cancel_ask_job,
    _build_overall_summary_prompt,
    _collect_overall_summary_inputs,
    _poll_overall_summary,
    _synthesize_overall_summary,
)
from prthinker.ci_signals import format_signals_block
from prthinker.diff import parse_unified_diff
from prthinker.step_planner import TIER_SKIP, classify_depth
from prthinker.formatters import (
    CommentOptions,
    format_pr_comment,
    format_pr_comment_pages,
)
from prthinker import pr_summary
from prthinker.cli_io import write_stdout
from prthinker.incremental_save import (
    IncrementalReviewWriter,
    ReviewMeta,
)
from prthinker.pipeline import (
    CoTPipeline,
    FileReviewResult,
    PerFileReviewOptions,
    ReviewResult,
)
from prthinker.repo_retrieval import RepoContextRetriever
from prthinker.repo_retrieval_factory import create_repo_retriever
from prthinker.review_presets import apply_review_preset
from prthinker.trajectory import TrajectorySink
from prthinker.rag import (
    FaissRAGRetriever,
    NoOpRetriever,
    RAGRetriever,
    RemoteRAGRetriever,
)
from prthinker.review_cache import ReviewCache
from prthinker.rules import load_rules_dir
from prthinker.schemas import InlineFinding, ReviewRequest

log = logging.getLogger("prthinker")


def _build_config(args: argparse.Namespace) -> Config:
    if args.use_remote_pipeline and args.backend != BackendKind.REMOTE.value:
        log.info("--use-remote-pipeline forces --backend remote")
        args.backend = BackendKind.REMOTE.value

    backend = BackendKind(args.backend)
    sub_configs: dict[str, object] = {
        "local": None,
        "remote": None,
        "openai": None,
        "anthropic": None,
        "gemini": None,
        "cohere": None,
        "mistral": None,
        "claude_cli": None,
        "codex_cli": None,
    }
    builder = BACKEND_CONFIG_BUILDERS.get(backend)
    if builder is not None:
        field, cfg = builder(args)
        sub_configs[field] = cfg

    steps = tuple(s.strip() for s in args.steps.split(",") if s.strip())
    cache_cfg, telemetry_cfg = build_cache_telemetry(args)

    return Config(
        backend=backend,
        local=sub_configs["local"],
        remote=sub_configs["remote"],
        openai=sub_configs["openai"],
        anthropic=sub_configs["anthropic"],
        gemini=sub_configs["gemini"],
        cohere=sub_configs["cohere"],
        mistral=sub_configs["mistral"],
        claude_cli=sub_configs["claude_cli"],
        codex_cli=sub_configs["codex_cli"],
        rag_enabled=not args.no_rag,
        rag_threshold=args.rag_threshold,
        max_new_tokens=args.max_new_tokens,
        steps=steps,
        step_plan=getattr(args, "step_plan", "full") or "full",
        cache=cache_cfg,
        telemetry=telemetry_cfg,
    )


# Remote calls keep the historical default: the inference server pins the
# qwen-era embedding index, whose calibrated cutoff is 0.7. The local FAISS
# retriever instead resolves None to the active embedding model's value.
_WIRE_DEFAULT_RAG_THRESHOLD = 0.7


def _wire_rag_threshold(config: Config) -> float:
    if config.rag_threshold is None:
        return _WIRE_DEFAULT_RAG_THRESHOLD
    return config.rag_threshold


def _build_retriever(args: argparse.Namespace, config: Config) -> RAGRetriever:
    if not config.rag_enabled:
        return NoOpRetriever()
    if args.remote_rag:
        if not args.remote_url:
            raise SystemExit("--remote-rag needs --remote-url")
        return RemoteRAGRetriever(
            url=args.remote_url,
            threshold=_wire_rag_threshold(config),
            timeout_seconds=args.remote_timeout,
            api_key=args.remote_api_key,
        )
    return FaissRAGRetriever(threshold=config.rag_threshold)


_KEEP_RATIO_STRATEGIES = frozenset({"lexical", "structural", "graph", "query_rewrite"})


def _repo_context_options(args: argparse.Namespace, backend: object) -> dict:
    """Translate repo-context CLI flags into factory kwargs for one strategy."""
    strategy = getattr(args, "repo_context_strategy", "none") or "none"
    builders = {
        "semantic": _semantic_context_options,
        "rerank": _rerank_context_options,
        "block_rerank": _block_rerank_context_options,
        "iterative": _iterative_context_options,
        "hypothesis": _hypothesis_context_options,
    }
    builder = builders.get(strategy, _default_context_options)
    return builder(args, backend)


def _hypothesis_context_options(args: argparse.Namespace, backend: object) -> dict:
    """Build factory kwargs for the propose-verify localization strategy."""
    return {
        "backend": backend,
        "max_rounds": max(1, int(getattr(args, "repo_context_rounds", 3) or 3)),
    }


def _context_top_k(args: argparse.Namespace) -> int:
    """Clamp the repo-context top-k flag to a positive int."""
    return max(1, int(getattr(args, "repo_context_top_k", 10) or 10))


def _context_votes(args: argparse.Namespace) -> int:
    """Clamp the repo-context self-consistency vote count to a positive int."""
    return max(1, int(getattr(args, "repo_context_votes", 1) or 1))


def _context_block_candidates(args: argparse.Namespace) -> int:
    """Clamp the repo-context block-candidate count to a positive int."""
    return max(1, int(getattr(args, "repo_context_block_candidates", 6) or 6))


def _default_context_options(args: argparse.Namespace, _backend: object) -> dict:
    """Build top-k kwargs, with keep-ratio for the lexical-family strategies."""
    strategy = getattr(args, "repo_context_strategy", "none") or "none"
    keep_ratio = float(getattr(args, "repo_context_keep_ratio", 0) or 0)
    options: dict = {"top_k": _context_top_k(args)}
    if strategy in _KEEP_RATIO_STRATEGIES and keep_ratio > 0:
        options["keep_ratio"] = keep_ratio
    return options


def _semantic_context_options(args: argparse.Namespace, _backend: object) -> dict:
    """Build factory kwargs for the semantic strategy."""
    return {"top_k": _context_top_k(args)}


def _rerank_context_options(args: argparse.Namespace, backend: object) -> dict:
    """Build factory kwargs for the model-in-the-loop rerank strategy."""
    return {"backend": backend, "votes": _context_votes(args)}


def _block_rerank_context_options(args: argparse.Namespace, backend: object) -> dict:
    """Build factory kwargs for the block-level rerank strategy."""
    return {
        "backend": backend,
        "block_candidates": _context_block_candidates(args),
        "focus_lines": _positive_or_none(
            getattr(args, "repo_context_focus_lines", 0)
        ),
        "votes": _context_votes(args),
    }


def _iterative_context_options(args: argparse.Namespace, backend: object) -> dict:
    """Build factory kwargs for the iterative repo-context strategy."""
    return {
        "backend": backend,
        "rounds": max(1, int(getattr(args, "repo_context_rounds", 3) or 3)),
        "block_candidates": _context_block_candidates(args),
        "focus_lines": _positive_or_none(
            getattr(args, "repo_context_focus_lines", 0)
        ),
    }


def _positive_or_none(value: object) -> int | None:
    """Return a positive int or None for optional line-window settings."""
    number = int(value or 0)
    return number if number > 0 else None


def _build_repo_context(
    args: argparse.Namespace, backend: object
) -> tuple[RepoContextRetriever | None, Path | None]:
    """Build optional cross-file repository context retrieval for local reviews."""
    strategy = getattr(args, "repo_context_strategy", "none") or "none"
    workdir = Path(getattr(args, "repo_context_workdir", ".") or ".")
    if strategy == "none":
        return None, None
    retriever = create_repo_retriever(
        strategy, **_repo_context_options(args, backend)
    )
    return retriever, workdir


def _read_stdin_or_file(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def _serialize_partial_review(result: ReviewResult) -> dict:
    """Pack a ReviewResult into a JSON-safe dict for the aggregate job.

    Only the fields the aggregate step actually merges are kept —
    inline_findings, per-file findings + verdict, and step_outputs.
    Fancy add-ons (counterfactuals, persona reviews, api_drift) are
    out of scope here; they can be added when the matrix workflow
    exercises them.
    """
    return {
        "code_diff": result.code_diff,
        "rag_docs": list(result.rag_docs),
        "step_outputs": dict(result.step_outputs),
        "inline_findings": [f.model_dump() for f in result.inline_findings],
        "per_file": [
            {
                "path": fr.path,
                "rag_docs": list(fr.rag_docs),
                "step_outputs": dict(fr.step_outputs),
                "inline_findings": [f.model_dump() for f in fr.inline_findings],
                "verdict": fr.verdict.model_dump() if fr.verdict else None,
                "is_binary": fr.is_binary,
                "is_deleted": fr.is_deleted,
            }
            for fr in result.per_file
        ],
    }


def _deserialize_partial_review(data: dict) -> ReviewResult:
    """Reconstruct a ReviewResult from the dict produced above."""
    from prthinker.schemas import JudgeVerdict

    inline_findings = [
        InlineFinding.model_validate(f) for f in data.get("inline_findings", [])
    ]
    per_file: list[FileReviewResult] = []
    for fr in data.get("per_file", []):
        verdict_dict = fr.get("verdict")
        per_file.append(
            FileReviewResult(
                path=fr["path"],
                rag_docs=list(fr.get("rag_docs", [])),
                step_outputs=dict(fr.get("step_outputs", {})),
                inline_findings=[
                    InlineFinding.model_validate(f)
                    for f in fr.get("inline_findings", [])
                ],
                verdict=(
                    JudgeVerdict.model_validate(verdict_dict) if verdict_dict else None
                ),
                is_binary=fr.get("is_binary", False),
                is_deleted=fr.get("is_deleted", False),
            )
        )
    return ReviewResult(
        code_diff=data.get("code_diff", ""),
        rag_docs=list(data.get("rag_docs", [])),
        step_outputs=dict(data.get("step_outputs", {})),
        inline_findings=inline_findings,
        per_file=per_file,
    )


def _apply_target_file_filter(files: list, args: argparse.Namespace) -> list:
    """Keep only the path named by --target-file, or all files when unset."""
    target = (getattr(args, "target_file", "") or "").strip()
    if not target:
        return files
    return [fd for fd in files if fd.path == target]


def _apply_exclude_globs_filter(files: list, args: argparse.Namespace) -> list:
    """Drop files matching any comma-separated --exclude-globs pattern."""
    import fnmatch

    excludes_raw = (getattr(args, "exclude_globs", "") or "").strip()
    patterns = [p.strip() for p in excludes_raw.split(",") if p.strip()]
    if not patterns:
        return files
    return [
        fd for fd in files if not any(fnmatch.fnmatch(fd.path, p) for p in patterns)
    ]


def _filter_per_file_targets(files: list, args: argparse.Namespace) -> list:
    """Apply --target-file / --exclude-globs to the parsed file list.

    Lets a CI matrix runner pick a single path (--target-file) so per-file
    review can be sharded across jobs, and lets the caller skip noisy paths
    (--exclude-globs) so generated data / IDE config doesn't waste model
    capacity. Both filters are no-ops when their args are empty.
    """
    files = _apply_target_file_filter(files, args)
    return _apply_exclude_globs_filter(files, args)


def _server_review_request(
    config: Config, code_diff: str, extra_rules: list, file_path: str | None = None
) -> ReviewRequest:
    """Build a ReviewRequest for one server-side review call."""
    return ReviewRequest(
        code_diff=code_diff,
        file_path=file_path,
        rag_enabled=config.rag_enabled,
        rag_threshold=_wire_rag_threshold(config),
        max_new_tokens=config.max_new_tokens,
        steps=list(config.steps) or None,
        extra_rules=extra_rules,
        step_plan=config.step_plan,
    )


def _review_whole_diff_via_server(
    client: RemotePipelineClient, config: Config, diff_text: str, extra_rules: list
) -> ReviewResult:
    """Run a single whole-diff review against the remote pipeline server."""
    response = client.review(_server_review_request(config, diff_text, extra_rules))
    return ReviewResult(
        code_diff=diff_text,
        rag_docs=response.rag_docs,
        step_outputs=response.step_map(),
        inline_findings=list(response.inline_findings),
    )


def _review_one_file_via_server(
    client: RemotePipelineClient, config: Config, fd: object, extra_rules: list
) -> tuple[FileReviewResult, dict[str, str]]:
    """Review one parsed file via the server; return its result + namespaced steps."""
    response = client.review(
        _server_review_request(config, fd.raw, extra_rules, file_path=fd.path)
    )
    step_map = response.step_map()
    namespaced = {f"{fd.path}::{name}": out for name, out in step_map.items()}
    findings = list(response.inline_findings)
    file_result = FileReviewResult(
        path=fd.path,
        rag_docs=response.rag_docs,
        step_outputs=step_map,
        inline_findings=findings,
        is_binary=fd.is_binary,
        is_deleted=fd.is_deleted,
    )
    return file_result, namespaced


def _review_per_file_via_server(
    client: RemotePipelineClient,
    args: argparse.Namespace,
    config: Config,
    diff_text: str,
    extra_rules: list,
) -> ReviewResult:
    """Run a per-file review against the remote pipeline server."""
    files = _filter_per_file_targets(parse_unified_diff(diff_text), args)
    all_findings: list[InlineFinding] = []
    aggregated_steps: dict[str, str] = {}
    per_file: list[FileReviewResult] = []
    for fd in files:
        if fd.is_binary or fd.is_deleted:
            continue
        if config.step_plan == "adaptive" and classify_depth(fd) == TIER_SKIP:
            # Generated / whitespace-only file: skip the server round-trip
            # entirely, but keep the file visible in the summary.
            log.info("step_plan: %s tier=skip — no server call", fd.path)
            per_file.append(
                FileReviewResult(
                    path=fd.path,
                    rag_docs=[],
                    step_outputs={"step_plan": TIER_SKIP},
                    inline_findings=[],
                )
            )
            continue
        file_result, namespaced = _review_one_file_via_server(
            client, config, fd, extra_rules
        )
        aggregated_steps.update(namespaced)
        all_findings.extend(file_result.inline_findings)
        per_file.append(file_result)
    return ReviewResult(
        code_diff=diff_text,
        rag_docs=[],
        step_outputs=aggregated_steps,
        inline_findings=all_findings,
        per_file=per_file,
    )


def _review_via_server(
    args: argparse.Namespace, config: Config, diff_text: str
) -> ReviewResult:
    if config.remote is None:
        raise ValueError("remote backend config required for server review")
    extra_rules = load_rules_dir(args.rules_dir)
    client = RemotePipelineClient(config.remote)
    try:
        if not args.per_file:
            return _review_whole_diff_via_server(client, config, diff_text, extra_rules)
        return _review_per_file_via_server(client, args, config, diff_text, extra_rules)
    finally:
        client.close()


def _review_via_pipeline(
    args: argparse.Namespace,
    config: Config,
    diff_text: str,
    output_dir: Path | None = None,
    *,
    dialogue_block: str = "",
) -> ReviewResult:
    backend = create_backend(config)
    retriever = _build_retriever(args, config)
    repo_retriever, repo_workdir = _build_repo_context(args, backend)
    extra_rules = load_rules_dir(args.rules_dir)
    pipeline = CoTPipeline(
        backend=backend,
        retriever=retriever,
        steps=config.steps,
        max_new_tokens=config.max_new_tokens,
        extra_rules=tuple(extra_rules),
        stream=bool(getattr(args, "stream", False)),
        step_dependencies=json.loads(args.step_dag)
        if getattr(args, "step_dag", "")
        else None,
        trajectory_sink=TrajectorySink(
            Path(args.trajectory_out), getattr(args, "head_sha", "") or "local"
        )
        if getattr(args, "trajectory_out", "")
        else None,
        repo_retriever=repo_retriever,
        repo_workdir=repo_workdir,
    )
    try:
        if args.per_file:
            return _run_per_file_review(
                pipeline, args, diff_text, output_dir, dialogue_block
            )
        return pipeline.run(diff_text, output_dir=output_dir)
    finally:
        backend.close()
        if isinstance(retriever, RemoteRAGRetriever):
            retriever.close()


def _build_review_cache(
    args: argparse.Namespace,
) -> tuple[ReviewCache | None, str, int]:
    """Resolve the diff-since-last review cache + repo / PR number from args."""
    if not (getattr(args, "diff_since_last", False) and args.inline_review):
        return None, "", 0
    return (
        ReviewCache(Path(args.diff_cache_path)),
        getattr(args, "repo", "") or "",
        int(getattr(args, "pr_number", 0) or 0),
    )


def _csv_tuple(args: argparse.Namespace, attr: str) -> tuple[str, ...]:
    """Split a comma-separated CLI string arg into a tuple of trimmed tokens."""
    raw = getattr(args, attr, "") or ""
    return tuple(s.strip() for s in raw.split(",") if s.strip())


def _flag(args: argparse.Namespace, name: str) -> bool:
    """True when the boolean CLI flag ``name`` is set on ``args``."""
    return bool(getattr(args, name, False))


def _collect_core_kwargs(args: argparse.Namespace) -> dict:
    """Collect the always-present per-file review toggles."""
    return {
        "inline_review": args.inline_review,
        "judge": _flag(args, "judge"),
        "self_correct": _flag(args, "self_correct"),
        "counterfactual": _flag(args, "counterfactual"),
        "walkthrough": _flag(args, "walkthrough"),
        "provenance": _flag(args, "provenance"),
        "max_findings_per_file": args.max_findings_per_file,
        "step_plan": getattr(args, "step_plan", "full") or "full",
    }


def _collect_verify_kwargs(args: argparse.Namespace) -> dict:
    """Collect the suggestion-verification per-file toggles."""
    return {
        "verify_suggestions": _flag(args, "verify_suggestions"),
        "verify_workdir": getattr(args, "verify_workdir", None),
        "verify_cmd": getattr(args, "verify_cmd", "") or "",
        "verify_timeout": float(getattr(args, "verify_timeout", 60.0) or 60.0),
    }


def _collect_classify_kwargs(args: argparse.Namespace) -> dict:
    """Collect the PR-classification / consistency per-file toggles."""
    return {
        "api_consistency_check": _flag(args, "api_consistency"),
        "pr_classify": _flag(args, "pr_classify"),
        "pr_title": getattr(args, "pr_title", "") or "",
        "pr_body": getattr(args, "pr_body", "") or "",
        "reproducibility_check": _flag(args, "reproducibility_check"),
        "dep_upgrade_check": _flag(args, "dep_upgrade_check"),
    }


def _collect_risk_kwargs(args: argparse.Namespace) -> dict:
    """Collect the persona / risk / entropy per-file toggles."""
    return {
        "persona_set": _csv_tuple(args, "personas"),
        "risk_weighted": _flag(args, "risk_weighted"),
        "risk_workdir": getattr(args, "risk_workdir", None),
        "diff_entropy_check": _flag(args, "diff_entropy"),
        "review_modes": _csv_tuple(args, "review_modes"),
        "parallelism": max(1, int(getattr(args, "parallelism", 1))),
    }


def _per_file_kwargs(args: argparse.Namespace) -> dict:
    """Collect the optional per-file review toggles from CLI args."""
    return {
        **_collect_core_kwargs(args),
        **_collect_verify_kwargs(args),
        **_collect_classify_kwargs(args),
        **_collect_risk_kwargs(args),
    }


def _run_per_file_review(
    pipeline: CoTPipeline,
    args: argparse.Namespace,
    diff_text: str,
    output_dir: Path | None,
    dialogue_block: str,
) -> ReviewResult:
    """Drive ``pipeline.run_per_file`` with cache + incremental-save wiring."""
    review_cache_obj, cache_repo, cache_pr_number = _build_review_cache(args)
    incremental_writer = _build_incremental_writer(args)
    on_file_done = (
        incremental_writer.write_file_result if incremental_writer is not None else None
    )
    options = PerFileReviewOptions(
        output_dir=output_dir,
        dialogue_block=dialogue_block,
        review_cache=review_cache_obj,
        cache_repo=cache_repo,
        cache_pr_number=cache_pr_number,
        on_file_done=on_file_done,
        **_per_file_kwargs(args),
    )
    result = pipeline.run_per_file(diff_text, options)
    if incremental_writer is not None:
        incremental_writer.write_final(result)
    return result


def _build_incremental_writer(
    args: argparse.Namespace,
) -> IncrementalReviewWriter | None:
    """Construct an IncrementalReviewWriter from args (or return None)."""
    path = (getattr(args, "incremental_save_dir", "") or "").strip()
    if not path:
        return None
    meta = ReviewMeta(
        repo=(getattr(args, "repo", "") or "").strip(),
        pr_number=int(getattr(args, "pr_number", 0) or 0),
        head_sha=(getattr(args, "head_sha", "") or "").strip(),
        started_at=_iso_now(),
    )
    return IncrementalReviewWriter(Path(path), meta=meta)


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _run_review(
    args: argparse.Namespace,
    config: Config,
    diff_text: str,
    output_dir: Path | None = None,
    *,
    dialogue_block: str = "",
) -> ReviewResult:
    if getattr(args, "redact_secrets", False):
        from prthinker.redaction import redact

        diff_text, report = redact(diff_text)
        if report:
            # nosemgrep: python.lang.security.audit.logging.logger-credential-leak.python-logger-credential-disclosure
            # report.summary() is an aggregate count of redacted patterns,
            # never the secret values themselves.
            log.warning(
                "Redaction summary for diff before backend call: %s",
                report.summary(),
            )
    if args.use_remote_pipeline:
        result = _review_via_server(args, config, diff_text)
    else:
        result = _review_via_pipeline(
            args,
            config,
            diff_text,
            output_dir=output_dir,
            dialogue_block=dialogue_block,
        )
    apply_arbitration(args, result)
    return result


def _cmd_review_file(args: argparse.Namespace) -> int:
    apply_review_preset(args)
    config = _build_config(args)
    code = _read_stdin_or_file(args.path)
    result = _run_review(args, config, code, output_dir=args.output_dir)
    write_stdout(format_pr_comment(result, marker=SUMMARY_MARKER))
    if result.inline_findings:
        write_stdout(f"\n[{len(result.inline_findings)} inline findings parsed]\n")
    return 0


def _validate_pr_args(args: argparse.Namespace) -> None:
    """Fail fast on the inputs ``review-pr`` cannot run without."""
    if not args.repo:
        raise SystemExit("--repo or $GITHUB_REPOSITORY / $CI_PROJECT_PATH is required")
    if not args.pr_number:
        raise SystemExit("--pr-number is required")
    if not args.github_token:
        raise SystemExit("--github-token / $GITHUB_TOKEN / $GITLAB_TOKEN is required")


def _maybe_fetch_pr_meta(args: argparse.Namespace, adapter: object) -> None:
    """Populate ``args.pr_title`` / ``args.pr_body`` for the classifier."""
    if not getattr(args, "pr_classify", False):
        return
    try:
        pr_title, pr_body = adapter.fetch_pr_meta()
    except Exception as exc:
        log.warning(
            "Could not fetch PR meta for classifier (%s); "
            "classifier will run on diff only",
            exc,
        )
        return
    args.pr_title = pr_title
    args.pr_body = pr_body
    log.info("Fetched PR meta: title=%r body_len=%d", pr_title[:60], len(pr_body))


def _resolve_head_sha(args: argparse.Namespace, adapter: object) -> str | None:
    """Fetch the head SHA only when the gate or CI signals need it."""
    needs = (args.gate_on != "none" and not args.dry_run) or args.include_ci_signals
    return adapter.fetch_head_sha() if needs else None


def _maybe_prepend_ci_signals(
    args: argparse.Namespace,
    diff: str,
    head_sha: str | None,
    adapter: object,
) -> str:
    """Prepend the platform's CI failure signals to the diff when enabled.

    The adapter decides what "CI" means (Actions runs on GitHub,
    pipelines on GitLab); platforms without a CI API return no signals.
    """
    if not (args.include_ci_signals and head_sha is not None):
        return diff
    signals = adapter.fetch_ci_failure_signals(
        head_sha,
        max_jobs=args.ci_signal_max_jobs,
        log_tail_chars=args.ci_signal_tail_chars,
    )
    block = format_signals_block(signals)
    if block:
        diff = block + diff
        log.info("Prepended %d CI failure signal(s) to diff", len(signals))
    return diff


def _open_gate_if_needed(
    args: argparse.Namespace,
    adapter: object,
    head_sha: str | None,
) -> object | None:
    """Open the status gate unless this is a dry-run / partial-output run."""
    skip = (
        args.gate_on == "none"
        or args.dry_run
        or getattr(args, "output_json", "")
        or head_sha is None
    )
    return None if skip else adapter.open_gate(head_sha)


def _close_gate_on_crash(adapter: object, gate_handle: object | None) -> None:
    """Mark the gate failed when the reviewer raises before publishing."""
    if gate_handle is None:
        return
    from prthinker.checks import CheckResult

    adapter.close_gate(
        gate_handle,
        CheckResult(
            conclusion="failure",
            title="Reviewer crashed",
            summary="The CoT reviewer raised an exception. Check workflow logs.",
            error_count=0,
            warning_count=0,
            info_count=0,
        ),
    )


def _emit_dry_run(result: ReviewResult, body: str) -> int:
    """Write the would-be comment to stdout for ``--dry-run``."""
    sys.stdout.write(body)
    if result.inline_findings:
        sys.stdout.write(
            f"\n[would post {len(result.inline_findings)} inline findings]\n"
        )
    return 0


def _emit_partial_json(result: ReviewResult, output_json: str) -> int:
    """Persist a partial ReviewResult for the aggregate job."""
    Path(output_json).parent.mkdir(parents=True, exist_ok=True)
    Path(output_json).write_text(
        json.dumps(_serialize_partial_review(result), indent=2),
        encoding="utf-8",
    )
    log.info(
        "Wrote partial review (files=%d, findings=%d) to %s",
        len(result.per_file),
        len(result.inline_findings),
        output_json,
    )
    return 0


# The PR summary is best-effort, but the comment is worth a few quick
# retries: a transient backend hiccup (a 5xx, a dropped connection, an
# empty reply while the GPU was momentarily contended by an overlapping
# run) otherwise drops the summary silently for the whole push.
_PR_SUMMARY_ATTEMPTS = 3
_PR_SUMMARY_RETRY_BACKOFF_SECONDS = 5.0


def _generate_summary_text(backend: object, prompt: str, max_new_tokens: int) -> str:
    """Generate + clean the summary, retrying transient backend failures.

    Returns the cleaned text, or '' when every attempt fails or yields
    nothing. Retries cover fast failures (network error, 5xx, an empty
    reply); a full-length timeout still consumes its attempt, but the loop
    makes its remaining tries within the calling step's own time budget.
    """
    for attempt in range(1, _PR_SUMMARY_ATTEMPTS + 1):
        try:
            text = pr_summary.clean_summary(backend.generate(prompt, max_new_tokens))
        except Exception as exc:  # noqa: BLE001 — retry any transient failure
            log.warning(
                "PR summary generate attempt %d/%d failed: %s",
                attempt,
                _PR_SUMMARY_ATTEMPTS,
                exc,
            )
            text = ""
        if text:
            return text
        if attempt < _PR_SUMMARY_ATTEMPTS:
            time.sleep(_PR_SUMMARY_RETRY_BACKOFF_SECONDS)
    log.warning("PR summary produced no text after %d attempts", _PR_SUMMARY_ATTEMPTS)
    return ""


def _generate_pr_summary_body(args: argparse.Namespace, adapter: object) -> str:
    """Build the marker-tagged PR-summary comment body, or '' to skip."""
    diff = adapter.fetch_diff()
    if not diff.strip():
        log.warning("Empty diff — skipping PR summary")
        return ""
    if getattr(args, "redact_secrets", False):
        from prthinker.redaction import redact

        diff, _ = redact(diff)
    title, body = adapter.fetch_pr_meta()
    commit_messages = tuple(adapter.fetch_commit_messages())
    config = _build_config(args)
    backend = create_backend(config)
    try:
        prompt = pr_summary.build_prompt(
            diff_text=diff,
            title=title,
            body=body,
            commit_messages=commit_messages,
        )
        text = _generate_summary_text(backend, prompt, config.max_new_tokens)
    finally:
        backend.close()
    if not text:
        return ""
    return pr_summary.render_comment(text, marker=pr_summary.DEFAULT_MARKER)


def _cmd_pr_summary(args: argparse.Namespace) -> int:
    """Generate the Copilot-style PR summary and upsert it as its own comment.

    Runs as a standalone pre-review step (e.g. the enumerate job) so the
    summary lands before the slower per-file review starts. Best-effort: a
    backend or network failure logs a warning and returns 0 so it never
    blocks the review matrix.
    """
    _validate_pr_args(args)
    adapter = build_platform_adapter(args)
    try:
        body = _generate_pr_summary_body(args, adapter)
    except Exception as exc:  # noqa: BLE001 — summary must never block the matrix
        log.warning("PR summary generation failed (%s); skipping", exc)
        return 0
    if not body:
        log.info("No PR summary produced; nothing to post")
        return 0
    if args.dry_run:
        sys.stdout.write(body)
        return 0
    adapter.upsert_marked_comment(body, marker=pr_summary.DEFAULT_MARKER)
    log.info("Posted PR summary comment")
    return 0


def _review_comment_pages(
    args: argparse.Namespace,
    adapter: object,
    result: ReviewResult,
    calibrated: tuple[list[InlineFinding], int] | None = None,
) -> list[str]:
    """Render the review into summary-comment pages plus footers."""
    posted_count, off_diff = _inline_post_breakdown(args, result)
    delta_line, progress_block = _review_progress(args, adapter, result)
    files_url = _pr_files_url(args)
    pages = format_pr_comment_pages(
        result,
        args.marker,
        CommentOptions(
            posted_count=posted_count,
            findings_only=getattr(args, "findings_only", False),
            hide_info=getattr(args, "hide_info", False),
            preliminary=_join_overview(
                _build_preliminary_overview(args, adapter, result),
                _impact_note(args, result),
                progress_block,
            ),
            files_url=files_url,
            delta=delta_line,
            min_confidence=getattr(args, "summary_min_confidence", 0.0),
            table=getattr(args, "summary_table", False),
            gate=_gate_line(args, result, files_url, calibrated),
            off_diff_findings=off_diff,
            extra_sections=_extra_sections(args, result, files_url),
        ),
    )
    _append_report_links(args, pages)
    _append_review_footer(args, result, pages)
    return pages


def _publish_review_result(
    args: argparse.Namespace,
    adapter: object,
    result: ReviewResult,
    gate_handle: object | None,
    platform_kind: object,
) -> int:
    """Post comment + inline review, close the gate, and trigger auto-fix."""
    _postprocess_findings(args, result)
    # Calibrated gate scoring runs per-finding SQLite queries; compute it
    # once here and hand the same tuple to the gate line and the gate close.
    calibrated = _gate_inputs(args, result)
    _emit_review_artifacts(args, result)
    pages = _review_comment_pages(args, adapter, result, calibrated)
    _maybe_write_job_summary(pages[0])
    if getattr(args, "api_impact", False):
        pages[-1] = _append_api_impact(pages[-1], result)
    if args.dry_run:
        return _emit_dry_run(result, "\n\n".join(pages))
    output_json = getattr(args, "output_json", "")
    if output_json:
        return _emit_partial_json(result, output_json)

    comment_ids = adapter.upsert_summary_comments(pages)
    log.info("Posted %d summary comment(s): %s", len(comment_ids), comment_ids)

    _submit_inline_review(args, adapter, result)
    _close_review_gate(args, adapter, result, gate_handle, calibrated)

    _maybe_set_labels(args, adapter, result)
    _maybe_update_pr_body(args, adapter, result)
    _maybe_autofix(args, result, platform_kind, adapter)
    _maybe_file_issues(args, result, platform_kind, adapter)
    return 0


def _cmd_review_pr(args: argparse.Namespace) -> int:
    apply_review_preset(args)
    config = _build_config(args)
    _validate_pr_args(args)

    from prthinker.platforms import PlatformKind

    platform_kind = PlatformKind(args.platform)
    adapter = build_platform_adapter(args)

    log.info(
        "Fetching diff for %s %s#%d", platform_kind.value, args.repo, args.pr_number
    )
    diff = adapter.fetch_diff()
    if not diff.strip():
        log.warning("Empty diff — skipping review")
        return 0

    _maybe_fetch_pr_meta(args, adapter)
    head_sha = _resolve_head_sha(args, adapter)
    diff = _maybe_prepend_ci_signals(args, diff, head_sha, adapter)
    gate_handle = _open_gate_if_needed(args, adapter, head_sha)
    dialogue_block = build_dialogue_block(args, adapter)

    try:
        result = _run_review(args, config, diff, dialogue_block=dialogue_block)
    except Exception:
        _close_gate_on_crash(adapter, gate_handle)
        raise

    return _publish_review_result(args, adapter, result, gate_handle, platform_kind)
