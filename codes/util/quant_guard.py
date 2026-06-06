"""Pure guard logic for the Qwen3-A3B bf16 deploy.

Deliberately free of ``torch`` / ``transformers`` imports so the rule can
be unit-tested without the GPU stack. The danger it encodes: bitsandbytes
4-bit engaging on transformers>=5 densifies the Qwen3-A3B MoE forward (the
allocation grows linearly with input length) and OOMs a 44 GiB L40S. The
supported deploy loads bf16 and never requests 4-bit.
"""

from __future__ import annotations


def major_version(version: str) -> int | None:
    """Leading integer of a version string (``'5.9.0' -> 5``), or None."""
    head = (version or "").strip().split(".", 1)[0]
    try:
        return int(head)
    except ValueError:
        return None


def densification_risk(is_4bit: bool, transformers_version: str) -> str | None:
    """Return an error message when transformers>=5 will densify the MoE, else None.

    transformers>=5 densifies the Qwen3-A3B MoE forward to a
    ``[seq, hidden, intermediate]`` tensor (~48 MiB per input token, linear
    in length) and OOMs the L40S on a multi-thousand-token review. This
    happens in **bf16 and 4-bit alike** — the bf16 densification was
    observed on 5.10.2 (a 2357-token file tried to allocate 110 GiB), so it
    is not specific to quantization. The 4.x MoE forward routes sparsely and
    is safe. An unparseable version fails open (cannot prove >=5).
    ``is_4bit`` only sharpens the message.
    """
    major = major_version(transformers_version)
    if major is None or major < 5:
        return None
    quant = "4-bit" if is_4bit else "bf16"
    return (
        f"transformers {transformers_version} densifies the Qwen3-A3B MoE "
        f"forward in {quant} (~48 MiB per input token, linear) and OOMs the "
        "GPU on a multi-thousand-token review. Pin transformers<5 — the 4.x "
        "MoE forward routes sparsely; the supported deploy loads bf16."
    )


# The cap must be low enough to FORCE a balanced base split, not just set a
# ceiling: device_map="auto" fills GPU 0 up to the cap before spilling to
# GPU 1, so a high cap (e.g. 35 of 44 usable GiB) yields a 35/25 split and
# the busier card OOMs on its larger LoRA share. The A3B base is ~60 GiB
# (≈30 per card) and the unmerged LoRA ~16 GiB; a ~31 GiB cap keeps the base
# near 30/30 and leaves ~13 GiB per card for the adapter + activations.
_DEFAULT_LORA_RESERVE_GIB = 13


def balanced_max_memory(
    total_gibs: list[int],
    override: str = "",
    reserve_gib: int = _DEFAULT_LORA_RESERVE_GIB,
) -> dict[int, str] | None:
    """Per-GPU memory caps for ``device_map="auto"``, or None for no GPUs.

    Without a low-enough cap, transformers packs the base model onto GPU 0
    to the cap while GPU 1 stays half-empty, then
    ``PeftModel.from_pretrained`` OOMs loading the unmerged ~16 GiB LoRA onto
    the busier card. Capping each card ``reserve_gib`` below its physical
    size both forces a balanced base split AND leaves headroom for the
    adapter + activations on every card.

    ``total_gibs`` is each GPU's total memory in GiB. ``override`` (from
    ``PRTHINKER_GPU_MAX_MEMORY``) sets an explicit per-GPU cap string
    verbatim. The computed cap is floored at 1 GiB so a too-large reserve
    never yields a non-positive cap. Pure: no torch import, so the split
    arithmetic is unit-testable without a GPU.
    """
    if not total_gibs:
        return None
    caps: dict[int, str] = {}
    for index, total in enumerate(total_gibs):
        caps[index] = override or f"{max(total - reserve_gib, 1)}GiB"
    return caps


__all__ = ["balanced_max_memory", "densification_risk", "major_version"]
