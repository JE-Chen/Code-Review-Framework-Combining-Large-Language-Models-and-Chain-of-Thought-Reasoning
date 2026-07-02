"""``_build_parser`` env-default resolution — the GitLab-CI frontend contract.

The ``.gitlab-ci.yml`` reference pipeline passes no ``--repo`` /
``--pr-number`` / ``--platform`` / token flags; it relies on the parser
resolving the GitLab-CI environment (``$CI_PROJECT_PATH``,
``$CI_MERGE_REQUEST_IID``, ``$GITLAB_TOKEN``) plus ``$PRTHINKER_PLATFORM``.
These tests lock that contract so a refactor can never silently stop
wiring up the non-GitHub frontend.
"""

from __future__ import annotations

import pytest

from prthinker.cli_parser import _build_parser

# Env vars that, if leaking from the host CI, would shadow the values
# under test. Cleared before each case so the test is hermetic.
_SHADOWING_VARS = (
    "GITHUB_REPOSITORY",
    "GITHUB_TOKEN",
    "PRTHINKER_PR_NUMBER",
    "PRTHINKER_PLATFORM",
    "CI_PROJECT_PATH",
    "CI_MERGE_REQUEST_IID",
    "GITLAB_TOKEN",
)


def _clear(monkeypatch: pytest.MonkeyPatch) -> None:
    for var in _SHADOWING_VARS:
        monkeypatch.delenv(var, raising=False)


def test_review_pr_resolves_gitlab_ci_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear(monkeypatch)
    monkeypatch.setenv("PRTHINKER_PLATFORM", "gitlab")
    monkeypatch.setenv("CI_PROJECT_PATH", "group/sub/proj")
    monkeypatch.setenv("CI_MERGE_REQUEST_IID", "77")
    monkeypatch.setenv("GITLAB_TOKEN", "glpat-fixture")

    args = _build_parser().parse_args(["review-pr"])

    assert args.platform == "gitlab"
    assert args.repo == "group/sub/proj"
    assert args.pr_number == 77
    assert args.github_token == "glpat-fixture"  # nosec B105 - test fixture token, not a credential


def test_review_pr_platform_defaults_to_github(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear(monkeypatch)
    args = _build_parser().parse_args(["review-pr"])
    assert args.platform == "github"


def test_pr_number_defaults_to_zero_without_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Neither forge's MR/PR identifier present — must clamp to 0, not crash.
    _clear(monkeypatch)
    args = _build_parser().parse_args(["review-pr"])
    assert args.pr_number == 0


def test_github_repository_takes_precedence_over_gitlab(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # When both forges' vars are present, GitHub wins (the ``or`` order).
    _clear(monkeypatch)
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/name")
    monkeypatch.setenv("CI_PROJECT_PATH", "group/proj")
    monkeypatch.setenv("GITHUB_TOKEN", "gh-fixture")
    monkeypatch.setenv("GITLAB_TOKEN", "gl-fixture")

    args = _build_parser().parse_args(["review-pr"])

    assert args.repo == "owner/name"
    assert args.github_token == "gh-fixture"  # nosec B105 - test fixture token, not a credential
