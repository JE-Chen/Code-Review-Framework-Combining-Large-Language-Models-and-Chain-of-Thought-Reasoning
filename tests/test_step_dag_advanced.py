from prthinker.step_dag import DagNode, execute_detailed
import time
import pytest


def test_dag_cache_retry_skip_and_resume():
    calls = {"n": 0}
    cache = {}

    def flaky(_):
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("retry")
        return 2

    nodes = [
        DagNode("a", flaky, retries=1, cache_key=lambda _: "a"),
        DagNode("b", lambda r: r["a"] + 1, ("a",)),
        DagNode("skip", lambda _: 9, when=lambda _: False),
    ]
    run = execute_detailed(nodes, cache=cache)
    assert (
        run.results["b"] == 3
        and run.attempts["a"] == 2
        and run.states["skip"] == "skipped"
    )
    rerun = execute_detailed(nodes, cache=cache)
    assert rerun.states["a"] == "cached"
    resumed = execute_detailed(
        [DagNode("b", lambda r: r["a"] + 1, ("a",))], initial={"a": 4}
    )
    assert resumed.results["b"] == 5


def test_dag_timeout_is_reported():
    with pytest.raises(TimeoutError):
        execute_detailed(
            [DagNode("slow", lambda _: time.sleep(0.05), timeout_seconds=0.001)]
        )
