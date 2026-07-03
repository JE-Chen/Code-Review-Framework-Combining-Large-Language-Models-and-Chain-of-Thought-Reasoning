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


def _run_node(
    node: DagNode, snapshot: dict[str, Any], cache: MutableMapping[str, Any] | None
):
    key = node.cache_key(snapshot) if node.cache_key else ""
    if key and cache is not None and key in cache:
        return cache[key], "cached", 1
    last = None
    for attempt in range(1, node.retries + 2):
        try:
            pool = ThreadPoolExecutor(max_workers=1)
            future = pool.submit(node.run, snapshot)
            try:
                value = future.result(timeout=node.timeout_seconds)
            finally:
                pool.shutdown(wait=False, cancel_futures=True)
            if key and cache is not None:
                cache[key] = value
            return value, "completed", attempt
        except TimeoutError:
            last = TimeoutError(f"node {node.name} timed out")
        except Exception as exc:
            last = exc
    raise last  # type: ignore[misc]


def execute_detailed(
    nodes, *, initial=None, cache=None, max_workers=4, fail_fast=True
) -> DagExecution:
    nodes = tuple(nodes)
    pending = {n.name: n for n in nodes}
    run = DagExecution(dict(initial or {}))
    if len(pending) != len(nodes):
        raise ValueError("duplicate DAG node")
    all_names = set(pending) | run.results.keys()
    missing = {d for n in nodes for d in n.depends_on if d not in all_names}
    if missing:
        raise ValueError(f"missing DAG dependencies: {sorted(missing)}")
    while pending:
        ready = [n for n in pending.values() if set(n.depends_on) <= run.results.keys()]
        if not ready:
            raise ValueError("cyclic DAG dependency")
        snapshot = dict(run.results)
        active = []
        for node in ready:
            pending.pop(node.name)
            if node.when is not None and not node.when(snapshot):
                run.results[node.name] = None
                run.states[node.name] = "skipped"
            else:
                active.append(node)
        with ThreadPoolExecutor(
            max_workers=max(1, min(max_workers, len(active) or 1))
        ) as pool:
            futures = {
                pool.submit(_run_node, node, snapshot, cache): node for node in active
            }
            for future, node in futures.items():
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
    return run


def execute(nodes, **kwargs):
    return execute_detailed(nodes, **kwargs).results
