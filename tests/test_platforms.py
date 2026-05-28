"""Platform Strategy — factory dispatch + GitLab adapter wiring.

Network calls are not exercised here (no mock-httpx fixture);
construction + URL building + payload shapes ARE.
"""

from __future__ import annotations

import urllib.parse

import pytest

from reviewmind.platforms import PlatformKind, create_platform_adapter
from reviewmind.platforms.base import PlatformAdapter
from reviewmind.platforms.github import GitHubAdapter
from reviewmind.platforms.gitlab import GitLabAdapter


def test_factory_dispatches_to_github() -> None:
    adapter = create_platform_adapter(
        PlatformKind.GITHUB, repo="o/r", token="t", pr_number=1,
    )
    assert isinstance(adapter, GitHubAdapter)
    assert isinstance(adapter, PlatformAdapter)


def test_factory_dispatches_to_gitlab() -> None:
    adapter = create_platform_adapter(
        PlatformKind.GITLAB, repo="group/project", token="t", pr_number=1,
    )
    assert isinstance(adapter, GitLabAdapter)
    assert isinstance(adapter, PlatformAdapter)


def test_factory_rejects_unknown_kind() -> None:
    with pytest.raises(ValueError):
        # Force a value that isn't in the enum.
        create_platform_adapter("svn", repo="r", token="t", pr_number=1)  # type: ignore[arg-type]


def test_factory_respects_custom_base_url() -> None:
    adapter = create_platform_adapter(
        PlatformKind.GITHUB, repo="o/r", token="t", pr_number=1,
        base_url="https://github.example.com/api/v3",
    )
    assert isinstance(adapter, GitHubAdapter)
    assert adapter.base_url == "https://github.example.com/api/v3"


def test_factory_passes_comment_marker_through() -> None:
    adapter = create_platform_adapter(
        PlatformKind.GITHUB, repo="o/r", token="t", pr_number=1,
        comment_marker="<!-- custom-marker -->",
    )
    assert adapter.comment_marker == "<!-- custom-marker -->"


# ----- GitLab-specific construction details -----------------------------

def test_gitlab_project_path_is_url_encoded() -> None:
    adapter = GitLabAdapter(project="group/subgroup/proj", token="t", mr_iid=42)
    assert adapter._project_quoted == urllib.parse.quote(  # noqa: SLF001
        "group/subgroup/proj", safe="",
    )
    # Should escape forward slashes — GitLab requires %2F.
    assert "%2F" in adapter._project_quoted


def test_gitlab_numeric_project_id_round_trips() -> None:
    adapter = GitLabAdapter(project="12345", token="t", mr_iid=1)
    assert adapter._project_quoted == "12345"  # noqa: SLF001


def test_gitlab_uses_gitlab_dot_com_default_base() -> None:
    adapter = create_platform_adapter(
        PlatformKind.GITLAB, repo="g/p", token="t", pr_number=1,
    )
    assert isinstance(adapter, GitLabAdapter)
    assert adapter.base_url.endswith("/api/v4")
