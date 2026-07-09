from pathlib import Path
from prthinker.ablation import compare_runs
from prthinker.benchmark_scoring import FindingLabel, CaseScore, score_case, aggregate
from prthinker.calibration import BetaCalibration, select_threshold, cosine_drift
from prthinker.context_graph import impact_slice
from prthinker.execution_evidence import run_tool
from prthinker.step_dag import DagNode, execute


def test_scoring_and_ablation():
    a = FindingLabel("a.py", 10, "missing input validation")
    score = score_case(
        "x", [a], [FindingLabel("a.py", 11, "input validation is missing")]
    )
    assert score.tp == 1 and aggregate([score])["f1"] == 1
    result = compare_runs(
        "a", [CaseScore("x", 0, 0, 1)], "b", [score], bootstrap_samples=10
    )
    assert result.wins == 1


def test_calibration_and_drift():
    assert BetaCalibration(9, 1).mean > 0.5
    assert select_threshold([(0.1, False), (0.9, True)]) == 0.9
    assert cosine_drift([1, 0], [1, 0]) == 0


def test_dag_and_impact():
    assert (
        execute(
            [DagNode("a", lambda _: 1), DagNode("b", lambda r: r["a"] + 1, ("a",))]
        )["b"]
        == 2
    )
    assert impact_slice({"core"}, {("api", "core"), ("ui", "api")}) == {
        "core",
        "api",
        "ui",
    }


def test_execution_evidence():
    result = run_tool(("git", "--version"), Path.cwd())
    assert result.exit_code == 0 and "git version" in result.stdout.lower()
