"""Command-line interface for prthinker.

Subcommands:
    review-pr    Pull a PR diff from GitHub, run the pipeline, post a comment
                 (and optionally inline-comment review).
    review-file  Run the pipeline against a local file or '-' for stdin.

Backend selection:
    --backend local                     in-process Hugging Face causal-LM
    --backend remote                    the project's own FastAPI server
    --backend openai                    any OpenAI-Chat-Completions endpoint
                                        (OpenAI, Azure, vLLM, Ollama /v1, …)
    --backend anthropic                 Anthropic Messages API

RAG selection:
    --no-rag         skip RAG entirely
    --remote-rag     call /rag instead of loading FAISS locally
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import httpx

from prthinker.backends import create_backend
from prthinker.backends.remote import RemotePipelineClient
from prthinker.cli_parser import (
    _apply_repo_defaults,
    _build_parser,
)
from prthinker.config import (
    AnthropicConfig,
    BackendKind,
    Config,
    GitHubConfig,
    LocalBackendConfig,
    OpenAICompatConfig,
    RemoteBackendConfig,
    env_str,
)
from prthinker.accepted import AcceptedExamplesStore
from prthinker.checks import (
    evaluate_gate,
)
from prthinker.ci_signals import (
    fetch_ci_failure_signals,
    format_signals_block,
)
from prthinker.diff import parse_unified_diff
from prthinker.dismissed import DismissedExamplesStore
from prthinker.formatters import format_pr_comment
from prthinker.harvest import harvest, harvest_accepted
from prthinker.incremental_save import (
    IncrementalReviewWriter,
    ReviewMeta,
)
from prthinker.kg_visualize import build_graph_data, render_html
from prthinker.repo_kg import (
    KnowledgeGraphStore,
    format_kg_block,
    scan_workdir_full,
)
from prthinker.pipeline import (
    CoTPipeline,
    FileReviewResult,
    ReviewResult,
)
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
    local_cfg: LocalBackendConfig | None = None
    remote_cfg: RemoteBackendConfig | None = None
    openai_cfg: OpenAICompatConfig | None = None
    anthropic_cfg: AnthropicConfig | None = None

    if backend is BackendKind.LOCAL:
        local_cfg = LocalBackendConfig(
            model_name=args.model_name,
            lora_path=args.lora_path,
        )
    elif backend is BackendKind.REMOTE:
        if not args.remote_url:
            raise SystemExit(
                "remote backend requires --remote-url or PRTHINKER_REMOTE_URL"
            )
        remote_cfg = RemoteBackendConfig(
            url=args.remote_url,
            timeout_seconds=args.remote_timeout,
            api_key=args.remote_api_key,
        )
    elif backend is BackendKind.OPENAI:
        if not args.openai_api_key:
            raise SystemExit(
                "openai backend requires --openai-api-key or "
                "$PRTHINKER_OPENAI_API_KEY / $OPENAI_API_KEY"
            )
        openai_cfg = OpenAICompatConfig(
            model=args.openai_model,
            api_key=args.openai_api_key,
            base_url=args.openai_base_url,
            organization=args.openai_organization,
            timeout_seconds=args.remote_timeout,
        )
    elif backend is BackendKind.ANTHROPIC:
        if not args.anthropic_api_key:
            raise SystemExit(
                "anthropic backend requires --anthropic-api-key or "
                "$PRTHINKER_ANTHROPIC_API_KEY / $ANTHROPIC_API_KEY"
            )
        anthropic_cfg = AnthropicConfig(
            model=args.anthropic_model,
            api_key=args.anthropic_api_key,
            base_url=args.anthropic_base_url,
            anthropic_version=args.anthropic_version,
            timeout_seconds=args.remote_timeout,
        )

    steps = tuple(s.strip() for s in args.steps.split(",") if s.strip())
    from prthinker.config import CacheConfig, TelemetryConfig

    cache_cfg = CacheConfig(
        enabled=bool(getattr(args, "cache_enabled", False)),
        path=str(getattr(args, "cache_path", ".prthinker/cache.sqlite")),
        ttl_days=(
            None
            if getattr(args, "cache_ttl_days", 7.0) in (None, 0, 0.0)
            else float(getattr(args, "cache_ttl_days", 7.0))
        ),
    )
    telemetry_cfg = TelemetryConfig(
        enabled=bool(getattr(args, "telemetry_enabled", False)),
        path=str(getattr(args, "telemetry_path", ".prthinker/telemetry.sqlite")),
    )

    return Config(
        backend=backend,
        local=local_cfg,
        remote=remote_cfg,
        openai=openai_cfg,
        anthropic=anthropic_cfg,
        rag_enabled=not args.no_rag,
        rag_threshold=args.rag_threshold,
        max_new_tokens=args.max_new_tokens,
        steps=steps,
        cache=cache_cfg,
        telemetry=telemetry_cfg,
    )


def _build_retriever(args: argparse.Namespace, config: Config) -> RAGRetriever:
    if not config.rag_enabled:
        return NoOpRetriever()
    if args.remote_rag:
        if not args.remote_url:
            raise SystemExit("--remote-rag needs --remote-url")
        return RemoteRAGRetriever(
            url=args.remote_url,
            threshold=config.rag_threshold,
            timeout_seconds=args.remote_timeout,
            api_key=args.remote_api_key,
        )
    return FaissRAGRetriever(threshold=config.rag_threshold)


def _read_stdin_or_file(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


# ----------------------------------------------------------------------------
# Server-orchestrated path: call /review per file.
# ----------------------------------------------------------------------------

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
                    JudgeVerdict.model_validate(verdict_dict)
                    if verdict_dict
                    else None
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


_OVERALL_SUMMARY_PER_CALL_TIMEOUT = 30.0
_OVERALL_SUMMARY_POLL_INTERVAL = 5.0
_OVERALL_SUMMARY_DEADLINE_SECONDS = 1800.0
_OVERALL_SUMMARY_MAX_NEW_TOKENS = 16784


def _collect_overall_summary_inputs(per_file: list) -> list[str]:
    """Return the non-empty per-file total summaries, ready for the prompt."""
    summaries: list[str] = []
    for fr in per_file:
        text = (fr.total_summary or "").strip()
        if text:
            summaries.append(f"### {fr.path}\n{text}")
    return summaries


def _build_overall_summary_prompt(summaries: list[str]) -> str:
    return (
        "You are summarising a code-review run. Below are per-file "
        "summaries from a single pull request. Write ONE concise PR-wide "
        "summary in 3-5 sentences. Capture the common themes, the most "
        "important findings, and the residual risk. Do not enumerate the "
        "per-file blocks verbatim.\n\n"
        + "\n\n".join(summaries)
    )


def _best_effort_cancel_ask_job(client: httpx.Client, job_id: str) -> None:
    """Tell the backend to release the GPU; ignore failures by design."""
    try:
        client.post(f"/ask/cancel/{job_id}")
    except httpx.HTTPError as exc:
        log.debug("Cancel for ask job %s failed (ignored): %s", job_id, exc)


def _poll_overall_summary(
    client: httpx.Client, job_id: str, deadline: float
) -> str:
    while True:
        if time.monotonic() >= deadline:
            _best_effort_cancel_ask_job(client, job_id)
            log.warning(
                "Overall summary synthesis exceeded deadline; skipping",
            )
            return ""
        time.sleep(_OVERALL_SUMMARY_POLL_INTERVAL)
        poll = client.get(f"/ask/result/{job_id}")
        poll.raise_for_status()
        payload = poll.json()
        status = payload.get("status")
        if status == "done":
            return (payload.get("result") or "").strip()
        if status == "error":
            log.warning(
                "Overall summary synthesis failed server-side: %s",
                payload.get("error"),
            )
            return ""
        if status == "cancelled":
            log.warning("Overall summary synthesis cancelled server-side")
            return ""


def _synthesize_overall_summary(per_file: list) -> str:
    """Ask the remote backend for a single PR-wide summary.

    Each matrix shard already produced its own per-file
    ``total_summary``; the aggregate needs to roll them up into one
    paragraph that captures the PR's overall shape — common themes,
    the heaviest findings, residual risk — without restating every
    file. Best-effort: a missing backend, a timeout, or any other
    failure logs a warning and returns an empty string so the
    formatter falls back to the per-file blocks alone.
    """
    summaries = _collect_overall_summary_inputs(per_file)
    if len(summaries) < 2:
        return ""

    remote_url = (env_str("PRTHINKER_REMOTE_URL", "") or "").strip()
    if not remote_url:
        return ""

    api_key = (env_str("PRTHINKER_REMOTE_API_KEY", "") or "").strip()
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    deadline = time.monotonic() + _OVERALL_SUMMARY_DEADLINE_SECONDS
    prompt = _build_overall_summary_prompt(summaries)
    try:
        with httpx.Client(
            base_url=remote_url.rstrip("/"),
            timeout=_OVERALL_SUMMARY_PER_CALL_TIMEOUT,
            headers=headers,
        ) as client:
            submit = client.post(
                "/ask/submit",
                json={
                    "prompt": prompt,
                    "max_new_tokens": _OVERALL_SUMMARY_MAX_NEW_TOKENS,
                },
            )
            submit.raise_for_status()
            job_id = submit.json()["job_id"]
            return _poll_overall_summary(client, job_id, deadline)
    except (httpx.HTTPError, KeyError, ValueError) as exc:
        log.warning("Overall summary synthesis failed (%s); skipping", exc)
        return ""


def _filter_per_file_targets(
    files: list, args: argparse.Namespace
) -> list:
    """Apply --target-file / --exclude-globs to the parsed file list.

    Lets a CI matrix runner pick a single path (--target-file) so per-file
    review can be sharded across jobs, and lets the caller skip noisy paths
    (--exclude-globs) so generated data / IDE config doesn't waste model
    capacity. Both filters are no-ops when their args are empty.
    """
    import fnmatch

    target = (getattr(args, "target_file", "") or "").strip()
    if target:
        files = [fd for fd in files if fd.path == target]

    excludes_raw = (getattr(args, "exclude_globs", "") or "").strip()
    if excludes_raw:
        patterns = [p.strip() for p in excludes_raw.split(",") if p.strip()]
        if patterns:
            def _matches_any(path: str) -> bool:
                return any(fnmatch.fnmatch(path, p) for p in patterns)
            files = [fd for fd in files if not _matches_any(fd.path)]

    return files


def _review_via_server(
    args: argparse.Namespace, config: Config, diff_text: str
) -> ReviewResult:
    assert config.remote is not None
    extra_rules = load_rules_dir(args.rules_dir)
    client = RemotePipelineClient(config.remote)
    try:
        if not args.per_file:
            response = client.review(
                ReviewRequest(
                    code_diff=diff_text,
                    rag_enabled=config.rag_enabled,
                    rag_threshold=config.rag_threshold,
                    max_new_tokens=config.max_new_tokens,
                    steps=list(config.steps) or None,
                    extra_rules=extra_rules,
                )
            )
            return ReviewResult(
                code_diff=diff_text,
                rag_docs=response.rag_docs,
                step_outputs=response.step_map(),
                inline_findings=list(response.inline_findings),
            )

        files = parse_unified_diff(diff_text)
        files = _filter_per_file_targets(files, args)
        all_findings: list[InlineFinding] = []
        aggregated_steps: dict[str, str] = {}
        per_file: list[FileReviewResult] = []
        for fd in files:
            if fd.is_binary or fd.is_deleted:
                continue
            response = client.review(
                ReviewRequest(
                    code_diff=fd.raw,
                    file_path=fd.path,
                    rag_enabled=config.rag_enabled,
                    rag_threshold=config.rag_threshold,
                    max_new_tokens=config.max_new_tokens,
                    steps=list(config.steps) or None,
                    extra_rules=extra_rules,
                )
            )
            sm = response.step_map()
            for name, output in sm.items():
                aggregated_steps[f"{fd.path}::{name}"] = output
            findings = list(response.inline_findings)
            all_findings.extend(findings)
            per_file.append(
                FileReviewResult(
                    path=fd.path,
                    rag_docs=response.rag_docs,
                    step_outputs=sm,
                    inline_findings=findings,
                    is_binary=fd.is_binary,
                    is_deleted=fd.is_deleted,
                )
            )
        return ReviewResult(
            code_diff=diff_text,
            rag_docs=[],
            step_outputs=aggregated_steps,
            inline_findings=all_findings,
            per_file=per_file,
        )
    finally:
        client.close()


# ----------------------------------------------------------------------------
# Runner-orchestrated path: build a CoTPipeline locally.
# ----------------------------------------------------------------------------

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
    extra_rules = load_rules_dir(args.rules_dir)
    pipeline = CoTPipeline(
        backend=backend,
        retriever=retriever,
        steps=config.steps,
        max_new_tokens=config.max_new_tokens,
        extra_rules=tuple(extra_rules),
        stream=bool(getattr(args, "stream", False)),
    )
    try:
        if args.per_file:
            review_cache_obj = None
            cache_repo = ""
            cache_pr_number = 0
            if getattr(args, "diff_since_last", False) and args.inline_review:
                review_cache_obj = ReviewCache(Path(args.diff_cache_path))
                cache_repo = getattr(args, "repo", "") or ""
                cache_pr_number = int(getattr(args, "pr_number", 0) or 0)
            incremental_writer = _build_incremental_writer(args)
            on_file_done = (
                incremental_writer.write_file_result
                if incremental_writer is not None else None
            )
            result = pipeline.run_per_file(
                diff_text,
                inline_review=args.inline_review,
                judge=bool(getattr(args, "judge", False)),
                self_correct=bool(getattr(args, "self_correct", False)),
                counterfactual=bool(getattr(args, "counterfactual", False)),
                provenance=bool(getattr(args, "provenance", False)),
                max_findings_per_file=args.max_findings_per_file,
                output_dir=output_dir,
                dialogue_block=dialogue_block,
                review_cache=review_cache_obj,
                cache_repo=cache_repo,
                cache_pr_number=cache_pr_number,
                verify_suggestions=bool(getattr(args, "verify_suggestions", False)),
                verify_workdir=getattr(args, "verify_workdir", None),
                verify_cmd=getattr(args, "verify_cmd", "") or "",
                verify_timeout=float(getattr(args, "verify_timeout", 60.0) or 60.0),
                api_consistency_check=bool(getattr(args, "api_consistency", False)),
                pr_classify=bool(getattr(args, "pr_classify", False)),
                pr_title=getattr(args, "pr_title", "") or "",
                pr_body=getattr(args, "pr_body", "") or "",
                reproducibility_check=bool(getattr(args, "reproducibility_check", False)),
                dep_upgrade_check=bool(getattr(args, "dep_upgrade_check", False)),
                persona_set=tuple(
                    s.strip() for s in (getattr(args, "personas", "") or "").split(",")
                    if s.strip()
                ),
                risk_weighted=bool(getattr(args, "risk_weighted", False)),
                risk_workdir=getattr(args, "risk_workdir", None),
                diff_entropy_check=bool(getattr(args, "diff_entropy", False)),
                on_file_done=on_file_done,
            )
            if incremental_writer is not None:
                incremental_writer.write_final(result)
            return result
        return pipeline.run(diff_text, output_dir=output_dir)
    finally:
        backend.close()
        if isinstance(retriever, RemoteRAGRetriever):
            retriever.close()


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
            log.warning(
                "Redacted secrets from diff before backend call: %s",
                report.summary(),
            )
    if args.use_remote_pipeline:
        return _review_via_server(args, config, diff_text)
    return _review_via_pipeline(
        args, config, diff_text,
        output_dir=output_dir,
        dialogue_block=dialogue_block,
    )


# ----------------------------------------------------------------------------
# Subcommand handlers
# ----------------------------------------------------------------------------

def _cmd_review_file(args: argparse.Namespace) -> int:
    config = _build_config(args)
    code = _read_stdin_or_file(args.path)
    result = _run_review(args, config, code, output_dir=args.output_dir)
    sys.stdout.write(
        format_pr_comment(result, marker="<!-- prthinker:summary -->")
    )
    if result.inline_findings:
        sys.stdout.write(
            f"\n[{len(result.inline_findings)} inline findings parsed]\n"
        )
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
        log.warning("Could not fetch PR meta for classifier (%s); "
                    "classifier will run on diff only", exc)
        return
    args.pr_title = pr_title
    args.pr_body = pr_body
    log.info("Fetched PR meta: title=%r body_len=%d", pr_title[:60], len(pr_body))


def _resolve_head_sha(args: argparse.Namespace, adapter: object) -> str | None:
    """Fetch the head SHA only when the gate or CI signals need it."""
    needs = (args.gate_on != "none" and not args.dry_run) or args.include_ci_signals
    return adapter.fetch_head_sha() if needs else None


def _maybe_prepend_ci_signals(
    args: argparse.Namespace, diff: str, head_sha: str | None, platform_kind: object,
) -> str:
    """Prepend CI failure signals to the diff (GitHub only) when enabled."""
    from prthinker.platforms import PlatformKind
    if not (args.include_ci_signals and head_sha is not None):
        return diff
    if platform_kind is not PlatformKind.GITHUB:
        log.info("CI signals not yet supported on %s — skipping", platform_kind.value)
        return diff
    signals = fetch_ci_failure_signals(
        args.repo, head_sha, args.github_token,
        max_jobs=args.ci_signal_max_jobs,
        log_tail_chars=args.ci_signal_tail_chars,
    )
    block = format_signals_block(signals)
    if block:
        diff = block + diff
        log.info("Prepended %d CI failure signal(s) to diff", len(signals))
    return diff


def _open_gate_if_needed(
    args: argparse.Namespace, adapter: object, head_sha: str | None,
) -> object | None:
    """Open the status gate unless this is a dry-run / partial-output run."""
    skip = (
        args.gate_on == "none"
        or args.dry_run
        or getattr(args, "output_json", "")
        or head_sha is None
    )
    return None if skip else adapter.open_gate(head_sha)


def _dialogue_from_replies(adapter: object) -> str:
    """Render the author-reply dialogue block; tolerate fetch failure."""
    try:
        replies = adapter.fetch_author_replies()
    except Exception as exc:
        log.warning("Failed to fetch author replies (%s); skipping dialogue", exc)
        return ""
    if not replies:
        return ""
    from prthinker.dialogue import render_dialogue_block
    log.info("Injecting %d author reply(ies) into inline-findings prompt", len(replies))
    return render_dialogue_block(replies)


def _dialogue_from_lessons(args: argparse.Namespace) -> str:
    """Render the derived-lessons block from the lessons store."""
    lessons_path = Path(getattr(args, "lessons_path", "") or ".prthinker/lessons.jsonl")
    if not lessons_path.exists():
        return ""
    from prthinker.lessons import LessonsStore, format_lessons_block
    top_k = int(getattr(args, "lessons_top_k", 5) or 5)
    recent = list(LessonsStore(lessons_path))[-top_k:]
    block = format_lessons_block(recent)
    if block:
        log.info("Injecting %d derived lesson(s) into inline-findings prompt", len(recent))
    return block


def _dialogue_from_kg(args: argparse.Namespace) -> str:
    """Render the repo knowledge-graph symbol block."""
    kg_store_path = Path(getattr(args, "kg_store", "") or ".prthinker/repo-kg.sqlite")
    if not kg_store_path.exists():
        return ""
    kg_workdir = Path(getattr(args, "kg_workdir", "") or ".")
    symbols = KnowledgeGraphStore(kg_store_path).all_symbols(kg_workdir)
    block = format_kg_block(symbols)
    if block:
        log.info("Injecting %d known symbol(s) into inline-findings prompt", len(symbols))
    return block


def _build_dialogue_block(args: argparse.Namespace, adapter: object) -> str:
    """Assemble the inline-findings context from replies, lessons, and KG."""
    if not args.inline_review:
        return ""
    block = _dialogue_from_replies(adapter) if getattr(args, "reply_to_author", False) else ""
    if getattr(args, "lessons", False):
        lessons = _dialogue_from_lessons(args)
        if lessons:
            block = (lessons + "\n\n" + block).strip()
    if getattr(args, "kg_ground", False):
        kg = _dialogue_from_kg(args)
        if kg:
            block = (kg + "\n\n" + block).strip()
    return block


def _close_gate_on_crash(adapter: object, gate_handle: object | None) -> None:
    """Mark the gate failed when the reviewer raises before publishing."""
    if gate_handle is None:
        return
    from prthinker.checks import CheckResult
    adapter.close_gate(gate_handle, CheckResult(
        conclusion="failure",
        title="Reviewer crashed",
        summary="The CoT reviewer raised an exception. Check workflow logs.",
        error_count=0, warning_count=0, info_count=0,
    ))


def _resolve_review_event(args: argparse.Namespace, result: ReviewResult) -> str:
    """Map aggregated judge verdicts to a platform review event."""
    if not (args.judge and result.per_file):
        return "COMMENT"
    from prthinker.judge import aggregate, to_github_event
    verdicts = [fr.verdict for fr in result.per_file if fr.verdict is not None]
    if not verdicts:
        return "COMMENT"
    event = to_github_event(aggregate(verdicts))
    log.info("Judge verdict aggregated → %s", event)
    return event


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
        len(result.per_file), len(result.inline_findings), output_json,
    )
    return 0


def _maybe_autofix(
    args: argparse.Namespace, result: ReviewResult, platform_kind: object,
) -> None:
    """Open a draft auto-fix PR (GitHub only) when the threshold is set."""
    from prthinker.platforms import PlatformKind
    if not (args.auto_fix_threshold and not args.dry_run):
        return
    if platform_kind is not PlatformKind.GITHUB:
        log.info("Auto-fix not yet supported on %s — skipping", platform_kind.value)
        return
    gh = GitHubConfig(
        repo=args.repo, pr_number=args.pr_number,
        token=args.github_token, comment_marker=args.marker,
    )
    _maybe_open_auto_fix_pr(gh, args, result)


def _publish_review_result(
    args: argparse.Namespace,
    adapter: object,
    result: ReviewResult,
    gate_handle: object | None,
    platform_kind: object,
) -> int:
    """Post comment + inline review, close the gate, and trigger auto-fix."""
    body = format_pr_comment(result, marker=args.marker)
    if args.dry_run:
        return _emit_dry_run(result, body)
    output_json = getattr(args, "output_json", "")
    if output_json:
        return _emit_partial_json(result, output_json)

    comment_id = adapter.upsert_summary_comment(body)
    log.info("Posted summary comment id=%d", comment_id)

    review_event = _resolve_review_event(args, result)
    if args.inline_review and result.inline_findings:
        review_id = adapter.submit_inline_review(
            result.inline_findings,
            summary_body="prthinker — inline findings",
            event=review_event,
        )
        log.info("Posted inline review id=%s (event=%s)", review_id, review_event)

    if gate_handle is not None:
        gate_result = evaluate_gate(result.inline_findings, gate_on=args.gate_on)
        adapter.close_gate(gate_handle, gate_result)
        log.info(
            "Gate conclusion=%s (errors=%d warnings=%d info=%d, floor=%s)",
            gate_result.conclusion, gate_result.error_count,
            gate_result.warning_count, gate_result.info_count, args.gate_on,
        )

    _maybe_autofix(args, result, platform_kind)
    return 0


def _cmd_review_pr(args: argparse.Namespace) -> int:
    config = _build_config(args)
    _validate_pr_args(args)

    from prthinker.platforms import PlatformKind, create_platform_adapter
    platform_kind = PlatformKind(args.platform)
    adapter = create_platform_adapter(
        platform_kind,
        repo=args.repo,
        token=args.github_token,
        pr_number=args.pr_number,
        comment_marker=args.marker,
        base_url=args.platform_base_url,
    )

    log.info("Fetching diff for %s %s#%d",
             platform_kind.value, args.repo, args.pr_number)
    diff = adapter.fetch_diff()
    if not diff.strip():
        log.warning("Empty diff — skipping review")
        return 0

    _maybe_fetch_pr_meta(args, adapter)
    head_sha = _resolve_head_sha(args, adapter)
    diff = _maybe_prepend_ci_signals(args, diff, head_sha, platform_kind)
    gate_handle = _open_gate_if_needed(args, adapter, head_sha)
    dialogue_block = _build_dialogue_block(args, adapter)

    try:
        result = _run_review(args, config, diff, dialogue_block=dialogue_block)
    except Exception:
        _close_gate_on_crash(adapter, gate_handle)
        raise

    return _publish_review_result(args, adapter, result, gate_handle, platform_kind)

def _maybe_open_auto_fix_pr(
    gh: GitHubConfig,
    args: argparse.Namespace,
    result: ReviewResult,
) -> None:
    """Apply ``--auto-fix-threshold`` to surviving warning suggestions."""
    eligible = [
        f for f in result.inline_findings
        if f.severity == "warning" and f.suggestion is not None
    ]
    if len(eligible) < args.auto_fix_threshold:
        log.info(
            "Auto-fix: %d eligible suggestion(s) below threshold %d — skipped",
            len(eligible), args.auto_fix_threshold,
        )
        return

    from prthinker.auto_fix import open_auto_fix_pr

    findings_by_file: dict[str, list[InlineFinding]] = {}
    for f in eligible:
        findings_by_file.setdefault(f.path, []).append(f)

    base_branch = args.auto_fix_base_branch
    if not base_branch:
        from prthinker.github_api import fetch_pr_base_branch
        try:
            base_branch = fetch_pr_base_branch(gh)
        except Exception as exc:
            log.warning("Auto-fix: could not fetch base branch: %s", exc)
            return

    repo_root = Path.cwd()
    try:
        auto_result = open_auto_fix_pr(
            config=gh,
            findings_by_file=findings_by_file,
            base_pr_number=gh.pr_number,
            base_branch=base_branch,
            repo_root=repo_root,
        )
    except Exception as exc:
        log.error("Auto-fix failed: %s", exc)
        return

    if auto_result is None:
        log.info("Auto-fix: no edits applied (every suggestion conflicted or "
                 "the target files did not exist)")
        return

    log.info(
        "Auto-fix PR #%s opened: %s (applied=%d skipped=%d files=%d)",
        auto_result.pr_number, auto_result.pr_url,
        auto_result.total_findings_applied,
        auto_result.total_findings_skipped,
        len(auto_result.files_changed),
    )


def _load_partial_payload(jp: Path) -> dict | None:
    try:
        return json.loads(Path(jp).read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 — surface the offending file
        log.warning("Skipping %s — not valid JSON (%s)", jp, exc)
        return None


@dataclass
class _MergeAccumulator:
    """Mutable buckets the per-partial merge loop appends into."""

    per_file: list[FileReviewResult] = field(default_factory=list)
    step_outputs: dict[str, str] = field(default_factory=dict)
    rag_docs: list[str] = field(default_factory=list)
    rag_docs_seen: set[str] = field(default_factory=set)
    paths_seen: set[str] = field(default_factory=set)


def _absorb_partial(partial: ReviewResult, acc: _MergeAccumulator) -> None:
    """Merge one deserialized partial into the running aggregate.

    Mutates ``acc`` in place. Dedupes per_file by path with last-
    write-wins, relying on the caller sorting prior-state partials
    BEFORE this run's shard partials so matrix output overrides prior.
    """
    acc.step_outputs.update(partial.step_outputs)
    for d in partial.rag_docs:
        if d not in acc.rag_docs_seen:
            acc.rag_docs_seen.add(d)
            acc.rag_docs.append(d)
    for fr in partial.per_file:
        if fr.path in acc.paths_seen:
            acc.per_file = [x for x in acc.per_file if x.path != fr.path]
        acc.paths_seen.add(fr.path)
        acc.per_file.append(fr)


def merge_partial_reviews(json_paths: list[Path]) -> ReviewResult:
    """Merge partial review JSONs into a single ReviewResult.

    per_file results are the single source of truth: the flat
    inline_findings list is derived from them AFTER merging, so a
    prior-run partial carried forward through the per-PR state cache
    (whose top-level inline_findings has been intentionally zeroed
    out, with the real data on per_file[i].inline_findings) still
    reaches submit_inline_review() and evaluate_gate(). This honours
    the project rule that a file's prior review result is never lost
    just because this run could not refresh it.
    """
    acc = _MergeAccumulator()
    for jp in sorted(json_paths):
        payload = _load_partial_payload(jp)
        if payload is None:
            continue
        _absorb_partial(_deserialize_partial_review(payload), acc)

    merged_findings: list[InlineFinding] = [
        f for fr in acc.per_file for f in fr.inline_findings
    ]
    return ReviewResult(
        code_diff="",  # the aggregate doesn't need the raw diff
        rag_docs=acc.rag_docs,
        step_outputs=acc.step_outputs,
        inline_findings=merged_findings,
        per_file=acc.per_file,
    )


def _cmd_aggregate(args: argparse.Namespace) -> int:
    """Merge partial review JSONs and post a single review to the PR.

    Counterpart to `review-pr --output-json`: a CI matrix that shards
    per-file review across multiple runners can stash each runner's
    partial result as an artifact, then call this command in a final
    job to do the GitHub-side posting exactly once.
    """
    if not args.repo:
        raise SystemExit("--repo or $GITHUB_REPOSITORY / $CI_PROJECT_PATH is required")
    if not args.pr_number:
        raise SystemExit("--pr-number is required")
    if not args.github_token:
        raise SystemExit("--github-token / $GITHUB_TOKEN / $GITLAB_TOKEN is required")
    input_dir_raw = (getattr(args, "aggregate_from", "") or "").strip()
    if not input_dir_raw:
        raise SystemExit(
            "--aggregate-from or $PRTHINKER_AGGREGATE_FROM is required"
        )
    input_dir = Path(input_dir_raw)
    if not input_dir.is_dir():
        raise SystemExit(f"{input_dir} is not a directory")

    # Walk the dir recursively so artifact-download layouts (which often
    # nest one folder per matrix iteration) are handled without extra
    # wiring on the workflow side.
    json_paths = sorted(input_dir.rglob("*.json"))
    if not json_paths:
        log.warning("No *.json found under %s — nothing to aggregate", input_dir)
        return 0

    merged = merge_partial_reviews(json_paths)
    log.info(
        "Aggregated %d partial(s): files=%d findings=%d",
        len(json_paths),
        len(merged.per_file),
        len(merged.inline_findings),
    )

    overall = _synthesize_overall_summary(merged.per_file)
    if overall:
        merged.step_outputs["total_summary"] = overall

    from prthinker.platforms import PlatformKind, create_platform_adapter

    platform_kind = PlatformKind(args.platform)
    adapter = create_platform_adapter(
        platform_kind,
        repo=args.repo,
        token=args.github_token,
        pr_number=args.pr_number,
        comment_marker=args.marker,
        base_url=args.platform_base_url,
    )

    head_sha: str | None = None
    needs_head_sha = args.gate_on != "none" and not args.dry_run
    if needs_head_sha:
        try:
            head_sha = adapter.fetch_head_sha()
        except Exception as exc:  # noqa: BLE001
            log.warning("Could not fetch head SHA (%s); skipping gate", exc)

    gate_handle = None
    if args.gate_on != "none" and not args.dry_run and head_sha is not None:
        gate_handle = adapter.open_gate(head_sha)

    body = format_pr_comment(merged, marker=args.marker)
    if args.dry_run:
        sys.stdout.write(body)
        if merged.inline_findings:
            sys.stdout.write(
                f"\n[would post {len(merged.inline_findings)} inline findings]\n"
            )
        return 0

    comment_id = adapter.upsert_summary_comment(body)
    log.info("Posted summary comment id=%d", comment_id)

    review_event = "COMMENT"
    if args.judge and merged.per_file:
        from prthinker.judge import aggregate as judge_aggregate
        from prthinker.judge import to_github_event
        verdicts = [fr.verdict for fr in merged.per_file if fr.verdict is not None]
        if verdicts:
            review_event = to_github_event(judge_aggregate(verdicts))
            log.info("Judge verdict aggregated → %s", review_event)

    if args.inline_review and merged.inline_findings:
        # Inline submission can still 422 on edge cases the diff-hunk
        # pre-filter misses (e.g. renamed files where the new path's
        # blob SHA differs from what `+++ b/<path>` records). Log and
        # continue — the summary comment is already posted above, and
        # the check-run gate below still needs to run to unblock merge.
        try:
            review_id = adapter.submit_inline_review(
                merged.inline_findings,
                summary_body="prthinker — inline findings",
                event=review_event,
            )
            log.info(
                "Posted inline review id=%s (event=%s)",
                review_id, review_event,
            )
        except Exception as exc:  # noqa: BLE001 — must not skip the gate below
            log.error(
                "Inline review submission failed (%s); summary comment "
                "and check run will still be posted",
                exc,
            )

    if gate_handle is not None:
        gate_result = evaluate_gate(merged.inline_findings, gate_on=args.gate_on)
        adapter.close_gate(gate_handle, gate_result)
        log.info(
            "Gate conclusion=%s (errors=%d warnings=%d info=%d, floor=%s)",
            gate_result.conclusion,
            gate_result.error_count, gate_result.warning_count,
            gate_result.info_count, args.gate_on,
        )

    return 0


def _cmd_harvest(args: argparse.Namespace) -> int:
    if not args.repo:
        raise SystemExit("--repo or $GITHUB_REPOSITORY is required")
    if not args.github_token:
        raise SystemExit("--github-token or $GITHUB_TOKEN is required")

    store = DismissedExamplesStore(args.out)
    stats = harvest(
        repo=args.repo,
        token=args.github_token,
        store=store,
        pr_number=args.pr_number,
        max_prs=args.max_prs,
    )
    sys.stdout.write(
        f"PRs scanned: {stats.prs_scanned}\n"
        f"Comments scanned: {stats.comments_scanned}\n"
        f"Dismissed appended: {stats.dismissed_found}\n"
        f"Store: {args.out}\n"
    )
    return 0


def _cmd_harvest_accepted(args: argparse.Namespace) -> int:
    if not args.repo:
        raise SystemExit("--repo or $GITHUB_REPOSITORY is required")
    if not args.github_token:
        raise SystemExit("--github-token or $GITHUB_TOKEN is required")

    store = AcceptedExamplesStore(args.out)
    stats = harvest_accepted(
        repo=args.repo,
        token=args.github_token,
        store=store,
        pr_number=args.pr_number,
        max_prs=args.max_prs,
    )
    sys.stdout.write(
        f"PRs scanned: {stats.prs_scanned}\n"
        f"Comments scanned: {stats.comments_scanned}\n"
        f"Accepted appended: {stats.accepted_found}\n"
        f"Store: {args.out}\n"
    )
    return 0


def _cmd_adversarial_eval(args: argparse.Namespace) -> int:
    from prthinker.adversarial_eval import run_eval

    config = _build_config(args)
    backend = create_backend(config)
    try:
        stats = run_eval(
            backend=backend,
            corpus_path=args.corpus,
            out_path=args.outcomes_path,
            max_new_tokens=config.max_new_tokens,
        )
    finally:
        backend.close()
    sys.stdout.write(
        f"adversarial-eval: ran {stats.total} case(s), {stats.errors} error(s). "
        f"Raw outcomes written to {args.outcomes_path}.\n"
        f"Per the no-fabrication rule, no aggregate detection-rate is "
        f"reported here — query the `outcomes` table directly.\n"
    )
    return 0


def _cmd_build_kg(args: argparse.Namespace) -> int:
    """Scan workdir + persist symbols (with import edges) to SQLite."""
    workdir = args.workdir.resolve()
    if not workdir.exists():
        raise SystemExit(f"build-kg: workdir does not exist: {workdir}")
    symbols, imports = scan_workdir_full(workdir)
    store = KnowledgeGraphStore(args.kg_store)
    n = store.rebuild(workdir, symbols, imports)
    sys.stdout.write(
        f"build-kg: extracted {n} symbol(s) from {workdir} "
        f"into {args.kg_store}.\n"
    )
    return 0


def _kg_html_path(output: Path, name: str) -> Path:
    """Resolve the KG page path. With a repo ``name`` the page is written
    to ``repo-kg-<slug>.html`` next to ``output`` so one server can host
    many repos' graphs (nginx routes ``/kg/<slug>/`` to each). The slug is
    restricted to the same charset nginx accepts, so it cannot path-
    traverse. With no name, ``output`` is returned unchanged.
    """
    name = (name or "").strip()
    if not name:
        return output
    slug = re.sub(r"[^A-Za-z0-9._-]", "-", name).strip("-.") or "repo"
    return output.parent / f"repo-kg-{slug}.html"


def _cmd_visualize_kg(args: argparse.Namespace) -> int:
    """Render the KG SQLite as a self-contained D3 force-graph HTML page."""
    workdir = args.workdir.resolve()
    if not workdir.exists():
        raise SystemExit(f"visualize-kg: workdir does not exist: {workdir}")

    store = KnowledgeGraphStore(args.kg_store)
    if len(store.all_symbols(workdir)) == 0:
        if getattr(args, "auto_build", False):
            symbols, imports = scan_workdir_full(workdir)
            store.rebuild(workdir, symbols, imports)
            sys.stdout.write(
                f"visualize-kg: auto-built {len(symbols)} symbol(s) "
                f"+ {len(imports)} import edge(s) for {workdir} "
                f"into {args.kg_store}\n"
            )
        else:
            raise SystemExit(
                f"visualize-kg: no symbols for {workdir} in "
                f"{args.kg_store}. Run `prthinker build-kg --workdir "
                f"{workdir}` first, or pass --auto-build."
            )

    data = build_graph_data(store, workdir)
    out_path = _kg_html_path(args.output, getattr(args, "name", ""))
    render_html(data, out_path)
    sys.stdout.write(
        f"visualize-kg: wrote {len(data['nodes'])} node(s) / "
        f"{len(data['links'])} edge(s) to {out_path}\n"
    )
    return 0


def _cmd_discover_rules(args: argparse.Namespace) -> int:
    """List finding clusters above the configured size threshold."""
    from prthinker.finding_clusters import (
        FindingClusterStore, greedy_cluster,
    )

    store = FindingClusterStore(args.cluster_store)
    if len(store) == 0:
        sys.stdout.write(
            "discover-rules: index is empty. Run review-pr with "
            "--cluster-store-path set on a few PRs first to populate it.\n"
        )
        return 0
    fingerprints = store.load(repo=args.repo or None)
    clusters = greedy_cluster(
        fingerprints,
        similarity_threshold=args.similarity_threshold,
        min_cluster_size=args.min_cluster_size,
    )
    if not clusters:
        sys.stdout.write(
            f"discover-rules: no clusters of size >= "
            f"{args.min_cluster_size} at similarity >= "
            f"{args.similarity_threshold:.2f}.\n"
        )
        return 0
    for i, c in enumerate(clusters, start=1):
        sys.stdout.write(
            f"#{i}  size={c.size}  files={len({m.file_path for m in c.members})}\n"
            f"    rep: {c.representative[:160]}\n"
        )
    return 0


def _cmd_derive_lessons(args: argparse.Namespace) -> int:
    """Batch dismissed + accepted, call backend, append to lessons.jsonl."""
    from prthinker.accepted import AcceptedExamplesStore
    from prthinker.dismissed import DismissedExamplesStore
    from prthinker.lessons import LessonsStore, derive_lessons

    dismissed_store = DismissedExamplesStore(args.dismissed_path)
    accepted_store = AcceptedExamplesStore(args.accepted_path)
    lessons_store = LessonsStore(args.lessons_path)

    if len(dismissed_store) == 0 and len(accepted_store) == 0:
        sys.stdout.write(
            "derive-lessons: both corpora are empty — nothing to learn from.\n"
        )
        return 0

    dismissed_recent = list(dismissed_store)[-args.lookback_recent:]
    accepted_recent = list(accepted_store)[-args.lookback_recent:]
    source_prs = tuple(sorted({
        getattr(ex, "pr_number", 0) for ex in accepted_recent
        if getattr(ex, "pr_number", 0)
    }))

    config = _build_config(args)
    backend = create_backend(config)
    try:
        rules = derive_lessons(
            backend=backend,
            dismissed=dismissed_recent,
            accepted=accepted_recent,
            source_prs=source_prs,
            max_rules=args.max_rules,
            max_new_tokens=config.max_new_tokens,
        )
    finally:
        backend.close()

    for r in rules:
        lessons_store.append(r)
    sys.stdout.write(
        f"derive-lessons: appended {len(rules)} rule(s) to {args.lessons_path}.\n"
    )
    return 0


def _cmd_report(args: argparse.Namespace) -> int:
    from prthinker.report import (
        ReportInputs,
        render_html,
        render_json,
        render_markdown,
    )

    inputs = ReportInputs(
        telemetry_path=args.telemetry_path,
        cache_path=args.cache_path,
        dismissed_path=args.dismissed_path,
        accepted_path=args.accepted_path,
        since_seconds=(
            None if args.since_days is None
            else float(args.since_days) * 86400.0
        ),
    )
    renderer = {
        "markdown": render_markdown,
        "html": render_html,
        "json": render_json,
    }[args.format]
    body = renderer(inputs)

    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(body, encoding="utf-8")
        log.info("Wrote %s report to %s", args.format, args.out)
    else:
        sys.stdout.write(body)
    return 0


def _cmd_hook(args: argparse.Namespace) -> int:
    """Pre-commit hook entry point.

    Reads ``git diff --cached`` and runs the per-file pipeline. Exits 0 if
    no finding at or above ``--block-on`` survives the dismissed filter;
    otherwise exits 1 with a short stderr summary so the developer sees
    exactly what blocked the commit.
    """
    import subprocess

    if args.advisory:
        # Force gate to none + override the block floor regardless.
        args.gate_on = "none"
    args.per_file = True
    args.inline_review = True

    try:
        proc = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True, text=True, check=True, encoding="utf-8",
        )
    except FileNotFoundError:
        sys.stderr.write("prthinker hook: `git` not found in PATH\n")
        return 0 if args.advisory else 1
    except subprocess.CalledProcessError as exc:
        sys.stderr.write(f"prthinker hook: `git diff --cached` failed: {exc}\n")
        return 0 if args.advisory else 1

    diff = proc.stdout
    if not diff.strip():
        # Nothing staged → nothing to review. Don't fail the commit.
        return 0

    config = _build_config(args)
    result = _run_review(args, config, diff)

    from prthinker.checks import evaluate_gate

    gate_result = evaluate_gate(
        result.inline_findings,
        gate_on=("none" if args.advisory else args.block_on),
    )

    if not result.inline_findings:
        sys.stderr.write("prthinker hook: no findings.\n")
        return 0

    sys.stderr.write(
        f"prthinker hook: {gate_result.error_count} error(s), "
        f"{gate_result.warning_count} warning(s), "
        f"{gate_result.info_count} info finding(s):\n"
    )
    for finding in result.inline_findings:
        sys.stderr.write(
            f"  {finding.severity:>7} {finding.path}:{finding.line} — "
            f"{finding.comment.splitlines()[0][:120]}\n"
        )

    if args.advisory or gate_result.conclusion == "success":
        return 0
    sys.stderr.write(
        f"\nCommit blocked: at least one finding at severity ≥ "
        f"'{args.block_on}'. Address the findings or rerun with "
        f"`git commit --no-verify` to bypass.\n"
    )
    return 1


def _cmd_stats(args: argparse.Namespace) -> int:
    from prthinker.cache import PromptCache
    from prthinker.telemetry import TelemetrySink

    telemetry_path = Path(args.telemetry_path)
    if not telemetry_path.exists():
        sys.stderr.write(
            f"No telemetry file at {telemetry_path}. Re-run a review with "
            f"--telemetry first.\n"
        )
        return 1
    sink = TelemetrySink(telemetry_path)
    window = None if args.since_days is None else args.since_days * 86400.0
    stats = sink.aggregate(since_seconds=window)
    if not stats:
        sys.stdout.write("No calls recorded in the selected window.\n")
        return 0

    range_label = (
        "all-time" if args.since_days is None
        else f"last {args.since_days:g} day(s)"
    )
    sys.stdout.write(f"# prthinker stats — {range_label}\n\n")

    fmt = "{backend:<10} {model:<35} {calls:>6} {hits:>5} {ptok:>9} {ctok:>9} {cost:>9} {p50:>8} {p95:>8}\n"
    sys.stdout.write(fmt.format(
        backend="backend", model="model", calls="calls", hits="hits",
        ptok="in-tok", ctok="out-tok", cost="USD",
        p50="p50 ms", p95="p95 ms",
    ))
    sys.stdout.write("-" * 110 + "\n")
    total_cost = 0.0
    total_calls = 0
    total_hits = 0
    for s in stats:
        total_cost += s.cost_usd
        total_calls += s.calls
        total_hits += s.cache_hits
        sys.stdout.write(fmt.format(
            backend=s.backend,
            model=(s.model[:33] + "..") if len(s.model) > 35 else s.model,
            calls=s.calls,
            hits=s.cache_hits,
            ptok=s.prompt_tokens,
            ctok=s.completion_tokens,
            cost=f"${s.cost_usd:.4f}",
            p50=f"{s.latency_p50_ms:.0f}",
            p95=f"{s.latency_p95_ms:.0f}",
        ))
    sys.stdout.write("-" * 110 + "\n")
    hit_rate = (total_hits / total_calls * 100) if total_calls else 0.0
    sys.stdout.write(
        f"Total: {total_calls} call(s), {total_hits} cache hits "
        f"({hit_rate:.1f}%), ${total_cost:.4f}\n"
    )

    cache_path = Path(args.cache_path)
    if cache_path.exists():
        cache = PromptCache(cache_path)
        cstats = cache.stats()
        sys.stdout.write(
            f"\nCache: {cstats.total_entries} entries stored, "
            f"{cstats.total_hits} lifetime hits at {cache_path}\n"
        )
    return 0


def _cmd_mcp(_args: argparse.Namespace) -> int:
    # Lazy import: the MCP server is an optional integration; keep it off the
    # import path of every other command.
    from prthinker.mcp_server import run as run_mcp  # noqa: PLC0415
    return run_mcp()


# Registry mapping subcommand name -> handler. Replaces a long if/elif
# dispatch chain so adding a command means adding one entry (Open/Closed).
_COMMAND_HANDLERS: dict[str, Callable[[argparse.Namespace], int]] = {
    "review-file": _cmd_review_file,
    "review-pr": _cmd_review_pr,
    "aggregate": _cmd_aggregate,
    "stats": _cmd_stats,
    "report": _cmd_report,
    "adversarial-eval": _cmd_adversarial_eval,
    "derive-lessons": _cmd_derive_lessons,
    "discover-rules": _cmd_discover_rules,
    "build-kg": _cmd_build_kg,
    "visualize-kg": _cmd_visualize_kg,
    "mcp": _cmd_mcp,
    "hook": _cmd_hook,
    "harvest-dismissed": _cmd_harvest,
    "harvest-accepted": _cmd_harvest_accepted,
}


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    # Peek at --config without forcing a parse, so YAML defaults apply
    # before argparse fixes the rest of the namespace.
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("--config", type=Path, default=None)
    pre_args, _ = pre.parse_known_args(argv)
    try:
        _apply_repo_defaults(parser, pre_args.config)
    except (FileNotFoundError, ValueError) as exc:
        sys.stderr.write(f"Config error: {exc}\n")
        return 2

    args = parser.parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    handler = _COMMAND_HANDLERS.get(args.command)
    if handler is None:
        parser.error(f"unknown command: {args.command}")
        return 2
    return handler(args)


__all__ = ["main"]
