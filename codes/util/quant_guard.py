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
    """Return an error message for the 4-bit + transformers>=5 combo, else None.

    That combination is the documented Qwen3-A3B MoE densification OOM. A
    safe load (bf16, or transformers<5) returns ``None``.
    """
    if not is_4bit:
        return None
    major = major_version(transformers_version)
    if major is None or major < 5:
        return None
    return (
        f"bitsandbytes 4-bit engaged on transformers {transformers_version}: "
        "transformers>=5 densifies the Qwen3-A3B MoE forward (the allocation "
        "grows linearly with input length) and OOMs the GPU. The supported "
        "deploy loads bf16 and never requests 4-bit; rebuild without 4-bit "
        "(or pin transformers<5)."
    )


__all__ = ["densification_risk", "major_version"]
