"""Typed DAG scheduler with fan-out, retry, timeout, cache and resume."""

from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from dataclasses import dataclass, field
from typing import Any, Callable, MutableMapping


@dataclass(frozen=True)
class DagNode:
    name: str
    run: Callable[[dict[str, Any]], Any]
    depends_on: tuple[str, ...] = ()
    when: Callable[[dict[str, Any]], bool] | None = None
    retries: int = 0
    timeout_seconds: float | None = None
    cache_key: Callable[[dict[str, Any]], str] | None = None


@dataclass
class DagExecution:
    results: dict[str, Any] = field(default_factory=dict)
    states: dict[str, str] = field(default_factory=dict)
    attempts: dict[str, int] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)


def _run_once(node: DagNode, snapshot: dict[str, Any]) -> Any:
    """Run a node body once, enforcing its timeout via a throwaway worker."""
    pool = ThreadPoolExecutor(max_workers=1)
    future = pool.submit(node.run, snapshot)
    try:
        return future.result(timeout=node.timeout_seconds)
    finally:
        pool.shutdown(wait=False, cancel_futures=True)


def _attempt(node: DagNode, snapshot: dict[str, Any]):
    """Run one attempt, returning ``(value, None)`` or ``(None, exception)``."""
    try:
        return _run_once(node, snapshot), None
    except TimeoutError:
        return None, TimeoutError(f"node {node.name} timed out")
    except Exception as exc:
        return None, exc


def _run_node(
    node: DagNode, snapshot: dict[str, Any], cache: MutableMapping[str, Any] | None
):
    key = node.cache_key(snapshot) if node.cache_key else ""
    cached = bool(key) and cache is not None
    if cached and key in cache:
        return cache[key], "cached", 1
    last = None
    for attempt in range(1, node.retries + 2):
        value, last = _attempt(node, snapshot)
        if last is None:
            if cached:
                cache[key] = value
            return value, "completed", attempt
    raise last  # type: ignore[misc]


def _validate_dag(nodes: tuple[DagNode, ...], run: DagExecution) -> dict[str, DagNode]:
    """Return the name→node map, raising on duplicate names or missing deps."""
    pending = {n.name: n for n in nodes}
    if len(pending) != len(nodes):
        raise ValueError("duplicate DAG node")
    all_names = set(pending) | run.results.keys()
    missing = {d for n in nodes for d in n.depends_on if d not in all_names}
    if missing:
        raise ValueError(f"missing DAG dependencies: {sorted(missing)}")
    return pending


def _take_active(
    ready: list[DagNode],
    pending: dict[str, DagNode],
    run: DagExecution,
    snapshot: dict[str, Any],
) -> list[DagNode]:
    """Remove ready nodes from pending; record skips and return the ones to run."""
    active = []
    for node in ready:
        pending.pop(node.name)
        if node.when is not None and not node.when(snapshot):
            run.results[node.name] = None
            run.states[node.name] = "skipped"
        else:
            active.append(node)
    return active


def _record_result(
    node: DagNode, future, run: DagExecution, fail_fast: bool
) -> None:
    """Store a completed node's outcome, re-raising on failure when fail_fast."""
    try:
        value, state, attempts = future.result()
        run.results[node.name] = value
        run.states[node.name] = state
        run.attempts[node.name] = attempts
    except Exception as exc:
        run.states[node.name] = "failed"
        run.errors[node.name] = repr(exc)
        if fail_fast:
            raise
        run.results[node.name] = None


def _run_wave(
    active: list[DagNode],
    snapshot: dict[str, Any],
    cache: MutableMapping[str, Any] | None,
    run: DagExecution,
    max_workers: int,
    fail_fast: bool,
) -> None:
    """Execute one wave of ready nodes concurrently and record their results."""
    with ThreadPoolExecutor(
        max_workers=max(1, min(max_workers, len(active) or 1))
    ) as pool:
        futures = {
            pool.submit(_run_node, node, snapshot, cache): node for node in active
        }
        for future, node in futures.items():
            _record_result(node, future, run, fail_fast)


def execute_detailed(
    nodes, *, initial=None, cache=None, max_workers=4, fail_fast=True
) -> DagExecution:
    nodes = tuple(nodes)
    run = DagExecution(dict(initial or {}))
    pending = _validate_dag(nodes, run)
    while pending:
        ready = [n for n in pending.values() if set(n.depends_on) <= run.results.keys()]
        if not ready:
            raise ValueError("cyclic DAG dependency")
        snapshot = dict(run.results)
        active = _take_active(ready, pending, run, snapshot)
        _run_wave(active, snapshot, cache, run, max_workers, fail_fast)
    return run


def execute(nodes, **kwargs):
    return execute_detailed(nodes, **kwargs).results
