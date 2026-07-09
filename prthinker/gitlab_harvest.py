"""Harvest dismissed / accepted inline notes from GitLab merge requests.

GitLab counterpart of :mod:`prthinker.harvest`, feeding the same
learned-corpora stores. The dismissal and acceptance semantics mirror
the GitHub harvester on purpose — both forges see the same reviewer
habits:

  - a diff note is "dismissed" when it carries a 👎 (``thumbsdown``)
    award emoji or a reply in its discussion matches the dismissal
    keywords;
  - an MR has "accepted" suggestions when one of its commits carries an
    applied-suggestion message; every diff note with a ```suggestion
    block on such an MR is then kept.
"""

from __future__ import annotations

import logging
import re
import urllib.parse
from typing import Iterable, Iterator

import httpx

from prthinker.accepted import AcceptedExample, AcceptedExamplesStore
from prthinker.dismissed import DismissedExample, DismissedExamplesStore
# The dismissal keywords and suggestion-block grammar are shared with
# the GitHub harvester so both platforms learn from the same signals.
from prthinker.harvest import (
    HarvestStats,
    _APPLY_COMMIT_RE,
    _DISMISS_RE,
    _SUGGESTION_RE,
    _extract_suggestion_block,
)

log = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://gitlab.com/api/v4"
_USER_AGENT = "prthinker-harvester/0.1"
_PER_PAGE = 100

# GitLab's default commit message for applied suggestions is
# "Apply %d suggestion(s) to %d file(s)". Projects with a custom
# template that mimics GitHub's wording are covered by the shared
# ``_APPLY_COMMIT_RE`` as well.
_GITLAB_APPLY_RE = re.compile(r"^Apply \d+ suggestion", re.MULTILINE)


def harvest(
    project: str,
    token: str,
    *,
    store: DismissedExamplesStore,
    mr_iid: int | None = None,
    max_mrs: int = 50,
    base_url: str = DEFAULT_BASE_URL,
) -> HarvestStats:
    """Harvest dismissed diff notes. If ``mr_iid`` is set, harvest just that MR."""
    project_quoted = urllib.parse.quote(str(project), safe="")
    stats = HarvestStats()
    with _client(token, base_url) as client:
        if mr_iid is not None:
            stats.prs_scanned = 1
            _harvest_one_mr(client, project_quoted, mr_iid, store, stats)
        else:
            for iid in _iter_recent_closed_mrs(client, project_quoted, max_mrs):
                stats.prs_scanned += 1
                try:
                    _harvest_one_mr(client, project_quoted, iid, store, stats)
                except httpx.HTTPStatusError as exc:
                    log.warning("MR !%d failed: %s", iid, exc)
                    continue

    log.info(
        "GitLab harvest done: scanned %d MR(s), %d note(s), kept %d dismissed",
        stats.prs_scanned, stats.comments_scanned, stats.dismissed_found,
    )
    return stats


def harvest_accepted(
    project: str,
    token: str,
    *,
    store: AcceptedExamplesStore,
    mr_iid: int | None = None,
    max_mrs: int = 50,
    base_url: str = DEFAULT_BASE_URL,
) -> HarvestStats:
    """Harvest accepted suggestion examples from GitLab MRs.

    Heuristic mirror of the GitHub harvester: an MR has accepted
    suggestions when one of its commits matches an applied-suggestion
    message; every diff note containing a ```suggestion``` block on such
    an MR is kept — best-effort, with no per-suggestion attribution.
    """
    project_quoted = urllib.parse.quote(str(project), safe="")
    stats = HarvestStats()
    with _client(token, base_url) as client:
        iids: Iterable[int]
        if mr_iid is not None:
            iids = [mr_iid]
        else:
            iids = list(_iter_recent_closed_mrs(client, project_quoted, max_mrs))

        for iid in iids:
            stats.prs_scanned += 1
            try:
                _harvest_accepted_one_mr(client, project_quoted, iid, store, stats)
            except httpx.HTTPStatusError as exc:
                log.warning("MR !%d failed: %s", iid, exc)
                continue

    log.info(
        "GitLab accepted harvest done: scanned %d MR(s), %d note(s), "
        "kept %d accepted",
        stats.prs_scanned, stats.comments_scanned, stats.accepted_found,
    )
    return stats


def _client(token: str, base_url: str) -> httpx.Client:
    return httpx.Client(
        base_url=base_url.rstrip("/"),
        headers={
            "PRIVATE-TOKEN": token,
            "User-Agent": _USER_AGENT,
        },
        timeout=30.0,
    )


def _iter_pages(
    client: httpx.Client, path: str, params: dict | None = None
) -> Iterator[dict]:
    """Yield every item of a paginated GitLab list endpoint."""
    page = 1
    while True:
        response = client.get(
            path,
            params={**(params or {}), "per_page": _PER_PAGE, "page": page},
        )
        response.raise_for_status()
        batch = response.json()
        if not batch:
            return
        yield from batch
        if len(batch) < _PER_PAGE:
            return
        page += 1


def _iter_recent_closed_mrs(
    client: httpx.Client, project_quoted: str, max_mrs: int
) -> Iterator[int]:
    """Yield the iids of recently-updated merged / closed MRs."""
    seen = 0
    for mr in _iter_pages(
        client,
        f"/projects/{project_quoted}/merge_requests",
        params={"order_by": "updated_at", "sort": "desc"},
    ):
        # Open MRs have no final verdict on their notes yet.
        if mr.get("state") == "opened":
            continue
        yield int(mr["iid"])
        seen += 1
        if seen >= max_mrs:
            return


def _discussions_path(project_quoted: str, mr_iid: int) -> str:
    return f"/projects/{project_quoted}/merge_requests/{mr_iid}/discussions"


def _harvest_one_mr(
    client: httpx.Client,
    project_quoted: str,
    mr_iid: int,
    store: DismissedExamplesStore,
    stats: HarvestStats,
) -> None:
    for discussion in _iter_pages(
        client, _discussions_path(project_quoted, mr_iid)
    ):
        notes = [
            n for n in (discussion.get("notes") or []) if not n.get("system")
        ]
        # Only diff notes (inline findings) are dismissal candidates.
        if not notes or notes[0].get("type") != "DiffNote":
            continue
        stats.comments_scanned += 1
        _harvest_dismissed_note(
            client, project_quoted, mr_iid, notes[0], notes[1:], store, stats,
        )


def _harvest_dismissed_note(
    client: httpx.Client,
    project_quoted: str,
    mr_iid: int,
    note: dict,
    replies: list[dict],
    store: DismissedExamplesStore,
    stats: HarvestStats,
) -> None:
    """Append the note as a dismissed example when it is dismissed and non-empty."""
    reason = _dismissal_reason(client, project_quoted, mr_iid, note, replies)
    if reason is None:
        return
    body = (note.get("body") or "").strip()
    if not body:
        return
    store.append(
        DismissedExample(
            path=_note_path(note),
            comment=body,
            reason=reason,
            # GitLab notes carry a position, not the hunk text itself.
            diff_snippet="",
        )
    )
    stats.dismissed_found += 1


def _note_path(note: dict) -> str:
    position = note.get("position") or {}
    return str(position.get("new_path") or position.get("old_path") or "")


def _dismissal_reason(
    client: httpx.Client,
    project_quoted: str,
    mr_iid: int,
    note: dict,
    replies: Iterable[dict],
) -> str | None:
    """Return a short reason string if this note is dismissed, else None."""
    if _has_thumbs_down(client, project_quoted, mr_iid, int(note["id"])):
        return "thumbs-down award"

    for reply in replies:
        text = reply.get("body") or ""
        match = _DISMISS_RE.search(text)
        if match:
            return f"reply matched: {match.group(0)!r}"

    return None


def _has_thumbs_down(
    client: httpx.Client, project_quoted: str, mr_iid: int, note_id: int
) -> bool:
    response = client.get(
        f"/projects/{project_quoted}/merge_requests/{mr_iid}"
        f"/notes/{note_id}/award_emoji",
    )
    if response.status_code == 404:
        return False
    response.raise_for_status()
    return any(a.get("name") == "thumbsdown" for a in response.json())


def _harvest_accepted_one_mr(
    client: httpx.Client,
    project_quoted: str,
    mr_iid: int,
    store: AcceptedExamplesStore,
    stats: HarvestStats,
) -> None:
    if not _mr_has_apply_commit(client, project_quoted, mr_iid):
        return

    for discussion in _iter_pages(
        client, _discussions_path(project_quoted, mr_iid)
    ):
        for note in discussion.get("notes") or []:
            if note.get("system"):
                continue
            stats.comments_scanned += 1
            _append_accepted_note(note, mr_iid, store, stats)


def _append_accepted_note(
    note: dict,
    mr_iid: int,
    store: AcceptedExamplesStore,
    stats: HarvestStats,
) -> None:
    body = note.get("body") or ""
    suggestion = _extract_suggestion_block(body)
    if not suggestion:
        return

    # Strip the suggestion block from the comment so the embedding
    # reflects the advisory text, not the patch.
    comment_text = _SUGGESTION_RE.sub("", body).strip() or "(suggestion only)"

    store.append(
        AcceptedExample(
            path=_note_path(note),
            comment=comment_text,
            suggestion=suggestion,
            pr_number=mr_iid,
        )
    )
    stats.accepted_found += 1


def _mr_has_apply_commit(
    client: httpx.Client, project_quoted: str, mr_iid: int
) -> bool:
    for commit in _iter_pages(
        client,
        f"/projects/{project_quoted}/merge_requests/{mr_iid}/commits",
    ):
        message = str(commit.get("message") or commit.get("title") or "")
        if _GITLAB_APPLY_RE.search(message) or _APPLY_COMMIT_RE.search(message):
            return True
    return False


__all__ = ["DEFAULT_BASE_URL", "harvest", "harvest_accepted"]
