"""Standalone summaries keep metadata reproducible and never leak input secrets."""

import json

import pytest

from prthinker.summary_command import generate_summary, load_summary_input
from tests.conftest import FakeBackend


def test_summary_metadata_and_redaction():
    backend = FakeBackend(["### Overview\nFix validation."])
    result = generate_summary(backend, {"diff": "+validate()", "title": "ghp_" + "x" * 30}, 32)
    assert result["metadata"]["max_new_tokens"] == 32
    assert len(result["metadata"]["input_sha256"]) == 64
    assert "ghp_" not in backend.calls[0][0]
    assert generate_summary(FakeBackend(["again"]), {"diff": "+validate()", "title": "ghp_" + "x" * 30}, 32)["metadata"] == result["metadata"]


@pytest.mark.parametrize("payload", [{}, [], {"diff": 2}, {"diff": "", "commits": ["ok", 2]}])
def test_invalid_input(tmp_path, payload):
    source = tmp_path / "input.json"
    source.write_text(json.dumps(payload))
    with pytest.raises(ValueError):
        load_summary_input(source)


def test_empty_output_is_a_failure():
    with pytest.raises(ValueError, match="empty"):
        generate_summary(FakeBackend([" "]), {"diff": "+x"}, 8)


def test_local_json_cli_needs_no_forge(tmp_path, monkeypatch):
    from types import SimpleNamespace

    from prthinker.cli import main

    source = tmp_path / "input.json"
    source.write_text('{"diff":"+validate()"}', encoding="utf-8")
    output = tmp_path / "summary.json"
    monkeypatch.setattr("prthinker.cli_review.create_backend", lambda _config: FakeBackend(["Validate inputs."]))
    monkeypatch.setattr("prthinker.cli_review._build_config", lambda _args: SimpleNamespace(max_new_tokens=32))
    def unexpected(_args):
        raise AssertionError("local summary must not construct a forge adapter")
    monkeypatch.setattr("prthinker.cli_review.build_platform_adapter", unexpected)
    assert main(["pr-summary", "--input-json", str(source), "--summary-format", "json",
                 "--summary-output", str(output)]) == 0
    assert json.loads(output.read_text())["summary"] == "Validate inputs."


def test_explicit_publish_upserts_marked_summary(tmp_path):
    from types import SimpleNamespace

    from prthinker.pr_summary import DEFAULT_MARKER
    from prthinker.summary_command import command

    source = tmp_path / "input.json"
    source.write_text('{"diff":"+validate()"}', encoding="utf-8")
    comments = {}
    class Adapter:
        def upsert_marked_comment(self, body, *, marker):
            comments[marker] = body
    args = SimpleNamespace(input_json=source, publish_summary=True, summary_format="json",
                           summary_output=tmp_path / "result.json")
    for text in ("first", "updated"):
        command(args, backend_factory=lambda _config, value=text: FakeBackend([value]),
                config_builder=lambda _args: SimpleNamespace(max_new_tokens=32),
                adapter_builder=lambda _args: Adapter())
    assert len(comments) == 1 and "updated" in comments[DEFAULT_MARKER]
