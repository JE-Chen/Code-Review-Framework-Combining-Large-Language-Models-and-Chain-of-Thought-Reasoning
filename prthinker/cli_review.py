"""Review-file / review-pr command handlers and review execution."""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

from prthinker.backends import create_backend
from prthinker.backends.remote import RemotePipelineClient
from prthinker.config import (
    BackendKind,
    Config,
    GitHubConfig,
    env_str,
)
from prthinker.cli_review_helpers import (
    BACKEND_CONFIG_BUILDERS,
    build_cache_telemetry,
    build_dialogue_block,
)
from prthinker.checks import (
    evaluate_gate,
)
from prthinker.ci_signals import (
    fetch_ci_failure_signals,
    format_signals_block,
)
from prthinker.api_surface import compute_api_surface
from prthinker.confidence import filter_by_confidence
from prthinker.diff import parse_unified_diff
from prthinker.finding_dedup import dedupe_findings
from prthinker.formatters import format_pr_comment, format_pr_comment_pages
from prthinker.github_api import count_findings_on_diff
from prthinker.pr_overview import build_overview_text
from prthinker.html_report import write_report
from prthinker.ignore import filter_findings, load_ignore
from prthinker.sarif import write_sarif
from prthinker.incremental_save import (
    IncrementalReviewWriter,
    ReviewMeta,
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

_OVERALL_SUMMARY_PER_CALL_TIMEOUT = 30.0
_OVERALL_SUMMARY_POLL_INTERVAL = 5.0
_OVERALL_SUMMARY_DEADLINE_SECONDS = 1800.0
_OVERALL_SUMMARY_MAX_NEW_TOKENS = 16784

def _build_config(args: argparse.Namespace) -> Config:
    if args.use_remote_pipeline and args.backend != BackendKind.REMOTE.value:
        log.info("--use-remote-pipeline forces --backend remote")
        args.backend = BackendKind.REMOTE.value

    backend = BackendKind(args.backend)
    sub_configs: dict[str, object] = {
        "local": None, "remote": None, "openai": None, "anthropic": None,
        "gemini": None, "cohere": None, "mistral": None,
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
        fd for fd in files
        if not any(fnmatch.fnmatch(fd.path, p) for p in patterns)
    ]

def _filter_per_file_targets(
    files: list, args: argparse.Namespace
) -> list:
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
        rag_threshold=config.rag_threshold,
        max_new_tokens=config.max_new_tokens,
        steps=list(config.steps) or None,
        extra_rules=extra_rules,
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
            return _review_whole_diff_via_server(
                client, config, diff_text, extra_rules
            )
        return _review_per_file_via_server(
            client, args, config, diff_text, extra_rules
        )
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


def _collect_core_kwargs(args: argparse.Namespace) -> dict:
    """Collect the always-present per-file review toggles."""
    return {
        "inline_review": args.inline_review,
        "judge": bool(getattr(args, "judge", False)),
        "self_correct": bool(getattr(args, "self_correct", False)),
        "counterfactual": bool(getattr(args, "counterfactual", False)),
        "provenance": bool(getattr(args, "provenance", False)),
        "max_findings_per_file": args.max_findings_per_file,
    }


def _collect_verify_kwargs(args: argparse.Namespace) -> dict:
    """Collect the suggestion-verification per-file toggles."""
    return {
        "verify_suggestions": bool(getattr(args, "verify_suggestions", False)),
        "verify_workdir": getattr(args, "verify_workdir", None),
        "verify_cmd": getattr(args, "verify_cmd", "") or "",
        "verify_timeout": float(getattr(args, "verify_timeout", 60.0) or 60.0),
    }


def _collect_classify_kwargs(args: argparse.Namespace) -> dict:
    """Collect the PR-classification / consistency per-file toggles."""
    return {
        "api_consistency_check": bool(getattr(args, "api_consistency", False)),
        "pr_classify": bool(getattr(args, "pr_classify", False)),
        "pr_title": getattr(args, "pr_title", "") or "",
        "pr_body": getattr(args, "pr_body", "") or "",
        "reproducibility_check": bool(getattr(args, "reproducibility_check", False)),
        "dep_upgrade_check": bool(getattr(args, "dep_upgrade_check", False)),
    }


def _collect_risk_kwargs(args: argparse.Namespace) -> dict:
    """Collect the persona / risk / entropy per-file toggles."""
    return {
        "persona_set": _csv_tuple(args, "personas"),
        "risk_weighted": bool(getattr(args, "risk_weighted", False)),
        "risk_workdir": getattr(args, "risk_workdir", None),
        "diff_entropy_check": bool(getattr(args, "diff_entropy", False)),
        "review_modes": _csv_tuple(args, "review_modes"),
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
        incremental_writer.write_file_result
        if incremental_writer is not None else None
    )
    result = pipeline.run_per_file(
        diff_text,
        output_dir=output_dir,
        dialogue_block=dialogue_block,
        review_cache=review_cache_obj,
        cache_repo=cache_repo,
        cache_pr_number=cache_pr_number,
        on_file_done=on_file_done,
        **_per_file_kwargs(args),
    )
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
        return _review_via_server(args, config, diff_text)
    return _review_via_pipeline(
        args, config, diff_text,
        output_dir=output_dir,
        dialogue_block=dialogue_block,
    )

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

def _postprocess_findings(args: argparse.Namespace, result: ReviewResult) -> None:
    """Apply .prthinkerignore suppression and de-duplication in place."""
    spec = load_ignore(getattr(args, "ignore_file", "") or ".prthinkerignore")
    if not spec.is_empty:
        result.inline_findings = filter_findings(result.inline_findings, spec)
        for file_result in result.per_file:
            file_result.inline_findings = filter_findings(
                file_result.inline_findings, spec
            )
    if getattr(args, "dedupe_findings", False):
        result.inline_findings = dedupe_findings(result.inline_findings)
    min_conf = float(getattr(args, "min_confidence", 0.0) or 0.0)
    if min_conf > 0:
        result.inline_findings = filter_by_confidence(result.inline_findings, min_conf)


def _emit_review_artifacts(args: argparse.Namespace, result: ReviewResult) -> None:
    """Write optional SARIF / HTML report artifacts when requested."""
    sarif_out = getattr(args, "sarif_out", "") or ""
    if sarif_out:
        write_sarif(result, sarif_out)
        log.info("Wrote SARIF to %s", sarif_out)
    html_out = getattr(args, "html_report", "") or ""
    if html_out:
        write_report(result, Path(html_out))
        log.info("Wrote HTML report to %s", html_out)


def _append_api_impact(body: str, result: ReviewResult) -> str:
    """Append a public-API semver-impact line to the summary comment."""
    report = compute_api_surface(parse_unified_diff(result.code_diff))
    log.info("api-surface impact=%s (+%d/-%d/~%d)", report.impact,
             len(report.added), len(report.removed), len(report.changed))
    return f"{body}\n\nPublic API impact: **{report.impact}**"


def _pr_files_url(args: argparse.Namespace) -> str | None:
    """Base URL of the PR's Files-changed tab, for diff deep links.

    Honours ``PRTHINKER_PR_FILES_URL`` (set this for GitHub Enterprise);
    otherwise defaults to github.com for the GitHub platform and returns
    None elsewhere (so links are simply omitted).
    """
    override = (env_str("PRTHINKER_PR_FILES_URL", "") or "").strip()
    if override:
        return override
    if getattr(args, "platform", "github") != "github":
        return None
    repo = getattr(args, "repo", "")
    pr_number = getattr(args, "pr_number", 0)
    if not repo or not pr_number:
        return None
    return f"https://github.com/{repo}/pull/{pr_number}/files"


def _build_preliminary_overview(
    args: argparse.Namespace, adapter: object, result: ReviewResult
) -> str | None:
    """Build the model-free PR overview from commits + changed files, or None.

    Best-effort: a commit-fetch failure degrades to a files-only overview
    rather than breaking the review.
    """
    if not getattr(args, "pr_overview", False):
        return None
    try:
        messages = adapter.fetch_commit_messages()
    except Exception as exc:  # noqa: BLE001 — overview is best-effort
        log.warning("Could not fetch commit messages for overview (%s)", exc)
        messages = []
    paths = [fr.path for fr in result.per_file]
    return build_overview_text(messages, paths) or None


def _publish_review_result(
    args: argparse.Namespace,
    adapter: object,
    result: ReviewResult,
    gate_handle: object | None,
    platform_kind: object,
) -> int:
    """Post comment + inline review, close the gate, and trigger auto-fix."""
    _postprocess_findings(args, result)
    _emit_review_artifacts(args, result)
    # The summary text reports how many findings actually land on a diff
    # hunk (= will be posted as inline comments) versus the raw total, so
    # it never claims findings outside the diff were posted. Only compute
    # it when inline review is enabled; otherwise nothing is posted inline
    # and the breakdown would be misleading.
    posted_count: int | None = None
    if getattr(args, "inline_review", False):
        posted_count = count_findings_on_diff(
            result.inline_findings, result.code_diff
        )
    pages = format_pr_comment_pages(
        result, marker=args.marker, posted_count=posted_count,
        findings_only=getattr(args, "findings_only", False),
        hide_info=getattr(args, "hide_info", False),
        preliminary=_build_preliminary_overview(args, adapter, result),
        files_url=_pr_files_url(args),
    )
    if getattr(args, "api_impact", False):
        pages[-1] = _append_api_impact(pages[-1], result)
    if args.dry_run:
        return _emit_dry_run(result, "\n\n".join(pages))
    output_json = getattr(args, "output_json", "")
    if output_json:
        return _emit_partial_json(result, output_json)

    comment_ids = adapter.upsert_summary_comments(pages)
    log.info("Posted %d summary comment(s): %s", len(comment_ids), comment_ids)

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
    dialogue_block = build_dialogue_block(args, adapter)

    try:
        result = _run_review(args, config, diff, dialogue_block=dialogue_block)
    except Exception:
        _close_gate_on_crash(adapter, gate_handle)
        raise

    return _publish_review_result(args, adapter, result, gate_handle, platform_kind)

def _resolve_auto_fix_base_branch(
    gh: GitHubConfig, args: argparse.Namespace
) -> str | None:
    """Return the auto-fix base branch, fetching it from the PR if unset."""
    base_branch = args.auto_fix_base_branch
    if base_branch:
        return base_branch

    from prthinker.github_api import fetch_pr_base_branch
    try:
        return fetch_pr_base_branch(gh)
    except Exception as exc:
        log.warning("Auto-fix: could not fetch base branch: %s", exc)
        return None

def _open_auto_fix_pr_and_report(
    gh: GitHubConfig,
    findings_by_file: dict[str, list[InlineFinding]],
    base_branch: str,
) -> None:
    """Open the auto-fix PR for the collected findings and log the outcome."""
    from prthinker.auto_fix import open_auto_fix_pr

    try:
        auto_result = open_auto_fix_pr(
            config=gh,
            findings_by_file=findings_by_file,
            base_pr_number=gh.pr_number,
            base_branch=base_branch,
            repo_root=Path.cwd(),
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

    findings_by_file: dict[str, list[InlineFinding]] = {}
    for f in eligible:
        findings_by_file.setdefault(f.path, []).append(f)

    base_branch = _resolve_auto_fix_base_branch(gh, args)
    if base_branch is None:
        return

    _open_auto_fix_pr_and_report(gh, findings_by_file, base_branch)
