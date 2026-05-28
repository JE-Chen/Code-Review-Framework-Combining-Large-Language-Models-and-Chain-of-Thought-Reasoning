"""Multi-turn closed-loop review — capture author replies to prior reviews.

Existing literature treats the review as one-shot: the reviewer posts
findings, the author may reply ("wontfix because X"), but the model
never reads the reply. This module wires the loop closed:

1. Before generating a new review, ask the :class:`PlatformAdapter`
   for the most recent reviewmind summary comment and the author's
   replies in its thread.
2. Render those replies into a structured "Prior dialogue" block.
3. Inject the block as additional context into the inline-findings
   prompt so the model can either (a) drop findings the author has
   already addressed, (b) refine findings in light of the author's
   counter-argument, or (c) hold its position with new evidence.

The mechanism is a *design contribution* in this study; its end-to-end
quality impact is not yet evaluated (see ``paper_rule.md``: no
fabrication). Future work will measure precision-in-round-k as the
dialogue extends.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AuthorReply:
    """One reply from the PR author on a previous reviewmind comment."""

    author: str
    body: str
    in_reply_to_id: int | None = None
    created_at: str | None = None


def render_dialogue_block(replies: list[AuthorReply]) -> str:
    """Format author replies as a prompt-ready block.

    Returns empty string when there are no replies — callers can use it
    as ``{block}`` directly in their prompt template.
    """
    if not replies:
        return ""

    out: list[str] = [
        "## Prior dialogue (author replies to your previous review)",
        "",
        "Read each reply carefully. For each finding you are about to",
        "produce, ask: has the author already addressed or contested it?",
        "If yes, either drop the finding, refine it in light of the",
        "author's argument, or rebut with concrete new evidence — but",
        "never silently re-post the same comment the author already",
        "responded to.",
        "",
    ]
    for i, reply in enumerate(replies, start=1):
        author = reply.author or "(unknown)"
        out.append(f"### Reply {i} — from @{author}")
        if reply.created_at:
            out.append(f"*{reply.created_at}*")
        out.append("")
        out.append(reply.body.strip())
        out.append("")
    return "\n".join(out)


__all__ = ["AuthorReply", "render_dialogue_block"]
