"""Platform Strategy — factory dispatch + GitLab adapter wiring.

Network calls are not exercised here (no mock-httpx fixture);
construction + URL building + payload shapes ARE.
"""

from __future__ import annotations

import urllib.parse

import pytest

from prthinker.platforms import PlatformKind, create_platform_adapter
from prthinker.platforms.base import PlatformAdapter
from prthinker.platforms.github import GitHubAdapter
from prthinker.platforms.gitlab import GitLabAdapter

# Test-fixture token. Bound to a name (not a string literal) so the bandit
# B106 hardcoded-password heuristic does not flag every adapter constructor.
_TOK = "t"


def test_factory_dispatches_to_github() -> None:
    adapter = create_platform_adapter(
        PlatformKind.GITHUB, repo="o/r", token=_TOK, pr_number=1,
    )
    assert isinstance(adapter, GitHubAdapter)
    assert isinstance(adapter, PlatformAdapter)


def test_factory_dispatches_to_gitlab() -> None:
    adapter = create_platform_adapter(
        PlatformKind.GITLAB, repo="group/project", token=_TOK, pr_number=1,
    )
    assert isinstance(adapter, GitLabAdapter)
    assert isinstance(adapter, PlatformAdapter)


def test_factory_rejects_unknown_kind() -> None:
    with pytest.raises(ValueError):
        # Force a value that isn't in the enum.
        create_platform_adapter("svn", repo="r", token=_TOK, pr_number=1)  # type: ignore[arg-type]


class _MiniAdapter(PlatformAdapter):
    """Bare adapter exercising only the base ``upsert_summary_comments``."""

    def __init__(self) -> None:
        self.posted: list[str] = []

    def fetch_diff(self) -> str:
        return ""

    def fetch_head_sha(self) -> str:
        return "sha"

    def fetch_base_branch(self) -> str:
        return "main"

    def upsert_summary_comment(self, body: str) -> int:
        self.posted.append(body)
        return len(self.posted)

    def submit_inline_review(self, findings, *, summary_body, event):  # noqa: ANN001
        return None

    def open_gate(self, head_sha, *, name="prthinker"):  # noqa: ANN001
        return None

    def close_gate(self, handle, result) -> None:  # noqa: ANN001
        return None


def test_base_upsert_comments_single_page() -> None:
    adapter = _MiniAdapter()
    ids = adapter.upsert_summary_comments(["only page"])
    assert ids == [1]
    assert adapter.posted == ["only page"]


def test_base_upsert_comments_empty() -> None:
    assert _MiniAdapter().upsert_summary_comments([]) == []


def test_base_fetch_commit_messages_default_empty() -> None:
    # Adapters without commit access degrade to a files-only overview.
    assert _MiniAdapter().fetch_commit_messages() == []


def test_base_set_labels_is_noop() -> None:
    # Adapters without label support skip silently (no raise).
    assert _MiniAdapter().set_labels(["prthinker/clean"]) is None


def test_base_update_body_section_is_noop() -> None:
    assert _MiniAdapter().update_body_section("digest") is None


def test_base_ci_failure_signals_default_empty(caplog) -> None:
    # Adapters without a CI API degrade to a review without failure context.
    with caplog.at_level("INFO"):
        assert _MiniAdapter().fetch_ci_failure_signals("sha") == []
    assert "does not support CI failure signals" in caplog.text


def test_base_upsert_comments_drops_overflow_pages(caplog) -> None:
    adapter = _MiniAdapter()
    with caplog.at_level("WARNING"):
        ids = adapter.upsert_summary_comments(["p1", "p2", "p3"])
    # Default supports one comment: posts the first, warns about the rest.
    assert ids == [1]
    assert adapter.posted == ["p1"]
    assert "overflow page(s) dropped" in caplog.text


def test_factory_respects_custom_base_url() -> None:
    adapter = create_platform_adapter(
        PlatformKind.GITHUB, repo="o/r", token=_TOK, pr_number=1,
        base_url="https://github.example.com/api/v3",
    )
    assert isinstance(adapter, GitHubAdapter)
    assert adapter.base_url == "https://github.example.com/api/v3"


def test_factory_passes_comment_marker_through() -> None:
    adapter = create_platform_adapter(
        PlatformKind.GITHUB, repo="o/r", token=_TOK, pr_number=1,
        comment_marker="<!-- custom-marker -->",
    )
    assert adapter.comment_marker == "<!-- custom-marker -->"


# ----- GitLab-specific construction details -----------------------------

def test_gitlab_project_path_is_url_encoded() -> None:
    adapter = GitLabAdapter(project="group/subgroup/proj", token=_TOK, mr_iid=42)
    assert adapter._project_quoted == urllib.parse.quote(  # noqa: SLF001
        "group/subgroup/proj", safe="",
    )
    # Should escape forward slashes — GitLab requires %2F.
    assert "%2F" in adapter._project_quoted


def test_gitlab_numeric_project_id_round_trips() -> None:
    adapter = GitLabAdapter(project="12345", token=_TOK, mr_iid=1)
    assert adapter._project_quoted == "12345"  # noqa: SLF001


def test_gitlab_uses_gitlab_dot_com_default_base(monkeypatch) -> None:
    monkeypatch.delenv("CI_API_V4_URL", raising=False)
    adapter = create_platform_adapter(
        PlatformKind.GITLAB, repo="g/p", token=_TOK, pr_number=1,
    )
    assert isinstance(adapter, GitLabAdapter)
    assert adapter.base_url.endswith("/api/v4")


def test_gitlab_autodetects_self_hosted_api_url(monkeypatch) -> None:
    # GitLab CI exposes the instance's API root; self-hosted pipelines
    # must not need an explicit --platform-base-url.
    monkeypatch.setenv("CI_API_V4_URL", "https://gitlab.example.com/api/v4")
    adapter = create_platform_adapter(
        PlatformKind.GITLAB, repo="g/p", token=_TOK, pr_number=1,
    )
    assert adapter.base_url == "https://gitlab.example.com/api/v4"


def test_gitlab_explicit_base_url_beats_ci_autodetect(monkeypatch) -> None:
    monkeypatch.setenv("CI_API_V4_URL", "https://gitlab.example.com/api/v4")
    adapter = create_platform_adapter(
        PlatformKind.GITLAB, repo="g/p", token=_TOK, pr_number=1,
        base_url="https://explicit.example.com/api/v4",
    )
    assert adapter.base_url == "https://explicit.example.com/api/v4"
