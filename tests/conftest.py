"""Shared fixtures.

A single ``FakeBackend`` covers every pipeline / cache / telemetry test
that would otherwise need a GPU or paid API key. Tests that need real
backends are out of scope here — they live in a separate marker
(currently unused) so the default ``pytest tests/`` run is fast,
deterministic, and offline.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable, Iterator

# Make ``prthinker`` importable when running pytest from the repo root
# without an editable install.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# Imports below depend on the sys.path insertion above.
import pytest  # noqa: E402

from prthinker.backends.base import InferenceBackend, Usage  # noqa: E402


class FakeBackend(InferenceBackend):
    """Returns canned responses; records every call for assertions.

    Usage:
        backend = FakeBackend(["first", "second"])
        backend.generate("...", 100)  # → "first"
        backend.generate("...", 100)  # → "second"
        backend.generate("...", 100)  # → "fake" (default once exhausted)

    Set ``usage_per_call`` to a list of ``Usage`` objects to drive
    telemetry tests; otherwise ``last_usage()`` returns ``None`` like a
    local backend.
    """

    def __init__(
        self,
        responses: Iterable[str] | None = None,
        *,
        kind: str = "fake",
        model: str = "fake-1",
        usage_per_call: Iterable[Usage] | None = None,
    ) -> None:
        self._responses = list(responses or [])
        self._usage = list(usage_per_call or [])
        self._kind = kind
        self._model = model
        self.calls: list[tuple[str, int]] = []
        self._last_usage: Usage | None = None

    def backend_kind(self) -> str:
        return self._kind

    def model_name(self) -> str:
        return self._model

    def last_usage(self) -> Usage | None:
        return self._last_usage

    def generate(self, prompt: str, max_new_tokens: int) -> str:
        self.calls.append((prompt, max_new_tokens))
        if self._usage:
            self._last_usage = self._usage.pop(0)
        else:
            self._last_usage = None
        if self._responses:
            return self._responses.pop(0)
        return "fake response"

    def stream_generate(
        self, prompt: str, max_new_tokens: int
    ) -> Iterator[str]:
        # Default behaviour: yield the full text once so tests do not need
        # to special-case the streaming path.
        yield self.generate(prompt, max_new_tokens)


@pytest.fixture
def fake_backend() -> FakeBackend:
    return FakeBackend()


@pytest.fixture
def tmp_jsonl(tmp_path: Path) -> Path:
    return tmp_path / "store.jsonl"


@pytest.fixture
def tmp_cache_path(tmp_path: Path) -> Path:
    return tmp_path / "cache.sqlite"


@pytest.fixture
def tmp_telemetry_path(tmp_path: Path) -> Path:
    return tmp_path / "telemetry.sqlite"


@pytest.fixture
def tmp_rules_dir(tmp_path: Path) -> Path:
    rules = tmp_path / "rules"
    rules.mkdir()
    (rules / "010-imports.md").write_text(
        "Use pathlib, never os.path.\n", encoding="utf-8"
    )
    (rules / "020-logging.md").write_text(
        "Prefer logging over print.\n", encoding="utf-8"
    )
    return rules
