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


__all__ = ["densification_risk", "major_version"]
