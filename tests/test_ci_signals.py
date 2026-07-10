"""Unit tests for the CI failure-signal fetcher and renderer."""

from __future__ import annotations

import io
import json
import zipfile

import httpx
import pytest

from prthinker import ci_signals
from prthinker.ci_signals import (
    FailureSignal,
    fetch_ci_failure_signals,
    format_signals_block,
)


def _zip_log(parts: dict[str, str]) -> bytes:
    """Build an in-memory zip of step .txt logs like the Actions API returns."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, body in parts.items():
            zf.writestr(name, body)
    return buf.getvalue()


def _install_router(
    monkeypatch: pytest.MonkeyPatch, handler
) -> None:
    """Patch ``_client`` to return an httpx.Client backed by a MockTransport."""
    transport = httpx.MockTransport(handler)

    def fake_client(
        token: str,  # noqa: ARG001 - signature parity
        base_url: str = "https://api.github.com",
    ) -> httpx.Client:
        return httpx.Client(base_url=base_url, transport=transport)

    monkeypatch.setattr(ci_signals, "_client", fake_client)


def _runs_payload(*conclusions: str) -> dict:
    runs = []
    for idx, conclusion in enumerate(conclusions, start=1):
        runs.append(
            {
                "id": 1000 + idx,
                "name": f"workflow-{idx}",
                "path": f".github/workflows/{idx}.yml",
                "conclusion": conclusion,
            }
        )
    return {"workflow_runs": runs}


def _jobs_payload(*conclusions: str, start_id: int = 1) -> dict:
    jobs = []
    for idx, conclusion in enumerate(conclusions, start=start_id):
        jobs.append(
            {"id": 2000 + idx, "name": f"job-{idx}", "conclusion": conclusion}
        )
    return {"jobs": jobs}


def test_happy_path_collects_failed_jobs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/actions/runs"):
            return httpx.Response(200, json=_runs_payload("failure", "success"))
        if request.url.path.endswith("/jobs"):
            page = request.url.params.get("page")
            if page == "1":
                return httpx.Response(
                    200, json=_jobs_payload("failure", "success")
                )
            return httpx.Response(200, json={"jobs": []})
        if request.url.path.endswith("/logs"):
            return httpx.Response(200, content=_zip_log({"1_step.txt": "boom"}))
        raise AssertionError(f"unexpected path {request.url.path}")

    _install_router(monkeypatch, handler)
    signals = fetch_ci_failure_signals("o/r", "deadbeefcafe", "tok")

    assert len(signals) == 1
    sig = signals[0]
    assert sig.workflow_name == "workflow-1"
    assert sig.job_name == "job-1"
    assert sig.conclusion == "failure"
    assert sig.log_tail == "boom"


def test_no_failed_runs_returns_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/actions/runs"):
            return httpx.Response(200, json=_runs_payload("success"))
        raise AssertionError(f"unexpected path {request.url.path}")

    _install_router(monkeypatch, handler)
    assert fetch_ci_failure_signals("o/r", "sha", "tok") == []


def test_max_jobs_caps_collection(monkeypatch: pytest.MonkeyPatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/actions/runs"):
            return httpx.Response(
                200, json=_runs_payload("failure", "failure", "failure")
            )
        if request.url.path.endswith("/jobs"):
            page = request.url.params.get("page")
            if page == "1":
                return httpx.Response(
                    200, json=_jobs_payload("failure", "failure")
                )
            return httpx.Response(200, json={"jobs": []})
        if request.url.path.endswith("/logs"):
            return httpx.Response(200, content=b"plain text log")
        raise AssertionError(f"unexpected path {request.url.path}")

    _install_router(monkeypatch, handler)
    signals = fetch_ci_failure_signals("o/r", "sha", "tok", max_jobs=2)
    assert len(signals) == 2


def test_missing_run_name_falls_back_to_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/actions/runs"):
            return httpx.Response(
                200,
                json={
                    "workflow_runs": [
                        {
                            "id": 7,
                            "path": ".github/workflows/x.yml",
                            "conclusion": "failure",
                        }
                    ]
                },
            )
        if request.url.path.endswith("/jobs"):
            page = request.url.params.get("page")
            if page == "1":
                return httpx.Response(
                    200, json={"jobs": [{"id": 9, "conclusion": "failure"}]}
                )
            return httpx.Response(200, json={"jobs": []})
        if request.url.path.endswith("/logs"):
            return httpx.Response(404)
        raise AssertionError(f"unexpected path {request.url.path}")

    _install_router(monkeypatch, handler)
    signals = fetch_ci_failure_signals("o/r", "sha", "tok")
    assert len(signals) == 1
    sig = signals[0]
    assert sig.workflow_name == ".github/workflows/x.yml"
    assert sig.job_name == ""
    assert sig.conclusion == "failure"
    assert sig.log_tail == ""


def test_missing_run_name_and_path_empty_string(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/actions/runs"):
            return httpx.Response(
                200,
                json={"workflow_runs": [{"id": 7, "conclusion": "failure"}]},
            )
        if request.url.path.endswith("/jobs"):
            page = request.url.params.get("page")
            if page == "1":
                return httpx.Response(
                    200,
                    json={
                        "jobs": [{"id": 9, "name": "j", "conclusion": None}]
                    },
                )
            return httpx.Response(200, json={"jobs": []})
        raise AssertionError(f"unexpected path {request.url.path}")

    # conclusion None means job is not 'failure' -> filtered out -> no logs call.
    _install_router(monkeypatch, handler)
    signals = fetch_ci_failure_signals("o/r", "sha", "tok")
    assert signals == []


def test_log_tail_truncated_to_tail_chars(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    body = "x" * 100

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/actions/runs"):
            return httpx.Response(200, json=_runs_payload("failure"))
        if request.url.path.endswith("/jobs"):
            page = request.url.params.get("page")
            if page == "1":
                return httpx.Response(200, json=_jobs_payload("failure"))
            return httpx.Response(200, json={"jobs": []})
        if request.url.path.endswith("/logs"):
            return httpx.Response(200, content=body.encode())
        raise AssertionError(f"unexpected path {request.url.path}")

    _install_router(monkeypatch, handler)
    signals = fetch_ci_failure_signals("o/r", "sha", "tok", log_tail_chars=10)
    assert signals[0].log_tail == "x" * 10


def test_jobs_pagination_walks_pages(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    full_page = ["failure"] * 100

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/actions/runs"):
            return httpx.Response(200, json=_runs_payload("failure"))
        if request.url.path.endswith("/jobs"):
            page = request.url.params.get("page")
            if page == "1":
                return httpx.Response(
                    200, json=_jobs_payload(*full_page, start_id=1)
                )
            if page == "2":
                return httpx.Response(
                    200, json=_jobs_payload("failure", start_id=200)
                )
            return httpx.Response(200, json={"jobs": []})
        if request.url.path.endswith("/logs"):
            return httpx.Response(200, content=b"log")
        raise AssertionError(f"unexpected path {request.url.path}")

    _install_router(monkeypatch, handler)
    # max_jobs default 5 caps the collection, but pagination must still be
    # reachable code: request a higher cap to walk page 2.
    signals = fetch_ci_failure_signals("o/r", "sha", "tok", max_jobs=200)
    assert len(signals) == 101


def test_extract_log_text_falls_back_to_plain_on_bad_zip() -> None:
    assert ci_signals._extract_log_text(b"not a zip") == "not a zip"


def test_extract_log_text_concatenates_zip_steps() -> None:
    blob = _zip_log({"2_b.txt": "second", "1_a.txt": "first"})
    assert ci_signals._extract_log_text(blob) == "first\nsecond"


def test_format_signals_block_empty_is_empty_string() -> None:
    assert format_signals_block([]) == ""


def test_format_signals_block_renders_header_and_logs() -> None:
    block = format_signals_block(
        [FailureSignal("wf", "jb", "failure", "trace line")]
    )
    assert "# CI Failure Signals" in block
    assert "## wf / jb (failure)" in block
    assert "trace line" in block
    assert block.startswith("<!-- CI Failure Signals -->")


def test_format_signals_block_empty_log_placeholder() -> None:
    block = format_signals_block([FailureSignal("wf", "jb", "failure", "   ")])
    assert "(no log captured)" in block


def test_failure_signal_is_dataclass_roundtrip() -> None:
    sig = FailureSignal("wf", "jb", "failure", "log")
    from dataclasses import asdict

    data = asdict(sig)
    assert FailureSignal(**data) == sig
    assert json.loads(json.dumps(data)) == data
