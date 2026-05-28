"""Tests for :mod:`prthinker.dialogue` — author-reply harvesting.

The renderer is a pure function over a list of :class:`AuthorReply`;
the platform-side fetching is exercised separately through the adapter
tests with httpx mocks. Both layers are independent so this file does
not stand up a fake GitHub.
"""

from __future__ import annotations

from prthinker.dialogue import AuthorReply, render_dialogue_block


def test_render_empty_returns_empty_string() -> None:
    assert render_dialogue_block([]) == ""


def test_render_one_reply_includes_author_and_body() -> None:
    reply = AuthorReply(
        author="alice", body="I disagree because X.",
        in_reply_to_id=42, created_at="2026-05-27T12:00:00Z",
    )
    rendered = render_dialogue_block([reply])
    assert "## Prior dialogue" in rendered
    assert "@alice" in rendered
    assert "I disagree because X." in rendered
    assert "2026-05-27T12:00:00Z" in rendered


def test_render_multiple_replies_numbered() -> None:
    replies = [
        AuthorReply(author="a", body="r1"),
        AuthorReply(author="b", body="r2"),
        AuthorReply(author="c", body="r3"),
    ]
    rendered = render_dialogue_block(replies)
    assert "### Reply 1" in rendered
    assert "### Reply 2" in rendered
    assert "### Reply 3" in rendered


def test_render_strips_reply_body_whitespace() -> None:
    reply = AuthorReply(author="x", body="\n\n  trimmed me  \n\n")
    rendered = render_dialogue_block([reply])
    assert "trimmed me" in rendered
    assert "\n\n\n" not in rendered  # collapsed surrounding blanks


def test_author_reply_is_immutable() -> None:
    reply = AuthorReply(author="x", body="b")
    try:
        reply.body = "y"  # type: ignore[misc]
    except Exception:
        return
    raise AssertionError("AuthorReply should be frozen")
