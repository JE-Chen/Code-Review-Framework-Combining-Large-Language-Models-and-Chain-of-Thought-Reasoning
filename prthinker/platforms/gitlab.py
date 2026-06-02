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
from prthinker.dialogue import AuthorReply
from prthinker.platforms.base import PlatformAdapter
from prthinker.schemas import InlineFinding

log = logging.getLogger(__name__)

_USER_AGENT = "prthinker/0.1"

# Map our event vocabulary to GitLab's discussion semantics. GitLab does
# not have an APPROVE / REQUEST_CHANGES verb on discussions themselves;
# instead the MR has a separate ``approvals`` endpoint and a ``Mark as
# Draft`` toggle. For now we record the verdict in the discussion body
# and let the user act on it manually; future work could call
# ``POST /merge_requests/:iid/approve`` when event == ``APPROVE``.
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
        """Pull the MR diff via the ``raw_diffs`` endpoint."""
        with self._client() as client:
            response = client.get(
                f"/projects/{self._project_quoted}"
                f"/merge_requests/{self.mr_iid}/raw_diffs",
            )
            response.raise_for_status()
            return response.text

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

    # ----- summary comment ----------------------------------------------

    def upsert_summary_comment(self, body: str) -> int:
        with self._client() as client:
            existing = self._find_marker_note(client)
            if existing is not None:
                log.info("GitLab: updating existing note %d", existing)
                response = client.put(
                    f"/projects/{self._project_quoted}"
                    f"/merge_requests/{self.mr_iid}/notes/{existing}",
                    json={"body": body},
                )
                response.raise_for_status()
                return existing
            log.info("GitLab: creating new note")
            response = client.post(
                f"/projects/{self._project_quoted}"
                f"/merge_requests/{self.mr_iid}/notes",
                json={"body": body},
            )
            response.raise_for_status()
            return int(response.json()["id"])

    def _find_marker_note(self, client: httpx.Client) -> int | None:
        page = 1
        while True:
            response = client.get(
                f"/projects/{self._project_quoted}"
                f"/merge_requests/{self.mr_iid}/notes",
                params={"per_page": 100, "page": page},
            )
            response.raise_for_status()
            batch = response.json()
            if not batch:
                return None
            for note in batch:
                if self.comment_marker in (note.get("body") or ""):
                    return int(note["id"])
            if len(batch) < 100:
                return None
            page += 1

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
            event_prefix = _EVENT_BODY_PREFIX.get(event, "")
            first_id: int | None = None
            for finding in findings:
                new_id = self._post_finding_discussion(
                    client, position_base, event_prefix, finding,
                )
                if first_id is None:
                    first_id = new_id

            if summary_body:
                # Drop a top-level note tying the discussions together.
                client.post(
                    f"/projects/{self._project_quoted}"
                    f"/merge_requests/{self.mr_iid}/notes",
                    json={"body": summary_body},
                )

            return first_id

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
            "body": event_prefix + _format_body(finding),
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
        notes: list[dict] = []
        page = 1
        while True:
            response = client.get(
                f"/projects/{self._project_quoted}"
                f"/merge_requests/{self.mr_iid}/notes",
                params={"per_page": 100, "page": page, "sort": "asc"},
            )
            response.raise_for_status()
            batch = response.json()
            if not batch:
                break
            notes.extend(batch)
            if len(batch) < 100:
                break
            page += 1
        return notes

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
        with self._client() as client:
            client.post(
                f"/projects/{self._project_quoted}/statuses/{handle['sha']}",
                params={
                    "state": gitlab_state,
                    "name": handle["name"],
                    "description": description,
                },
            ).raise_for_status()


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
