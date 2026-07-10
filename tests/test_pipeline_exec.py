"""``PipelineExecutionMixin`` — the shared single-step executor.

Exercises ``_execute_step`` directly (sequential and DAG callers share
it): backend invocation, output-file persistence, capping, streaming
mirroring, trajectory recording, and the ``_verify_suggestions``
field-preserving reconstruction.
"""

from __future__ import annotations

import io
from pathlib import Path
from types import SimpleNamespace

from prthinker import sandbox
from prthinker.pipeline import CoTPipeline, FileReviewResult
from prthinker.rag import NoOpRetriever
from prthinker.schemas import InlineFinding, JudgeVerdict
from prthinker.steps import ReviewContext

from tests.conftest import FakeBackend


def _ctx() -> ReviewContext:
    return ReviewContext(code_diff="diff", rag_docs=[], file_path="a.py")


# ----- _execute_step -----------------------------------------------------

def test_execute_step_returns_output_and_writes_file(tmp_path: Path) -> None:
    backend = FakeBackend(["step body"])
    pipeline = CoTPipeline(backend=backend, retriever=NoOpRetriever())
    step_cls = pipeline._step_classes[0]

    out = pipeline._execute_step(step_cls, _ctx(), tmp_path)

    assert out == "step body"
    assert len(backend.calls) == 1
    written = (tmp_path / f"{step_cls.name}_result.md").read_text("utf-8")
    assert written == "step body"


def test_execute_step_caps_result_but_persists_full_text(
    tmp_path: Path,
) -> None:
    full = "x" * 100
    backend = FakeBackend([full])
    pipeline = CoTPipeline(
        backend=backend, retriever=NoOpRetriever(), max_step_result_chars=10
    )
    step_cls = pipeline._step_classes[0]

    out = pipeline._execute_step(step_cls, _ctx(), tmp_path)

    assert out.startswith("x" * 10)
    assert out.endswith("... [truncated]\n")
    # The on-disk copy keeps the full, uncapped output.
    assert (tmp_path / f"{step_cls.name}_result.md").read_text("utf-8") == full


def test_execute_step_no_output_dir_writes_nothing(tmp_path: Path) -> None:
    pipeline = CoTPipeline(backend=FakeBackend(["ok"]), retriever=NoOpRetriever())
    out = pipeline._execute_step(pipeline._step_classes[0], _ctx(), None)
    assert out == "ok"
    assert list(tmp_path.iterdir()) == []


def test_execute_step_streaming_mirrors_to_sink() -> None:
    sink = io.StringIO()
    backend = FakeBackend(["streamed text"])
    pipeline = CoTPipeline(
        backend=backend,
        retriever=NoOpRetriever(),
        stream=True,
        stream_sink=sink,
    )
    step_cls = pipeline._step_classes[0]

    out = pipeline._execute_step(step_cls, _ctx(), None, stream=True)

    assert out == "streamed text"
    mirrored = sink.getvalue()
    assert f"[{step_cls.name} :: a.py]" in mirrored
    assert "streamed text" in mirrored


class _RecordingSink:
    """Minimal trajectory stand-in capturing ``record`` calls."""

    def __init__(self) -> None:
        self.events: list[tuple[str, dict]] = []

    def record(self, event: str, *, content: str = "", **fields) -> None:
        del content
        self.events.append((event, fields))


def test_execute_step_records_trajectory_when_asked() -> None:
    sink = _RecordingSink()
    pipeline = CoTPipeline(
        backend=FakeBackend(["ok"]),
        retriever=NoOpRetriever(),
        trajectory_sink=sink,
    )
    step_cls = pipeline._step_classes[0]

    pipeline._execute_step(step_cls, _ctx(), None, record_trajectory=True)

    assert [event for event, _ in sink.events] == ["step"]
    fields = sink.events[0][1]
    assert fields["tool"] == step_cls.name
    assert fields["path"] == "a.py"
    assert fields["status"] == "ok"
    assert fields["duration_ms"] >= 0


def test_dag_runner_does_not_record_trajectory() -> None:
    # The DAG node body shares _execute_step but keeps its historical
    # behaviour of not emitting per-step trajectory events.
    sink = _RecordingSink()
    pipeline = CoTPipeline(
        backend=FakeBackend(["dag out"]),
        retriever=NoOpRetriever(),
        trajectory_sink=sink,
    )
    step_cls = pipeline._step_classes[0]

    run = pipeline._make_step_runner(step_cls, _ctx(), None)
    assert run({}) == "dag out"
    assert sink.events == []


def test_dag_runner_uses_snapshot_not_shared_ctx() -> None:
    backend = FakeBackend(["out"])
    pipeline = CoTPipeline(backend=backend, retriever=NoOpRetriever())
    ctx = _ctx()
    ctx.results["stale"] = "must not leak"
    step_cls = pipeline._step_classes[-1]  # total_summary reads prior results

    run = pipeline._make_step_runner(step_cls, ctx, None)
    run({"first_summary": "snapshot value"})

    prompt = backend.calls[0][0]
    assert "snapshot value" in prompt
    assert "must not leak" not in prompt


# ----- _verify_suggestions -----------------------------------------------

def test_verify_suggestions_preserves_all_other_fields(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        sandbox,
        "verify_suggestion",
        lambda finding, **_: SimpleNamespace(
            status="pass", verify_cmd="pytest", duration_ms=7, reason=""
        ),
    )
    with_suggestion = InlineFinding(
        path="a.py", line=3, severity="warning", comment="c", suggestion="fix()"
    )
    without_suggestion = InlineFinding(
        path="a.py", line=9, severity="info", comment="plain"
    )
    verdict = JudgeVerdict(verdict="approve", score=9)
    original = FileReviewResult(
        path="a.py",
        rag_docs=["rule"],
        step_outputs={"linter": "out"},
        inline_findings=[with_suggestion, without_suggestion],
        verdict=verdict,
        is_binary=False,
        is_deleted=False,
    )
    pipeline = CoTPipeline(backend=FakeBackend(), retriever=NoOpRetriever())

    result = pipeline._verify_suggestions(
        original, workdir=tmp_path, verify_cmd="pytest", timeout_seconds=5
    )

    # dataclasses.replace: every non-findings field carried over untouched.
    assert result.path == "a.py"
    assert result.rag_docs == ["rule"]
    assert result.step_outputs == {"linter": "out"}
    assert result.verdict == verdict
    assert result.counterfactuals == []
    # Only the finding with a suggestion gains a verification badge.
    assert result.inline_findings[0].verification is not None
    assert result.inline_findings[0].verification.status == "pass"
    assert result.inline_findings[1].verification is None
