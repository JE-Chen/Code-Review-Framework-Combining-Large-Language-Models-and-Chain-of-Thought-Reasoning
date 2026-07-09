"""Tests for auto-filing findings as issues (:mod:`prthinker.issue_autofile`)."""

from __future__ import annotations

import httpx

from prthinker.issue_autofile import (
    draft_from_finding,
    file_findings_as_issues,
    finding_fingerprint,
    known_fingerprints,
)
from prthinker.issue_tracker import Issue
from prthinker.schemas import InlineFinding


class _FakeTracker:
    """IssueTracker stand-in: canned open issues, recorded creates."""

    def __init__(self, existing_bodies=(), fail_titles=()) -> None:
        self._existing = [
            Issue(n, "t", body) for n, body in enumerate(existing_bodies, 1)]
        self._fail_titles = fail_titles
        self.created: list[tuple[str, str, tuple[str, ...]]] = []

    def list_open_issues(self, *, label="", limit=50):
        del label, limit
        return list(self._existing)

    def create_issue(self, *, title, body, labels=()):
        if any(fragment in title for fragment in self._fail_titles):
            raise httpx.HTTPError("boom")
        self.created.append((title, body, labels))
        return Issue(100 + len(self.created), title, body)


def _finding(**overrides) -> InlineFinding:
    base = {
        "path": "pkg/mod.py", "line": 12, "severity": "warning",
        "comment": "Mutable default argument shared across calls",
    }
    base.update(overrides)
    return InlineFinding(**base)


class TestFingerprint:
    def test_stable_across_runs(self):
        assert finding_fingerprint(_finding()) == finding_fingerprint(_finding())

    def test_normalises_whitespace_and_case(self):
        noisy = _finding(comment="  Mutable   DEFAULT argument\nshared across calls ")
        assert finding_fingerprint(noisy) == finding_fingerprint(_finding())

    def test_ignores_line_number_drift(self):
        assert finding_fingerprint(_finding(line=99)) == finding_fingerprint(_finding())

    def test_differs_by_path(self):
        assert finding_fingerprint(_finding(path="other.py")) != finding_fingerprint(_finding())


class TestDraft:
    def test_body_carries_marker_and_location(self):
        draft = draft_from_finding(_finding())
        assert f"<!-- prthinker:auto-issue:{draft.fingerprint} -->" in draft.body
        assert "`pkg/mod.py` (line 12)" in draft.body
        assert "Mutable default argument" in draft.body

    def test_title_is_single_line_and_capped(self):
        draft = draft_from_finding(_finding(comment="word " * 100))
        assert "\n" not in draft.title
        assert draft.title.startswith("[prthinker] warning: pkg/mod.py:12")

    def test_suggestion_rendered_as_code_block(self):
        draft = draft_from_finding(_finding(suggestion="def f(x=None):"))
        assert "```\ndef f(x=None):\n```" in draft.body

    def test_no_suggestion_no_code_block(self):
        assert "```" not in draft_from_finding(_finding()).body


class TestKnownFingerprints:
    def test_round_trips_through_issue_bodies(self):
        draft = draft_from_finding(_finding())
        issues = [Issue(1, "t", draft.body), Issue(2, "t", "no marker here")]
        assert known_fingerprints(issues) == {draft.fingerprint}

    def test_empty_issues_empty_set(self):
        assert known_fingerprints([]) == set()


class TestFileFindingsAsIssues:
    def test_files_new_findings_with_labels(self):
        tracker = _FakeTracker()
        issues = file_findings_as_issues(
            tracker, [_finding()], labels=("prthinker", "bug"))
        assert [issue.number for issue in issues] == [101]
        assert tracker.created[0][2] == ("prthinker", "bug")

    def test_skips_findings_already_filed(self):
        already = draft_from_finding(_finding())
        tracker = _FakeTracker(existing_bodies=(already.body,))
        fresh = _finding(path="other.py")
        issues = file_findings_as_issues(tracker, [_finding(), fresh])
        assert len(issues) == 1
        assert issues[0].title == draft_from_finding(fresh).title

    def test_dedups_within_one_batch(self):
        tracker = _FakeTracker()
        assert len(file_findings_as_issues(tracker, [_finding(), _finding()])) == 1

    def test_max_new_issues_caps_a_run(self):
        tracker = _FakeTracker()
        findings = [_finding(path=f"f{n}.py") for n in range(5)]
        assert len(file_findings_as_issues(tracker, findings, max_new_issues=2)) == 2

    def test_create_failure_logs_and_continues(self):
        tracker = _FakeTracker(fail_titles=("a.py",))
        findings = [_finding(path="a.py"), _finding(path="b.py")]
        issues = file_findings_as_issues(tracker, findings)
        assert len(issues) == 1
        assert "b.py" in issues[0].title

    def test_empty_findings_create_nothing(self):
        tracker = _FakeTracker()
        assert file_findings_as_issues(tracker, []) == []
        assert tracker.created == []
