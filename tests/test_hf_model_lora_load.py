"""Regression test for the LoRA adapter load device in codes.util.hf_model_util.

The 30B-A3B deploy loads the base bf16 across both L40S cards and then
attaches an unmerged ~13 GiB r=64 expert LoRA. PEFT defaults the adapter
load to ``cuda:0``; from there the transient peak (base already on GPU 0
plus the whole adapter buffered there) OOMs the card before PEFT can
redistribute the adapter tensors to their base layers. Staging the
adapter on CPU avoids the spike, so the load MUST pass
``torch_device="cpu"`` to ``PeftModel.from_pretrained``. This test pins
that contract without needing a GPU by stubbing the heavy collaborators.
"""

from __future__ import annotations

import importlib
import sys
from types import SimpleNamespace

import pytest

_A3B_MODEL = "Qwen/Qwen3-Coder-30B-A3B-Instruct"


@pytest.fixture
def _hf_model_util(monkeypatch):
    """Import codes.util.hf_model_util with torch/transformers/peft stubbed."""
    fake_torch = SimpleNamespace(
        bfloat16=object(),
        cuda=SimpleNamespace(
            is_available=lambda: False,
            OutOfMemoryError=type("FakeOOM", (RuntimeError,), {}),
        ),
    )
    monkeypatch.setitem(sys.modules, "torch", fake_torch)
    monkeypatch.setitem(
        sys.modules,
        "transformers",
        SimpleNamespace(
            AutoModelForCausalLM=object,
            AutoTokenizer=object,
            BitsAndBytesConfig=object,
            StoppingCriteria=type("SC", (), {}),
            StoppingCriteriaList=type("SCL", (list,), {}),
        ),
    )
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


def _stub_load_pipeline(module, monkeypatch, recorder):
    """Replace every GPU-touching collaborator with a CPU-safe stub."""
    fake_model = SimpleNamespace(config=SimpleNamespace(_attn_implementation="sdpa"))

    def _fake_peft_from_pretrained(model, path, **kwargs):
        recorder["model"] = model
        recorder["path"] = path
        recorder["kwargs"] = kwargs
        return SimpleNamespace(config=SimpleNamespace(_attn_implementation="sdpa"))

    monkeypatch.setattr(
        module,
        "AutoModelForCausalLM",
        SimpleNamespace(from_pretrained=lambda *a, **k: fake_model),
    )
    monkeypatch.setattr(
        module,
        "AutoTokenizer",
        SimpleNamespace(from_pretrained=lambda *a, **k: object()),
    )
    monkeypatch.setattr(
        module, "PeftModel", SimpleNamespace(from_pretrained=_fake_peft_from_pretrained)
    )
    monkeypatch.setattr(module, "_gpu_max_memory", lambda: None)
    monkeypatch.setattr(module, "_describe_load", lambda _model: "")
    monkeypatch.setattr(module, "_verify_non_eager_attention", lambda _model: None)
    monkeypatch.setattr(module, "_verify_quant_safe", lambda _model: None)
    monkeypatch.setattr(module, "_probe_generation", lambda _model, _tok: None)
    return fake_model


def test_lora_adapter_staged_on_cpu(_hf_model_util, monkeypatch):
    recorder: dict = {}
    base = _stub_load_pipeline(_hf_model_util, monkeypatch, recorder)

    model, tokenizer = _hf_model_util.load_hf_model(
        lora_path="/some/adapter", model_name=_A3B_MODEL, quantization=False
    )

    assert recorder["kwargs"].get("torch_device") == "cpu"
    assert recorder["path"] == "/some/adapter"
    assert recorder["model"] is base
    assert model is not None
    assert tokenizer is not None


def test_no_lora_skips_peft_load(_hf_model_util, monkeypatch):
    recorder: dict = {}
    _stub_load_pipeline(_hf_model_util, monkeypatch, recorder)

    _hf_model_util.load_hf_model(
        lora_path=None, model_name=_A3B_MODEL, quantization=False
    )

    assert recorder == {}
