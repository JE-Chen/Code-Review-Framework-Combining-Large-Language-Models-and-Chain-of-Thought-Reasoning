"""Copilot-style PR overview — summarise a PR's intent from its own words.

The review pipeline's ``first_summary`` step looks only at the diff. This
module produces the complementary *author-intent* overview: it reads what
the PR author actually wrote — the title, the description body, and every
commit message — alongside the diff, and asks the model to distil the
PR's key points the way GitHub Copilot's PR summary does.

It mirrors :mod:`prthinker.pr_classifier`: a runner-safe module that owns
its prompt template inline (no heavy imports, no ``codes`` dependency),
exposes a pure :func:`build_prompt`, and a best-effort post-processor
:func:`clean_summary`. Inference itself runs through the injected backend
in :class:`prthinker.pipeline.CoTPipeline`, never here.
"""

from __future__ import annotations

import re

# Distinct marker so the PR summary lives in its own comment, separate
# from the review summary comment (which uses ``prthinker:summary``).
DEFAULT_MARKER = "<!-- prthinker:pr-summary -->"

# The diff is truncated: the summary needs the *shape* of the change, not
# every line, and a multi-thousand-line diff would blow the context budget.
_DEFAULT_DIFF_CHARS = 12000
# Cap the commit list so a PR with hundreds of commits cannot dominate the
# prompt; the subjects of the most recent commits carry the intent.
_MAX_COMMITS = 50

_NO_TITLE = "(no title)"
_NO_BODY = "(no description provided)"
_NO_COMMITS = "(no commit messages)"

PROMPT_TEMPLATE = """\
# Pull Request Summary

You are summarising a Pull Request for reviewers, the way a senior
engineer would brief the team before they read the code. Use the
author's own words (title, description, commit messages) AND the diff,
and reconcile them: if the description claims something the diff does
not show — or the diff does something the description never mentions —
say so explicitly.

Write GitHub-flavoured Markdown with these sections, and nothing else:

* **Overview** — two or three sentences on what this PR does and why.
* **Key changes** — a bullet list of the most important changes.
* **Areas to review** — bullet points a reviewer should focus on (risk,
  missing tests, behaviour changes), or "None obvious".
* **Notes** — include only when the description and the diff disagree;
  otherwise omit this section entirely.

Keep it concise and high-level. Do not invent changes that are not in the
diff. Do not restate the entire diff line by line.

## PR title
{title}

## PR description
{body}

## Commit messages
{commits}

## Diff (truncated to first {diff_chars} characters)
{diff_excerpt}
"""


def _format_commits(commit_messages: tuple[str, ...]) -> str:
    """Render commit messages as a bullet list of subjects, capped."""
    cleaned = [m.strip() for m in commit_messages if m and m.strip()]
    if not cleaned:
        return _NO_COMMITS
    # Keep only the subject line of each commit — it carries the intent;
    # full bodies bloat the prompt without adding signal.
    subjects = [m.splitlines()[0].strip() for m in cleaned[:_MAX_COMMITS]]
    return "\n".join(f"- {subject}" for subject in subjects)


def build_prompt(
    *,
    diff_text: str,
    title: str = "",
    body: str = "",
    commit_messages: tuple[str, ...] = (),
    diff_chars: int = _DEFAULT_DIFF_CHARS,
) -> str:
    """Render the PR-summary prompt from the author's words plus the diff.

    Every input is optional: a PR with no description still produces a
    diff-grounded summary. ``diff_chars`` clamps the diff excerpt (negative
    values clamp to zero) so a huge PR cannot blow the context budget.
    """
    chars = max(0, diff_chars)
    return PROMPT_TEMPLATE.format(
        title=(title or "").strip() or _NO_TITLE,
        body=(body or "").strip() or _NO_BODY,
        commits=_format_commits(tuple(commit_messages)),
        diff_chars=chars,
        diff_excerpt=(diff_text or "")[:chars],
    )


_FENCE_RE = re.compile(
    r"^\s*```(?:markdown|md)?\s*\n([\s\S]*?)\n```\s*$", re.IGNORECASE
)


def clean_summary(raw_output: str) -> str:
    """Best-effort tidy of the model's summary text.

    Strips a single wrapping Markdown code fence (some models wrap the
    whole answer in ``` ```markdown ```) and trims surrounding whitespace.
    Returns an empty string for empty / whitespace-only input.
    """
    text = (raw_output or "").strip()
    if not text:
        return ""
    fence = _FENCE_RE.match(text)
    if fence:
        return fence.group(1).strip()
    return text


def render_comment(summary: str, *, marker: str = DEFAULT_MARKER) -> str:
    """Wrap the summary in a marker-tagged comment body.

    The marker (an HTML comment, invisible in rendered Markdown) lets the
    adapter upsert this comment in place across re-runs, exactly like the
    review summary comment.
    """
    return f"{marker}\n## PR Summary\n\n{summary.strip()}\n"


__all__ = [
    "DEFAULT_MARKER",
    "PROMPT_TEMPLATE",
    "build_prompt",
    "clean_summary",
    "render_comment",
]
