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
        # Rewrap so the error landing in the runner's traceback points
        # at the config root cause instead of the literal allocation
        # size, which has fooled multiple debugging sessions into
        # blaming prompt length when the real fault was eager attention.
        raise RuntimeError(
            f"CUDA OOM during generate (input={input_len} tokens, "
            f"max_new_tokens={max_new_tokens}, "
            f"attn_implementation={impl!r}). On a 30B-class model with "
            "a 44 GiB GPU, OOM on a reasonable prompt almost always "
            "means attention is running eager — verify flash-attn or "
            "SDPA is actually dispatched. Original: " + str(exc)
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

