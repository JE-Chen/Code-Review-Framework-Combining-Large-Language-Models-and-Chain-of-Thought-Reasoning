"""Protocol patches require both explicit approval and a matching file digest."""

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from prthinker.ide_protocol import (
    IDERequest,
    IDEServer,
    apply_approved_patch,
    safe_target,
)
from tests.conftest import FakeBackend


def test_patch_approval_staleness_and_syntax(tmp_path):
    target = tmp_path / "mod.py"
    target.write_bytes(b"x = 1\n")
    request = IDERequest(request_id="1", operation="apply_patch", workdir=str(tmp_path),
                         path="mod.py", replacement="x = 2\n", original_sha256=hashlib.sha256(target.read_bytes()).hexdigest())
    with pytest.raises(ValueError, match="approval"):
        apply_approved_patch(request)
    approved = request.model_copy(update={"approved": True})
    apply_approved_patch(approved)
    assert target.read_text() == "x = 2\n"
    with pytest.raises(ValueError, match="stale"):
        apply_approved_patch(approved)


def test_version_unknown_fields_and_path_traversal(tmp_path):
    with pytest.raises(ValidationError):
        IDERequest(request_id="1", operation="review", protocol_version=2)
    with pytest.raises(ValueError):
        safe_target(tmp_path, "../secret")
    request = IDERequest(request_id="1", operation="review")
    assert IDERequest.model_validate_json(request.model_dump_json()) == request


def test_server_events_and_duplicate_ids():
    events = []
    server = IDEServer(lambda: FakeBackend(["summary"] * 5 + ["[]"]), events.append)
    request = IDERequest(request_id="1", operation="review",
                         diff="diff --git a/x.py b/x.py\n--- a/x.py\n+++ b/x.py\n@@ -1 +1 @@\n-x=1\n+x=2\n")
    server.submit(request)
    with pytest.raises(ValueError, match="duplicate"):
        server.submit(request)
    server.pool.shutdown(wait=True)
    assert events[0]["event"] == "progress"
    assert events[-1]["event"] == "terminal" and events[-1]["status"] == "completed"


def test_cancel_unknown_job_has_explicit_terminal():
    events = []
    server = IDEServer(lambda: FakeBackend([]), events.append)
    server.submit(IDERequest(request_id="cancel", operation="cancel", target_request_id="unknown"))
    server.close()
    assert events[-1]["status"] == "unsupported"


def test_protocol_uses_utf8_even_with_legacy_console_encoding(tmp_path):
    target = tmp_path / "程式.py"
    target.write_text("value = '舊字'\n", encoding="utf-8")
    request = IDERequest(request_id="utf8", operation="apply_patch", workdir=str(tmp_path),
                         path=target.name, approved=True, replacement="value = '新字'\n",
                         original_sha256=hashlib.sha256(target.read_bytes()).hexdigest())
    result = subprocess.run([sys.executable, "-m", "prthinker", "ide", "--remote-url", "http://127.0.0.1:1",
                             "--no-rag"], cwd=tmp_path,
                            env={**os.environ, "PYTHONIOENCODING": "cp950",
                                 "PYTHONPATH": str(Path(__file__).resolve().parents[1])},
                            input=request.model_dump_json().encode("utf-8") + b"\n",
                            capture_output=True, timeout=30, check=False)
    assert result.returncode == 0, result.stderr.decode("utf-8", "replace")
    event = json.loads(result.stdout)
    assert event["status"] == "completed" and event["result"]["path"] == target.name
    assert target.read_text(encoding="utf-8") == "value = '新字'\n"
