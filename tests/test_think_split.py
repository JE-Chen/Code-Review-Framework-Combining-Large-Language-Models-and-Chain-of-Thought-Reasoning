"""Tests for the torch-free reasoning-marker split helpers."""

from __future__ import annotations

from codes.util.think_split import (
    THINK_END_TOKEN,
    think_end_token_id,
    thinking_boundary,
)

_QWEN_THINK_END_ID = 151668


class _StubTokenizer:
    """Duck-typed tokenizer: a vocab dict plus an optional UNK fallback."""

    def __init__(self, vocab: dict[str, int], unk_id: int | None = None):
        self._vocab = vocab
        self._reverse = {v: k for k, v in vocab.items()}
        self._unk_id = unk_id

    def convert_tokens_to_ids(self, token: str) -> int | None:
        return self._vocab.get(token, self._unk_id)

    def convert_ids_to_tokens(self, token_id: int) -> str | None:
        return self._reverse.get(token_id, "<unk>")


# --- think_end_token_id --------------------------------------------------

def test_marker_resolved_from_vocab():
    tok = _StubTokenizer({THINK_END_TOKEN: _QWEN_THINK_END_ID})
    assert think_end_token_id(tok) == _QWEN_THINK_END_ID


def test_vocab_without_marker_and_no_unk_is_none():
    # Tokenizers without an UNK id return None for unknown tokens.
    tok = _StubTokenizer({"<eos>": 1})
    assert think_end_token_id(tok) is None


def test_marker_mapped_to_unk_is_rejected():
    # convert_tokens_to_ids silently maps missing tokens to the UNK id;
    # the round-trip check must reject that, not split on UNK.
    tok = _StubTokenizer({"<unk>": 0, "<eos>": 1}, unk_id=0)
    assert think_end_token_id(tok) is None


def test_negative_or_non_int_id_is_rejected():
    tok = _StubTokenizer({THINK_END_TOKEN: -1})
    assert think_end_token_id(tok) is None
    tok_str = _StubTokenizer({THINK_END_TOKEN: "151668"})  # type: ignore[dict-item]
    assert think_end_token_id(tok_str) is None


# --- thinking_boundary ----------------------------------------------------

def test_boundary_after_marker():
    ids = [10, 11, _QWEN_THINK_END_ID, 20, 21]
    assert thinking_boundary(ids, _QWEN_THINK_END_ID) == 3


def test_boundary_uses_last_marker():
    ids = [_QWEN_THINK_END_ID, 10, _QWEN_THINK_END_ID, 20]
    assert thinking_boundary(ids, _QWEN_THINK_END_ID) == 3


def test_boundary_marker_at_end_means_all_thinking():
    ids = [10, 11, _QWEN_THINK_END_ID]
    assert thinking_boundary(ids, _QWEN_THINK_END_ID) == len(ids)


def test_no_marker_in_output_is_zero():
    assert thinking_boundary([10, 11, 12], _QWEN_THINK_END_ID) == 0


def test_none_marker_id_is_zero():
    # Vocabulary without the marker (e.g. Gemma): whole output is content.
    assert thinking_boundary([10, 11, 12], None) == 0


def test_empty_output_is_zero():
    assert thinking_boundary([], _QWEN_THINK_END_ID) == 0
    assert thinking_boundary([], None) == 0
