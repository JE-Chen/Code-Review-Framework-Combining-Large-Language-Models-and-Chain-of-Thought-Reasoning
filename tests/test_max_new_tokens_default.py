"""Lock the review ``max_new_tokens`` default at 8192.

A per-file CoT review fans a prompt through ~9 sequential steps; on the
single-card GPU backend each step generated up to the old 32768-token cap,
pushing a file past 15 minutes and risking the per-file poll budget. The
default was halved to 8192 — this test pins every declaration in the review
chain so a future edit cannot silently drift one of them back up.
"""

from __future__ import annotations

import argparse

from prthinker.cli_parser_groups import add_rag_args
from prthinker.config import BackendKind, Config, RemoteBackendConfig
from prthinker.repo_config import RepoConfig
from prthinker.schemas import ReviewRequest

_REVIEW_DEFAULT = 8192


def test_config_default():
    cfg = Config(
        backend=BackendKind.REMOTE,
        remote=RemoteBackendConfig(url="https://example.test"),
    )
    assert cfg.max_new_tokens == _REVIEW_DEFAULT


def test_review_request_wire_default():
    assert ReviewRequest(code_diff="x").max_new_tokens == _REVIEW_DEFAULT


def test_repo_config_default():
    assert RepoConfig().max_new_tokens == _REVIEW_DEFAULT


def test_cli_parser_default_when_env_absent(monkeypatch):
    monkeypatch.delenv("PRTHINKER_MAX_NEW_TOKENS", raising=False)
    parser = argparse.ArgumentParser()
    add_rag_args(parser)
    args = parser.parse_args([])
    assert args.max_new_tokens == _REVIEW_DEFAULT


def test_cli_parser_env_override(monkeypatch):
    monkeypatch.setenv("PRTHINKER_MAX_NEW_TOKENS", "2048")
    parser = argparse.ArgumentParser()
    add_rag_args(parser)
    args = parser.parse_args([])
    assert args.max_new_tokens == 2048
