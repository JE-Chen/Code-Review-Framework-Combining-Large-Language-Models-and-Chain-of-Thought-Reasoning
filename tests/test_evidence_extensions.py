from pathlib import Path
from prthinker.calibration import CalibrationStore
from prthinker.retrieval_eval import evaluate
from prthinker.trajectory import TrajectorySink
from prthinker.verification_tiers import ToolSpec, run_tier
from argparse import Namespace
from prthinker.cli_review_emit import _postprocess_findings
from prthinker.pipeline import ReviewResult
from prthinker.schemas import InlineFinding, Provenance
from prthinker.cli import main
import json
import subprocess
import sys
from prthinker.execution_sandbox import DockerExecutor
from prthinker.execution_sandbox import LocalExecutor
from prthinker.verification_tiers import verify_base_head


def test_unsupported_tool_is_explicit(tmp_path: Path):
    evidence = run_tier(
        ToolSpec("bounded", "missing", ("prthinker-tool-that-does-not-exist",)),
        tmp_path,
    )
    assert evidence.status == "unsupported"


def test_probe_only_never_claims_verification(tmp_path: Path):
    evidence = run_tier(
        ToolSpec("bounded", "git-probe", ("git", "--version"), probe_only=True),
        tmp_path,
    )
    assert evidence.status == "inconclusive"


def test_calibration_store_preserves_both_outcomes(tmp_path: Path):
    store = CalibrationStore(tmp_path / "cal.sqlite")
    store.record("r", "a", "security", True)
    store.record("r", "a", "security", False)
    value = store.calibration("r", "a", "security")
    assert (value.accepted, value.dismissed) == (1, 1)


def test_calibration_deduplicates_and_abstains_until_minimum(tmp_path: Path):
    store = CalibrationStore(tmp_path / "cal.sqlite")
    store.record("r", "a", "security", True, event_id="same")
    store.record("r", "a", "security", True, event_id="same")
    posterior = store.hierarchical("r", "a", "security")
    assert 0.99 <= posterior.accepted <= 1.0
    assert (
        store.decision(0.9, "r", "a", "security", minimum_samples=2)
        == "request-human-review"
    )


def test_trajectory_hashes_content_without_storing_it(tmp_path: Path):
    path = tmp_path / "trace.jsonl"
    TrajectorySink(path, "run").record("retrieve", content="secret")
    text = path.read_text(encoding="utf-8")
    assert "secret" not in text and "input_sha256" in text


def test_retrieval_metrics():
    metric = evaluate(["a", "b"], ["a", "c"], ["a"], [True, False])
    assert (
        metric.recall == 0.5 and metric.precision == 0.5 and metric.utilization == 0.5
    )


def test_calibration_store_drives_confidence_filter(tmp_path: Path):
    store = CalibrationStore(tmp_path / "cal.sqlite")
    for index in range(10):
        store.record("repo", "author", "security", False, event_id=str(index))
    result = ReviewResult(
        code_diff="",
        rag_docs=[],
        inline_findings=[
            InlineFinding(
                path="a.py", line=1, comment="x", provenance=Provenance(confidence=0.4)
            )
        ],
    )
    args = Namespace(
        ignore_file=str(tmp_path / "missing"),
        dedupe_findings=False,
        min_confidence=0.0,
        calibration_store=str(tmp_path / "cal.sqlite"),
        calibration_author="author",
        calibration_category="security",
        calibration_min_samples=10,
        calibration_half_life_days=90,
        repo="repo",
    )
    _postprocess_findings(args, result)
    assert result.inline_findings == []


def test_verify_refuses_unsandboxed_by_default(tmp_path: Path, capsys):
    assert (
        main(
            [
                "verify",
                "--workdir",
                str(tmp_path),
                "--tiers",
                "dynamic",
                "--sandbox",
                "none",
            ]
        )
        == 0
    )
    rows = json.loads(capsys.readouterr().out)
    assert rows[0]["status"] == "unsupported"


def test_docker_sandbox_requires_pinned_image(tmp_path: Path):
    result = DockerExecutor("python:latest").run(("python", "-V"), tmp_path, 1)
    assert result.unsupported and "sha256" in result.stderr


def test_base_head_archive_isolates_regression(tmp_path: Path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True
    )
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    flag = tmp_path / "flag"
    flag.write_text("good", encoding="utf-8")
    subprocess.run(["git", "add", "flag"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "base"], cwd=tmp_path, check=True)
    base = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    flag.write_text("bad", encoding="utf-8")
    subprocess.run(["git", "commit", "-qam", "head"], cwd=tmp_path, check=True)
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    command = (
        sys.executable,
        "-c",
        "from pathlib import Path; raise SystemExit(Path('flag').read_text() == 'bad')",
    )
    evidence = verify_base_head(tmp_path, base, head, command, executor=LocalExecutor())
    assert evidence[-1].status == "confirmed"


def test_verify_binds_evidence_to_finding(tmp_path: Path, capsys):
    finding = InlineFinding(path="a.py", line=1, comment="bug")
    source = tmp_path / "findings.json"
    source.write_text(json.dumps([finding.model_dump(mode="json")]), encoding="utf-8")
    assert (
        main(
            [
                "verify",
                "--workdir",
                str(tmp_path),
                "--tiers",
                "dynamic",
                "--sandbox",
                "none",
                "--findings-file",
                str(source),
                "--finding-id",
                finding.finding_id,
            ]
        )
        == 0
    )
    payload = json.loads(capsys.readouterr().out)
    assert payload["findings"][0]["evidence"][0]["finding_id"] == finding.finding_id
