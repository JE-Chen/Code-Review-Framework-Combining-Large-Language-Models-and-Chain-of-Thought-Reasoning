"""Registry + pipeline-integration tests for opt-in review modes."""

from __future__ import annotations

import pytest

from prthinker.pipeline import CoTPipeline, PerFileReviewOptions
from prthinker.rag import NoOpRetriever
from prthinker.review_modes import (
    available_modes,
    get_mode,
    register_mode,
    run_review_modes,
)
from tests.conftest import FakeBackend

_ONE_FILE_DIFF = (
    "diff --git a/a.py b/a.py\n--- a/a.py\n+++ b/a.py\n@@ -1 +1,2 @@\n x\n+y\n"
)


class _RecordingBackend:
    def __init__(self):
        self.prompts: list[str] = []

    def generate(self, prompt: str, *, max_new_tokens: int = 0) -> str:
        self.prompts.append(prompt)
        return f"out[{len(self.prompts)}]"


# ---------- registry --------------------------------------------------------


def test_builtin_modes_registered():
    assert set(available_modes()) == {
        "security",
        "performance",
        "test-coverage",
        "iac",
        "db-migration",
        "accessibility",
        "secret-scan",
        "pii",
        "refactoring",
        "ai-generated",
    }


def test_each_mode_builds_a_prompt_embedding_the_diff():
    for name in available_modes():
        prompt = get_mode(name).build_prompt(_ONE_FILE_DIFF)
        assert isinstance(prompt, str) and prompt.strip()
        assert "+y" in prompt  # diff embedded


def test_register_duplicate_name_raises():
    with pytest.raises(ValueError, match="already registered"):
        register_mode("security", "dup")(lambda diff: diff)


def test_run_review_modes_keys_outputs_and_skips_unknown():
    backend = _RecordingBackend()
    out = run_review_modes(
        backend,
        _ONE_FILE_DIFF,
        ["security", "iac", "does-not-exist"],
        128,
    )
    assert set(out) == {"review_mode::security", "review_mode::iac"}
    assert len(backend.prompts) == 2


def test_run_review_modes_empty_enabled_is_noop():
    backend = _RecordingBackend()
    assert run_review_modes(backend, _ONE_FILE_DIFF, [], 128) == {}
    assert backend.prompts == []


# ---------- pipeline integration --------------------------------------------


def test_run_per_file_runs_enabled_review_modes():
    # 5 CoT steps for the single file + 1 review-mode call.
    backend = FakeBackend(["s"] * 5 + ["SECURITY FINDINGS"])
    pipeline = CoTPipeline(backend=backend, retriever=NoOpRetriever())
    result = pipeline.run_per_file(
        _ONE_FILE_DIFF,
        PerFileReviewOptions(inline_review=False, review_modes=("security",)),
    )
    assert "review_mode::security" in result.step_outputs
    assert result.step_outputs["review_mode::security"] == "SECURITY FINDINGS"
    assert len(backend.calls) == 6


def test_run_per_file_without_review_modes_adds_nothing():
    backend = FakeBackend(["s"] * 5)
    pipeline = CoTPipeline(backend=backend, retriever=NoOpRetriever())
    result = pipeline.run_per_file(
        _ONE_FILE_DIFF, PerFileReviewOptions(inline_review=False)
    )
    assert not any(k.startswith("review_mode::") for k in result.step_outputs)
