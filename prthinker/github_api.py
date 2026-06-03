"""GitHub REST helpers — fetch PR diffs, upsert summary comment, submit
inline-comment reviews.

- Summary comment: a single PR conversation comment, upserted by marker.
- Inline review:  posts a `POST /pulls/:n/reviews` with `comments[]` keyed
                  by `path` + `line` (GitHub's new-side line number).

We use only the GitHub REST API via httpx to avoid pulling in PyGithub.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterable

import httpx

from prthinker.config import GitHubConfig
from prthinker.schemas import InlineFinding

log = logging.getLogger(__name__)

_API_ROOT = "https://api.github.com"
_USER_AGENT = "prthinker/0.1"


@dataclass
class _Comment:
    id: int
    body: str


def _client(token: str) -> httpx.Client:
    return httpx.Client(
        base_url=_API_ROOT,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": _USER_AGENT,
        },
        timeout=30.0,
    )


# GitHub rejects the ``.diff`` / ``.patch`` media type with 406 once a PR's
# diff grows past its rendering cap. The files API still serves each file's
# hunks, so we reconstruct the diff from there instead of crashing.
_DIFF_TOO_LARGE = 406


def _file_patch_to_diff(file_entry: dict) -> str:
    """Reconstruct one file's unified-diff text from a files-API entry.

    Emits the ``diff --git`` + ``---`` / ``+++`` headers the pipeline's
    parser and the inline diff-hunk filter need, followed by GitHub's
    ``patch`` hunks. Files with no textual patch (binary, or a per-file
    patch too large for GitHub to return) are recorded as binary so the
    file is still listed rather than silently lost.
    """
    new_path = file_entry["filename"]
    old_path = file_entry.get("previous_filename", new_path)
    header = f"diff --git a/{old_path} b/{new_path}\n"
    patch = file_entry.get("patch")
    if not patch:
        return f"{header}Binary files a/{old_path} and b/{new_path} differ\n"
    status = file_entry.get("status")
    a_side = "/dev/null" if status == "added" else f"a/{old_path}"
    b_side = "/dev/null" if status == "removed" else f"b/{new_path}"
    body = patch if patch.endswith("\n") else patch + "\n"
    return f"{header}--- {a_side}\n+++ {b_side}\n{body}"


def _reconstruct_diff_from_files(
    client: httpx.Client, config: GitHubConfig
) -> str:
    """Rebuild a unified diff from the paginated PR files API."""
    parts: list[str] = []
    page = 1
    while True:
        resp = client.get(
            f"/repos/{config.repo}/pulls/{config.pr_number}/files",
            params={"per_page": 100, "page": page},
        )
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        parts.extend(_file_patch_to_diff(f) for f in batch)
        if len(batch) < 100:
            break
        page += 1
    return "".join(parts)


def fetch_pr_diff(config: GitHubConfig) -> str:
    """Return the unified diff for the PR. Empty PRs return ''.

    A large PR makes GitHub reject the diff media type with 406; we then
    rebuild the diff from the paginated files API rather than failing the
    whole review.
    """
    with _client(config.token) as client:
        response = client.get(
            f"/repos/{config.repo}/pulls/{config.pr_number}",
            headers={"Accept": "application/vnd.github.v3.diff"},
        )
        if response.status_code == _DIFF_TOO_LARGE:
            log.warning(
                "Diff media type rejected (406, too large) for %s#%d; "
                "reconstructing from the files API",
                config.repo, config.pr_number,
            )
            return _reconstruct_diff_from_files(client, config)
        response.raise_for_status()
        return response.text


def fetch_pr_head_sha(config: GitHubConfig) -> str:
    """Return the HEAD commit SHA of the PR — required by the Checks API."""
    with _client(config.token) as client:
        response = client.get(
            f"/repos/{config.repo}/pulls/{config.pr_number}",
        )
        response.raise_for_status()
        return str(response.json()["head"]["sha"])


def fetch_pr_base_branch(config: GitHubConfig) -> str:
    """Return the PR's base branch name — used as the target for auto-fix PRs."""
    with _client(config.token) as client:
        response = client.get(
            f"/repos/{config.repo}/pulls/{config.pr_number}",
        )
        response.raise_for_status()
        return str(response.json()["base"]["ref"])


def fetch_pr_commit_messages(config: GitHubConfig) -> list[str]:
    """Return every commit message on the PR, oldest first (paginated)."""
    messages: list[str] = []
    page = 1
    with _client(config.token) as client:
        while True:
            response = client.get(
                f"/repos/{config.repo}/pulls/{config.pr_number}/commits",
                params={"per_page": 100, "page": page},
            )
            response.raise_for_status()
            batch = response.json()
            if not batch:
                break
            messages.extend(
                (c.get("commit") or {}).get("message", "") for c in batch
            )
            if len(batch) < 100:
                break
            page += 1
    return messages


def _iter_existing_comments(
    client: httpx.Client, config: GitHubConfig
) -> list[_Comment]:
    comments: list[_Comment] = []
    page = 1
    while True:
        response = client.get(
            f"/repos/{config.repo}/issues/{config.pr_number}/comments",
            params={"per_page": 100, "page": page},
        )
        response.raise_for_status()
        batch = response.json()
        if not batch:
            break
        comments.extend(_Comment(id=int(c["id"]), body=c.get("body") or "") for c in batch)
        if len(batch) < 100:
            break
        page += 1
    return comments


# GitHub rejects an issue / PR comment body longer than 65 536 chars
# with a 422. The aggregate summary on a multi-file matrix run easily
# clears that when every shard's per-file block lands in one comment.
# Cap at 60 000 to leave headroom for the marker + the truncation
# notice; the per-file detail still lives in the matrix shards'
# job logs.
_GITHUB_COMMENT_BODY_MAX = 60000


def _cap_comment_body(body: str, marker: str) -> str:
    if len(body) <= _GITHUB_COMMENT_BODY_MAX:
        return body
    notice = (
        f"\n\n---\n\n_⚠️ Comment truncated from {len(body)} to "
        f"{_GITHUB_COMMENT_BODY_MAX} chars to fit GitHub's 65 536 char "
        "limit. Full per-step output is in the matrix shard job logs._\n"
    )
    keep = _GITHUB_COMMENT_BODY_MAX - len(notice) - len(marker) - 4
    if keep < 0:
        # Should never happen: marker + notice alone fits comfortably.
        return marker + notice
    head = body[:keep]
    # Always keep the marker so the next run's upsert can find this
    # comment.
    if marker not in head:
        head = marker + "\n" + head[len(marker) + 1:]
    return head + notice


def _patch_issue_comment(
    client: httpx.Client, config: GitHubConfig, comment_id: int, body: str
) -> int:
    response = client.patch(
        f"/repos/{config.repo}/issues/comments/{comment_id}",
        json={"body": body},
    )
    response.raise_for_status()
    return comment_id


def _create_issue_comment(
    client: httpx.Client, config: GitHubConfig, body: str
) -> int:
    response = client.post(
        f"/repos/{config.repo}/issues/{config.pr_number}/comments",
        json={"body": body},
    )
    response.raise_for_status()
    return int(response.json()["id"])


def _delete_issue_comment(
    client: httpx.Client, config: GitHubConfig, comment_id: int
) -> None:
    response = client.delete(
        f"/repos/{config.repo}/issues/comments/{comment_id}",
    )
    if response.status_code >= 400:
        log.warning(
            "Failed to delete stale summary comment %d (%d)",
            comment_id, response.status_code,
        )


def _reconcile_summary_comments(
    client: httpx.Client,
    config: GitHubConfig,
    existing: list[_Comment],
    bodies: list[str],
) -> list[int]:
    """Patch the first N existing comments, create extras, delete leftovers."""
    ids: list[int] = []
    for i, body in enumerate(bodies):
        if i < len(existing):
            ids.append(_patch_issue_comment(client, config, existing[i].id, body))
        else:
            ids.append(_create_issue_comment(client, config, body))
    for stale in existing[len(bodies):]:
        log.info("Deleting orphan summary comment %d", stale.id)
        _delete_issue_comment(client, config, stale.id)
    return ids


def upsert_pr_comments(config: GitHubConfig, bodies: list[str]) -> list[int]:
    """Create / update / reconcile the marker-tagged summary comment(s).

    A long review is paginated across multiple comments (GitHub caps a
    single comment body at 65 536 chars). Existing prthinker summary
    comments — matched by marker and ordered by id — are updated in
    place; extra pages are created; any leftover comments from a
    previous, longer run are deleted so stale parts never linger.
    Returns the comment ids in page order.
    """
    marker = config.comment_marker
    capped = [_cap_comment_body(b, marker) for b in bodies]
    for body in capped:
        if marker not in body:
            raise ValueError("each body must contain the configured comment marker")
    if not capped:
        return []
    with _client(config.token) as client:
        existing = sorted(
            (c for c in _iter_existing_comments(client, config) if marker in c.body),
            key=lambda c: c.id,
        )
        return _reconcile_summary_comments(client, config, existing, capped)


def upsert_pr_comment(config: GitHubConfig, body: str) -> int:
    """Create or update the marker-tagged PR comment. Returns its id."""
    return upsert_pr_comments(config, [body])[0]


# Hidden marker embedded in every prthinker inline review's summary
# body so the NEXT run can identify and clean up its own predecessors.
# Distinct from the summary-comment marker so the two never collide.
_INLINE_REVIEW_MARKER = "<!-- prthinker:inline -->"


def _collect_our_review_ids(client: httpx.Client, config: GitHubConfig) -> set[int]:
    """Page through PR reviews and collect those carrying our marker."""
    our_review_ids: set[int] = set()
    page = 1
    while True:
        resp = client.get(
            f"/repos/{config.repo}/pulls/{config.pr_number}/reviews",
            params={"per_page": 100, "page": page},
        )
        resp.raise_for_status()
        reviews = resp.json()
        if not reviews:
            return our_review_ids
        for r in reviews:
            if _INLINE_REVIEW_MARKER in (r.get("body") or ""):
                our_review_ids.add(int(r["id"]))
        if len(reviews) < 100:
            return our_review_ids
        page += 1


def _delete_inline_comments_for_reviews(
    client: httpx.Client,
    config: GitHubConfig,
    review_ids: set[int],
) -> int:
    """Page through PR review comments and delete those owned by review_ids."""
    deleted = 0
    page = 1
    while True:
        resp = client.get(
            f"/repos/{config.repo}/pulls/{config.pr_number}/comments",
            params={"per_page": 100, "page": page},
        )
        resp.raise_for_status()
        comments = resp.json()
        if not comments:
            return deleted
        for c in comments:
            if c.get("pull_request_review_id") in review_ids:
                deleted += _delete_one_inline_comment(client, config, int(c["id"]))
        if len(comments) < 100:
            return deleted
        page += 1


def _delete_one_inline_comment(
    client: httpx.Client, config: GitHubConfig, comment_id: int
) -> int:
    del_resp = client.delete(
        f"/repos/{config.repo}/pulls/comments/{comment_id}",
    )
    if del_resp.status_code < 400:
        return 1
    log.warning(
        "Failed to delete inline comment %d (%d)",
        comment_id, del_resp.status_code,
    )
    return 0


def _dismiss_stale_inline_reviews(
    config: GitHubConfig, exclude: set[int] | None = None
) -> None:
    """Delete the inline comments left by previous prthinker reviews.

    GitHub's review-dismissal endpoint refuses ``COMMENT``-state reviews
    (which is what prthinker posts by default), so we can't strike the
    review wrappers themselves. Deleting each review's child comments
    is the next best thing — the wrapper stays on the PR timeline as a
    stub but the noisy inline annotations disappear from the diff.

    Identification is by ``_INLINE_REVIEW_MARKER`` in the review body,
    not by author. Filtering by the bot user would catch reviews from
    every other workflow that uses ``GITHUB_TOKEN`` too.

    ``exclude`` holds review ids that must be kept — in particular the
    review just posted this run, which also carries the marker and would
    otherwise delete its own freshly-posted comments.
    """
    exclude = exclude or set()
    with _client(config.token) as client:
        our_review_ids = _collect_our_review_ids(client, config) - exclude
        if not our_review_ids:
            log.info("No prior prthinker inline reviews to clean up")
            return
        deleted = _delete_inline_comments_for_reviews(
            client, config, our_review_ids
        )
        log.info(
            "Cleaned up %d inline comment(s) from %d prior review(s)",
            deleted, len(our_review_ids),
        )


def _parse_new_side_file_header(raw: str) -> tuple[bool, str | None]:
    """Parse a unified diff ``+++ ...`` header.

    Returns ``(is_file_header, current_path)``. ``current_path`` is
    ``None`` when the file header points at ``/dev/null`` (deletion).
    """
    if not raw.startswith("+++ "):
        return False, None
    path = raw[4:].split("\t", 1)[0].strip()
    if path == "/dev/null":
        return True, None
    return True, (path[2:] if path.startswith("b/") else path)


def _parse_new_side_hunk_header(raw: str) -> tuple[bool, int]:
    """Parse a unified diff ``@@ -... +new_start[,new_count] @@`` header.

    Returns ``(is_hunk_header, new_start)``. ``new_start`` is ``0`` when
    the line begins with ``@@`` but cannot be parsed (degenerate hunk);
    the caller treats that as "stop tracking until the next valid
    header".
    """
    if not raw.startswith("@@"):
        return False, 0
    try:
        hunk_meta = raw.split("@@", 2)[1].strip()
        new_part = next(
            p for p in hunk_meta.split() if p.startswith("+")
        )
        return True, int(new_part[1:].split(",", 1)[0])
    except (StopIteration, ValueError, IndexError):
        return True, 0


def _new_side_lines(diff_text: str) -> dict[str, set[int]]:
    """Map every file in a unified diff to the new-side line numbers
    that appear inside a hunk.

    GitHub's PR review API rejects the entire review with 422
    ``Line could not be resolved`` if any single comment targets a
    ``side: RIGHT`` line outside the diff hunks. Pre-filtering
    against this set keeps a hallucinated line from one file from
    poisoning every other finding in the review.

    Returns ``{filename: {new_line_no, ...}}``. ``filename`` is taken
    from the ``+++ b/<path>`` header (stripped of the ``b/`` prefix).
    Files that the diff records as deleted (``+++ /dev/null``) are
    excluded.
    """
    result: dict[str, set[int]] = {}
    current_path: str | None = None
    new_line = 0
    in_hunk = False

    for raw in diff_text.splitlines():
        is_file, path = _parse_new_side_file_header(raw)
        if is_file:
            current_path = path
            in_hunk = False
            continue
        is_hunk, new_start = _parse_new_side_hunk_header(raw)
        if is_hunk:
            new_line = new_start - 1
            in_hunk = new_start > 0
            continue
        if not in_hunk or current_path is None:
            continue
        # "+" and " " advance the new-side counter; "-" is an old-side
        # deletion and is intentionally ignored.
        if raw[:1] in ("+", " "):
            new_line += 1
            result.setdefault(current_path, set()).add(new_line)
    return result


def _finding_diff_miss(
    finding: InlineFinding, valid: dict[str, set[int]]
) -> str | None:
    """Return why a finding is off-diff, or ``None`` if it lands on a hunk.

    The returned string is a ready-to-log reason so the caller does not
    have to re-derive which endpoint (``line`` vs ``start_line``) failed.
    """
    file_lines = valid.get(finding.path)
    if not file_lines or finding.line not in file_lines:
        return f"{finding.path}:{finding.line} — line not on a diff hunk"
    # Multi-line comment: BOTH endpoints must be hunk lines.
    if (
        finding.is_multiline
        and finding.start_line is not None
        and finding.start_line not in file_lines
    ):
        return (
            f"{finding.path}:{finding.start_line}-{finding.line} "
            "— start_line not on a diff hunk"
        )
    return None


def _filter_findings_to_diff(
    findings: list[InlineFinding], diff_text: str
) -> list[InlineFinding]:
    """Drop findings whose ``(path, line)`` is outside any diff hunk."""
    valid = _new_side_lines(diff_text)
    kept: list[InlineFinding] = []
    dropped = 0
    for f in findings:
        miss = _finding_diff_miss(f, valid)
        if miss is not None:
            log.warning("Dropping inline finding %s", miss)
            dropped += 1
            continue
        kept.append(f)
    if dropped:
        log.info(
            "Pre-filtered %d inline finding(s) outside the diff; %d remain",
            dropped, len(kept),
        )
    return kept


def count_findings_on_diff(
    findings: Iterable[InlineFinding], diff_text: str
) -> int:
    """Count findings whose line(s) fall on a diff hunk (i.e. are postable).

    This is the silent, non-mutating companion to
    :func:`_filter_findings_to_diff`: it answers "how many of these would
    actually be posted as inline comments" without logging a warning per
    drop, so the summary comment can report an accurate count before the
    review is submitted.
    """
    valid = _new_side_lines(diff_text)
    return sum(1 for f in findings if _finding_diff_miss(f, valid) is None)


def _prefilter_inline_findings(
    config: GitHubConfig, items: list[InlineFinding]
) -> list[InlineFinding]:
    """Drop findings off the PR's diff hunks; submit all if the diff fetch fails.

    A single hallucinated line number 422s the whole review, so the diff
    pre-filter is the first line of defence. If the diff cannot be
    fetched we fall through to the unfiltered set — the caller already
    handles a 422 by logging and continuing.
    """
    try:
        diff_text = fetch_pr_diff(config)
        return _filter_findings_to_diff(items, diff_text)
    except Exception as exc:  # noqa: BLE001 — pre-filter is best-effort
        log.warning(
            "Could not pre-filter findings against diff (%s); submitting all",
            exc,
        )
        return items


def _post_inline_review(
    config: GitHubConfig,
    items: list[InlineFinding],
    summary_body: str | None,
    event: str,
) -> int:
    """POST the review payload and return the new review id (raises on 4xx/5xx)."""
    base_body = summary_body or "prthinker — inline findings"
    marked_body = f"{base_body}\n\n{_INLINE_REVIEW_MARKER}"
    comments = [_build_inline_comment(f) for f in items]
    payload: dict[str, object] = {
        "event": event,
        "comments": comments,
        "body": marked_body,
    }
    with _client(config.token) as client:
        response = client.post(
            f"/repos/{config.repo}/pulls/{config.pr_number}/reviews",
            json=payload,
        )
        if response.status_code >= 400:
            log.error(
                "Review submission failed (%d): %s",
                response.status_code, response.text,
            )
        response.raise_for_status()
        review_id = int(response.json()["id"])
    log.info("Submitted review %d with %d inline comments",
             review_id, len(comments))
    return review_id


def submit_inline_review(
    config: GitHubConfig,
    findings: Iterable[InlineFinding],
    summary_body: str | None = None,
    event: str = "COMMENT",
) -> int | None:
    """Post a PR review containing one inline comment per finding.

    Returns the new review id, or None if there were no findings (we skip
    creating an empty review).

    `event` is one of GitHub's review states: COMMENT, APPROVE, REQUEST_CHANGES.

    The new review is posted FIRST; only after it succeeds are the inline
    comments from previous prthinker reviews removed (identified by
    ``_INLINE_REVIEW_MARKER``, excluding the just-posted review). Posting
    before dismissing means a 422 leaves the prior run's suggestions
    intact instead of wiping them ahead of a failed re-post.

    Findings whose line falls outside the PR's diff hunks are dropped
    silently — GitHub returns ``422 Line could not be resolved`` and
    rejects the entire review (not just the offending comment) if any
    single entry points at an unresolvable line.
    """
    items = list(findings)
    if not items:
        log.info("No inline findings — skipping review submission")
        return None

    items = _prefilter_inline_findings(config, items)
    if not items:
        log.info("All inline findings dropped — skipping review submission")
        return None

    review_id = _post_inline_review(config, items, summary_body, event)

    try:
        _dismiss_stale_inline_reviews(config, exclude={review_id})
    except Exception as exc:  # noqa: BLE001 — cleanup failure must not block posting
        log.warning("Inline-review cleanup failed (%s); continuing", exc)

    return review_id


_SEVERITY_BADGE: dict[str, str] = {
    "error": "🔴 **error**",
    "warning": "🟡 **warning**",
    "info": "🔵 _info_",
}


def _build_inline_comment(finding: InlineFinding) -> dict[str, object]:
    """Build the JSON payload for one entry in `comments[]` of a Review.

    For multi-line suggestions, GitHub requires `start_line` + `start_side`
    in addition to `line` + `side`.
    """
    payload: dict[str, object] = {
        "path": finding.path,
        "line": finding.line,
        "side": "RIGHT",
        "body": _format_inline_body(finding),
    }
    if finding.is_multiline and finding.start_line is not None:
        payload["start_line"] = finding.start_line
        payload["start_side"] = "RIGHT"
    return payload


def _format_inline_body(finding: InlineFinding) -> str:
    badge = _SEVERITY_BADGE.get(finding.severity, finding.severity)
    body = f"{badge} — {finding.comment.strip()}"
    if finding.suggestion is not None:
        # GitHub renders ```suggestion blocks as a one-click "Apply" button.
        body += "\n\n```suggestion\n" + finding.suggestion.rstrip("\n") + "\n```"
    return body


__all__ = [
    "fetch_pr_diff",
    "fetch_pr_head_sha",
    "fetch_pr_base_branch",
    "fetch_pr_commit_messages",
    "upsert_pr_comment",
    "upsert_pr_comments",
    "submit_inline_review",
    "count_findings_on_diff",
]
