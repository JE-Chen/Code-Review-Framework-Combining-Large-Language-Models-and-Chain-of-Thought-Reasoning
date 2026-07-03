"""Platform adapter Strategy — GitHub, GitLab, … behind one interface.

The pipeline depends only on :class:`PlatformAdapter`; concrete classes
live in this package. New platforms add a single file + one factory
branch.
"""

from __future__ import annotations

import os

from prthinker.platforms.base import PlatformAdapter, PlatformKind


def create_platform_adapter(
    kind: PlatformKind,
    *,
    repo: str,
    token: str,
    pr_number: int,
    comment_marker: str = "<!-- prthinker:summary -->",
    base_url: str | None = None,
) -> PlatformAdapter:
    """Lazy-import the concrete adapter so unused platforms add no cost."""
    if kind is PlatformKind.GITHUB:
        from prthinker.platforms.github import GitHubAdapter

        return GitHubAdapter(
            repo=repo, token=token, pr_number=pr_number,
            comment_marker=comment_marker,
            base_url=base_url or "https://api.github.com",
        )

    if kind is PlatformKind.GITLAB:
        from prthinker.platforms.gitlab import GitLabAdapter

        # GitLab CI exposes the instance's API root as CI_API_V4_URL, so
        # self-hosted pipelines work without an explicit --platform-base-url.
        return GitLabAdapter(
            project=repo, token=token, mr_iid=pr_number,
            comment_marker=comment_marker,
            base_url=(
                base_url
                or os.environ.get("CI_API_V4_URL")
                or "https://gitlab.com/api/v4"
            ),
        )

    if kind is PlatformKind.GITEA:
        from prthinker.platforms.gitea import GiteaAdapter

        return GiteaAdapter(
            repo=repo, token=token, pr_number=pr_number,
            comment_marker=comment_marker,
            base_url=base_url or "https://gitea.com/api/v1",
        )

    raise ValueError(f"Unsupported platform: {kind!r}")


__all__ = [
    "PlatformAdapter",
    "PlatformKind",
    "create_platform_adapter",
]
