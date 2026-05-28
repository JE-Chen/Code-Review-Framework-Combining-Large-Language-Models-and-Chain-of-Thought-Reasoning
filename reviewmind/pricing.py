"""Per-(backend, model) pricing in USD per million tokens.

Numbers reflect provider list prices at the time of writing. Update this
table as providers move prices — the source of truth is each provider's
public pricing page.

Models not in the table return ``None`` cost and the telemetry layer logs
them as "unpriced" without estimating.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Rate:
    input_per_mtok: float   # USD per 1,000,000 input tokens
    output_per_mtok: float  # USD per 1,000,000 output tokens


# (backend_kind, model_name) -> Rate
_PRICING: dict[tuple[str, str], Rate] = {
    # ----- OpenAI ---------------------------------------------------------
    ("openai", "gpt-4o"):                  Rate(2.50,  10.00),
    ("openai", "gpt-4o-mini"):             Rate(0.15,   0.60),
    ("openai", "gpt-4-turbo"):             Rate(10.00, 30.00),
    ("openai", "gpt-4.1"):                 Rate(2.00,   8.00),
    ("openai", "gpt-4.1-mini"):            Rate(0.40,   1.60),
    ("openai", "gpt-4.1-nano"):            Rate(0.10,   0.40),
    ("openai", "o1"):                      Rate(15.00, 60.00),
    ("openai", "o1-mini"):                 Rate(3.00,  12.00),

    # ----- Anthropic ------------------------------------------------------
    # Claude 4.x family — list prices.
    ("anthropic", "claude-opus-4-7"):              Rate(15.00, 75.00),
    ("anthropic", "claude-sonnet-4-6"):            Rate( 3.00, 15.00),
    ("anthropic", "claude-haiku-4-5-20251001"):    Rate( 1.00,  5.00),
    # Older but still callable.
    ("anthropic", "claude-3-5-sonnet-20241022"):   Rate( 3.00, 15.00),
    ("anthropic", "claude-3-5-haiku-20241022"):    Rate( 0.80,  4.00),
    ("anthropic", "claude-3-opus-20240229"):       Rate(15.00, 75.00),
}


def rate_for(backend_kind: str, model: str) -> Rate | None:
    return _PRICING.get((backend_kind, model))


def estimate_cost(
    backend_kind: str,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
) -> float | None:
    """Return USD cost for the call, or None if no rate is on file.

    Local and self-hosted-remote backends always return ``None`` — the
    user is paying GPU / electricity directly and a price table would be
    misleading.
    """
    if backend_kind in {"local", "remote"}:
        return None
    rate = rate_for(backend_kind, model)
    if rate is None:
        return None
    return (
        prompt_tokens * rate.input_per_mtok
        + completion_tokens * rate.output_per_mtok
    ) / 1_000_000


__all__ = ["Rate", "rate_for", "estimate_cost"]
