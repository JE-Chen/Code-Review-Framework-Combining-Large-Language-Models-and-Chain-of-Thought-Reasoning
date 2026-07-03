"""GitLab :class:`PlatformAdapter`.

Maps the same five-method API the pipeline uses for GitHub onto
GitLab's MR endpoints. Three differences that the unit tests pin:

* **Project identifier** — GitLab accepts either a numeric ID or the
  URL-encoded ``group/subgroup/project`` path. We URL-encode the path
  once at adapter construction.
* **Inline comments** — GitLab calls them *discussions*, posted to
  ``POST /projects/:id/merge_requests/:iid/discussions`` with a
  ``position`` object specifying ``base_sha`` / ``head_sha`` /
  ``start_sha`` and the ``new_path`` + ``new_line``. We fetch the SHAs
  once per call and reuse them across all findings.
* **Gate equivalent** — GitLab has no Check Run API; commit statuses
  via ``POST /projects/:id/statuses/:sha`` play the role. Two states:
  ``pending`` for open, ``success`` / ``failed`` for closed. We map our
  :class:`prthinker.checks.CheckResult.conclusion` onto these.
"""

from __future__ import annotations

import logging
import urllib.parse
from dataclasses import dataclass
from typing import Any

import httpx

from prthinker.checks import CheckResult
from prthinker.ci_signals import FailureSignal
from prthinker.dialogue import AuthorReply
from prthinker.github_api import (
    filter_findings_to_diff,
    new_side_lines,
    replace_marked_section,
)
from prthinker.gitlab_ci_signals import fetch_gitlab_ci_failure_signals
from prthinker.platforms.base import PlatformAdapter
from prthinker.pr_labels import MANAGED_PREFIX
from prthinker.schemas import InlineFinding

log = logging.getLogger(__name__)

_USER_AGENT = "prthinker/0.1"
_NOTES_PER_PAGE = 100

# Map our event vocabulary to GitLab's discussion semantics. GitLab has
# no APPROVE / REQUEST_CHANGES verb on discussions themselves; the
# verdict is recorded as a body prefix AND mirrored onto the MR's
# approvals endpoint (``POST /merge_requests/:iid/approve`` /
# ``/unapprove``) by ``_apply_event_verdict``.
_EVENT_BODY_PREFIX: dict[str, str] = {
    "APPROVE":         "**Verdict: APPROVE** — ",
    "REQUEST_CHANGES": "**Verdict: REQUEST_CHANGES** — ",
    "COMMENT":         "",
}

_SEVERITY_BADGE: dict[str, str] = {
    "error":   "🔴 **error**",
    "warning": "🟡 **warning**",
    "info":    "🔵 _info_",
}

# Hidden marker embedded in every inline discussion and its companion
# summary note so the NEXT run can identify and delete its own
# predecessors — same value and purpose as the GitHub adapter's
# ``_INLINE_REVIEW_MARKER``. Distinct from the summary-comment marker so
# the two never collide.
_INLINE_REVIEW_MARKER = "<!-- prthinker:inline -->"


@dataclass
class GitLabAdapter(PlatformAdapter):
    project: str           # "group/project" or numeric id
    token: str
    mr_iid: int            # GitLab's per-project iid (NOT global id)
    comment_marker: str = "<!-- prthinker:summary -->"
    base_url: str = "https://gitlab.com/api/v4"

    def __post_init__(self) -> None:
        # URL-encode once; numeric IDs come through unchanged.
        self._project_quoted = urllib.parse.quote(str(self.project), safe="")
        # Cache MR metadata so we don't refetch SHAs across calls.
        self._mr_cache: dict[str, Any] | None = None

    def _client(self) -> httpx.Client:
        return httpx.Client(
            base_url=self.base_url.rstrip("/"),
            timeout=30.0,
            headers={
                "PRIVATE-TOKEN": self.token,
                "User-Agent": _USER_AGENT,
            },
        )

    def _mr(self, client: httpx.Client) -> dict[str, Any]:
        if self._mr_cache is not None:
            return self._mr_cache
        response = client.get(
            f"/projects/{self._project_quoted}"
            f"/merge_requests/{self.mr_iid}",
        )
        response.raise_for_status()
        self._mr_cache = response.json()
        return self._mr_cache

    # ----- metadata ------------------------------------------------------

    def fetch_diff(self) -> str:
        """Pull the MR diff via ``raw_diffs``, rebuilding from ``diffs`` on failure.

        Mirrors the GitHub adapter's 406 fallback: when the whole-MR diff
        endpoint rejects an oversized MR, the paginated per-file ``diffs``
        endpoint still serves each file's hunks, so the diff is
        reconstructed instead of failing the review.
        """
        with self._client() as client:
            response = client.get(
                f"/projects/{self._project_quoted}"
                f"/merge_requests/{self.mr_iid}/raw_diffs",
            )
            if response.status_code < 400:
                return response.text
            log.warning(
                "GitLab: raw_diffs returned %d for MR %d; reconstructing "
                "the diff from the paginated diffs endpoint",
                response.status_code, self.mr_iid,
            )
            entries = self._paginate(
                client,
                f"/projects/{self._project_quoted}"
                f"/merge_requests/{self.mr_iid}/diffs",
            )
        return "".join(_diff_entry_to_text(entry) for entry in entries)

    def fetch_head_sha(self) -> str:
        with self._client() as client:
            return str(self._mr(client).get("sha") or "")

    def fetch_base_branch(self) -> str:
        with self._client() as client:
            return str(self._mr(client).get("target_branch") or "")

    def fetch_pr_meta(self) -> tuple[str, str]:
        """Pull ``(title, body)`` from the MR endpoint we already cache."""
        with self._client() as client:
            mr = self._mr(client)
        return (str(mr.get("title") or ""), str(mr.get("description") or ""))

    def fetch_commit_messages(self) -> list[str]:
        """Return the MR's commit messages, oldest first (paginated)."""
        with self._client() as client:
            commits = self._paginate(
                client,
                f"/projects/{self._project_quoted}"
                f"/merge_requests/{self.mr_iid}/commits",
            )
        # GitLab serves MR commits newest first; the overview wants
        # chronological order.
        return [
            str(c.get("message") or c.get("title") or "")
            for c in reversed(commits)
        ]

    def fetch_changed_paths(self) -> list[str]:
        """Return every changed file path on the MR (paginated)."""
        with self._client() as client:
            diffs = self._paginate(
                client,
                f"/projects/{self._project_quoted}"
                f"/merge_requests/{self.mr_iid}/diffs",
            )
        return [
            str(d.get("new_path") or d.get("old_path") or "")
            for d in diffs
            if d.get("new_path") or d.get("old_path")
        ]

    def _paginate(
        self, client: httpx.Client, path: str, params: dict | None = None
    ) -> list[dict]:
        """Collect every page of a GitLab list endpoint."""
        items: list[dict] = []
        page = 1
        while True:
            response = client.get(
                path,
                params={
                    **(params or {}),
                    "per_page": _NOTES_PER_PAGE,
                    "page": page,
                },
            )
            response.raise_for_status()
            batch = response.json()
            if not batch:
                break
            items.extend(batch)
            if len(batch) < _NOTES_PER_PAGE:
                break
            page += 1
        return items

    # ----- labels + description -----------------------------------------

    def set_labels(self, labels: list[str]) -> None:
        """Reconcile the managed-prefix labels on the MR, keeping human ones."""
        with self._client() as client:
            mr = self._mr(client)
            current = [str(name) for name in (mr.get("labels") or [])]
            human = [n for n in current if not n.startswith(MANAGED_PREFIX)]
            desired = human + [n for n in labels if n not in human]
            for name in labels:
                self._ensure_label_exists(client, name)
            response = client.put(
                f"/projects/{self._project_quoted}"
                f"/merge_requests/{self.mr_iid}",
                json={"labels": ",".join(desired)},
            )
            response.raise_for_status()
            self._mr_cache = None
        log.info("GitLab: set MR labels: %s", labels)

    def _ensure_label_exists(self, client: httpx.Client, name: str) -> None:
        """Create the project label if missing; an existing one is fine."""
        response = client.post(
            f"/projects/{self._project_quoted}/labels",
            json={"name": name, "color": "#ededed"},
        )
        if response.status_code >= 400 and response.status_code != 409:
            log.debug(
                "GitLab: label %r create returned %d (already exists or "
                "insufficient rights); continuing",
                name, response.status_code,
            )

    def update_body_section(self, section: str) -> None:
        """Insert / replace the prthinker block in the MR description."""
        with self._client() as client:
            body = str(self._mr(client).get("description") or "")
            new_body = replace_marked_section(body, section)
            if new_body == body:
                return
            response = client.put(
                f"/projects/{self._project_quoted}"
                f"/merge_requests/{self.mr_iid}",
                json={"description": new_body},
            )
            response.raise_for_status()
            self._mr_cache = None
        log.info("GitLab: updated MR description section")

    # ----- summary comment ----------------------------------------------

    def upsert_summary_comment(self, body: str) -> int:
        with self._client() as client:
            return self._upsert_note(client, body, self.comment_marker)

    def upsert_marked_comment(self, body: str, *, marker: str) -> int:
        """Create-or-update a secondary MR note keyed by ``marker``."""
        with self._client() as client:
            return self._upsert_note(client, body, marker)

    def upsert_summary_comments(self, bodies: list[str]) -> list[int]:
        """Create / update / reconcile the paginated summary notes.

        Mirrors the GitHub reconcile semantics: existing marker notes
        (ascending id) are updated in page order, extra pages are
        created, and leftover notes from a previous longer run are
        deleted so stale parts never linger.
        """
        if not bodies:
            return []
        with self._client() as client:
            existing = self._find_marker_notes(client, self.comment_marker)
            ids: list[int] = []
            for index, body in enumerate(bodies):
                if index < len(existing):
                    ids.append(self._put_note(client, existing[index], body))
                else:
                    ids.append(self._post_note(client, body))
            for stale_id in existing[len(bodies):]:
                self._delete_note(client, stale_id)
        return ids

    def _upsert_note(
        self, client: httpx.Client, body: str, marker: str
    ) -> int:
        """Update the first note carrying ``marker``, or create one."""
        existing = self._find_marker_notes(client, marker)
        if existing:
            log.info("GitLab: updating existing note %d", existing[0])
            return self._put_note(client, existing[0], body)
        log.info("GitLab: creating new note")
        return self._post_note(client, body)

    def _find_marker_notes(
        self, client: httpx.Client, marker: str
    ) -> list[int]:
        """Ids of every note containing ``marker``, ascending."""
        notes = self._paginate(
            client,
            f"/projects/{self._project_quoted}"
            f"/merge_requests/{self.mr_iid}/notes",
        )
        return sorted(
            int(note["id"])
            for note in notes
            if marker in (note.get("body") or "")
        )

    def _put_note(self, client: httpx.Client, note_id: int, body: str) -> int:
        response = client.put(
            f"/projects/{self._project_quoted}"
            f"/merge_requests/{self.mr_iid}/notes/{note_id}",
            json={"body": body},
        )
        response.raise_for_status()
        return note_id

    def _post_note(self, client: httpx.Client, body: str) -> int:
        response = client.post(
            f"/projects/{self._project_quoted}"
            f"/merge_requests/{self.mr_iid}/notes",
            json={"body": body},
        )
        response.raise_for_status()
        return int(response.json()["id"])

    def _delete_note(self, client: httpx.Client, note_id: int) -> None:
        response = client.delete(
            f"/projects/{self._project_quoted}"
            f"/merge_requests/{self.mr_iid}/notes/{note_id}",
        )
        if response.status_code >= 400:
            log.warning(
                "GitLab: could not delete stale note %d (%d)",
                note_id, response.status_code,
            )

    # ----- inline review ------------------------------------------------

    def submit_inline_review(
        self,
        findings: list[InlineFinding],
        *,
        summary_body: str | None,
        event: str,
    ) -> int | None:
        if not findings:
            log.info("GitLab: no findings — skipping discussion creation")
            return None

        with self._client() as client:
            mr = self._mr(client)
            position_base = self._build_position_base(mr.get("diff_refs") or {})
            stale_note_ids = self._collect_stale_inline_notes(client)
            event_prefix = _EVENT_BODY_PREFIX.get(event, "")
            first_id: int | None = None
            for finding in self._prefilter_findings(client, findings):
                new_id = self._post_finding_discussion(
                    client, position_base, event_prefix, finding,
                )
                if first_id is None:
                    first_id = new_id

            if summary_body:
                # Drop a top-level note tying the discussions together.
                self._post_note(
                    client, f"{summary_body}\n\n{_INLINE_REVIEW_MARKER}",
                )

            self._apply_event_verdict(client, event)
            self._cleanup_stale_inline_notes(client, stale_note_ids)
            return first_id

    def _collect_stale_inline_notes(self, client: httpx.Client) -> list[int]:
        """Ids of the previous runs' marked inline notes (best-effort).

        Collected BEFORE the new discussions are posted so the fresh notes
        can never be swept up. A listing failure degrades to "clean up
        nothing" — stale threads linger but the review still posts.
        """
        try:
            return self._find_marker_notes(client, _INLINE_REVIEW_MARKER)
        except httpx.HTTPError as exc:
            log.warning(
                "GitLab: could not list prior inline notes (%s); "
                "skipping cleanup", exc,
            )
            return []

    def _cleanup_stale_inline_notes(
        self, client: httpx.Client, note_ids: list[int]
    ) -> None:
        """Delete the inline notes left by previous prthinker reviews.

        Runs AFTER the new discussions landed (mirroring the GitHub
        adapter) so a failed re-post leaves the prior run's findings
        intact instead of wiping them first.
        """
        if not note_ids:
            log.info("GitLab: no prior inline notes to clean up")
            return
        for note_id in note_ids:
            self._delete_note(client, note_id)
        log.info(
            "GitLab: cleaned up %d stale inline note(s)", len(note_ids),
        )

    def _prefilter_findings(
        self, client: httpx.Client, findings: list[InlineFinding]
    ) -> list[InlineFinding]:
        """Drop findings off the MR's diff hunks before any discussion POST.

        Same first-line-of-defence as the GitHub adapter: an off-hunk
        position 400s its discussion, so filtering keeps hallucinated
        lines from producing a run of failed POSTs. Fail-open — when the
        diff cannot be fetched or yields no hunk lines, every finding is
        submitted and the per-POST 4xx skip stays the backstop.
        """
        try:
            response = client.get(
                f"/projects/{self._project_quoted}"
                f"/merge_requests/{self.mr_iid}/raw_diffs",
            )
            response.raise_for_status()
            diff_text = response.text
        except httpx.HTTPError as exc:
            log.warning(
                "GitLab: could not fetch MR diff for pre-filtering (%s); "
                "submitting all findings", exc,
            )
            return findings
        if not new_side_lines(diff_text):
            log.info(
                "GitLab: MR diff yielded no hunk lines; "
                "submitting all findings unfiltered",
            )
            return findings
        return filter_findings_to_diff(findings, diff_text)

    def _apply_event_verdict(self, client: httpx.Client, event: str) -> None:
        """Mirror the verdict onto the MR approvals endpoint (best-effort).

        ``APPROVE`` approves the MR; ``REQUEST_CHANGES`` revokes a prior
        approval. ``COMMENT`` leaves approvals untouched. Failures (e.g.
        the token's user cannot approve, or nothing to unapprove) are
        logged and swallowed — the discussions and summary already landed.
        """
        action = {"APPROVE": "approve", "REQUEST_CHANGES": "unapprove"}.get(event)
        if action is None:
            return
        response = client.post(
            f"/projects/{self._project_quoted}"
            f"/merge_requests/{self.mr_iid}/{action}",
        )
        if response.status_code >= 400:
            log.warning(
                "GitLab: MR %s returned %d; verdict stays in the "
                "discussion bodies only",
                action, response.status_code,
            )

    def _build_position_base(self, diff_refs: dict[str, Any]) -> dict[str, Any]:
        """Validate diff_refs and assemble the shared discussion position."""
        position_base = {
            "base_sha":  diff_refs.get("base_sha"),
            "start_sha": diff_refs.get("start_sha"),
            "head_sha":  diff_refs.get("head_sha"),
            "position_type": "text",
        }
        if not all([
            position_base["base_sha"], position_base["start_sha"],
            position_base["head_sha"],
        ]):
            raise RuntimeError(
                f"GitLab MR {self.mr_iid}: diff_refs missing required SHAs"
            )
        return position_base

    def _post_finding_discussion(
        self,
        client: httpx.Client,
        position_base: dict[str, Any],
        event_prefix: str,
        finding: InlineFinding,
    ) -> int | None:
        """POST one finding as a discussion; return its id or None on failure."""
        payload = {
            "body": (
                f"{event_prefix}{_format_body(finding)}"
                f"\n\n{_INLINE_REVIEW_MARKER}"
            ),
            "position": {
                **position_base,
                "new_path": finding.path,
                "new_line": finding.line,
            },
        }
        response = client.post(
            f"/projects/{self._project_quoted}"
            f"/merge_requests/{self.mr_iid}/discussions",
            json=payload,
        )
        if response.status_code >= 400:
            log.warning(
                "GitLab discussion POST failed (%d) for %s:%d: %s",
                response.status_code, finding.path, finding.line, response.text,
            )
            return None
        return int(response.json().get("id", 0)) or None

    # ----- dialogue ------------------------------------------------------

    def fetch_author_replies(self) -> list[AuthorReply]:
        """Notes posted after the most recent prthinker marker note,
        excluding the bot's own author.

        GitLab does not expose the issue-comment "in_reply_to" linkage
        the way GitHub does; the convention used here is positional —
        anything after the marker note is treated as a candidate reply
        until the next marker note overwrites it.
        """
        with self._client() as client:
            notes = self._collect_all_notes(client)

        marker_idx = self._find_last_marker_idx(notes, self.comment_marker)
        if marker_idx is None:
            return []
        return self._build_replies(notes, marker_idx)

    def _collect_all_notes(self, client: httpx.Client) -> list[dict]:
        """Page through every MR note in ascending creation order."""
        return self._paginate(
            client,
            f"/projects/{self._project_quoted}"
            f"/merge_requests/{self.mr_iid}/notes",
            params={"sort": "asc"},
        )

    @staticmethod
    def _find_last_marker_idx(notes: list[dict], marker: str) -> int | None:
        """Index of the last note containing the prthinker marker, else None."""
        marker_idx: int | None = None
        for i, note in enumerate(notes):
            if marker in (note.get("body") or ""):
                marker_idx = i  # last wins
        return marker_idx

    @staticmethod
    def _note_username(note: dict) -> str:
        """Author username for a note, or empty string when absent."""
        return (note.get("author") or {}).get("username") or ""

    @staticmethod
    def _build_replies(notes: list[dict], marker_idx: int) -> list[AuthorReply]:
        """Author replies trailing the marker note, dropping bot/system notes."""
        marker_user = GitLabAdapter._note_username(notes[marker_idx])
        marker_id = int(notes[marker_idx]["id"])
        replies: list[AuthorReply] = []
        for note in notes[marker_idx + 1:]:
            author = GitLabAdapter._note_username(note)
            if author == marker_user or note.get("system"):
                continue
            replies.append(AuthorReply(
                author=author,
                body=str(note.get("body") or "").strip(),
                in_reply_to_id=marker_id,
                created_at=str(note.get("created_at") or ""),
            ))
        return replies

    # ----- CI failure signals ---------------------------------------------

    def fetch_ci_failure_signals(
        self,
        head_sha: str,
        *,
        max_jobs: int = 5,
        log_tail_chars: int = 4000,
    ) -> list[FailureSignal]:
        return fetch_gitlab_ci_failure_signals(
            self.project, head_sha, self.token,
            base_url=self.base_url,
            max_jobs=max_jobs, log_tail_chars=log_tail_chars,
        )

    # ----- gate (commit status) -----------------------------------------

    def open_gate(self, head_sha: str, *, name: str = "prthinker") -> dict[str, str]:
        with self._client() as client:
            client.post(
                f"/projects/{self._project_quoted}/statuses/{head_sha}",
                params={"state": "pending", "name": name},
            ).raise_for_status()
        return {"sha": head_sha, "name": name}

    def close_gate(self, handle: dict[str, str], result: CheckResult) -> None:
        # GitLab states: pending / running / success / failed / canceled.
        gitlab_state = "success" if result.conclusion == "success" else "failed"
        description = result.title[:255]
        if result.annotations:
            # Commit statuses have no per-line annotation channel (that is
            # a Check Run feature); the findings still reach the MR via
            # inline discussions, and `--codequality-out` feeds the MR's
            # Code Quality widget for a per-line list.
            log.info(
                "GitLab: commit statuses cannot carry per-line "
                "annotations; %d annotation(s) not attached to the gate",
                len(result.annotations),
            )
        with self._client() as client:
            client.post(
                f"/projects/{self._project_quoted}/statuses/{handle['sha']}",
                params={
                    "state": gitlab_state,
                    "name": handle["name"],
                    "description": description,
                },
            ).raise_for_status()


def _diff_entry_to_text(entry: dict[str, Any]) -> str:
    """Reconstruct one file's unified-diff text from a ``diffs`` entry.

    Emits the ``diff --git`` + ``---`` / ``+++`` headers the pipeline's
    parser and the inline diff-hunk filter need, followed by GitLab's
    per-file hunks. Entries without textual hunks (binary, or collapsed
    because the per-file diff itself is too large) are recorded as binary
    so the file is still listed rather than silently lost.
    """
    new_path = str(entry.get("new_path") or entry.get("old_path") or "")
    old_path = str(entry.get("old_path") or new_path)
    header = f"diff --git a/{old_path} b/{new_path}\n"
    hunks = entry.get("diff") or ""
    if not hunks:
        return f"{header}Binary files a/{old_path} and b/{new_path} differ\n"
    a_side = "/dev/null" if entry.get("new_file") else f"a/{old_path}"
    b_side = "/dev/null" if entry.get("deleted_file") else f"b/{new_path}"
    body = hunks if hunks.endswith("\n") else hunks + "\n"
    return f"{header}--- {a_side}\n+++ {b_side}\n{body}"


def _format_body(finding: InlineFinding) -> str:
    badge = _SEVERITY_BADGE.get(finding.severity, finding.severity)
    body = f"{badge} — {finding.comment.strip()}"
    if finding.suggestion is not None:
        # GitLab also supports the ```suggestion block syntax in MR notes,
        # but its line-range semantics differ slightly from GitHub's; the
        # safer cross-platform default is plain code fence.
        body += "\n\n```\n" + finding.suggestion.rstrip("\n") + "\n```"
    return body


__all__ = ["GitLabAdapter"]
