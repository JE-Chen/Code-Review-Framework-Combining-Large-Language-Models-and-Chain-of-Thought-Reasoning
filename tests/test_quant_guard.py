"""Tests for the bf16-deploy quantization guard (torch-free logic)."""

from __future__ import annotations

import pytest

from codes.util.quant_guard import (
    QUANT_MODE_BF16,
    QUANT_MODE_FP8,
    balanced_max_memory,
    densification_risk,
    major_version,
    normalize_quant_mode,
)


# --- balanced_max_memory (device_map split arithmetic, torch-free) ------

def test_balanced_max_memory_reserves_headroom_per_gpu():
    # 2x46 GiB cards, default 13 GiB reserve -> 33 GiB cap each, low enough
    # to force an even base split that leaves room for the unmerged LoRA.
    assert balanced_max_memory([46, 46]) == {0: "33GiB", 1: "33GiB"}


def test_balanced_max_memory_none_when_no_gpus():
    assert balanced_max_memory([]) is None


def test_balanced_max_memory_override_used_verbatim():
    assert balanced_max_memory([46, 46], override="40GiB") == {
        0: "40GiB", 1: "40GiB",
    }


def test_balanced_max_memory_cap_floored_at_one_gib():
    # An over-large reserve never yields a non-positive cap.
    assert balanced_max_memory([8], reserve_gib=50) == {0: "1GiB"}


def test_balanced_max_memory_single_gpu():
    assert balanced_max_memory([46]) == {0: "33GiB"}


def test_major_version_parses_leading_int():
    assert major_version("5.9.0") == 5
    assert major_version("4.57.3") == 4
    assert major_version(" 5 ") == 5


def test_major_version_unparseable_is_none():
    assert major_version("") is None
    assert major_version("dev") is None
    assert major_version(None) is None  # type: ignore[arg-type]


def test_transformers_4_is_safe_in_both_quants():
    # The 4.x MoE forward routes sparsely — safe in bf16 and 4-bit.
    assert densification_risk(False, "4.57.3") is None
    assert densification_risk(True, "4.57.3") is None


def test_bf16_on_transformers_5_is_risk():
    # The bf16 densification observed on 5.10.2 — must be flagged now.
    msg = densification_risk(False, "5.10.2")
    assert msg is not None
    assert "bf16" in msg and "5.10.2" in msg


def test_4bit_on_transformers_5_is_risk():
    msg = densification_risk(True, "5.9.0")
    assert msg is not None
    assert "4-bit" in msg and "5.9.0" in msg


def test_risk_unknown_version_treated_safe():
    # Cannot prove >=5 → do not block (fail open).
    assert densification_risk(True, "weird") is None
    assert densification_risk(False, "dev") is None


# --- model-aware scoping (config.model_type) ----------------------------

def test_qwen3_moe_on_transformers_5_is_risk():
    msg = densification_risk(False, "5.10.2", "qwen3_moe")
    assert msg is not None
    assert "qwen3_moe" in msg


def test_dense_model_types_pass_on_transformers_5():
    # Dense architectures have no MoE forward to densify; Gemma 4 in
    # particular REQUIRES transformers>=5 and must not be blocked.
    assert densification_risk(False, "5.10.2", "gemma4_text") is None
    assert densification_risk(True, "5.10.2", "gemma4") is None
    assert densification_risk(False, "5.7.0", "llama") is None
    assert densification_risk(False, "5.7.0", "qwen3") is None


def test_unknown_model_type_fails_closed_on_transformers_5():
    # Cannot prove the model is not the A3B MoE → block (fail closed).
    for unknown in (None, "", "   "):
        msg = densification_risk(False, "5.9.0", unknown)
        assert msg is not None
        assert "unknown" in msg


def test_model_type_matching_is_case_insensitive():
    assert densification_risk(False, "5.9.0", "Qwen3_MoE") is not None
    assert densification_risk(False, "5.9.0", "Gemma4_Text") is None


def test_dense_model_type_safe_on_transformers_4_too():
    assert densification_risk(False, "4.57.3", "gemma4_text") is None
    assert densification_risk(True, "4.57.3", "qwen3_moe") is None


# --- normalize_quant_mode (PRTHINKER_QUANT parsing, torch-free) ----------

def test_quant_mode_defaults_to_bf16_when_unset():
    assert normalize_quant_mode(None) == QUANT_MODE_BF16
    assert normalize_quant_mode("") == QUANT_MODE_BF16


def test_quant_mode_bf16_aliases():
    for raw in ("bf16", "none", "off", "BF16", "  None  "):
        assert normalize_quant_mode(raw) == QUANT_MODE_BF16


def test_quant_mode_fp8_case_and_whitespace_insensitive():
    for raw in ("fp8", "FP8", "  fp8 "):
        assert normalize_quant_mode(raw) == QUANT_MODE_FP8


def test_quant_mode_unknown_raises():
    with pytest.raises(ValueError, match="Unsupported PRTHINKER_QUANT"):
        normalize_quant_mode("int4")
