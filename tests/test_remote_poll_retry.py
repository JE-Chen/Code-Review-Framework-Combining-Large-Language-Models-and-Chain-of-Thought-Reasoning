"""Tests for RemotePipelineClient's poll-retry behaviour."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import httpx
import pytest

from prthinker.backends import remote as remote_mod
from prthinker.config import RemoteBackendConfig


class _ScriptedClient:
    """Stand-in for httpx.Client that replays a scripted sequence."""

    def __init__(self, get_responses: Iterable[Any], submit_payload: dict) -> None:
        self._get_iter = iter(get_responses)
        self._submit_payload = submit_payload
        self.cancel_calls: list[str] = []
        self.get_calls: list[str] = []

    def post(self, path: str, json: dict | None = None) -> httpx.Response:
        del json
        if path == "/review/submit":
            req = httpx.Request("POST", "http://test" + path)
            return httpx.Response(200, request=req, json=self._submit_payload)
        if path.startswith("/review/cancel/"):
            self.cancel_calls.append(path)
            return httpx.Response(
                200, request=httpx.Request("POST", "http://test" + path)
            )
        raise AssertionError(f"unexpected POST {path}")

    def get(self, path: str) -> httpx.Response:
        self.get_calls.append(path)
        nxt = next(self._get_iter)
        if isinstance(nxt, Exception):
            raise nxt
        return nxt

    def close(self) -> None:
        return None


def _ok_done_response(payload: dict) -> httpx.Response:
    return httpx.Response(
        200,
        request=httpx.Request("GET", "http://test/review/result/x"),
        json={"status": "done", "result": payload},
    )


def _http_status_response(code: int) -> httpx.Response:
    return httpx.Response(
        code,
        request=httpx.Request("GET", "http://test/review/result/x"),
        text=f"{code} from upstream",
    )


@pytest.fixture
def _no_sleep(monkeypatch):
    monkeypatch.setattr(remote_mod.time, "sleep", lambda _s: None)


def _make_client(get_responses: Iterable[Any]) -> remote_mod.RemotePipelineClient:
    cfg = RemoteBackendConfig(url="http://test", timeout_seconds=600.0)
    client = remote_mod.RemotePipelineClient(cfg)
    client._client.close()
    client._client = _ScriptedClient(get_responses, {"job_id": "x"})
    return client


_DIFF = "--- a\n+++ b\n@@ -0,0 +1 @@\n+x\n"


def _minimal_review_payload() -> dict:
    return {"code_diff": _DIFF, "rag_docs": [], "steps": []}


def _make_request() -> remote_mod.ReviewRequest:
    return remote_mod.ReviewRequest(code_diff=_DIFF)


def test_transient_502_is_retried_then_succeeds(_no_sleep):
    payload = _minimal_review_payload()
    client = _make_client(
        [
            _http_status_response(502),
            _http_status_response(502),
            _http_status_response(502),
            _ok_done_response(payload),
        ]
    )
    resp = client.review(_make_request())
    assert isinstance(resp, remote_mod.ReviewResponse)
    assert client._client.cancel_calls == []
    assert len(client._client.get_calls) == 4


def test_exceeds_failure_budget_raises_and_cancels(_no_sleep):
    failures = [_http_status_response(502)] * (
        remote_mod._MAX_CONSECUTIVE_POLL_FAILURES + 1
    )
    client = _make_client(failures)
    with pytest.raises(httpx.HTTPStatusError):
        client.review(_make_request())
    assert client._client.cancel_calls == ["/review/cancel/x"]


def test_failure_counter_resets_on_success(_no_sleep):
    payload = _minimal_review_payload()
    pending = httpx.Response(
        200,
        request=httpx.Request("GET", "http://test/review/result/x"),
        json={"status": "running"},
    )
    script = (
        [_http_status_response(502)] * 4
        + [pending]
        + [_http_status_response(502)] * 4
        + [_ok_done_response(payload)]
    )
    client = _make_client(script)
    client.review(_make_request())
    assert client._client.cancel_calls == []
