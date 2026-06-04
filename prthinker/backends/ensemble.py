"""Ensemble backend that queries several backends and picks one answer.

Pure composition over :class:`InferenceBackend`: it fans a single prompt
out to every wrapped backend, tolerates individual failures (logging and
skipping them), and selects one result according to a configurable policy.

Policies:

- ``"longest"`` — return the longest output (most detailed reviewer wins).
- ``"first"`` — return the first backend's output that did not raise.
- ``"majority"`` — return the most common normalized output; ties resolve
  to the earliest such output in call order.

The selector is runner-safe: stdlib only, no heavy ML imports, and it
never runs inference itself — that lives entirely in the wrapped backends.
"""

from __future__ import annotations

import logging
from collections import Counter
from typing import Iterator

from prthinker.backends.base import InferenceBackend

log = logging.getLogger(__name__)

_POLICY_LONGEST = "longest"
_POLICY_FIRST = "first"
_POLICY_MAJORITY = "majority"
_VALID_POLICIES = (_POLICY_LONGEST, _POLICY_FIRST, _POLICY_MAJORITY)


class EnsembleBackend(InferenceBackend):
    """Fan a prompt out to several backends and select one answer."""

    def __init__(
        self,
        backends: tuple[InferenceBackend, ...],
        policy: str = _POLICY_LONGEST,
    ) -> None:
        if not backends:
            raise ValueError("EnsembleBackend requires at least one backend")
        if policy not in _VALID_POLICIES:
            raise ValueError(
                f"unknown policy {policy!r}; expected one of {_VALID_POLICIES}"
            )
        self._backends = backends
        self._policy = policy

    def generate(
        self,
        prompt: str,
        max_new_tokens: int,
        *,
        cancel_event: object | None = None,
    ) -> str:
        """Query every backend and select one output per the policy."""
        results = self._collect(prompt, max_new_tokens, cancel_event)
        if not results:
            raise RuntimeError("all ensemble backends failed to generate")
        return self._select(results)

    def _collect(
        self,
        prompt: str,
        max_new_tokens: int,
        cancel_event: object | None,
    ) -> list[str]:
        """Call each backend, skipping (and logging) the ones that raise."""
        results: list[str] = []
        for backend in self._backends:
            try:
                output = backend.generate(
                    prompt, max_new_tokens, cancel_event=cancel_event
                )
            except Exception:  # noqa: BLE001 — tolerate one bad backend
                log.warning(
                    "ensemble backend %s failed; skipping",
                    backend.backend_kind(),
                    exc_info=True,
                )
                continue
            results.append(output)
        return results

    def _select(self, results: list[str]) -> str:
        """Apply the configured policy to the successful outputs."""
        if self._policy == _POLICY_FIRST:
            return results[0]
        if self._policy == _POLICY_LONGEST:
            return max(results, key=len)
        return self._select_majority(results)

    @staticmethod
    def _select_majority(results: list[str]) -> str:
        """Return the modal output; ties resolve to the earliest output."""
        normalized = [text.strip() for text in results]
        counts = Counter(normalized)
        winner = max(normalized, key=lambda text: (counts[text], -normalized.index(text)))
        return results[normalized.index(winner)]

    def stream_generate(
        self, prompt: str, max_new_tokens: int
    ) -> Iterator[str]:
        """Delegate streaming to the first wrapped backend."""
        return self._backends[0].stream_generate(prompt, max_new_tokens)

    def backend_kind(self) -> str:
        return "ensemble"

    def model_name(self) -> str:
        summary = ", ".join(
            backend.model_name() for backend in self._backends
        )
        return f"ensemble[{self._policy}]({summary})"

    def close(self) -> None:
        for backend in self._backends:
            backend.close()
