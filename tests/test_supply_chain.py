import json
from pathlib import Path
from prthinker.cli import main


def test_attest_outputs_three_standard_artifacts(tmp_path: Path, capsys):
    review = tmp_path / "review.json"
    review.write_text("{}", encoding="utf-8")
    out = tmp_path / "out"
    assert (
        main(
            [
                "attest",
                "--repository",
                "https://example/repo",
                "--revision",
                "abc",
                "--review-file",
                str(review),
                "--output-dir",
                str(out),
                "--model",
                "model-x",
            ]
        )
        == 0
    )
    assert json.loads((out / "review-attestation.json").read_text())["_type"].endswith(
        "Statement/v1"
    )
    assert (
        json.loads((out / "slsa-provenance.json").read_text())["predicateType"]
        == "https://slsa.dev/provenance/v1"
    )
    assert json.loads((out / "ai-bom.cdx.json").read_text())["bomFormat"] == "CycloneDX"
