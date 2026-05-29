"""Active-learning lessons store — derive reusable rules from past
``dismissed`` / ``accepted`` examples and inject them back into future
reviews.

The existing ``dismissed.jsonl`` / ``accepted.jsonl`` are first-order
signals: "this exact comment got dropped" / "this exact suggestion got
applied". This module closes the loop one level higher: every N days
the framework batches recent dismissals + acceptances and asks the
model to extract the *general rule* the human reviewer implicitly
taught the reviewer-bot. Those rules live in ``lessons.jsonl`` and
get retrieved top-K at review time, alongside accepted exemplars.

Per ``paper_rule.md``'s no-fabrication rule, this module ships the
mechanism only — no claim about how much the derived rules improve
review quality. That measurement is future work.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from prthinker.backends.base import InferenceBackend

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class LessonRule:
    """One reusable rule the model extracted from prior corrections.

    ``trigger`` is the situation the rule applies to ("when the diff
    adds a logger.debug call ..."); ``action`` is what the reviewer
    should do ("... do not flag it as a missing logging level"). The
    paired ``derived_from_pr_numbers`` lets a future human audit which
    corrections this rule was distilled from.
    """

    name: str
    trigger: str
    action: str
    derived_from_pr_numbers: tuple[int, ...] = ()
    ts: float = 0.0

    def to_jsonl(self) -> str:
        return json.dumps({
            "name": self.name,
            "trigger": self.trigger,
            "action": self.action,
            "derived_from_pr_numbers": list(self.derived_from_pr_numbers),
            "ts": self.ts,
        }, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict) -> "LessonRule":
        prs = data.get("derived_from_pr_numbers", []) or []
        return cls(
            name=str(data.get("name", "")).strip(),
            trigger=str(data.get("trigger", "")).strip(),
            action=str(data.get("action", "")).strip(),
            derived_from_pr_numbers=tuple(int(p) for p in prs if str(p).isdigit()),
            ts=float(data.get("ts", 0.0) or 0.0),
        )


class LessonsStore:
    """Append-only JSONL store of derived lessons.

    Symmetric to :class:`prthinker.accepted.AcceptedExamplesStore` — the
    file is the authoritative state; the in-memory list is a cache that
    gets reloaded on construction. Cross-process appends are safe
    because each row is one ``\\n``-terminated JSON object.
    """

    def __init__(self, path: Path) -> None:
        self._path = Path(path)
        self._rules: list[LessonRule] = []
        if self._path.exists():
            self._load()

    def _load(self) -> None:
        for raw in self._path.read_text(encoding="utf-8").splitlines():
            raw = raw.strip()
            if not raw:
                continue
            try:
                self._rules.append(LessonRule.from_dict(json.loads(raw)))
            except json.JSONDecodeError:
                log.debug("Skipping malformed lesson row: %s", raw[:80])

    def __len__(self) -> int:
        return len(self._rules)

    def __iter__(self):
        return iter(self._rules)

    def append(self, rule: LessonRule) -> None:
        self._rules.append(rule)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding="utf-8") as fh:
            fh.write(rule.to_jsonl() + "\n")


DERIVE_PROMPT_TEMPLATE = """\
# Derive review lessons from past corrections

You are given two short corpora of past code-review interactions on
this repository:

* ``dismissed`` — comments the bot reviewer raised that the PR author
  rejected (with the rejection reason where available).
* ``accepted`` — suggestions the bot reviewer raised that the PR
  author applied as-is.

Your job is to extract up to {max_rules} *general rules* that explain
what the bot reviewer should have done differently or should keep
doing. Each rule must be reusable on *future* PRs, not a re-statement
of a single past correction.

You MUST output ONLY a JSON array. Each element conforms to:

  {{
    "name":    "<short kebab-case rule id>",
    "trigger": "<one sentence: the situation the rule applies to>",
    "action":  "<one sentence: what the reviewer should do>"
  }}

Rules:

- If neither corpus contains enough signal to generalise, output
  exactly ``[]``. A made-up rule is worse than no rule.
- Do not reproduce single examples verbatim; abstract over them.
- Do not contradict existing rules already in the repo's
  ``--rules-dir`` (we cannot show you those here — keep your rules
  framed positively, never "ignore rule X").

## Dismissed corpus (latest {n_dismissed} entries)

{dismissed_block}

## Accepted corpus (latest {n_accepted} entries)

{accepted_block}
"""


def _render_dismissed_block(dismissed: Iterable) -> str:
    items = list(dismissed)
    if not items:
        return "(no dismissed examples in the lookback window)"
    out: list[str] = []
    for i, ex in enumerate(items, start=1):
        out.append(
            f"### {i}. `{getattr(ex, 'path', '?')}`\n"
            f"Comment: {getattr(ex, 'comment', '').strip()}\n"
            f"Reason: {getattr(ex, 'reason', '').strip()}\n"
        )
    return "\n".join(out)


def _render_accepted_block(accepted: Iterable) -> str:
    items = list(accepted)
    if not items:
        return "(no accepted examples in the lookback window)"
    out: list[str] = []
    for i, ex in enumerate(items, start=1):
        out.append(
            f"### {i}. `{getattr(ex, 'path', '?')}` (PR "
            f"#{getattr(ex, 'pr_number', 0)})\n"
            f"Comment: {getattr(ex, 'comment', '').strip()}\n"
        )
    return "\n".join(out)


def build_derive_prompt(
    *, dismissed: Iterable, accepted: Iterable, max_rules: int = 5,
) -> str:
    """Render the derive-lessons prompt for the model."""
    dismissed_list = list(dismissed)
    accepted_list = list(accepted)
    return DERIVE_PROMPT_TEMPLATE.format(
        max_rules=max_rules,
        n_dismissed=len(dismissed_list),
        n_accepted=len(accepted_list),
        dismissed_block=_render_dismissed_block(dismissed_list),
        accepted_block=_render_accepted_block(accepted_list),
    )


def parse_lessons(raw_output: str, *, source_prs: tuple[int, ...]) -> list[LessonRule]:
    """Best-effort parse of the model's JSON-array reply.

    Bad rows are dropped silently; never crashes the derive job.
    ``source_prs`` is recorded on each rule for traceability.
    """
    import re
    body = raw_output.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", body, re.IGNORECASE)
    if fence:
        body = fence.group(1).strip()
    if not body or body == "[]":
        return []
    match = re.search(r"\[[\s\S]*\]", body)
    if match is None:
        log.warning("lessons parser: no JSON array found")
        return []
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        log.warning("lessons parser: JSON decode failed (%s)", exc)
        return []
    if not isinstance(data, list):
        return []
    out: list[LessonRule] = []
    now = time.time()
    for entry in data:
        if not isinstance(entry, dict):
            continue
        name = str(entry.get("name", "")).strip()
        trigger = str(entry.get("trigger", "")).strip()
        action = str(entry.get("action", "")).strip()
        if not name or not trigger or not action:
            continue
        out.append(LessonRule(
            name=name, trigger=trigger, action=action,
            derived_from_pr_numbers=source_prs, ts=now,
        ))
    return out


def derive_lessons(
    *,
    backend: InferenceBackend,
    dismissed: Iterable,
    accepted: Iterable,
    source_prs: tuple[int, ...] = (),
    max_rules: int = 5,
    max_new_tokens: int = 4096,
) -> list[LessonRule]:
    """Build the derive prompt, call the backend, parse the reply.

    Pure orchestration; the persistent store is the caller's job
    (see :class:`LessonsStore` for append-only persistence).
    """
    prompt = build_derive_prompt(
        dismissed=dismissed, accepted=accepted, max_rules=max_rules,
    )
    raw = backend.generate(prompt, max_new_tokens=max_new_tokens)
    return parse_lessons(raw, source_prs=source_prs)


def format_lessons_block(rules: Iterable[LessonRule]) -> str:
    """Render top-K lessons as a prompt-ready block. Empty list → ''."""
    items = list(rules)
    if not items:
        return ""
    lines = [
        "## Repo-derived review lessons (from past dismissed / accepted corrections)",
        "",
        "Treat these as soft guidance learned from this repo's prior",
        "review history. Do not re-state them as findings; just let",
        "them shape what you flag and how you flag it.",
        "",
    ]
    for i, r in enumerate(items, start=1):
        lines += [
            f"### Lesson {i}: `{r.name}`",
            f"- **Trigger:** {r.trigger}",
            f"- **Action:** {r.action}",
            "",
        ]
    return "\n".join(lines)


__all__ = [
    "DERIVE_PROMPT_TEMPLATE",
    "LessonRule",
    "LessonsStore",
    "build_derive_prompt",
    "derive_lessons",
    "format_lessons_block",
    "parse_lessons",
]
