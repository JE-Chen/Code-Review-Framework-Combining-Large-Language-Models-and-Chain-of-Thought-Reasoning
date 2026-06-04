"""Tests for the bf16-deploy quantization guard (torch-free logic)."""

from __future__ import annotations

from codes.util.quant_guard import densification_risk, major_version


def test_major_version_parses_leading_int():
    assert major_version("5.9.0") == 5
    assert major_version("4.57.3") == 4
    assert major_version(" 5 ") == 5


def test_major_version_unparseable_is_none():
    assert major_version("") is None
    assert major_version("dev") is None
    assert major_version(None) is None  # type: ignore[arg-type]


def test_no_risk_when_not_4bit():
    # bf16 (the supported deploy) is safe on any transformers version.
    assert densification_risk(False, "5.9.0") is None
    assert densification_risk(False, "4.57.3") is None


def test_no_risk_when_4bit_on_transformers_4():
    # 4-bit is only dangerous on the densifying 5.x line.
    assert densification_risk(True, "4.57.3") is None


def test_risk_when_4bit_on_transformers_5():
    msg = densification_risk(True, "5.9.0")
    assert msg is not None
    assert "4-bit" in msg and "5.9.0" in msg
    assert "bf16" in msg


def test_risk_unknown_version_treated_safe():
    # Cannot prove >=5 → do not block (fail open).
    assert densification_risk(True, "weird") is None
