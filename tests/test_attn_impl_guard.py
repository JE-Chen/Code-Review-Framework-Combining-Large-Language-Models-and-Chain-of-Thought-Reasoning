"""Tests for the eager-attention boot guard in codes.util.hf_model_util.

The guard's job is to refuse to start the server when transformers
silently dropped the requested attention kernel and resolved to
``"eager"`` — that path OOMs at ~1500 tokens on a 30B-class model with
a 44 GiB GPU and turns a config mistake into an opaque mid-review
crash. These tests exercise the verify function with a fake config
object so the check runs in a CPU-only test process; no model weights,
no torch.cuda involvement.
"""

from __future__ import annotations

import importlib
import sys
from types import SimpleNamespace

import pytest


@pytest.fixture
def _hf_model_util(monkeypatch):
    """Import codes.util.hf_model_util with the heavy deps stubbed.

    transformers / peft / torch import at module-import time and we
    don't need them for the guard test, so stand in lightweight stubs.
    """
    # Stub torch with the symbols the module touches at import time.
    fake_torch = SimpleNamespace(
        bfloat16=object(),
        cuda=SimpleNamespace(
            OutOfMemoryError=type("FakeOOM", (RuntimeError,), {}),
        ),
    )
    monkeypatch.setitem(sys.modules, "torch", fake_torch)

    class _StoppingCriteria:
        pass

    class _StoppingCriteriaList(list):
        pass

    fake_transformers = SimpleNamespace(
        AutoModelForCausalLM=object,
        AutoTokenizer=object,
        BitsAndBytesConfig=object,
        StoppingCriteria=_StoppingCriteria,
        StoppingCriteriaList=_StoppingCriteriaList,
    )
    monkeypatch.setitem(sys.modules, "transformers", fake_transformers)
    monkeypatch.setitem(sys.modules, "peft", SimpleNamespace(PeftModel=object))
    monkeypatch.setitem(
        sys.modules,
        "prthinker.pipeline",
        SimpleNamespace(ReviewCancelledError=type("RCE", (Exception,), {})),
    )

    sys.modules.pop("codes.util.hf_model_util", None)
    module = importlib.import_module("codes.util.hf_model_util")
    yield module
    sys.modules.pop("codes.util.hf_model_util", None)


def _model_with_attn(impl: str | None):
    return SimpleNamespace(config=SimpleNamespace(_attn_implementation=impl))


def test_verify_accepts_flash_attention_2(_hf_model_util):
    _hf_model_util._verify_non_eager_attention(_model_with_attn("flash_attention_2"))


def test_verify_accepts_sdpa(_hf_model_util):
    _hf_model_util._verify_non_eager_attention(_model_with_attn("sdpa"))


def test_verify_rejects_eager(_hf_model_util, monkeypatch):
    monkeypatch.delenv("PRTHINKER_ALLOW_EAGER_ATTENTION", raising=False)
    with pytest.raises(RuntimeError, match="Refusing to start"):
        _hf_model_util._verify_non_eager_attention(_model_with_attn("eager"))


def test_verify_rejects_missing_attn_impl(_hf_model_util, monkeypatch):
    monkeypatch.delenv("PRTHINKER_ALLOW_EAGER_ATTENTION", raising=False)
    with pytest.raises(RuntimeError, match="Refusing to start"):
        _hf_model_util._verify_non_eager_attention(_model_with_attn(None))


def test_verify_eager_override_env_allows_eager(_hf_model_util, monkeypatch):
    monkeypatch.setenv("PRTHINKER_ALLOW_EAGER_ATTENTION", "1")
    # Should not raise; emits warning via log.
    _hf_model_util._verify_non_eager_attention(_model_with_attn("eager"))


@pytest.mark.parametrize("value", ["0", "false", "no", ""])
def test_verify_eager_override_disabled_values_still_reject(
    _hf_model_util, monkeypatch, value
):
    monkeypatch.setenv("PRTHINKER_ALLOW_EAGER_ATTENTION", value)
    with pytest.raises(RuntimeError, match="Refusing to start"):
        _hf_model_util._verify_non_eager_attention(_model_with_attn("eager"))


def test_pick_attn_implementation_returns_flash_when_importable(
    _hf_model_util, monkeypatch
):
    monkeypatch.setitem(sys.modules, "flash_attn", SimpleNamespace())
    assert _hf_model_util._pick_attn_implementation() == "flash_attention_2"


def test_pick_attn_implementation_falls_back_to_sdpa(_hf_model_util, monkeypatch):
    sys.modules.pop("flash_attn", None)

    real_import = __import__

    def _no_flash_import(name, *args, **kwargs):
        if name == "flash_attn":
            raise ImportError("simulated: flash_attn not installed")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", _no_flash_import)
    assert _hf_model_util._pick_attn_implementation() == "sdpa"
