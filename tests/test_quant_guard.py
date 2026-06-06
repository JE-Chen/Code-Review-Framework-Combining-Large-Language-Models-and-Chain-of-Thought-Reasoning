"""Tests for the bf16-deploy quantization guard (torch-free logic)."""

from __future__ import annotations

from codes.util.quant_guard import (
    balanced_max_memory,
    densification_risk,
    major_version,
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
