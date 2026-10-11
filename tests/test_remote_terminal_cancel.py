"""A timeout cannot leave an orphan job while the next benchmark case starts."""

import httpx
import pytest

from prthinker.backends.remote import _AsyncJobClient


class Client:
    def __init__(self, terminal=True):
        self.posts = []
        self.terminal = terminal

    def post(self, path, json=None):
        self.posts.append(path)
        return httpx.Response(200, json={"job_id": "job"},
                              request=httpx.Request("POST", "https://test" + path))

    def get(self, path):
        return httpx.Response(200, json={"status": "cancelled" if self.terminal else "running"},
                              request=httpx.Request("GET", "https://test" + path))


def test_timeout_waits_for_terminal(monkeypatch):
    client = Client()
    job = _AsyncJobClient(client, "ask", 0)
    monkeypatch.setattr("prthinker.backends.remote.time.sleep", lambda _seconds: None)
    with pytest.raises(TimeoutError):
        job.run({}, lambda payload: payload)
    assert client.posts == ["/ask/submit", "/ask/cancel/job"]
    assert job._unsafe_job is None


def test_nonterminal_cancel_prevents_next_submission(monkeypatch):
    client = Client(terminal=False)
    job = _AsyncJobClient(client, "ask", 0)
    monkeypatch.setattr("prthinker.backends.remote.time.sleep", lambda _seconds: None)
    with pytest.raises(TimeoutError):
        job.run({}, lambda payload: payload)
    with pytest.raises(RuntimeError, match="refusing"):
        job.run({}, lambda payload: payload)
    assert client.posts.count("/ask/submit") == 1
