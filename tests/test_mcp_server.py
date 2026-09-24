"""Tests for the MCP server's environment-driven Config construction."""

from __future__ import annotations

import builtins
import os
import sys
from pathlib import Path

import anyio
import pytest

from prthinker import mcp_server
from prthinker.config import BackendKind


@pytest.fixture(autouse=True)
def _clear_prthinker_env(monkeypatch):
    """Drop every PRTHINKER_*/provider env var so each test starts clean."""
    import os

    for name in list(os.environ):
        if name.startswith("PRTHINKER_") or name in {
            "OPENAI_API_KEY",
            "OPENAI_ORG_ID",
            "ANTHROPIC_API_KEY",
        }:
            monkeypatch.delenv(name, raising=False)


def test_default_backend_is_remote_requires_url(monkeypatch):
    """Default backend is remote and demands PRTHINKER_REMOTE_URL."""
    with pytest.raises(RuntimeError, match="PRTHINKER_REMOTE_URL is required"):
        mcp_server._config_from_env()


def test_remote_backend_happy_path(monkeypatch):
    monkeypatch.setenv("PRTHINKER_REMOTE_URL", "https://example.test")
    monkeypatch.setenv("PRTHINKER_REMOTE_API_KEY", "secret")
    monkeypatch.setenv("PRTHINKER_REMOTE_TIMEOUT", "123")
    cfg = mcp_server._config_from_env()
    assert cfg.backend is BackendKind.REMOTE
    assert cfg.remote is not None
    assert cfg.remote.url == "https://example.test"
    assert cfg.remote.api_key == "secret"
    assert cfg.remote.timeout_seconds == 123.0
    assert cfg.local is None
    assert cfg.openai is None
    assert cfg.anthropic is None


def test_local_backend(monkeypatch):
    monkeypatch.setenv("PRTHINKER_BACKEND", "local")
    monkeypatch.setenv("PRTHINKER_MODEL_NAME", "my/model")
    monkeypatch.setenv("PRTHINKER_LORA_PATH", "/data/lora")
    cfg = mcp_server._config_from_env()
    assert cfg.backend is BackendKind.LOCAL
    assert cfg.local is not None
    assert cfg.local.model_name == "my/model"
    assert cfg.local.lora_path == "/data/lora"


def test_local_backend_default_model(monkeypatch):
    monkeypatch.setenv("PRTHINKER_BACKEND", "local")
    cfg = mcp_server._config_from_env()
    assert cfg.local is not None
    assert cfg.local.model_name == "Qwen/Qwen3-Coder-30B-A3B-Instruct"
    assert cfg.local.lora_path is None


def test_openai_backend_happy_path(monkeypatch):
    monkeypatch.setenv("PRTHINKER_BACKEND", "openai")
    monkeypatch.setenv("PRTHINKER_OPENAI_API_KEY", "k1")
    monkeypatch.setenv("PRTHINKER_OPENAI_MODEL", "gpt-x")
    monkeypatch.setenv("PRTHINKER_OPENAI_BASE_URL", "https://oai.test/v1")
    monkeypatch.setenv("PRTHINKER_OPENAI_ORGANIZATION", "org-1")
    cfg = mcp_server._config_from_env()
    assert cfg.backend is BackendKind.OPENAI
    assert cfg.openai is not None
    assert cfg.openai.api_key == "k1"
    assert cfg.openai.model == "gpt-x"
    assert cfg.openai.base_url == "https://oai.test/v1"
    assert cfg.openai.organization == "org-1"


def test_openai_backend_falls_back_to_standard_env(monkeypatch):
    monkeypatch.setenv("PRTHINKER_BACKEND", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "fallback")
    monkeypatch.setenv("OPENAI_ORG_ID", "org-fallback")
    cfg = mcp_server._config_from_env()
    assert cfg.openai is not None
    assert cfg.openai.api_key == "fallback"
    assert cfg.openai.organization == "org-fallback"
    assert cfg.openai.model == "gpt-4o-mini"
    assert cfg.openai.base_url == "https://api.openai.com/v1"


def test_openai_backend_missing_key_raises(monkeypatch):
    monkeypatch.setenv("PRTHINKER_BACKEND", "openai")
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY is required"):
        mcp_server._config_from_env()


def test_anthropic_backend_happy_path(monkeypatch):
    monkeypatch.setenv("PRTHINKER_BACKEND", "anthropic")
    monkeypatch.setenv("PRTHINKER_ANTHROPIC_API_KEY", "ak")
    monkeypatch.setenv("PRTHINKER_ANTHROPIC_MODEL", "claude-x")
    monkeypatch.setenv("PRTHINKER_ANTHROPIC_BASE_URL", "https://anthropic.test")
    monkeypatch.setenv("PRTHINKER_ANTHROPIC_VERSION", "2099-01-01")
    cfg = mcp_server._config_from_env()
    assert cfg.backend is BackendKind.ANTHROPIC
    assert cfg.anthropic is not None
    assert cfg.anthropic.api_key == "ak"
    assert cfg.anthropic.model == "claude-x"
    assert cfg.anthropic.base_url == "https://anthropic.test"
    assert cfg.anthropic.anthropic_version == "2099-01-01"


def test_anthropic_backend_defaults_and_fallback(monkeypatch):
    monkeypatch.setenv("PRTHINKER_BACKEND", "anthropic")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "ak-fallback")
    cfg = mcp_server._config_from_env()
    assert cfg.anthropic is not None
    assert cfg.anthropic.api_key == "ak-fallback"
    assert cfg.anthropic.model == "claude-opus-4-7"
    assert cfg.anthropic.base_url == "https://api.anthropic.com"
    assert cfg.anthropic.anthropic_version == "2023-06-01"


def test_anthropic_backend_missing_key_raises(monkeypatch):
    monkeypatch.setenv("PRTHINKER_BACKEND", "anthropic")
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY is required"):
        mcp_server._config_from_env()


def test_shared_config_fields(monkeypatch):
    monkeypatch.setenv("PRTHINKER_REMOTE_URL", "https://example.test")
    monkeypatch.setenv("PRTHINKER_RAG_ENABLED", "false")
    monkeypatch.setenv("PRTHINKER_RAG_THRESHOLD", "0.55")
    monkeypatch.setenv("PRTHINKER_MAX_NEW_TOKENS", "100")
    monkeypatch.setenv("PRTHINKER_CACHE_ENABLED", "true")
    monkeypatch.setenv("PRTHINKER_CACHE_PATH", "/data/c.sqlite")
    monkeypatch.setenv("PRTHINKER_TELEMETRY_ENABLED", "true")
    monkeypatch.setenv("PRTHINKER_TELEMETRY_PATH", "/data/t.sqlite")
    cfg = mcp_server._config_from_env()
    assert cfg.rag_enabled is False
    assert cfg.rag_threshold == 0.55
    assert cfg.max_new_tokens == 100
    assert cfg.cache.enabled is True
    assert cfg.cache.path == "/data/c.sqlite"
    assert cfg.telemetry.enabled is True
    assert cfg.telemetry.path == "/data/t.sqlite"


def test_shared_config_defaults(monkeypatch):
    monkeypatch.setenv("PRTHINKER_REMOTE_URL", "https://example.test")
    cfg = mcp_server._config_from_env()
    assert cfg.rag_enabled is True
    assert cfg.rag_threshold == 0.7
    assert cfg.max_new_tokens == 32768
    assert cfg.cache.enabled is False
    assert cfg.cache.path == ".prthinker/cache.sqlite"
    assert cfg.telemetry.enabled is False
    assert cfg.telemetry.path == ".prthinker/telemetry.sqlite"


REPO_ROOT = Path(__file__).resolve().parents[1]
MCP_TOOLS = {"review_diff", "triage_diff", "evaluate_retrieval", "make_review_attestation", "stats"}


def test_mcp_extra_allows_both_sdk_lines():
    """``prthinker mcp`` runs on the 1.x ``FastMCP`` and the 2.x ``MCPServer``."""
    import tomllib

    from packaging.requirements import Requirement

    with (REPO_ROOT / "pyproject.toml").open("rb") as handle:
        specs = tomllib.load(handle)["project"]["optional-dependencies"]["mcp"]
    requirement = Requirement(specs[0])
    assert requirement.name == "mcp"
    assert requirement.specifier.contains("1.30.0")
    assert requirement.specifier.contains("2.2.0")
    assert not requirement.specifier.contains("1.28.0")
    assert not requirement.specifier.contains("3.0.0")


def test_run_names_the_sdk_version_it_needs(monkeypatch, capsys):
    """Without either server class the message names the SDK range to install."""
    real_import = builtins.__import__

    def _no_fastmcp(name, *args, **kwargs):
        if name in ("mcp.server.fastmcp", "mcp.server.mcpserver"):
            raise ModuleNotFoundError(f"No module named {name!r}")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _no_fastmcp)
    assert mcp_server.run() == 1
    assert "mcp>=1.28.1,<3" in capsys.readouterr().err


def test_stdio_round_trip_with_the_official_client(tmp_path):
    """Start ``prthinker mcp`` and drive it the way an MCP host does."""
    pytest.importorskip("mcp")
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    env = {
        key: value for key, value in os.environ.items()
        if not key.startswith("PRTHINKER_") and key not in {"OPENAI_API_KEY", "ANTHROPIC_API_KEY"}
    }
    env["PYTHONPATH"] = os.pathsep.join(filter(None, [str(REPO_ROOT), env.get("PYTHONPATH")]))
    env["PRTHINKER_REMOTE_URL"] = "https://example.test"
    params = StdioServerParameters(
        command=sys.executable, args=["-m", "prthinker", "mcp"], env=env, cwd=str(tmp_path))

    async def _list_tools() -> set:
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                return {tool.name for tool in (await session.list_tools()).tools}

    assert anyio.run(_list_tools) == MCP_TOOLS
