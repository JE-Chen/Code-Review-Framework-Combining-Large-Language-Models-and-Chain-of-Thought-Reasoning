"""Self-consistency sampling helper for prompt-in / text-out backends."""

from __future__ import annotations

import re
from collections import Counter
from typing import Protocol

_WHITESPACE_RE = re.compile(r"\s+")
_TRAILING_PUNCT = ".!?,;:"

_DEFAULT_K = 3
_DEFAULT_MAX_NEW_TOKENS = 1024


class _GenerateBackend(Protocol):
    """Structural type for any backend exposing ``generate``."""

    def generate(self, prompt: str, max_new_tokens: int) -> str:
        """Return generated text for ``prompt``."""


def _normalize(text: str) -> str:
    """Return a comparison key: lowercase, collapsed whitespace, no end punctuation."""
    collapsed = _WHITESPACE_RE.sub(" ", text).strip().lower()
    return collapsed.rstrip(_TRAILING_PUNCT).strip()


def self_consistent_generate(
    backend: _GenerateBackend,
    prompt: str,
    *,
    k: int = _DEFAULT_K,
    max_new_tokens: int = _DEFAULT_MAX_NEW_TOKENS,
) -> str:
    """Sample ``backend`` ``k`` times and return the majority output.

    Outputs are grouped by a normalized key (lowercase + collapsed
    whitespace); the original text of the most frequent group is
    returned. Ties are broken by first-seen order. When ``k <= 1`` a
    single call is made and its raw output returned unchanged.
    """
    if k <= 1:
        return backend.generate(prompt, max_new_tokens=max_new_tokens)

    samples = [
        backend.generate(prompt, max_new_tokens=max_new_tokens)
        for _ in range(k)
    ]
    counts: Counter[str] = Counter(_normalize(sample) for sample in samples)
    first_text_by_key: dict[str, str] = {}
    for sample in samples:
        first_text_by_key.setdefault(_normalize(sample), sample)

    best_key = max(samples, key=lambda sample: counts[_normalize(sample)])
    return first_text_by_key[_normalize(best_key)]
