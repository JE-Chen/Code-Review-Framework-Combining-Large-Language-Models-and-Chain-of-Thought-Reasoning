"""Judge verdict parser + aggregation + GitHub event mapping."""

from __future__ import annotations

from reviewmind.judge import aggregate, parse_verdict, to_github_event
from reviewmind.schemas import JudgeVerdict


def test_parse_clean_json() -> None:
    raw = '{"verdict": "approve", "score": 9, "reasons": ["clean diff"]}'
    v = parse_verdict(raw)
    assert v.verdict == "approve"
    assert v.score == 9
    assert v.reasons == ["clean diff"]


def test_parse_json_inside_code_fence() -> None:
    raw = '```json\n{"verdict": "request_changes", "score": 3, "reasons": []}\n```'
    v = parse_verdict(raw)
    assert v.verdict == "request_changes"
    assert v.score == 3


def test_parse_falls_back_safely_on_garbage() -> None:
    v = parse_verdict("not a json verdict, just prose")
    assert v.verdict == "comment"
    # The score stays inside [0, 10] so the schema accepts it.
    assert 0 <= v.score <= 10


def test_parse_falls_back_safely_on_invalid_schema() -> None:
    # ``score`` is out of range — Pydantic should reject and we fall back.
    v = parse_verdict('{"verdict": "approve", "score": 99}')
    assert v.verdict == "comment"


def test_aggregate_request_changes_wins() -> None:
    verdicts = [
        JudgeVerdict(verdict="approve", score=9),
        JudgeVerdict(verdict="request_changes", score=2),
        JudgeVerdict(verdict="comment", score=5),
    ]
    assert aggregate(verdicts) == "request_changes"


def test_aggregate_all_approve_collapses_to_approve() -> None:
    verdicts = [
        JudgeVerdict(verdict="approve", score=9),
        JudgeVerdict(verdict="approve", score=10),
    ]
    assert aggregate(verdicts) == "approve"


def test_aggregate_mixed_approve_and_comment_is_comment() -> None:
    verdicts = [
        JudgeVerdict(verdict="approve", score=9),
        JudgeVerdict(verdict="comment", score=6),
    ]
    assert aggregate(verdicts) == "comment"


def test_aggregate_empty_list_is_comment() -> None:
    assert aggregate([]) == "comment"


def test_github_event_mapping_is_canonical() -> None:
    assert to_github_event("approve") == "APPROVE"
    assert to_github_event("request_changes") == "REQUEST_CHANGES"
    assert to_github_event("comment") == "COMMENT"
