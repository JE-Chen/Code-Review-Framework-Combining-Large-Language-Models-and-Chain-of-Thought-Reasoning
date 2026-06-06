"""Tests for the low-attention (noise) file classifier."""

from __future__ import annotations

from prthinker.noise_files import format_noise_note, noise_files


def test_lockfiles_flagged():
    changed = ["poetry.lock", "frontend/package-lock.json", "go.sum"]
    result = noise_files(changed)
    assert ("poetry.lock", "lockfile") in result
    assert ("frontend/package-lock.json", "lockfile") in result
    assert ("go.sum", "lockfile") in result


def test_minified_and_maps_flagged():
    changed = ["static/app.min.js", "static/app.min.css", "static/app.js.map"]
    reasons = {reason for _, reason in noise_files(changed)}
    assert reasons == {"minified/generated"}


def test_vendored_dirs_flagged():
    changed = ["vendor/lib/x.go", "node_modules/pkg/index.js"]
    result = dict(noise_files(changed))
    assert result["vendor/lib/x.go"] == "vendored"
    assert result["node_modules/pkg/index.js"] == "vendored"


def test_snapshots_flagged():
    changed = ["tests/__snapshots__/x.ambr", "ui/Button.test.tsx.snap"]
    reasons = {reason for _, reason in noise_files(changed)}
    assert reasons == {"snapshot"}


def test_handwritten_code_not_flagged():
    changed = ["prthinker/cli.py", "src/app.tsx", "README.md"]
    assert noise_files(changed) == []


def test_empty_input():
    assert noise_files([]) == []


def test_result_is_sorted_by_path():
    changed = ["z/poetry.lock", "a/yarn.lock"]
    paths = [p for p, _ in noise_files(changed)]
    assert paths == ["a/yarn.lock", "z/poetry.lock"]


def test_case_insensitive_lockfile_match():
    assert noise_files(["Cargo.lock"]) == [("Cargo.lock", "lockfile")]


def test_lockfile_precedence_over_generated_suffix():
    # ``poetry.lock`` ends with ``.lock`` but must report 'lockfile'.
    assert noise_files(["poetry.lock"]) == [("poetry.lock", "lockfile")]


def test_format_note_lists_files_with_reasons():
    note = format_noise_note([("poetry.lock", "lockfile")])
    assert "1 low-attention file(s)" in note
    assert "`poetry.lock` — lockfile" in note
    assert note.startswith("<details>")


def test_format_note_empty_is_blank():
    assert format_noise_note([]) == ""


def test_format_note_caps_overflow():
    noise = [(f"vendor/m{i}.js", "vendored") for i in range(15)]
    note = format_noise_note(noise)
    assert "15 low-attention file(s)" in note
    assert "… and 3 more" in note
