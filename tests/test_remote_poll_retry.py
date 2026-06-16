"""Tests for the async submit/poll machinery shared by /ask and /review."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import httpx
import pytest

from prthinker.backends import remote as remote_mod
from prthinker.config import RemoteBackendConfig


class _ScriptedClient:
    """Stand-in for httpx.Client that replays a scripted sequence.

    ``kind`` selects the endpoint family so the same harness drives both the
    ``/review`` and ``/ask`` job paths.
    """

    def __init__(
        self,
        get_responses: Iterable[Any],
        submit_payload: dict,
        kind: str = "review",
    ) -> None:
        self._get_iter = iter(get_responses)
        self._submit_payload = submit_payload
        self._kind = kind
        self.cancel_calls: list[str] = []
        self.get_calls: list[str] = []

    def post(self, path: str, json: dict | None = None) -> httpx.Response:
        del json
        if path == f"/{self._kind}/submit":
            req = httpx.Request("POST", "http://test" + path)
            return httpx.Response(200, request=req, json=self._submit_payload)
        if path.startswith(f"/{self._kind}/cancel/"):
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


def _ok_done_response(payload: Any, kind: str = "review") -> httpx.Response:
    return httpx.Response(
        200,
        request=httpx.Request("GET", f"http://test/{kind}/result/x"),
        json={"status": "done", "result": payload},
    )


def _http_status_response(code: int, kind: str = "review") -> httpx.Response:
    return httpx.Response(
        code,
        request=httpx.Request("GET", f"http://test/{kind}/result/x"),
        text=f"{code} from upstream",
    )


@pytest.fixture
def _no_sleep(monkeypatch):
    monkeypatch.setattr(remote_mod.time, "sleep", lambda _s: None)


def _inject(owner: Any, scripted: _ScriptedClient) -> None:
    """Swap the real httpx client on a backend/client for the scripted one."""
    owner._job._client.close()
    owner._job._client = scripted


def _make_client(get_responses: Iterable[Any]) -> remote_mod.RemotePipelineClient:
    cfg = RemoteBackendConfig(url="http://test", timeout_seconds=600.0)
    client = remote_mod.RemotePipelineClient(cfg)
    _inject(client, _ScriptedClient(get_responses, {"job_id": "x"}))
    return client


def _make_ask_backend(
    get_responses: Iterable[Any],
) -> remote_mod.RemoteHttpBackend:
    cfg = RemoteBackendConfig(url="http://test", timeout_seconds=600.0)
    backend = remote_mod.RemoteHttpBackend(cfg)
    _inject(backend, _ScriptedClient(get_responses, {"job_id": "x"}, kind="ask"))
    return backend


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
    assert client._job._client.cancel_calls == []
    assert len(client._job._client.get_calls) == 4


def test_exceeds_failure_budget_raises_and_cancels(_no_sleep):
    failures = [_http_status_response(502)] * (
        remote_mod._MAX_CONSECUTIVE_POLL_FAILURES + 1
    )
    client = _make_client(failures)
    with pytest.raises(httpx.HTTPStatusError):
        client.review(_make_request())
    assert client._job._client.cancel_calls == ["/review/cancel/x"]


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
    assert client._job._client.cancel_calls == []


# --- /ask async job (RemoteHttpBackend.generate) ---------------------------


def test_ask_submits_and_polls_returning_text(_no_sleep):
    backend = _make_ask_backend(
        [
            httpx.Response(
                200,
                request=httpx.Request("GET", "http://test/ask/result/x"),
                json={"status": "pending"},
            ),
            _ok_done_response("generated summary", kind="ask"),
        ]
    )
    out = backend.generate("hello", max_new_tokens=64)
    assert out == "generated summary"
    assert backend._job._client.get_calls == [
        "/ask/result/x",
        "/ask/result/x",
    ]
    assert backend._job._client.cancel_calls == []


def test_ask_transient_502_retried_then_succeeds(_no_sleep):
    backend = _make_ask_backend(
        [
            _http_status_response(502, kind="ask"),
            _http_status_response(504, kind="ask"),
            _ok_done_response("ok", kind="ask"),
        ]
    )
    assert backend.generate("p", max_new_tokens=8) == "ok"
    assert backend._job._client.cancel_calls == []


def test_ask_empty_result_returns_empty_string(_no_sleep):
    backend = _make_ask_backend(
        [_ok_done_response(None, kind="ask")]
    )
    assert backend.generate("p", max_new_tokens=8) == ""


def test_ask_server_error_raises_and_cancels(_no_sleep):
    backend = _make_ask_backend(
        [
            httpx.Response(
                200,
                request=httpx.Request("GET", "http://test/ask/result/x"),
                json={"status": "error", "error": "boom"},
            )
        ]
    )
    with pytest.raises(RuntimeError, match="boom"):
        backend.generate("p", max_new_tokens=8)
    # The terminal error raises out of the poll loop before the run is marked
    # complete, so the finally-block fires a best-effort cancel (harmless: the
    # server-side job has already reached a terminal state).
    assert backend._job._client.cancel_calls == ["/ask/cancel/x"]


def test_ask_cancelled_status_raises_and_cancels(_no_sleep):
    backend = _make_ask_backend(
        [
            httpx.Response(
                200,
                request=httpx.Request("GET", "http://test/ask/result/x"),
                json={"status": "cancelled"},
            )
        ]
    )
    with pytest.raises(RuntimeError, match="cancelled server-side"):
        backend.generate("p", max_new_tokens=8)
    assert backend._job._client.cancel_calls == ["/ask/cancel/x"]
