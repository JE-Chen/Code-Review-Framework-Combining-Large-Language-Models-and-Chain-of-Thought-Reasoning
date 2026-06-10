"""Pure helpers for splitting generated ids at the reasoning-close marker.

Deliberately free of ``torch`` / ``transformers`` imports (the tokenizer
is duck-typed) so the split rule can be unit-tested without the GPU
stack, mirroring ``quant_guard``. Qwen3 vocabularies carry a literal
``</think>`` special token that closes the reasoning segment; model
families without one (e.g. Gemma) resolve to None and the caller treats
the entire generation as content instead of splitting.
"""

from __future__ import annotations

THINK_END_TOKEN = "</think>"


def think_end_token_id(tokenizer) -> int | None:
    """Vocab id of the reasoning-close marker, or None when absent.

    ``convert_tokens_to_ids`` maps tokens missing from the vocabulary to
    the UNK id (or None on tokenizers without one); the round-trip check
    rejects that so a vocabulary lacking a literal ``</think>`` token
    never yields a bogus split id.
    """
    token_id = tokenizer.convert_tokens_to_ids(THINK_END_TOKEN)
    if not isinstance(token_id, int) or token_id < 0:
        return None
    if tokenizer.convert_ids_to_tokens(token_id) != THINK_END_TOKEN:
        return None
    return token_id


def thinking_boundary(output_ids: list[int], think_end_id: int | None) -> int:
    """Index one past the LAST reasoning-close marker, or 0 when absent.

    Everything before the boundary is thinking, everything at and after
    it is content — matching the "reasoning, ``</think>``, answer" output
    layout of Qwen3-style models. A None ``think_end_id`` (vocabulary has
    no marker) or a generation without the marker both yield 0, i.e. the
    whole output is content.
    """
    if think_end_id is None:
        return 0
    try:
        return len(output_ids) - output_ids[::-1].index(think_end_id)
    except ValueError:
        return 0


__all__ = ["THINK_END_TOKEN", "think_end_token_id", "thinking_boundary"]
