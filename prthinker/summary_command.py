"""Standalone summary generation with local input and auditable JSON output."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from prthinker import pr_summary
from prthinker.cli_io import emit_text
from prthinker.redaction import redact


def load_summary_input(path: Path) -> dict:
    """Validate local PR metadata without requiring a forge connection."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("diff"), str):
        raise ValueError("summary input requires a string diff")  # noqa: TRY004 - CLI validation
    for key in ("title", "body"):
        if key in payload and not isinstance(payload[key], str):
            raise ValueError(f"{key} must be a string")
    commits = payload.get("commits", [])
    if not isinstance(commits, list) or any(not isinstance(item, str) for item in commits):
        raise ValueError("commits must be a list of strings")
    return payload


def generate_summary(backend, payload: dict, max_new_tokens: int) -> dict:
    """Use one backend independently of the multi-stage review pipeline."""
    prompt = pr_summary.build_prompt(
        diff_text=redact(payload["diff"])[0], title=redact(payload.get("title", ""))[0],
        body=redact(payload.get("body", ""))[0],
        commit_messages=tuple(redact(item)[0] for item in payload.get("commits", [])),
    )
    text = pr_summary.clean_summary(backend.generate(prompt, max_new_tokens))
    if not text:
        raise ValueError("summary backend returned empty text")
    return {
        "schema_version": 1, "summary": redact(text)[0],
        "metadata": {"backend": backend.backend_kind(), "model": backend.model_name(),
                     "max_new_tokens": max_new_tokens,
                     "input_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest()},
    }


def command(args, *, backend_factory, config_builder, adapter_builder) -> int:
    """Generate text/JSON locally, or explicitly publish a marked comment."""
    adapter = None
    if args.input_json:
        payload = load_summary_input(args.input_json)
    else:
        adapter = adapter_builder(args)
        title, body = adapter.fetch_pr_meta()
        payload = {"title": title, "body": body, "diff": adapter.fetch_diff(),
                   "commits": list(adapter.fetch_commit_messages())}
    config = config_builder(args)
    backend = backend_factory(config)
    try:
        result = generate_summary(backend, payload, config.max_new_tokens)
    finally:
        backend.close()
    if args.publish_summary:
        adapter = adapter or adapter_builder(args)
        adapter.upsert_marked_comment(pr_summary.render_comment(result["summary"]),
                                      marker=pr_summary.DEFAULT_MARKER)
    text = json.dumps(result, ensure_ascii=False, indent=2) if args.summary_format == "json" else result["summary"]
    emit_text(text + "\n", args.summary_output)
    return 0
