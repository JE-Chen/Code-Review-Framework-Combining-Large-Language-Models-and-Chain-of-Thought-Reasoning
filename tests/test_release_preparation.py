"""Blocked or mismatched releases leave all version metadata untouched."""

import json

import pytest

from scripts.prepare_release import prepare


def source(tmp_path):
    (tmp_path / "release").mkdir()
    (tmp_path / "release/evidence.json").write_text(json.dumps({"target_version": "1.0.0"}))
    (tmp_path / "prthinker").mkdir()
    (tmp_path / "pyproject.toml").write_text('[project]\nversion = "0.1.0"\n')
    (tmp_path / "CITATION.cff").write_text('version: 0.1.0\n')
    (tmp_path / "prthinker/__init__.py").write_text('__version__ = "0.1.0"\n')
    return tmp_path


def test_blocked_release_changes_nothing(tmp_path):
    root = source(tmp_path)
    with pytest.raises(ValueError, match="gates"):
        prepare(root, "v1.0.0", lambda _path: {"ready": False})
    assert '"0.1.0"' in (root / "pyproject.toml").read_text()
    with pytest.raises(ValueError, match="target"):
        prepare(root, "v1.0.1", lambda _path: {"ready": True})


def test_verified_release_synchronizes_both_versions(tmp_path):
    root = source(tmp_path)
    assert prepare(root, "v1.0.0", lambda _path: {"ready": True}) == "1.0.0"
    assert 'version = "1.0.0"' in (root / "pyproject.toml").read_text()
    assert '__version__ = "1.0.0"' in (root / "prthinker/__init__.py").read_text()
    assert 'version: 1.0.0' in (root / "CITATION.cff").read_text()
