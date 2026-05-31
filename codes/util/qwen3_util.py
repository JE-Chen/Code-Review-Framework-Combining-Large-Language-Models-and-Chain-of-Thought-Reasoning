import datetime
import logging
import os

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    StoppingCriteria,
    StoppingCriteriaList,
)
from peft import PeftModel

from prthinker.pipeline import ReviewCancelledError

log = logging.getLogger(__name__)


def _pick_attn_implementation() -> str:
    """Prefer FlashAttention 2 → SDPA. Eager is intentionally never returned.

    FA2 keeps attention memory O(N) instead of O(N²), which is the only
    way the 5-step CoT pipeline's final ``total_summary`` step (whose
    prompt concatenates every prior step's output) stays under the L40S
    44 GiB ceiling. SDPA is the fallback on environments where flash_attn
    is not installable; it dispatches to PyTorch's memory-efficient
    backend on modern CUDA stacks, also O(N).

    Eager attention materialises a full L² score matrix and OOMs around
    1500 tokens of input on a 30B-class model with a 44 GiB GPU — far
    below any realistic CoT prompt. _verify_non_eager_attention() below
    refuses to serve if the loaded model still ends up on the eager
    path, so deploys that silently drop flash_attn fail at boot instead
    of at the first review.
    """
    try:
        import flash_attn  # noqa: F401
        return "flash_attention_2"
    except ImportError:
        log.warning(
            "flash_attn not importable; falling back to SDPA. "
            "Rebuild the server image to compile flash-attn (see "
            "docker/Dockerfile.server) if review prompts exceed ~16K "
            "tokens — SDPA's math fallback can still OOM on very "
            "long contexts."
        )
        return "sdpa"


def _describe_load(model) -> str:
    """One-line summary of how the model actually loaded: dtype + whether
    bitsandbytes quantization is in effect. Used in OOM diagnostics and the
    boot probe so 'requested 4-bit but loaded bf16' is visible, not hidden.
    """
    dtype = getattr(model, "dtype", None) or getattr(
        getattr(model, "config", None), "torch_dtype", None
    )
    is_4bit = bool(getattr(model, "is_loaded_in_4bit", False))
    is_8bit = bool(getattr(model, "is_loaded_in_8bit", False))
    quant = "4bit" if is_4bit else "8bit" if is_8bit else "none"
    return f"dtype={dtype}, quant={quant}"


def _probe_generation(model, tokenizer) -> None:
    """Ground-truth boot check: actually run a short generation on a
    multi-thousand-token prompt and confirm it does not OOM.

    The config-string check in _verify_non_eager_attention() cannot catch
    failure modes that live in real memory rather than in
    ``_attn_implementation`` — e.g. transformers>=5 densifying the Qwen3
    MoE forward to an fp32 [seq, hidden, intermediate] tensor (~48 MiB per
    input token), or 4-bit quantization silently not applying so the model
    sits in bf16. Both sail past the string check and then OOM on the first
    real review. Probing ~4K tokens at boot turns that into a loud,
    actionable startup failure instead.

    Skip with PRTHINKER_SKIP_BOOT_PROBE=1 (e.g. on a card large enough that
    the probe itself is wasteful).
    """
    if os.environ.get(
        "PRTHINKER_SKIP_BOOT_PROBE", ""
    ).strip().lower() in ("1", "true", "yes"):
        log.info("PRTHINKER_SKIP_BOOT_PROBE set; skipping generation probe.")
        return

    probe_tokens = int(os.environ.get("PRTHINKER_BOOT_PROBE_TOKENS", "4096"))
    log.info(
        "Boot probe: generating from a ~%d-token prompt to verify memory "
        "scaling (%s)", probe_tokens, _describe_load(model),
    )
    text = "def f():\n    return 1\n" * (probe_tokens // 8)
    inputs = tokenizer([text], return_tensors="pt").to(model.device)
    actual = inputs["input_ids"].shape[-1]
    try:
        with torch.no_grad():
            model.generate(**inputs, max_new_tokens=8, do_sample=False)
    except torch.cuda.OutOfMemoryError as exc:
        raise RuntimeError(
            f"Boot probe OOM: a {actual}-token prompt could not run an "
            f"8-token generation ({_describe_load(model)}). The server "
            "would OOM on the first real review. Most likely "
            "transformers>=5 MoE densification or 4-bit quantization not "
            "applied — pin transformers<5 and verify load_in_4bit. "
            "Bypass with PRTHINKER_SKIP_BOOT_PROBE=1. Original: " + str(exc)
        ) from exc
    log.info("Boot probe passed: %d-token prompt generated without OOM.", actual)


def _verify_non_eager_attention(model) -> None:
    """Refuse to keep the model alive if it resolved to eager attention.

    transformers may silently fall back to ``"eager"`` when an
    architecture lacks the requested kernel; flash_attn may import
    successfully and still not be used by the model class. After load
    the only ground-truth is ``model.config._attn_implementation``.

    On a 30B-class model with a 44 GiB GPU, eager attention OOMs
    around 1500 tokens of input — far below any realistic CoT prompt,
    and the failure mode is an opaque "Tried to allocate 269 GiB" deep
    inside a review job that already burned setup time. Failing here at
    server boot turns that into a loud, actionable error before any
    review hits the GPU.

    Override with ``PRTHINKER_ALLOW_EAGER_ATTENTION=1`` only when the
    GPU has enough headroom for the worst-case prompt (e.g. debugging
    on a much larger card).
    """
    impl = getattr(model.config, "_attn_implementation", None)
    if impl in ("flash_attention_2", "sdpa"):
        log.info("Attention implementation verified: %s", impl)
        return
    if os.environ.get(
        "PRTHINKER_ALLOW_EAGER_ATTENTION", ""
    ).strip().lower() in ("1", "true", "yes"):
        log.warning(
            "PRTHINKER_ALLOW_EAGER_ATTENTION set; serving with %s "
            "attention. Prompts above ~1500 tokens are expected to OOM.",
            impl,
        )
        return
    raise RuntimeError(
        f"Refusing to start: model loaded with attn_implementation={impl!r}. "
        "30B-class models with eager attention OOM around 1500 tokens of "
        "input on a 44 GiB GPU. Install flash-attn (`pip install flash-attn "
        "--no-build-isolation`) or ensure PyTorch SDPA is dispatched. "
        "Bypass at your own risk with PRTHINKER_ALLOW_EAGER_ATTENTION=1."
    )


class _CancelStoppingCriteria(StoppingCriteria):
    """Stops generation when ``cancel_event`` flips. Polled every token
    so cancellation lands within ~one token (~50-100ms on L40S)."""

    def __init__(self, cancel_event):
        super().__init__()
        self._cancel_event = cancel_event

    def __call__(self, input_ids, scores, **kwargs):
        return (
            self._cancel_event is not None
            and self._cancel_event.is_set()
        )


def load_qwen3_model(lora_path: str = None, model_name: str = "Qwen/Qwen3-30B-A3B-Thinking-2507", quantization: bool = True):

    print("Loading model across all GPUs...")
    attn_impl = _pick_attn_implementation()
    print(f"Attention implementation: {attn_impl}")
    if model_name in ["Qwen/Qwen3-30B-A3B-Thinking-2507", "Qwen/Qwen3-Coder-30B-A3B-Instruct"]:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,  # bf16 compute if supported
        )
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            quantization_config=bnb_config,
            attn_implementation=attn_impl,
        )
    elif not quantization:
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            attn_implementation=attn_impl,
        )
    else:
        bnb_config = BitsAndBytesConfig(
            load_in_8bit=True,
        )
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            attn_implementation=attn_impl,
            quantization_config=bnb_config,
        )

    print(datetime.datetime.now(), "Model loaded")
    log.info("Model load summary: %s", _describe_load(model))

    # Refuse to keep going if transformers silently fell back to eager
    # attention (e.g. flash_attn imported but the model class doesn't
    # use it). Better a loud boot failure than a 269 GiB OOM mid-review.
    _verify_non_eager_attention(model)

    # === 一次載入模型與 tokenizer ===
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    if lora_path:
        model = PeftModel.from_pretrained(model, lora_path)
        print(datetime.datetime.now(), "LoRa loaded")
        # PeftModel wraps the base; re-verify in case the LoRA path
        # somehow swapped the attention class.
        _verify_non_eager_attention(model)

    # Ground-truth memory probe on the fully-assembled (base + LoRA) model.
    # Catches real-memory regressions the config-string check cannot see.
    _probe_generation(model, tokenizer)

    return model, tokenizer

def qwen3_ask(prompt: str, model, tokenizer, max_new_tokens: int = 16784, cancel_event=None):
    messages = [
        {"role": "user", "content": prompt}
    ]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    stopping_criteria = None
    if cancel_event is not None:
        stopping_criteria = StoppingCriteriaList(
            [_CancelStoppingCriteria(cancel_event)]
        )

    try:
        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=max_new_tokens,
            stopping_criteria=stopping_criteria,
        )
    except torch.cuda.OutOfMemoryError as exc:
        impl = getattr(model.config, "_attn_implementation", "unknown")
        input_len = model_inputs["input_ids"].shape[-1]
        load = _describe_load(model)
        # Do NOT assert "eager attention" here. Two distinct failure modes
        # produce a giant "Tried to allocate N GiB":
        #   * O(N^2) in input length  -> eager attention materialising the
        #     score matrix; verify flash-attn / SDPA is dispatched.
        #   * O(N)   in input length  -> NOT attention. Seen with
        #     transformers>=5 on Qwen3-*-A3B: the MoE forward densifies to
        #     an fp32 [seq, hidden, intermediate] tensor (~48 MiB/token),
        #     or 4-bit quantization silently failed and the model is in
        #     bf16. Pin transformers<5 and confirm load is 4-bit.
        # Compare the allocation size across two different input lengths to
        # tell them apart (linear => MoE/quant, quadratic => eager).
        raise RuntimeError(
            f"CUDA OOM during generate (input={input_len} tokens, "
            f"max_new_tokens={max_new_tokens}, "
            f"attn_implementation={impl!r}, {load}). If the attempted "
            "allocation grows LINEARLY with input length it is NOT "
            "attention — suspect transformers>=5 MoE densification or "
            "4-bit quantization not applied (pin transformers<5, verify "
            "load_in_4bit). If it grows QUADRATICALLY, attention is "
            "running eager — verify flash-attn/SDPA. Original: " + str(exc)
        ) from exc

    # If the stopping criterion fired because the cancel_event was set,
    # bail out before decoding — the partial output is useless to the
    # caller and the worker's exception handler needs to see this as a
    # cancellation, not a truncated success.
    if cancel_event is not None and cancel_event.is_set():
        raise ReviewCancelledError(
            "Generation interrupted mid-stream by cancel_event"
        )

    output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()

    try:
        index = len(output_ids) - output_ids[::-1].index(151668)
    except ValueError:
        index = 0

    thinking_content = tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
    content = tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")
    print(datetime.datetime.now(), "Generation completed.")
    return content, thinking_content

