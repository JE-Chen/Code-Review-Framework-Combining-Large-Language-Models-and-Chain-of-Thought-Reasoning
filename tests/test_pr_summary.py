"""Tests for the Copilot-style PR summary feature.

Covers the pure prompt/clean/render helpers, the pipeline integration via
``FakeBackend``, the platform-adapter ``upsert_marked_comment`` contract,
and the CLI posting helper.
"""

from __future__ import annotations

import argparse
from types import SimpleNamespace

import pytest

from prthinker import pr_summary
from prthinker.platforms.base import PlatformAdapter
from prthinker.platforms.github import GitHubAdapter
from tests.conftest import FakeBackend

_ONE_FILE_DIFF = (
    "diff --git a/a.py b/a.py\n--- a/a.py\n+++ b/a.py\n@@ -1 +1,2 @@\n x\n+y\n"
)


# ---------- build_prompt ----------------------------------------------------

def test_build_prompt_embeds_all_inputs() -> None:
    prompt = pr_summary.build_prompt(
        diff_text=_ONE_FILE_DIFF,
        title="Add retry logic",
        body="Retries failed HTTP calls up to 3 times.",
        commit_messages=("feat: add retry", "fix: cap retries at 3"),
    )
    assert "Add retry logic" in prompt
    assert "Retries failed HTTP calls" in prompt
    assert "- feat: add retry" in prompt
    assert "- fix: cap retries at 3" in prompt
    assert "+y" in prompt  # diff embedded


def test_build_prompt_uses_placeholders_for_empty_inputs() -> None:
    prompt = pr_summary.build_prompt(diff_text="")
    assert pr_summary._NO_TITLE in prompt
    assert pr_summary._NO_BODY in prompt
    assert pr_summary._NO_COMMITS in prompt


def test_build_prompt_truncates_diff_at_boundary() -> None:
    big_diff = "Z" * 50
    prompt = pr_summary.build_prompt(diff_text=big_diff, diff_chars=10)
    # Exactly 10 Z's land in the excerpt; the 11th does not.
    assert "Z" * 10 in prompt
    assert "Z" * 11 not in prompt


def test_build_prompt_clamps_negative_diff_chars_to_zero() -> None:
    prompt = pr_summary.build_prompt(diff_text="abc", diff_chars=-5)
    # No diff body leaks through, and the label reads 0 — no crash.
    assert "first 0 characters" in prompt


def test_commit_subjects_only_first_line_kept() -> None:
    prompt = pr_summary.build_prompt(
        diff_text="",
        commit_messages=("feat: thing\n\nLong body paragraph here.",),
    )
    assert "- feat: thing" in prompt
    assert "Long body paragraph" not in prompt


def test_commit_list_is_capped() -> None:
    messages = tuple(f"commit {i}" for i in range(pr_summary._MAX_COMMITS + 10))
    prompt = pr_summary.build_prompt(diff_text="", commit_messages=messages)
    assert prompt.count("- commit ") == pr_summary._MAX_COMMITS


def test_blank_commit_messages_fall_back_to_placeholder() -> None:
    prompt = pr_summary.build_prompt(diff_text="", commit_messages=("", "   "))
    assert pr_summary._NO_COMMITS in prompt


# ---------- clean_summary ---------------------------------------------------

def test_clean_summary_strips_markdown_fence() -> None:
    raw = "```markdown\n## PR Summary\n\nDoes a thing.\n```"
    assert pr_summary.clean_summary(raw) == "## PR Summary\n\nDoes a thing."


def test_clean_summary_leaves_plain_text_untouched() -> None:
    assert pr_summary.clean_summary("  Plain text.  ") == "Plain text."


def test_clean_summary_empty_returns_empty() -> None:
    assert pr_summary.clean_summary("") == ""
    assert pr_summary.clean_summary("   \n  ") == ""


# ---------- render_comment --------------------------------------------------

def test_render_comment_wraps_with_marker_and_heading() -> None:
    body = pr_summary.render_comment("Overview text.")
    assert body.startswith(pr_summary.DEFAULT_MARKER)
    assert "## PR Summary" in body
    assert "Overview text." in body


def test_default_marker_is_distinct_from_review_marker() -> None:
    # Must differ from the review summary marker so it gets its own comment.
    assert pr_summary.DEFAULT_MARKER == "<!-- prthinker:pr-summary -->"
    assert "summary" in pr_summary.DEFAULT_MARKER


# ---------- adapter contract ------------------------------------------------

class _MiniAdapter(PlatformAdapter):
    """Minimal adapter exercising the base ``upsert_marked_comment``."""

    def fetch_diff(self) -> str:
        return ""

    def fetch_head_sha(self) -> str:
        return "sha"

    def fetch_base_branch(self) -> str:
        return "main"

    def upsert_summary_comment(self, body: str) -> int:
        return 1

    def submit_inline_review(self, findings, *, summary_body, event):  # noqa: ANN001
        return None

    def open_gate(self, head_sha, *, name="prthinker"):  # noqa: ANN001
        return None

    def close_gate(self, handle, result) -> None:  # noqa: ANN001
        return None


def test_base_upsert_marked_comment_is_noop(caplog) -> None:
    with caplog.at_level("INFO"):
        assert _MiniAdapter().upsert_marked_comment("body", marker="<!-- m -->") == -1
    assert "does not support auxiliary marked comments" in caplog.text


def test_github_upsert_marked_comment_uses_given_marker(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def _fake_upsert(config, body):  # noqa: ANN001
        captured["marker"] = config.comment_marker
        captured["body"] = body
        return 99

    monkeypatch.setattr(
        "prthinker.platforms.github.upsert_pr_comment", _fake_upsert
    )
    adapter = GitHubAdapter(repo="o/r", token="t", pr_number=1)
    cid = adapter.upsert_marked_comment("hello", marker="<!-- prthinker:pr-summary -->")
    assert cid == 99
    assert captured["marker"] == "<!-- prthinker:pr-summary -->"
    assert captured["body"] == "hello"


# ---------- standalone pr-summary command -----------------------------------

class _SummaryAdapter(_MiniAdapter):
    """Adapter feeding the standalone pr-summary command its PR inputs."""

    def __init__(self, *, diff: str = _ONE_FILE_DIFF) -> None:
        self.marked: list[tuple[str, str]] = []
        self._diff = diff

    def upsert_marked_comment(self, body: str, *, marker: str) -> int:
        self.marked.append((body, marker))
        return len(self.marked)

    def fetch_diff(self) -> str:
        return self._diff

    def fetch_pr_meta(self) -> tuple[str, str]:
        return ("Add y", "Appends y to a.py.")

    def fetch_commit_messages(self) -> list[str]:
        return ["feat: append y"]


def _cmd_args(**kwargs) -> argparse.Namespace:
    base = {
        "platform": "github",
        "platform_base_url": "",
        "repo": "o/r",
        "github_token": "t",
        "pr_number": 1,
        "marker": "<!-- prthinker:summary -->",
        "dry_run": False,
        "redact_secrets": False,
    }
    base.update(kwargs)
    return argparse.Namespace(**base)


def _patch_backend(monkeypatch: pytest.MonkeyPatch, responses: list[str]) -> FakeBackend:
    backend = FakeBackend(responses)
    monkeypatch.setattr(
        "prthinker.cli_review._build_config",
        lambda args: SimpleNamespace(max_new_tokens=512),
    )
    monkeypatch.setattr("prthinker.cli_review.create_backend", lambda config: backend)
    return backend


def _patch_adapter(monkeypatch: pytest.MonkeyPatch, adapter: _SummaryAdapter) -> None:
    monkeypatch.setattr(
        "prthinker.platforms.create_platform_adapter",
        lambda *a, **k: adapter,
    )


def test_generate_pr_summary_body_builds_marked_comment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from prthinker.cli_review import _generate_pr_summary_body

    backend = _patch_backend(monkeypatch, ["## PR Summary\n\nAppends y."])
    adapter = _SummaryAdapter()
    body = _generate_pr_summary_body(_cmd_args(), adapter)
    assert body.startswith(pr_summary.DEFAULT_MARKER)
    assert "Appends y." in body
    # The prompt carried the PR's own words and the diff.
    prompt = backend.calls[0][0]
    assert "Add y" in prompt and "feat: append y" in prompt and "+y" in prompt


def test_generate_pr_summary_body_empty_diff_returns_blank(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from prthinker.cli_review import _generate_pr_summary_body

    _patch_backend(monkeypatch, ["unused"])
    assert _generate_pr_summary_body(_cmd_args(), _SummaryAdapter(diff="   ")) == ""


def test_cmd_pr_summary_upserts_marked_comment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from prthinker.cli_review import _cmd_pr_summary

    _patch_backend(monkeypatch, ["## PR Summary\n\nAppends y."])
    adapter = _SummaryAdapter()
    _patch_adapter(monkeypatch, adapter)
    assert _cmd_pr_summary(_cmd_args()) == 0
    assert len(adapter.marked) == 1
    body, marker = adapter.marked[0]
    assert marker == pr_summary.DEFAULT_MARKER
    assert "Appends y." in body


def test_cmd_pr_summary_dry_run_does_not_post(
    monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    from prthinker.cli_review import _cmd_pr_summary

    _patch_backend(monkeypatch, ["## PR Summary\n\nAppends y."])
    adapter = _SummaryAdapter()
    _patch_adapter(monkeypatch, adapter)
    assert _cmd_pr_summary(_cmd_args(dry_run=True)) == 0
    assert adapter.marked == []
    assert "Appends y." in capsys.readouterr().out


def test_cmd_pr_summary_swallows_backend_error(
    monkeypatch: pytest.MonkeyPatch, caplog
) -> None:
    from prthinker.cli_review import _cmd_pr_summary

    monkeypatch.setattr(
        "prthinker.cli_review._build_config",
        lambda args: SimpleNamespace(max_new_tokens=512),
    )

    def _boom(config):  # noqa: ANN001
        raise RuntimeError("backend down")

    monkeypatch.setattr("prthinker.cli_review.create_backend", _boom)
    adapter = _SummaryAdapter()
    _patch_adapter(monkeypatch, adapter)
    with caplog.at_level("WARNING"):
        assert _cmd_pr_summary(_cmd_args()) == 0
    assert adapter.marked == []
    assert "PR summary generation failed" in caplog.text


def test_pr_summary_command_is_registered() -> None:
    from prthinker.cli import _COMMAND_HANDLERS
    from prthinker.cli_review import _cmd_pr_summary

    assert _COMMAND_HANDLERS["pr-summary"] is _cmd_pr_summary


def test_pr_summary_parser_routes_command() -> None:
    from prthinker.cli import _build_parser

    args = _build_parser().parse_args(
        ["pr-summary", "--repo", "o/r", "--pr-number", "1", "--github-token", "t"]
    )
    assert args.command == "pr-summary"
