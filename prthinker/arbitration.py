"""Multi-model arbitration over inline review findings.

Opt-in post-review layer (``--arbitration``): a panel of arbiter
backends votes ``confirm`` / ``reject`` on each inline finding produced
by the primary review model, and a pluggable
:class:`ArbitrationStrategy` combines the votes to decide which findings
survive.

Fail-open posture throughout — arbitration may only ever *drop* noise,
never invent findings, and it must not lose real findings to arbiter
flakiness:

* an arbiter whose call raises or whose output cannot be parsed
  **abstains** (contributes no votes);
* a finding that collected **zero countable votes is kept**;
* the whole layer is skipped when there are no findings or no arbiters.

Runner-safe: stdlib + pydantic only; inference lives entirely in the
injected :class:`~prthinker.backends.base.InferenceBackend` strategies.
"""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass

from prthinker.backends.base import InferenceBackend
from prthinker.lenient_json import iter_json_arrays
from prthinker.schemas import InlineFinding

log = logging.getLogger(__name__)

_VERDICT_CONFIRM = "confirm"
_VERDICT_REJECT = "reject"

DEFAULT_ARBITRATION_MAX_NEW_TOKENS = 4096


# --- prompt template ------------------------------------------------------


def _format_finding_row(index: int, finding: InlineFinding) -> str:
    """Render one numbered finding line for the arbitration prompt."""
    return (
        f"{index}. [{finding.severity}] {finding.path}:{finding.line} — "
        f"{finding.comment.strip()}"
    )


def build_arbitration_prompt(
    diff_text: str, findings: Sequence[InlineFinding]
) -> str:
    """Build the vote request sent to each arbiter backend."""
    rows = "\n".join(
        _format_finding_row(i, f) for i, f in enumerate(findings, start=1)
    )
    return (
        "You are an independent code-review arbiter. Another reviewer "
        "produced the findings below for the unified diff that follows. "
        "For EACH finding, judge whether it is a real, actionable issue "
        "in this diff (confirm) or noise / incorrect / not supported by "
        "the diff (reject).\n\n"
        "End your reply with ONLY a JSON array, one object per finding, "
        "and nothing after it:\n"
        '[{"id": 1, "verdict": "confirm"}, {"id": 2, "verdict": "reject"}]\n\n'
        "Findings:\n"
        f"{rows}\n\n"
        "Diff:\n"
        f"{diff_text}"
    )


# --- vote parsing ---------------------------------------------------------


def _vote_from_item(item: object, count: int) -> tuple[int, bool] | None:
    """Extract ``(finding_index, confirmed)`` from one vote object, or None."""
    if not isinstance(item, dict):
        return None
    raw_id = item.get("id")
    verdict = str(item.get("verdict") or "").strip().lower()
    if not isinstance(raw_id, int) or not 1 <= raw_id <= count:
        return None
    if verdict not in (_VERDICT_CONFIRM, _VERDICT_REJECT):
        return None
    return raw_id, verdict == _VERDICT_CONFIRM


def _votes_from_array(candidate: str, count: int) -> dict[int, bool]:
    """Parse one ``[...]`` candidate into votes; ``{}`` if it is not a JSON
    list of well-formed vote objects. Duplicate ids keep the last vote."""
    try:
        data = json.loads(candidate)
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, list):
        return {}
    votes: dict[int, bool] = {}
    for item in data:
        vote = _vote_from_item(item, count)
        if vote is not None:
            votes[vote[0]] = vote[1]
    return votes


def parse_votes(raw: str, count: int) -> dict[int, bool]:
    """Best-effort parse of one arbiter's votes; ``{}`` means abstain.

    Scans every bracket-balanced ``[...]`` span in the reply and keeps the
    votes from the **last** span that yields at least one well-formed vote
    — the model's final answer, even when preceded by chain-of-thought
    prose or a non-JSON code fence and followed by trailing text (all of
    which used to make the old fenced/greedy-regex parser abstain, so the
    fail-open path then wrongly *kept* the noise the arbiter had rejected).
    Only vote objects whose id is within ``1..count`` count; duplicate ids
    keep the last vote.
    """
    votes: dict[int, bool] = {}
    for candidate in iter_json_arrays(raw):
        parsed = _votes_from_array(candidate, count)
        if parsed:
            votes = parsed
    if not votes:
        log.debug("Arbiter output yielded no countable votes: %r", raw[:200])
    return votes


# --- vote-combination strategies -----------------------------------------


class ArbitrationStrategy(ABC):
    """Decide whether a finding survives given its confirm / reject tallies."""

    name: str = ""

    @abstractmethod
    def keep(self, confirms: int, rejects: int) -> bool:
        """Return True when the finding should be kept.

        Called only for findings with at least one countable vote; the
        zero-vote fail-open path is handled by the arbitrator itself.
        """


class MajorityStrategy(ArbitrationStrategy):
    """Drop a finding only when rejects outnumber confirms (ties keep)."""

    name = "majority"

    def keep(self, confirms: int, rejects: int) -> bool:
        return rejects <= confirms


class UnanimousStrategy(ArbitrationStrategy):
    """Keep a finding only when no arbiter rejected it."""

    name = "unanimous"

    def keep(self, confirms: int, rejects: int) -> bool:
        del confirms
        return rejects == 0


class AnyConfirmStrategy(ArbitrationStrategy):
    """Keep a finding as soon as one arbiter confirmed it."""

    name = "any"

    def keep(self, confirms: int, rejects: int) -> bool:
        del rejects
        return confirms >= 1


_STRATEGIES: dict[str, type[ArbitrationStrategy]] = {
    cls.name: cls
    for cls in (MajorityStrategy, UnanimousStrategy, AnyConfirmStrategy)
}

STRATEGY_NAMES: tuple[str, ...] = tuple(_STRATEGIES)


def create_arbitration_strategy(name: str) -> ArbitrationStrategy:
    """Factory for vote-combination strategies; raises on unknown names."""
    strategy_cls = _STRATEGIES.get(name)
    if strategy_cls is None:
        raise ValueError(
            f"unknown arbitration strategy {name!r}; "
            f"expected one of {STRATEGY_NAMES}"
        )
    return strategy_cls()


# --- the arbitrator -------------------------------------------------------


@dataclass(frozen=True)
class ArbitrationOutcome:
    """Partition of the input findings plus the per-finding tallies.

    ``tallies`` maps the 1-based finding index to ``(confirms, rejects)``.
    """

    kept: list[InlineFinding]
    dropped: list[InlineFinding]
    tallies: dict[int, tuple[int, int]]


class FindingArbitrator:
    """Fan findings out to arbiter backends and apply the vote strategy."""

    def __init__(
        self,
        backends: Sequence[InferenceBackend],
        strategy: ArbitrationStrategy,
        max_new_tokens: int = DEFAULT_ARBITRATION_MAX_NEW_TOKENS,
    ) -> None:
        if not backends:
            raise ValueError("FindingArbitrator requires at least one backend")
        self._backends = tuple(backends)
        self._strategy = strategy
        self._max_new_tokens = max_new_tokens

    def arbitrate(
        self,
        findings: Sequence[InlineFinding],
        diff_text: str,
        *,
        cancel_event: "object | None" = None,
    ) -> ArbitrationOutcome:
        """Collect votes from every arbiter and partition the findings."""
        items = list(findings)
        if not items:
            return ArbitrationOutcome(kept=[], dropped=[], tallies={})
        prompt = build_arbitration_prompt(diff_text, items)
        tallies = self._collect_tallies(prompt, len(items), cancel_event)
        return self._partition(items, tallies)

    def _collect_tallies(
        self,
        prompt: str,
        count: int,
        cancel_event: "object | None",
    ) -> dict[int, tuple[int, int]]:
        """Query each arbiter, skipping (and logging) the ones that raise."""
        tallies: dict[int, tuple[int, int]] = {}
        for backend in self._backends:
            try:
                raw = backend.generate(
                    prompt, self._max_new_tokens, cancel_event=cancel_event
                )
            except Exception:  # noqa: BLE001 — one flaky arbiter must not kill the review
                log.warning(
                    "Arbiter backend %s failed; it abstains",
                    backend.backend_kind(),
                    exc_info=True,
                )
                continue
            for index, confirmed in parse_votes(raw, count).items():
                confirms, rejects = tallies.get(index, (0, 0))
                tallies[index] = (
                    (confirms + 1, rejects) if confirmed
                    else (confirms, rejects + 1)
                )
        return tallies

    def _partition(
        self,
        items: list[InlineFinding],
        tallies: dict[int, tuple[int, int]],
    ) -> ArbitrationOutcome:
        """Split findings into kept / dropped; zero-vote findings are kept."""
        kept: list[InlineFinding] = []
        dropped: list[InlineFinding] = []
        for index, finding in enumerate(items, start=1):
            confirms, rejects = tallies.get(index, (0, 0))
            if confirms + rejects == 0 or self._strategy.keep(confirms, rejects):
                kept.append(finding)
                continue
            log.info(
                "Arbitration dropped %s:%d (confirm=%d reject=%d)",
                finding.path, finding.line, confirms, rejects,
            )
            dropped.append(finding)
        return ArbitrationOutcome(kept=kept, dropped=dropped, tallies=tallies)


__all__ = [
    "ArbitrationOutcome",
    "ArbitrationStrategy",
    "AnyConfirmStrategy",
    "DEFAULT_ARBITRATION_MAX_NEW_TOKENS",
    "FindingArbitrator",
    "MajorityStrategy",
    "STRATEGY_NAMES",
    "UnanimousStrategy",
    "build_arbitration_prompt",
    "create_arbitration_strategy",
    "parse_votes",
]
