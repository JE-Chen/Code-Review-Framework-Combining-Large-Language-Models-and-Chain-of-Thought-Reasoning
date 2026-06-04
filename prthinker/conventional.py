"""Conventional-Comments labelling for inline review comments.

`conventionalcomments.org <https://conventionalcomments.org>`_ gives a
review comment a small, machine-parseable label — ``issue``,
``suggestion``, ``nitpick`` — so a reader (and tooling) can triage at a
glance whether a remark is blocking or optional. We derive the label from
the finding's severity and decorate it with the category (when set) so a
comment reads ``🔴 **issue (security):** …`` instead of a bare badge.

Runner-safe: pure mapping over the finding's own fields.
"""

from __future__ import annotations

from prthinker.schemas import InlineFinding

# Severity → emoji tier (the at-a-glance colour) and Conventional-Comments
# label (the blocking/optional intent). Kept side by side so the two never
# drift: error blocks (issue), warning should be addressed (suggestion),
# info is optional (nitpick).
_SEVERITY_EMOJI: dict[str, str] = {
    "error": "🔴",
    "warning": "🟡",
    "info": "🔵",
}
_CONVENTIONAL_LABEL: dict[str, str] = {
    "error": "issue",
    "warning": "suggestion",
    "info": "nitpick",
}


def conventional_prefix(finding: InlineFinding) -> str:
    """Return the ``🔴 **issue (security):**`` prefix for a finding.

    Falls back to the raw severity string for an unknown severity, and
    omits the ``(category)`` decoration when the finding carries no
    category.
    """
    emoji = _SEVERITY_EMOJI.get(finding.severity, "")
    label = _CONVENTIONAL_LABEL.get(finding.severity, finding.severity)
    decoration = f" ({finding.category})" if finding.category else ""
    tag = f"**{label}{decoration}:**"
    return f"{emoji} {tag}" if emoji else tag


def format_inline_body(finding: InlineFinding) -> str:
    """Render a finding as an inline-comment body (prefix + comment + fix).

    Shared by every platform adapter so the Conventional-Comments label
    and the one-click ```suggestion`` block stay identical across GitHub,
    Gitea, and any future host.
    """
    body = f"{conventional_prefix(finding)} {finding.comment.strip()}"
    if finding.suggestion is not None:
        # GitHub / Gitea render ```suggestion blocks as a one-click apply.
        body += "\n\n```suggestion\n" + finding.suggestion.rstrip("\n") + "\n```"
    return body


__all__ = ["conventional_prefix", "format_inline_body"]
