"""Unit tests for the self-consistency sampling helper."""

from __future__ import annotations

from prthinker.self_consistency import _normalize, self_consistent_generate


class _ScriptedBackend:
    """Returns a scripted list of outputs and records call count."""

    def __init__(self, outputs: list[str]) -> None:
        self._outputs = list(outputs)
        self.calls = 0

    def generate(self, prompt: str, max_new_tokens: int) -> str:
        del prompt, max_new_tokens
        self.calls += 1
        return self._outputs.pop(0)


def test_majority_two_vs_one() -> None:
    backend = _ScriptedBackend(["yes", "no", "yes"])
    result = self_consistent_generate(backend, "p", k=3)
    assert result == "yes"
    assert backend.calls == 3


def test_k_one_single_call() -> None:
    backend = _ScriptedBackend(["only"])
    result = self_consistent_generate(backend, "p", k=1)
    assert result == "only"
    assert backend.calls == 1


def test_all_distinct_returns_first() -> None:
    backend = _ScriptedBackend(["alpha", "beta", "gamma"])
    result = self_consistent_generate(backend, "p", k=3)
    assert result == "alpha"
    assert backend.calls == 3


def test_normalization_groups_variants() -> None:
    # "Yes." and "yes" share a normalized key, beating the single "no".
    backend = _ScriptedBackend(["Yes.", "no", "yes"])
    result = self_consistent_generate(backend, "p", k=3)
    assert result == "Yes."
    assert backend.calls == 3


def test_normalize_helper() -> None:
    assert _normalize("  Yes \n there ") == "yes there"
    assert _normalize("YES") == _normalize("yes")
