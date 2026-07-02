"""Tests for the GitLab pipelines CI-failure-signal fetcher.

No network: ``_client`` is monkeypatched with a scripted stand-in that
routes GETs by path suffix, pinning the pipeline → failed-jobs → trace
walk, the ``max_jobs`` cap, and the tail truncation offline.
"""

from __future__ import annotations

import httpx
import pytest

from prthinker import gitlab_ci_signals
from prthinker.gitlab_ci_signals import fetch_gitlab_ci_failure_signals


class _ScriptedClient:
    """Routes GETs by path shape; records every request path."""

    def __init__(
        self,
        *,
        pipelines: list[dict] | None = None,
        jobs: dict[int, list[dict]] | None = None,
        traces: dict[int, str] | None = None,
        trace_status: int = 200,
    ) -> None:
        self._pipelines = pipelines or []
        self._jobs = jobs or {}
        self._traces = traces or {}
        self._trace_status = trace_status
        self.paths: list[str] = []

    def __enter__(self) -> _ScriptedClient:
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    def get(self, path: str, params: dict | None = None) -> httpx.Response:
        self.paths.append(path)
        request = httpx.Request("GET", "http://test" + path)
        if path.endswith("/trace"):
            job_id = int(path.rsplit("/", 2)[-2])
            return httpx.Response(
                self._trace_status, request=request,
                text=self._traces.get(job_id, ""),
            )
        if "/pipelines/" in path and path.endswith("/jobs"):
            pipeline_id = int(path.rsplit("/", 2)[-2])
            page = (params or {}).get("page", 1)
            batch = self._jobs.get(pipeline_id, []) if page == 1 else []
            return httpx.Response(200, request=request, json=batch)
        return httpx.Response(200, request=request, json=self._pipelines)


@pytest.fixture
def scripted(monkeypatch: pytest.MonkeyPatch):
    def _install(client: _ScriptedClient) -> _ScriptedClient:
        monkeypatch.setattr(
            gitlab_ci_signals, "_client", lambda token, base_url: client
        )
        return client

    return _install


def test_happy_path_collects_failed_job_traces(scripted) -> None:
    scripted(_ScriptedClient(
        pipelines=[{"id": 9, "ref": "feature-x"}],
        jobs={9: [{"id": 1, "name": "pytest", "status": "failed"},
                  {"id": 2, "name": "lint", "status": "failed"}]},
        traces={1: "assert failed", 2: "E501"},
    ))
    signals = fetch_gitlab_ci_failure_signals("g/p", "sha", "tok")
    assert [(s.workflow_name, s.job_name, s.conclusion, s.log_tail)
            for s in signals] == [
        ("feature-x", "pytest", "failed", "assert failed"),
        ("feature-x", "lint", "failed", "E501"),
    ]


def test_no_failed_pipelines_returns_empty(scripted) -> None:
    scripted(_ScriptedClient(pipelines=[]))
    assert fetch_gitlab_ci_failure_signals("g/p", "sha", "tok") == []


def test_max_jobs_caps_collection(scripted) -> None:
    scripted(_ScriptedClient(
        pipelines=[{"id": 9, "ref": "main"}],
        jobs={9: [{"id": i, "name": f"j{i}", "status": "failed"}
                  for i in range(1, 6)]},
    ))
    signals = fetch_gitlab_ci_failure_signals("g/p", "sha", "tok", max_jobs=2)
    assert len(signals) == 2


def test_missing_trace_yields_empty_tail(scripted) -> None:
    scripted(_ScriptedClient(
        pipelines=[{"id": 9, "ref": "main"}],
        jobs={9: [{"id": 1, "name": "j", "status": "failed"}]},
        trace_status=404,
    ))
    signals = fetch_gitlab_ci_failure_signals("g/p", "sha", "tok")
    assert signals[0].log_tail == ""


def test_trace_truncated_to_tail(scripted) -> None:
    scripted(_ScriptedClient(
        pipelines=[{"id": 9, "ref": "main"}],
        jobs={9: [{"id": 1, "name": "j", "status": "failed"}]},
        traces={1: "HEAD-" + "x" * 100 + "-TAIL"},
    ))
    signals = fetch_gitlab_ci_failure_signals(
        "g/p", "sha", "tok", log_tail_chars=5
    )
    assert signals[0].log_tail == "-TAIL"


def test_project_path_is_url_encoded(scripted) -> None:
    client = scripted(_ScriptedClient(
        pipelines=[{"id": 9, "ref": "main"}],
        jobs={9: [{"id": 1, "name": "j", "status": "failed"}]},
    ))
    fetch_gitlab_ci_failure_signals("group/sub/proj", "sha", "tok")
    assert all(p.startswith("/projects/group%2Fsub%2Fproj/") for p in client.paths)


def test_non_list_pipelines_payload_is_tolerated(scripted) -> None:
    scripted(_ScriptedClient(pipelines={"message": "403 Forbidden"}))  # type: ignore[arg-type]
    assert fetch_gitlab_ci_failure_signals("g/p", "sha", "tok") == []
