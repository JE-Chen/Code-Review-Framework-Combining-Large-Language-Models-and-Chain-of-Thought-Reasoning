"""Integration tests for the Wave-1 feature wiring.

Covers the platform-factory branch, the new CLI flags / subcommand, and
the publish-path helpers that thread ignore / dedup / SARIF / HTML /
API-impact into a review.
"""

from types import SimpleNamespace

from prthinker.cli import _build_parser
from prthinker.cli_review import (
    _append_api_impact,
    _emit_review_artifacts,
    _postprocess_findings,
)
from prthinker.pipeline import FileReviewResult, ReviewResult
from prthinker.platforms import PlatformKind, create_platform_adapter
from prthinker.platforms.gitea import GiteaAdapter
from prthinker.schemas import InlineFinding


def _finding(path="a.py", line=1, severity="warning", comment="msg"):
    return InlineFinding(path=path, line=line, severity=severity, comment=comment)


def _result(findings=None, per_file=None, code_diff="diff"):
    return ReviewResult(
        code_diff=code_diff,
        rag_docs=[],
        inline_findings=list(findings or []),
        per_file=list(per_file or []),
    )


# ---------- platform factory ------------------------------------------------

def test_factory_returns_gitea_adapter():
    adapter = create_platform_adapter(
        PlatformKind.GITEA, repo="o/r", token="t", pr_number=1,
    )
    assert isinstance(adapter, GiteaAdapter)


def test_platform_kind_has_gitea():
    assert PlatformKind("gitea") is PlatformKind.GITEA


# ---------- parser surface --------------------------------------------------

def test_new_common_flags_parse():
    ns = _build_parser().parse_args([
        "review-file", "-", "--backend", "openai", "--openai-api-key", "k",
        "--sarif-out", "x.sarif", "--html-report", "r.html",
        "--ignore-file", ".pi", "--dedupe-findings", "--api-impact",
    ])
    assert ns.sarif_out == "x.sarif"
    assert ns.html_report == "r.html"
    assert ns.ignore_file == ".pi"
    assert ns.dedupe_findings is True
    assert ns.api_impact is True


def test_gitea_is_a_platform_choice():
    ns = _build_parser().parse_args([
        "review-pr", "--platform", "gitea",
        "--backend", "remote", "--remote-url", "http://h",
    ])
    assert ns.platform == "gitea"


def test_review_commits_subcommand_registered():
    parser = _build_parser()
    sub = next(a for a in parser._actions if a.__class__.__name__ == "_SubParsersAction")
    assert "review-commits" in sub.choices


# ---------- publish-path helpers --------------------------------------------

def test_postprocess_applies_ignore_glob(tmp_path):
    ignore = tmp_path / ".prthinkerignore"
    ignore.write_text("generated/*\n", encoding="utf-8")
    fr = FileReviewResult(
        path="generated/x.py", rag_docs=[], step_outputs={},
        inline_findings=[_finding(path="generated/x.py")],
    )
    result = _result(findings=[_finding(path="generated/x.py"), _finding(path="src/a.py")],
                     per_file=[fr])
    args = SimpleNamespace(ignore_file=str(ignore), dedupe_findings=False)
    _postprocess_findings(args, result)
    assert [f.path for f in result.inline_findings] == ["src/a.py"]
    assert result.per_file[0].inline_findings == []


def test_postprocess_dedupes_when_enabled(tmp_path):
    result = _result(findings=[_finding(), _finding()])  # identical
    args = SimpleNamespace(ignore_file=str(tmp_path / "absent"), dedupe_findings=True)
    _postprocess_findings(args, result)
    assert len(result.inline_findings) == 1


def test_emit_artifacts_writes_sarif_and_html(tmp_path):
    sarif = tmp_path / "out.sarif"
    html = tmp_path / "out.html"
    result = _result(findings=[_finding()])
    args = SimpleNamespace(sarif_out=str(sarif), html_report=str(html))
    _emit_review_artifacts(args, result)
    assert sarif.exists() and '"version"' in sarif.read_text(encoding="utf-8")
    assert html.exists() and "<html" in html.read_text(encoding="utf-8").lower()


def test_emit_artifacts_noop_without_flags():
    # No paths set -> no exception, nothing written.
    _emit_review_artifacts(SimpleNamespace(sarif_out="", html_report=""), _result())


def test_append_api_impact_adds_line():
    diff = (
        "diff --git a/m.py b/m.py\n"
        "--- a/m.py\n+++ b/m.py\n"
        "@@ -0,0 +1,2 @@\n+def new_public():\n+    return 1\n"
    )
    body = _append_api_impact("SUMMARY", _result(code_diff=diff))
    assert "Public API impact:" in body
    assert body.startswith("SUMMARY")
