import contextlib
import datetime
import logging
import os

import torch
import transformers
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    StoppingCriteria,
    StoppingCriteriaList,
)
from peft import PeftModel

from codes.util.quant_guard import balanced_max_memory, densification_risk
from codes.util.think_split import think_end_token_id, thinking_boundary
from prthinker.pipeline import ReviewCancelledError

log = logging.getLogger(__name__)

# Models served in plain bf16 with a balanced dual-card split — never
# bitsandbytes. The Qwen3-A3B pair because 4-bit + transformers>=5
# densifies their MoE forward; Gemma 4 31B (dense, ~61 GiB bf16) because
# it fits the same dual-L40S deploy and 8-bit would only slow decode.
_BF16_MODELS = (
    "Qwen/Qwen3-30B-A3B-Thinking-2507",
    "Qwen/Qwen3-Coder-30B-A3B-Instruct",
    "google/gemma-4-31B-it",
)


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
        # Lazy by design: probe whether flash_attn is installed without
        # forcing it as a hard dependency of the server module.
        import flash_attn  # noqa: F401  # pylint: disable=import-outside-toplevel,unused-import
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
            "would OOM on the first real review. The supported deploy is "
            "bf16 (no 4-bit); if quant shows 4bit here, transformers>=5 is "
            "densifying the MoE — rebuild without 4-bit (see CLAUDE.md "
            "'GPU Server: bf16'). Bypass with PRTHINKER_SKIP_BOOT_PROBE=1. "
            "Original: " + str(exc)
        ) from exc
    log.info("Boot probe passed: %d-token prompt generated without OOM.", actual)


def _verify_quant_safe(model) -> None:
    """Refuse to serve a transformers>=5 build that densifies the A3B MoE.

    transformers>=5 densifies the Qwen3-A3B MoE forward (~48 MiB per input
    token, linear) and OOMs on the first multi-thousand-token review — in
    bf16 AND 4-bit alike (bf16 densification observed on 5.10.2). The
    supported Qwen3 deploy pins transformers<5, whose MoE forward routes
    sparsely. Fail loudly at boot instead of OOMing mid-review.

    Model-aware: the rule is scoped by ``config.model_type``. Dense
    architectures (e.g. Gemma 4, which *requires* transformers>=5) pass;
    only the Qwen3-MoE types — or an undetermined model_type, which fails
    closed — are refused on >=5. Override with
    ``PRTHINKER_ALLOW_DENSIFYING_QUANT=1``.
    """
    is_4bit = bool(getattr(model, "is_loaded_in_4bit", False))
    model_type = getattr(getattr(model, "config", None), "model_type", None)
    risk = densification_risk(is_4bit, transformers.__version__, model_type)
    if risk is None:
        return
    if os.environ.get(
        "PRTHINKER_ALLOW_DENSIFYING_QUANT", ""
    ).strip().lower() in ("1", "true", "yes"):
        log.warning("PRTHINKER_ALLOW_DENSIFYING_QUANT set; %s", risk)
        return
    raise RuntimeError("Refusing to start: " + risk)


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


def _gpu_max_memory():
    """Balanced per-GPU ``max_memory`` caps for ``device_map="auto"``, or None.

    Reads each visible card's total memory and delegates the split
    arithmetic to ``quant_guard.balanced_max_memory`` (pure, torch-free) so
    the base model is spread evenly and leaves headroom for the unmerged
    LoRA. Without this, ``device_map="auto"`` fills GPU 0 to the brim and
    ``PeftModel.from_pretrained`` OOMs loading the adapter. Returns None on a
    CPU-only host. Override the per-GPU cap with ``PRTHINKER_GPU_MAX_MEMORY``.
    """
    if not torch.cuda.is_available():
        return None
    totals = [
        torch.cuda.get_device_properties(i).total_memory // (1024 ** 3)
        for i in range(torch.cuda.device_count())
    ]
    return balanced_max_memory(
        totals, os.environ.get("PRTHINKER_GPU_MAX_MEMORY", "").strip()
    )


def load_qwen3_model(lora_path: str = None, model_name: str = "Qwen/Qwen3-30B-A3B-Thinking-2507", quantization: bool = True):

    print("Loading model across all GPUs...")
    attn_impl = _pick_attn_implementation()
    print(f"Attention implementation: {attn_impl}")
    if model_name in _BF16_MODELS:
        # bf16, NOT 4-bit. On transformers>=5 a 4-bit A3B MoE densifies its
        # forward (allocation linear in input length) and OOMs the L40S.
        # bf16 across both cards (device_map="auto") avoids that entirely;
        # see CLAUDE.md "GPU Server: bf16, no flash-attn". max_memory caps
        # each card below physical so the base splits evenly and leaves room
        # for the unmerged LoRA loaded afterwards (else GPU 0 fills and the
        # adapter OOMs).
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            torch_dtype=torch.bfloat16,
            attn_implementation=attn_impl,
            max_memory=_gpu_max_memory(),
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
    # Refuse the 4-bit + transformers>=5 densification combo (this deploy
    # is bf16); a rebuild that re-engages 4-bit would OOM mid-review.
    _verify_quant_safe(model)

    # === 一次載入模型與 tokenizer ===
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    if lora_path:
        # Stage the ~13 GiB adapter on CPU, not a GPU. PEFT defaults the
        # adapter load to cuda:0; from there it either piles the whole
        # adapter onto GPU 0 (low_cpu_mem_usage=True) or buffers the full
        # state dict on GPU 0 before redistributing (the default), and
        # either way the transient peak OOMs the already-loaded card on
        # this 30B-A3B + r=64 expert LoRA. torch_device="cpu" keeps the
        # source in host RAM; PEFT then moves each adapter tensor straight
        # to its base layer's device, so the adapter splits evenly across
        # both cards (~6.3 GiB each) and neither GPU spikes during load.
        model = PeftModel.from_pretrained(
            model, lora_path, torch_device="cpu"
        )
        print(datetime.datetime.now(), "LoRa loaded")
        # PeftModel wraps the base; re-verify in case the LoRA path
        # somehow swapped the attention class.
        _verify_non_eager_attention(model)

    # Ground-truth memory probe on the fully-assembled (base + LoRA) model.
    # Catches real-memory regressions the config-string check cannot see.
    _probe_generation(model, tokenizer)

    return model, tokenizer

@contextlib.contextmanager
def _force_efficient_sdpa():
    """Force SDPA to flash or mem-efficient backends; disable math.

    The math backend materialises a full L^2 score matrix and is what
    silently OOMs at long context (the "127 GiB at 35K tokens" failure
    mode at bf16 + 4-bit + sdpa on a 44 GiB L40S). Disabling it makes
    long generations either dispatch to a memory-efficient kernel
    (which is O(N) in memory) or fail loudly with a clear "no
    available SDPA backend" error instead of swallowing 100+ GiB.

    Tries the new ``torch.nn.attention.sdpa_kernel`` (PyTorch 2.5+)
    first, then the older ``torch.backends.cuda.sdp_kernel``. If
    neither is available the context is a no-op and generate runs
    with whatever default PyTorch picks (i.e. the previous behaviour).
    """
    try:
        # Lazy by design: the new ``torch.nn.attention`` namespace
        # only exists on PyTorch >= 2.5; the legacy fallback below
        # covers older runtimes.
        from torch.nn.attention import (  # type: ignore[attr-defined]  # noqa: PLC0415  # pylint: disable=import-outside-toplevel
            SDPBackend,
            sdpa_kernel,
        )
        with sdpa_kernel(
            [SDPBackend.FLASH_ATTENTION, SDPBackend.EFFICIENT_ATTENTION]
        ):
            yield
        return
    except (ImportError, AttributeError):
        pass
    try:
        with torch.backends.cuda.sdp_kernel(
            enable_flash=True,
            enable_mem_efficient=True,
            enable_math=False,
        ):
            yield
        return
    except (AttributeError, RuntimeError):
        pass
    yield


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
        with _force_efficient_sdpa():
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

    # Model-aware reasoning split: resolve the closing marker from the
    # tokenizer's own vocabulary (151668 on Qwen3) instead of hardcoding
    # the Qwen id. Vocabularies without the marker (e.g. Gemma) get
    # boundary 0 — the whole generation is content.
    index = thinking_boundary(output_ids, think_end_token_id(tokenizer))

    thinking_content = tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
    content = tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")
    print(datetime.datetime.now(), "Generation completed.")
    return content, thinking_content
