"""``.prthinker.yaml`` loading.

Two foot-guns specifically:
* YAML 1.1 treats unquoted ``on`` as boolean ``True``. The schema uses
  ``severity`` to dodge this — make sure regressions don't reintroduce it.
* Unknown keys must raise (not silently ignore).
"""

from __future__ import annotations

import textwrap

import pytest

from prthinker.repo_config import (
    RepoConfig,
    load_repo_config,
    to_argparse_defaults,
)


def _write(tmp_path, text: str):
    p = tmp_path / ".prthinker.yaml"
    p.write_text(textwrap.dedent(text), encoding="utf-8")
    return p


def test_empty_file_yields_defaults(tmp_path) -> None:
    p = _write(tmp_path, "")
    cfg = load_repo_config(p)
    assert cfg.backend == "remote"
    assert cfg.per_file is False
    assert cfg.gate.severity == "none"


def test_gate_severity_uses_string_not_boolean(tmp_path) -> None:
    # YAML 1.1: `on: error` would be parsed as `{True: "error"}`.
    # We use ``severity:`` to dodge that.
    p = _write(tmp_path, """
        gate:
          severity: error
    """)
    cfg = load_repo_config(p)
    assert cfg.gate.severity == "error"


def test_unknown_key_is_rejected(tmp_path) -> None:
    p = _write(tmp_path, "totally_made_up_key: 7")
    with pytest.raises(Exception):
        load_repo_config(p)


def test_unknown_subkey_is_rejected(tmp_path) -> None:
    p = _write(tmp_path, """
        cache:
          enable: true   # typo: should be enabled
    """)
    with pytest.raises(Exception):
        load_repo_config(p)


def test_to_argparse_defaults_translates_keys() -> None:
    cfg = RepoConfig.model_validate({
        "backend": "openai",
        "per_file": True,
        "gate": {"severity": "error"},
        "cache": {"enabled": True, "ttl_days": 14},
        "telemetry": {"enabled": True},
        "openai": {"model": "gpt-4o"},
    })
    defaults = to_argparse_defaults(cfg)
    assert defaults["backend"] == "openai"
    assert defaults["per_file"] is True
    assert defaults["gate_on"] == "error"
    assert defaults["cache_enabled"] is True
    assert defaults["cache_ttl_days"] == 14
    assert defaults["telemetry_enabled"] is True
    assert defaults["openai_model"] == "gpt-4o"


def test_none_values_are_stripped_so_argparse_keeps_its_defaults() -> None:
    # ``rules_dir`` is unset → should not appear in defaults at all,
    # so argparse's own default (None) wins instead of being clobbered.
    cfg = RepoConfig()
    defaults = to_argparse_defaults(cfg)
    assert "rules_dir" not in defaults
