"""Corpora, knowledge-graph, and maintenance command handlers."""

from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from prthinker.telemetry import BackendStats


from prthinker.backends import create_backend
from prthinker.accepted import AcceptedExamplesStore
from prthinker.checks import (
    evaluate_gate,
)
from prthinker.dismissed import DismissedExamplesStore
from prthinker.formatters import format_pr_comment_pages
from prthinker.harvest import harvest, harvest_accepted
from prthinker.kg_visualize import build_graph_data, render_html
from prthinker.repo_kg import (
    KnowledgeGraphStore,
    scan_workdir_full,
)
from prthinker.cli_review import (
    _build_config,
    _build_preliminary_overview,
    _impact_note,
    _join_overview,
    _maybe_set_labels,
    _maybe_write_job_summary,
    _pr_files_url,
    _review_progress,
    _run_review,
    _synthesize_overall_summary,
)
from prthinker.sarif import write_sarif
from prthinker.cli_commands_helpers import (
    _close_aggregate_gate,
    _open_aggregate_gate,
    _resolve_review_event,
    _submit_aggregate_inline_review,
    _validate_aggregate_args,
    merge_partial_reviews,
)
from prthinker.commit_review import build_prompt, parse_review
from prthinker.pipeline import (
    ReviewResult,
)

log = logging.getLogger("prthinker")

_STATS_ROW_FMT = (
    "{backend:<10} {model:<35} {calls:>6} {hits:>5} {ptok:>9} "
    "{ctok:>9} {cost:>9} {p50:>8} {p95:>8}\n"
)
_STATS_RULE = "-" * 110 + "\n"
_STATS_MODEL_CAP = 35


def _maybe_write_sarif(args: argparse.Namespace, result: ReviewResult) -> None:
    """Write SARIF for upload to GitHub code scanning when requested."""
    out = getattr(args, "sarif_out", "") or ""
    if not out:
        return
    write_sarif(result, out)
    log.info("Wrote SARIF to %s", out)


def _cmd_aggregate(args: argparse.Namespace) -> int:
    """Merge partial review JSONs and post a single review to the PR.

    Counterpart to `review-pr --output-json`: a CI matrix that shards
    per-file review across multiple runners can stash each runner's
    partial result as an artifact, then call this command in a final
    job to do the GitHub-side posting exactly once.
    """
    input_dir = _validate_aggregate_args(args)

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

    gate_handle = _open_aggregate_gate(args, adapter)

    _agg_delta, _agg_resolved = _review_progress(args, adapter, merged)
    pages = format_pr_comment_pages(
        merged, marker=args.marker,
        findings_only=getattr(args, "findings_only", False),
        hide_info=getattr(args, "hide_info", False),
        preliminary=_join_overview(
            _build_preliminary_overview(args, adapter, merged),
            _impact_note(args, merged), _agg_resolved,
        ),
        files_url=_pr_files_url(args),
        delta=_agg_delta,
        min_confidence=getattr(args, "summary_min_confidence", 0.0),
        table=getattr(args, "summary_table", False),
    )
    _maybe_write_job_summary(pages[0])
    _maybe_write_sarif(args, merged)
    if args.dry_run:
        sys.stdout.write("\n\n".join(pages))
        if merged.inline_findings:
            sys.stdout.write(
                f"\n[would post {len(merged.inline_findings)} inline findings "
                f"across {len(pages)} summary comment(s)]\n"
            )
        return 0

    comment_ids = adapter.upsert_summary_comments(pages)
    log.info("Posted %d summary comment(s): %s", len(comment_ids), comment_ids)

    review_event = _resolve_review_event(args, merged)
    _submit_aggregate_inline_review(args, adapter, merged, review_event)
    _close_aggregate_gate(args, adapter, merged, gate_handle)
    _maybe_set_labels(args, adapter, merged)

    return 0

_STATUS_PLACEHOLDER = (
    "## CoT Code Review\n\n"
    "⏳ **Review in progress…** The reviewer has started; the full summary "
    "will replace this comment when it finishes."
)


def _cmd_post_status(args: argparse.Namespace) -> int:
    """Upsert a 'review in progress' placeholder under the summary marker.

    Posted early (e.g. by the enumerate job) so the PR shows the review
    has started; the later aggregate run reconciles it into the real
    summary via the same marker.
    """
    from prthinker.platforms import PlatformKind, create_platform_adapter

    adapter = create_platform_adapter(
        PlatformKind(args.platform),
        repo=args.repo,
        token=args.github_token,
        pr_number=args.pr_number,
        comment_marker=args.marker,
        base_url=args.platform_base_url,
    )
    body = f"{args.marker}\n{_STATUS_PLACEHOLDER}\n"
    if args.dry_run:
        sys.stdout.write(body)
        return 0
    adapter.upsert_summary_comments([body])
    log.info("Posted review-in-progress placeholder")
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
        render_html as render_report_html,
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
        "html": render_report_html,
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

def _read_staged_diff(advisory: bool) -> tuple[str | None, int]:
    """Return staged diff text, or ``(None, exit_code)`` when git fails."""
    import subprocess

    try:
        proc = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True, text=True, check=True, encoding="utf-8",
        )
    except FileNotFoundError:
        sys.stderr.write("prthinker hook: `git` not found in PATH\n")
        return None, 0 if advisory else 1
    except subprocess.CalledProcessError as exc:
        sys.stderr.write(f"prthinker hook: `git diff --cached` failed: {exc}\n")
        return None, 0 if advisory else 1
    return proc.stdout, 0


def _emit_hook_findings(result: ReviewResult, gate_result: object) -> None:
    """Write the per-finding hook summary to stderr."""
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


def _cmd_hook(args: argparse.Namespace) -> int:
    """Pre-commit hook entry point.

    Reads ``git diff --cached`` and runs the per-file pipeline. Exits 0 if
    no finding at or above ``--block-on`` survives the dismissed filter;
    otherwise exits 1 with a short stderr summary so the developer sees
    exactly what blocked the commit.
    """
    if args.advisory:
        # Force gate to none + override the block floor regardless.
        args.gate_on = "none"
    args.per_file = True
    args.inline_review = True

    diff, exit_code = _read_staged_diff(args.advisory)
    if diff is None:
        return exit_code
    if not diff.strip():
        # Nothing staged → nothing to review. Don't fail the commit.
        return 0

    config = _build_config(args)
    result = _run_review(args, config, diff)

    gate_result = evaluate_gate(
        result.inline_findings,
        gate_on=("none" if args.advisory else args.block_on),
    )

    if not result.inline_findings:
        sys.stderr.write("prthinker hook: no findings.\n")
        return 0

    _emit_hook_findings(result, gate_result)

    if args.advisory or gate_result.conclusion == "success":
        return 0
    sys.stderr.write(
        f"\nCommit blocked: at least one finding at severity ≥ "
        f"'{args.block_on}'. Address the findings or rerun with "
        f"`git commit --no-verify` to bypass.\n"
    )
    return 1

def _cmd_review_commits(args: argparse.Namespace) -> int:
    """Review commit-message quality for messages read from stdin (one per line)."""
    messages = [line.strip() for line in sys.stdin if line.strip()]
    if not messages:
        sys.stderr.write("No commit messages on stdin\n")
        return 1
    config = _build_config(args)
    backend = create_backend(config)
    raw = backend.generate(
        build_prompt(messages), max_new_tokens=config.max_new_tokens,
    )
    notes = parse_review(raw)
    if not notes:
        sys.stdout.write("No commit-message issues found.\n")
        return 0
    for note in notes:
        sys.stdout.write(
            f"[{note.message_index}] {note.issue}\n    -> {note.suggestion}\n"
        )
    return 0


def _cmd_stats(args: argparse.Namespace) -> int:
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

    _write_stats_table(stats)
    _write_cache_summary(Path(args.cache_path))
    return 0


def _write_stats_table(stats: list[BackendStats]) -> None:
    """Write the per-backend table plus the aggregate totals footer."""
    sys.stdout.write(_STATS_ROW_FMT.format(
        backend="backend", model="model", calls="calls", hits="hits",
        ptok="in-tok", ctok="out-tok", cost="USD",
        p50="p50 ms", p95="p95 ms",
    ))
    sys.stdout.write(_STATS_RULE)
    total_cost = 0.0
    total_calls = 0
    total_hits = 0
    for s in stats:
        total_cost += s.cost_usd
        total_calls += s.calls
        total_hits += s.cache_hits
        _write_stats_row(s)
    sys.stdout.write(_STATS_RULE)
    hit_rate = (total_hits / total_calls * 100) if total_calls else 0.0
    sys.stdout.write(
        f"Total: {total_calls} call(s), {total_hits} cache hits "
        f"({hit_rate:.1f}%), ${total_cost:.4f}\n"
    )


def _write_stats_row(s: BackendStats) -> None:
    """Write a single backend statistics row, truncating long model names."""
    model = (s.model[:33] + "..") if len(s.model) > _STATS_MODEL_CAP else s.model
    sys.stdout.write(_STATS_ROW_FMT.format(
        backend=s.backend,
        model=model,
        calls=s.calls,
        hits=s.cache_hits,
        ptok=s.prompt_tokens,
        ctok=s.completion_tokens,
        cost=f"${s.cost_usd:.4f}",
        p50=f"{s.latency_p50_ms:.0f}",
        p95=f"{s.latency_p95_ms:.0f}",
    ))


def _write_cache_summary(cache_path: Path) -> None:
    """Append the prompt-cache summary line when a cache db exists."""
    if not cache_path.exists():
        return
    from prthinker.cache import PromptCache

    cache = PromptCache(cache_path)
    cstats = cache.stats()
    sys.stdout.write(
        f"\nCache: {cstats.total_entries} entries stored, "
        f"{cstats.total_hits} lifetime hits at {cache_path}\n"
    )

def _cmd_mcp(_args: argparse.Namespace) -> int:
    # Lazy import: the MCP server is an optional integration; keep it off the
    # import path of every other command.
    from prthinker.mcp_server import run as run_mcp  # noqa: PLC0415
    return run_mcp()
