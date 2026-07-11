"""Hypothesis-verification localisation — propose, statically verify, iterate.

Upgrades "retrieve more context each round" (the iterative retriever) to a
model-in-the-loop propose-and-verify loop: each round the backend proposes
specific suspect locations (path / symbol / line) as testable hypotheses,
every hypothesis is verified statically against the work-tree (path
existence, symbol definition with its real line span, import-graph
callers/dependents as supporting evidence), and the verdicts are fed back
verbatim so the next round can correct refuted guesses. Confirmed locations
accumulate and rank ahead of the base retrieval; a malformed or empty round
fails open to the base results.

Runner-safe: stdlib + the injected backend.
"""

from __future__ import annotations

import ast
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

from prthinker.findings import extract_lenient_json
from prthinker.prompts.localization_hypothesis import (
    LOCALIZATION_HYPOTHESIS_TEMPLATE,
)
from prthinker.repo_graph import build_import_adjacency
from prthinker.repo_retrieval import (
    RepoContext,
    RepoContextRetriever,
    _Backend,
    _rerank_snippet,
)

log = logging.getLogger(__name__)

_JSON_OBJECT_RE = re.compile(r"\{[\s\S]*\}")
_DEFAULT_MAX_ROUNDS = 3
_DEFAULT_MAX_HYPOTHESES = 5
_DEFAULT_MAX_NEW_TOKENS = 2048
_MAX_NEIGHBOUR_EVIDENCE = 5
_NO_FEEDBACK_TEXT = "None yet — this is the first round."
_NO_CANDIDATES_TEXT = "(no candidates retrieved)"

# Keyword-introduced definitions across the non-Python languages in scope.
_DEF_KEYWORDS = r"def|class|function|func|fn|interface|struct|trait|enum"


@dataclass(frozen=True)
class Hypothesis:
    """One proposed suspect location from a hypothesis round."""

    path: str
    symbol: str = ""
    line: int | None = None
    reason: str = ""
    confidence: float = 0.0


@dataclass(frozen=True)
class Verification:
    """The static verdict on one hypothesis, with the feedback line for the model."""

    path: str
    symbol: str
    confirmed: bool
    feedback: str
    span: tuple[int, int] | None = None


def _coerce_hypothesis(item: object) -> Hypothesis | None:
    """Build a :class:`Hypothesis` from one JSON item, or None when malformed."""
    if not isinstance(item, dict) or not str(item.get("path", "") or "").strip():
        return None
    line = item.get("line")
    try:
        confidence = float(item.get("confidence", 0.0))
    except (TypeError, ValueError):
        confidence = 0.0
    return Hypothesis(
        path=str(item["path"]).strip(),
        symbol=str(item.get("symbol", "") or "").strip(),
        line=line if isinstance(line, int) else None,
        reason=str(item.get("reason", "") or "").strip(),
        confidence=confidence,
    )


def parse_hypothesis_round(
    raw: str, max_hypotheses: int
) -> tuple[list[Hypothesis], bool] | None:
    """Parse one round's JSON payload; None when the output is malformed."""
    parsed = extract_lenient_json(raw, pattern=_JSON_OBJECT_RE)
    if not isinstance(parsed.data, dict):
        return None
    items = parsed.data.get("hypotheses", [])
    if not isinstance(items, list):
        return None
    hypotheses = [hyp for hyp in map(_coerce_hypothesis, items) if hyp is not None]
    return hypotheses[:max_hypotheses], bool(parsed.data.get("done", False))


def _safe_relpath(raw_path: str) -> str | None:
    """Normalise a proposed path to a safe workdir-relative form, else None.

    Rejects absolute paths, drive-qualified paths and ``..`` traversal so a
    model hypothesis can never escape the work-tree.
    """
    rel = raw_path.strip().replace("\\", "/")
    if not rel or rel.startswith("/"):
        return None
    candidate = Path(rel)
    if candidate.is_absolute() or candidate.drive or ".." in candidate.parts:
        return None
    return candidate.as_posix()


def _ast_symbol_span(text: str, symbol: str) -> tuple[int, int] | None:
    """Line span of a def/class named ``symbol`` via the Python AST, else None."""
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return None
    definitions = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
    for node in ast.walk(tree):
        if isinstance(node, definitions) and node.name == symbol:
            return node.lineno, node.end_lineno or node.lineno
    return None


def _regex_symbol_span(text: str, symbol: str) -> tuple[int, int] | None:
    """Line of a keyword-introduced definition of ``symbol`` (regex fallback)."""
    pattern = re.compile(rf"\b(?:{_DEF_KEYWORDS})\s+{re.escape(symbol)}\b")
    for lineno, line in enumerate(text.splitlines(), 1):
        if pattern.search(line):
            return lineno, lineno
    return None


def find_symbol_span(
    text: str, symbol: str, *, is_python: bool
) -> tuple[int, int] | None:
    """Verified line span of ``symbol``'s definition in ``text``, else None."""
    if is_python:
        span = _ast_symbol_span(text, symbol)
        if span is not None:
            return span
    return _regex_symbol_span(text, symbol)


def verify_hypothesis(workdir: Path, hypothesis: Hypothesis) -> Verification:
    """Statically verify one hypothesis against the work-tree."""
    rel = _safe_relpath(hypothesis.path)
    if rel is None or not (workdir / rel).is_file():
        feedback = f"REFUTED {hypothesis.path}: path does not exist"
        return Verification(hypothesis.path, hypothesis.symbol, False, feedback)
    if not hypothesis.symbol:
        return Verification(rel, "", True, f"CONFIRMED {rel}: path exists")
    try:
        text = (workdir / rel).read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return Verification(rel, hypothesis.symbol, False, f"REFUTED {rel}: file unreadable")
    span = find_symbol_span(text, hypothesis.symbol, is_python=rel.endswith(".py"))
    if span is None:
        feedback = f"REFUTED {rel}: symbol '{hypothesis.symbol}' not found in this file"
        return Verification(rel, hypothesis.symbol, False, feedback)
    feedback = (
        f"CONFIRMED {rel}: symbol '{hypothesis.symbol}' defined at "
        f"lines {span[0]}-{span[1]}"
    )
    return Verification(rel, hypothesis.symbol, True, feedback, span)


@dataclass
class _LoopState:
    """Accumulated candidates, verdicts and feedback across the rounds."""

    candidates: list[str]
    confirmed: dict[tuple[str, str], Verification] = field(default_factory=dict)
    feedback: list[str] = field(default_factory=list)
    seen: set[tuple[str, str]] = field(default_factory=set)


@dataclass(frozen=True)
class _RoundOutcome:
    """Whether a round produced new information and whether the model is done."""

    progressed: bool
    done: bool


def _assemble_context(base: RepoContext, confirmed: list[Verification]) -> RepoContext:
    """Rank confirmed files first; verified spans/symbols override base data."""
    confirmed_files = list(dict.fromkeys(verdict.path for verdict in confirmed))
    known = set(confirmed_files)
    files = confirmed_files + [rel for rel in base.files if rel not in known]
    spans: dict[str, list[tuple[int, int]]] = {}
    symbols: dict[str, list[str]] = {}
    for verdict in confirmed:
        if verdict.symbol:
            symbols.setdefault(verdict.path, []).append(verdict.symbol)
        if verdict.span:
            spans.setdefault(verdict.path, []).append(verdict.span)
    for rel in files:
        spans.setdefault(rel, list(base.spans.get(rel, [])))
        symbols.setdefault(rel, list(base.symbols.get(rel, [])))
    return RepoContext(tuple(files), spans, symbols)


class HypothesisRetriever(RepoContextRetriever):
    """Model-in-the-loop hypothesis-verification localisation.

    Each round the backend proposes suspect locations from the candidate
    pool; every hypothesis is verified statically (path existence, symbol
    definition + line span, import-graph callers/dependents as evidence),
    refutations are fed back verbatim so the next round can correct course,
    and confirmed locations accumulate (deduped by path + symbol).
    Iteration stops on ``done``, the round budget, or a round contributing
    no new information; with nothing confirmed the base retrieval is
    returned untouched (fail-open).
    """

    def __init__(
        self,
        backend: _Backend,
        base_retriever: RepoContextRetriever,
        *,
        max_rounds: int = _DEFAULT_MAX_ROUNDS,
        max_hypotheses: int = _DEFAULT_MAX_HYPOTHESES,
        max_new_tokens: int = _DEFAULT_MAX_NEW_TOKENS,
    ) -> None:
        self._backend = backend
        self._base = base_retriever
        self._max_rounds = max(1, max_rounds)
        self._max_hypotheses = max(1, max_hypotheses)
        self._max_new_tokens = max_new_tokens
        # Adjacency memo keyed by workdir: building the import graph reads
        # the whole work-tree, so it is computed once per retriever lifetime.
        self._adjacency_cache: dict[Path, dict[str, set[str]]] = {}

    def retrieve(self, query: str, workdir: Path) -> RepoContext:
        """Run up to ``max_rounds`` propose-verify rounds over the base seeds."""
        workdir = Path(workdir)
        base = self._base.retrieve(query, workdir)
        state = _LoopState(candidates=list(base.files))
        for _ in range(self._max_rounds):
            outcome = self._run_round(query, workdir, base, state)
            if outcome.done or not outcome.progressed:
                break
        return _assemble_context(base, list(state.confirmed.values()))

    def _run_round(
        self, query: str, workdir: Path, base: RepoContext, state: _LoopState
    ) -> _RoundOutcome:
        """Generate one hypothesis round and verify everything it proposed."""
        prompt = self._round_prompt(query, workdir, base, state)
        raw = self._backend.generate(prompt, self._max_new_tokens)
        parsed = parse_hypothesis_round(raw, self._max_hypotheses)
        if parsed is None:
            log.warning(
                "Hypothesis round returned malformed JSON; treating as empty round"
            )
            return _RoundOutcome(progressed=False, done=False)
        hypotheses, done = parsed
        progressed = False
        for hypothesis in hypotheses:
            if self._absorb(workdir, hypothesis, state):
                progressed = True
        return _RoundOutcome(progressed=progressed, done=done)

    def _absorb(self, workdir: Path, hypothesis: Hypothesis, state: _LoopState) -> bool:
        """Verify one unseen hypothesis; True when the round gained information.

        A repeat of an already-verified hypothesis (confirmed or refuted) is
        skipped and contributes no progress, so a round that only re-proposes
        old guesses ends the iteration.
        """
        key = (hypothesis.path, hypothesis.symbol)
        if key in state.seen:
            return False
        state.seen.add(key)
        verdict = verify_hypothesis(workdir, hypothesis)
        state.feedback.append(verdict.feedback)
        if verdict.confirmed and (verdict.path, verdict.symbol) not in state.confirmed:
            state.confirmed[(verdict.path, verdict.symbol)] = verdict
            self._add_neighbour_evidence(workdir, verdict.path, state)
        return True

    def _add_neighbour_evidence(
        self, workdir: Path, rel: str, state: _LoopState
    ) -> None:
        """Feed a confirmed file's import-graph callers/dependents forward."""
        neighbours = sorted(self._adjacency(workdir).get(rel, set()))
        neighbours = neighbours[:_MAX_NEIGHBOUR_EVIDENCE]
        if not neighbours:
            return
        state.feedback.append(
            f"EVIDENCE {rel}: import-graph callers/dependents: "
            + ", ".join(neighbours)
        )
        state.candidates.extend(
            neighbour for neighbour in neighbours if neighbour not in state.candidates
        )

    def _adjacency(self, workdir: Path) -> dict[str, set[str]]:
        """Bidirectional import adjacency for ``workdir``, built once and memoized."""
        key = workdir.resolve()
        cached = self._adjacency_cache.get(key)
        if cached is None:
            cached = build_import_adjacency(workdir)
            self._adjacency_cache[key] = cached
        return cached

    def _round_prompt(
        self, query: str, workdir: Path, base: RepoContext, state: _LoopState
    ) -> str:
        """Assemble the round prompt: issue, candidate excerpts, prior verdicts."""
        blocks = [
            f"- {rel}\n{_rerank_snippet(workdir, rel, base.spans.get(rel, []))}"
            for rel in state.candidates
        ]
        feedback = "\n".join(state.feedback) if state.feedback else _NO_FEEDBACK_TEXT
        return LOCALIZATION_HYPOTHESIS_TEMPLATE.format(
            issue_text=query,
            candidate_files="\n".join(blocks) or _NO_CANDIDATES_TEXT,
            verification_feedback=feedback,
            max_hypotheses=self._max_hypotheses,
        )


def create_hypothesis_retriever(
    backend: _Backend, base: RepoContextRetriever, **knobs
) -> HypothesisRetriever:
    """Factory: hypothesis-verification retriever for the coordinator to wire."""
    return HypothesisRetriever(backend, base, **knobs)
