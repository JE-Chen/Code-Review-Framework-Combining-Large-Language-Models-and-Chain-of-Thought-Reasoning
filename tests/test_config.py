"""Typed env-var readers in ``prthinker.config`` (env_int / env_float / env_path)."""

from __future__ import annotations

from pathlib import Path

import pytest

from prthinker.config import env_float, env_int, env_path

_VAR = "PRTHINKER_TEST_ENV_READER"


@pytest.fixture(autouse=True)
def _clean_var(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv(_VAR, raising=False)


# --- env_int -----------------------------------------------------------------

def test_env_int_unset_returns_default() -> None:
    assert env_int(_VAR, 42) == 42


def test_env_int_empty_returns_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(_VAR, "")
    assert env_int(_VAR, 42) == 42


def test_env_int_whitespace_returns_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(_VAR, "   ")
    assert env_int(_VAR, 42) == 42


def test_env_int_parses_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(_VAR, "7")
    assert env_int(_VAR, 42) == 7


def test_env_int_parses_zero_and_negative(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(_VAR, "0")
    assert env_int(_VAR, 42) == 0
    monkeypatch.setenv(_VAR, "-3")
    assert env_int(_VAR, 42) == -3


def test_env_int_invalid_returns_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(_VAR, "not-a-number")
    assert env_int(_VAR, 42) == 42


def test_env_int_float_string_returns_default(monkeypatch: pytest.MonkeyPatch) -> None:
    # int() rejects "3.5"; the reader clamps to the default instead of raising.
    monkeypatch.setenv(_VAR, "3.5")
    assert env_int(_VAR, 42) == 42


# --- env_float ---------------------------------------------------------------

def test_env_float_unset_returns_default() -> None:
    assert env_float(_VAR, 0.7) == 0.7


def test_env_float_empty_returns_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(_VAR, "")
    assert env_float(_VAR, 0.7) == 0.7


def test_env_float_parses_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(_VAR, "0.85")
    assert env_float(_VAR, 0.7) == 0.85


def test_env_float_parses_int_string(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(_VAR, "4")
    assert env_float(_VAR, 0.7) == 4.0


def test_env_float_invalid_returns_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(_VAR, "seven")
    assert env_float(_VAR, 0.7) == 0.7


# --- env_path ----------------------------------------------------------------

def test_env_path_unset_returns_default() -> None:
    assert env_path(_VAR, ".prthinker/x.sqlite") == Path(".prthinker/x.sqlite")


def test_env_path_empty_returns_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(_VAR, "")
    assert env_path(_VAR, ".prthinker/x.sqlite") == Path(".prthinker/x.sqlite")


def test_env_path_whitespace_returns_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(_VAR, "  ")
    assert env_path(_VAR, "fallback") == Path("fallback")


def test_env_path_returns_env_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(_VAR, "custom/store.sqlite")
    assert env_path(_VAR, "fallback") == Path("custom/store.sqlite")


def test_env_path_always_returns_path_type(monkeypatch: pytest.MonkeyPatch) -> None:
    assert isinstance(env_path(_VAR, "d"), Path)
    monkeypatch.setenv(_VAR, "v")
    assert isinstance(env_path(_VAR, "d"), Path)
