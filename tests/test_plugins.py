"""Unit tests for the third-party review-step plugin loader."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from importlib import metadata
from typing import Callable

import pytest

from prthinker import plugins


@dataclass(frozen=True)
class _FakeEntryPoint:
    """Minimal stand-in for ``importlib.metadata.EntryPoint``."""

    name: str
    _loader: Callable[[], object]

    def load(self) -> object:
        return self._loader()


def _good_loader() -> object:
    return object()


def _bad_loader() -> object:
    raise ImportError("broken plugin module")


def _patch_entry_points(
    monkeypatch: pytest.MonkeyPatch, points: list[_FakeEntryPoint]
) -> None:
    def fake_entry_points(*, group: str) -> list[_FakeEntryPoint]:
        if group == plugins.PLUGIN_STEPS_GROUP:
            return points
        return []

    monkeypatch.setattr(metadata, "entry_points", fake_entry_points)


def test_loads_good_and_swallows_bad(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    points = [
        _FakeEntryPoint("good_step", _good_loader),
        _FakeEntryPoint("bad_step", _bad_loader),
    ]
    _patch_entry_points(monkeypatch, points)

    with caplog.at_level(logging.WARNING):
        loaded = plugins.load_plugin_steps()

    assert loaded == ["good_step"]
    assert "bad_step" in caplog.text


def test_empty_entry_points(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_entry_points(monkeypatch, [])
    assert plugins.load_plugin_steps() == []


def test_all_good(monkeypatch: pytest.MonkeyPatch) -> None:
    points = [
        _FakeEntryPoint("alpha", _good_loader),
        _FakeEntryPoint("beta", _good_loader),
    ]
    _patch_entry_points(monkeypatch, points)
    assert plugins.load_plugin_steps() == ["alpha", "beta"]


def test_all_bad_returns_empty(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    points = [
        _FakeEntryPoint("x", _bad_loader),
        _FakeEntryPoint("y", _bad_loader),
    ]
    _patch_entry_points(monkeypatch, points)
    with caplog.at_level(logging.WARNING):
        assert plugins.load_plugin_steps() == []
    assert "x" in caplog.text
    assert "y" in caplog.text
