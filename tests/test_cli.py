"""CLI parser shape + YAML override + subparser default propagation.

The subparser-default propagation bug (set_defaults on the parent parser
doesn't reach subparsers) was painful to discover live; pin it here.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from prthinker.cli import _apply_repo_defaults, _build_parser, _build_config
from prthinker.config import BackendKind


def test_parser_help_lists_all_subcommands() -> None:
    p = _build_parser()
    sub_action = next(
        a for a in p._actions  # noqa: SLF001
        if getattr(a, "choices", None) and "review-pr" in a.choices
    )
    assert set(sub_action.choices) >= {
        "review-pr", "review-file",
        "harvest-dismissed", "harvest-accepted",
        "stats", "mcp",
    }


def test_redact_secrets_flag_parses() -> None:
    p = _build_parser()
    ns = p.parse_args([
        "review-file", "-", "--backend", "remote",
        "--remote-url", "http://x", "--redact-secrets",
    ])
    assert ns.redact_secrets is True


def test_findings_only_flag_parses() -> None:
    p = _build_parser()
    ns = p.parse_args([
        "review-file", "-", "--backend", "remote",
        "--remote-url", "http://x", "--findings-only",
    ])
    assert ns.findings_only is True


def test_findings_only_defaults_false() -> None:
    p = _build_parser()
    ns = p.parse_args([
        "review-file", "-", "--backend", "remote", "--remote-url", "http://x",
    ])
    assert ns.findings_only is False


def test_hide_info_flag_parses() -> None:
    p = _build_parser()
    ns = p.parse_args([
        "review-file", "-", "--backend", "remote",
        "--remote-url", "http://x", "--hide-info",
    ])
    assert ns.hide_info is True


def test_pr_overview_flag_parses() -> None:
    p = _build_parser()
    ns = p.parse_args([
        "review-file", "-", "--backend", "remote",
        "--remote-url", "http://x", "--pr-overview",
    ])
    assert ns.pr_overview is True


def test_summary_min_confidence_flag_parses() -> None:
    p = _build_parser()
    ns = p.parse_args([
        "review-file", "-", "--backend", "remote",
        "--remote-url", "http://x", "--summary-min-confidence", "0.4",
    ])
    assert ns.summary_min_confidence == 0.4


def test_pr_files_url_github_default() -> None:
    import argparse as _argparse

    from prthinker.cli_review import _pr_files_url
    ns = _argparse.Namespace(platform="github", repo="o/r", pr_number=7)
    assert _pr_files_url(ns) == "https://github.com/o/r/pull/7/files"


def test_pr_files_url_none_for_non_github() -> None:
    import argparse as _argparse

    from prthinker.cli_review import _pr_files_url
    ns = _argparse.Namespace(platform="gitlab", repo="o/r", pr_number=7)
    assert _pr_files_url(ns) is None


def test_each_backend_choice_is_accepted() -> None:
    p = _build_parser()
    for kind in BackendKind:
        extras: list[str] = []
        if kind is BackendKind.REMOTE:
            extras = ["--remote-url", "http://x"]
        elif kind is BackendKind.OPENAI:
            extras = ["--openai-api-key", "k"]
        elif kind is BackendKind.ANTHROPIC:
            extras = ["--anthropic-api-key", "k"]
        ns = p.parse_args(["review-file", "-", "--backend", kind.value] + extras)
        assert ns.backend == kind.value


def test_subparser_defaults_pick_up_yaml(tmp_path: Path) -> None:
    """Regression: set_defaults must propagate to every subparser."""
    yml = tmp_path / ".prthinker.yaml"
    yml.write_text(textwrap.dedent("""
        backend: openai
        per_file: true
        inline_review: true
        gate:
          severity: error
        cache:
          enabled: true
          ttl_days: 14
        telemetry:
          enabled: true
        openai:
          model: gpt-4o
    """), encoding="utf-8")
    p = _build_parser()
    _apply_repo_defaults(p, yml)

    ns = p.parse_args(["review-file", "-", "--openai-api-key", "sk-test"])
    assert ns.backend == "openai"
    assert ns.per_file is True
    assert ns.inline_review is True
    assert ns.gate_on == "error"
    assert ns.cache_enabled is True
    assert ns.cache_ttl_days == 14
    assert ns.telemetry_enabled is True
    assert ns.openai_model == "gpt-4o"


def test_cli_flag_overrides_yaml(tmp_path: Path) -> None:
    yml = tmp_path / ".prthinker.yaml"
    yml.write_text("openai:\n  model: gpt-4o\n", encoding="utf-8")
    p = _build_parser()
    _apply_repo_defaults(p, yml)
    ns = p.parse_args([
        "review-file", "-", "--backend", "openai",
        "--openai-api-key", "k",
        "--openai-model", "gpt-4o-mini",
    ])
    assert ns.openai_model == "gpt-4o-mini"


def test_missing_remote_url_fails_with_clear_message() -> None:
    p = _build_parser()
    ns = p.parse_args(["review-file", "-", "--backend", "remote"])
    with pytest.raises(SystemExit, match=r"remote-url"):
        _build_config(ns)


def test_missing_openai_key_fails_with_clear_message() -> None:
    p = _build_parser()
    ns = p.parse_args(["review-file", "-", "--backend", "openai"])
    with pytest.raises(SystemExit, match=r"openai"):
        _build_config(ns)


def test_kg_html_path_default_unchanged() -> None:
    from prthinker.cli import _kg_html_path
    out = Path(".prthinker/repo-kg.html")
    assert _kg_html_path(out, "") == out
    assert _kg_html_path(out, "   ") == out


def test_kg_html_path_uses_repo_name() -> None:
    from prthinker.cli import _kg_html_path
    out = Path(".prthinker/repo-kg.html")
    assert _kg_html_path(out, "my-svc") == Path(".prthinker/repo-kg-my-svc.html")


def test_kg_html_path_sanitizes_traversal_and_unsafe_chars() -> None:
    from prthinker.cli import _kg_html_path
    out = Path(".prthinker/repo-kg.html")
    # Slashes / dots / spaces are neutralised so the name can't escape the dir.
    assert _kg_html_path(out, "../../etc/passwd") == Path(".prthinker/repo-kg-etc-passwd.html")
    assert _kg_html_path(out, "Org/Repo X") == Path(".prthinker/repo-kg-Org-Repo-X.html")
    # A name that sanitises to nothing falls back to a safe stub.
    assert _kg_html_path(out, "...") == Path(".prthinker/repo-kg-repo.html")
