"""Unit tests for :mod:`prthinker.backends.ensemble`."""

from __future__ import annotations

from typing import Iterator

import pytest

from prthinker.backends.base import InferenceBackend
from prthinker.backends.ensemble import EnsembleBackend


class _StubBackend(InferenceBackend):
    """Returns a canned string, or raises if configured to."""

    def __init__(
        self,
        output: str = "",
        *,
        raises: bool = False,
        kind: str = "stub",
        model: str = "stub-1",
    ) -> None:
        self._output = output
        self._raises = raises
        self._kind = kind
        self._model = model

    def generate(
        self,
        prompt: str,
        max_new_tokens: int,
        *,
        cancel_event: object | None = None,
    ) -> str:
        del prompt, max_new_tokens, cancel_event
        if self._raises:
            raise ValueError("stub failure")
        return self._output

    def stream_generate(
        self, prompt: str, max_new_tokens: int
    ) -> Iterator[str]:
        del prompt, max_new_tokens
        yield f"stream:{self._output}"

    def backend_kind(self) -> str:
        return self._kind

    def model_name(self) -> str:
        return self._model


def _run(backends: tuple[InferenceBackend, ...], policy: str) -> str:
    return EnsembleBackend(backends, policy=policy).generate("p", 16)


def test_longest_policy_picks_longest() -> None:
    backends = (_StubBackend("ab"), _StubBackend("abcd"), _StubBackend("a"))
    assert _run(backends, "longest") == "abcd"


def test_first_policy_picks_first() -> None:
    backends = (_StubBackend("first"), _StubBackend("second-longer"))
    assert _run(backends, "first") == "first"


def test_majority_picks_modal_output() -> None:
    backends = (
        _StubBackend("yes"),
        _StubBackend("no"),
        _StubBackend("yes"),
    )
    assert _run(backends, "majority") == "yes"


def test_majority_tie_resolves_to_earliest() -> None:
    backends = (_StubBackend("alpha"), _StubBackend("beta"))
    assert _run(backends, "majority") == "alpha"


def test_raising_backend_is_skipped() -> None:
    backends = (
        _StubBackend(raises=True),
        _StubBackend("survivor"),
    )
    assert _run(backends, "longest") == "survivor"


def test_all_raise_propagates() -> None:
    backends = (_StubBackend(raises=True), _StubBackend(raises=True))
    with pytest.raises(RuntimeError, match="all ensemble backends failed"):
        _run(backends, "longest")


def test_unknown_policy_raises_value_error() -> None:
    with pytest.raises(ValueError, match="unknown policy"):
        EnsembleBackend((_StubBackend("x"),), policy="bogus")


def test_empty_backends_raises_value_error() -> None:
    with pytest.raises(ValueError, match="at least one backend"):
        EnsembleBackend((), policy="first")


def test_stream_delegates_to_first_backend() -> None:
    backend = EnsembleBackend(
        (_StubBackend("a"), _StubBackend("b")), policy="first"
    )
    assert list(backend.stream_generate("p", 8)) == ["stream:a"]


def test_backend_kind_and_model_name() -> None:
    backend = EnsembleBackend(
        (_StubBackend("x", model="m1"), _StubBackend("y", model="m2")),
        policy="longest",
    )
    assert backend.backend_kind() == "ensemble"
    assert backend.model_name() == "ensemble[longest](m1, m2)"
