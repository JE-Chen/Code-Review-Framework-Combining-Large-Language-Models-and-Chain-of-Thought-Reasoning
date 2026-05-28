"""Pre-commit hook subcommand wiring.

We don't exercise the full git path (would need a real repo + staged
diff); we exercise the argparse shape so the manifest in
``.pre-commit-hooks.yaml`` keeps pointing at a valid entry.
"""

from __future__ import annotations

import pytest

from prthinker.cli import _build_parser


def test_hook_subcommand_is_registered() -> None:
    p = _build_parser()
    sub_action = next(
        a for a in p._actions  # noqa: SLF001
        if getattr(a, "choices", None) and "review-pr" in a.choices
    )
    assert "hook" in sub_action.choices


def test_hook_inherits_backend_flags() -> None:
    p = _build_parser()
    ns = p.parse_args([
        "hook",
        "--backend", "openai",
        "--openai-api-key", "k",
    ])
    assert ns.command == "hook"
    assert ns.backend == "openai"
    assert ns.openai_api_key == "k"


def test_hook_default_block_on_error() -> None:
    p = _build_parser()
    ns = p.parse_args([
        "hook",
        "--backend", "remote", "--remote-url", "http://x",
    ])
    assert ns.block_on == "error"
    assert ns.advisory is False


def test_hook_advisory_mode_flag_parses() -> None:
    p = _build_parser()
    ns = p.parse_args([
        "hook", "--advisory",
        "--backend", "remote", "--remote-url", "http://x",
    ])
    assert ns.advisory is True


@pytest.mark.parametrize("severity", ["none", "warning", "error"])
def test_hook_block_on_accepts_all_levels(severity: str) -> None:
    p = _build_parser()
    ns = p.parse_args([
        "hook", "--block-on", severity,
        "--backend", "remote", "--remote-url", "http://x",
    ])
    assert ns.block_on == severity
