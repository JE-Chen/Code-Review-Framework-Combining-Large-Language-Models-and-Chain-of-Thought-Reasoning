"""Local in-process backend — any Hugging Face causal-LM with optional LoRA."""

from __future__ import annotations

from prthinker.backends.base import InferenceBackend
from prthinker.config import LocalBackendConfig


class LocalHFBackend(InferenceBackend):
    """Loads a Hugging Face causal-LM once and reuses it for every prompt.

    Works with any chat-tuned HF model identifier — Qwen, Llama-3, Mistral,
    CodeLlama, etc. — because generation goes through the model's bundled
    chat template. Heavy imports (torch, transformers) are deferred so a
    runner that only uses online backends does not pay the import cost.

    LoRA adapter and 4-bit / 8-bit quantization come from the existing
    `codes/util/qwen3_util.load_qwen3_model` factory (the name is
    historical; the function accepts any HF id).
    """

    def __init__(self, config: LocalBackendConfig) -> None:
        from codes.util.qwen3_util import load_qwen3_model

        self._config = config
        model, tokenizer = load_qwen3_model(
            model_name=config.model_name,
            lora_path=config.lora_path,
            quantization=config.quantization,
        )
        model.eval()
        self._model = model
        self._tokenizer = tokenizer

    def backend_kind(self) -> str:
        return "local"

    def model_name(self) -> str:
        return self._config.model_name

    def generate(self, prompt: str, max_new_tokens: int) -> str:
        from codes.util.qwen3_util import qwen3_ask

        content, _thinking = qwen3_ask(
            prompt,
            self._model,
            self._tokenizer,
            max_new_tokens=max_new_tokens,
        )
        return content

    def close(self) -> None:
        self._model = None
        self._tokenizer = None


# Backwards-compatible alias — old code / docs still importing
# `LocalQwen3Backend` keeps working until the deprecation cycle ends.
LocalQwen3Backend = LocalHFBackend
