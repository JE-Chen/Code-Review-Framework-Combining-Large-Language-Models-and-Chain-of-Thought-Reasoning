"""Shared request/response schemas for the FastAPI server and runner.

Pydantic v2 is required. Keeping these in the package (rather than on the
server side) so the runner can serialize requests with the same models the
server validates against — single source of truth for the wire format.
"""

from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, Field, model_validator

Severity = Literal["info", "warning", "error"]
# Descending display/gate order for the Severity ladder above; renderers
# and gates import this instead of re-declaring their own copy.
SEVERITY_ORDER: tuple[str, ...] = ("error", "warning", "info")


class AskRequest(BaseModel):
    prompt: str
    max_new_tokens: int = Field(default=32768, ge=1, le=32768)


class RagRequest(BaseModel):
    query: str
    threshold: float = 0.7
    k: int = 15


class RagResponse(BaseModel):
    docs: list[str]


class RetrievalEvalRequest(BaseModel):
    retrieved: list[str] = Field(default_factory=list)
    expected: list[str] = Field(default_factory=list)
    used: list[str] = Field(default_factory=list)
    cited_correct: list[bool] = Field(default_factory=list)


class RetrievalEvalResponse(BaseModel):
    recall: float
    precision: float
    utilization: float
    citation_correctness: float


class ReviewAttestationRequest(BaseModel):
    repository: str
    revision: str
    base_revision: str = ""
    policy_digest: str = ""
    review_digest: str


class StepOutput(BaseModel):
    name: str
    output: str


CitationKind = Literal["rag_rule", "accepted_example", "diff_evidence"]


class ProvenanceCitation(BaseModel):
    """One pointer to *why* the model raised a finding.

    Three kinds, matching the three sources the inline-findings prompt
    can expose:

    * ``rag_rule`` — an entry from the retrieved RAG rule list. ``index``
      is 1-based into the numbered ``Available RAG rules`` block.
    * ``accepted_example`` — a past comment + suggestion the author
      already accepted. ``index`` is 1-based into the ``Examples of
      past advice that was accepted`` block.
    * ``diff_evidence`` — line numbers in the new side of the diff that
      ground the finding. ``index`` is unused; the supporting lines go
      in ``lines``.

    ``note`` is a one-line rationale tying the citation to the finding
    (e.g. "matches rule on returning None in branching code").
    """

    kind: CitationKind
    index: int | None = Field(default=None, ge=1)
    lines: list[int] = Field(default_factory=list)
    note: str = ""


class Provenance(BaseModel):
    """Why the model thinks this finding is correct.

    Optional on every :class:`InlineFinding`. Empty when the user did
    not enable ``--provenance``. ``confidence`` is the model's own
    self-rated calibration in ``[0, 1]`` — surfaced for transparency,
    NEVER used to silently drop a finding (the project's safe-failure
    posture: drop nothing real on parse errors or low confidence).
    """

    citations: list[ProvenanceCitation] = Field(default_factory=list)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)


FindingCategory = Literal[
    "correctness",
    "security",
    "performance",
    "design",
    "test",
    "docs",
    "style",
    "other",
]


VerificationStatus = Literal["pass", "fail", "skip", "error"]

EvidenceStatus = Literal[
    "confirmed", "rejected", "inconclusive", "unsupported", "error"
]


class Evidence(BaseModel):
    """Reproducible evidence supporting or rejecting a finding."""

    kind: Literal["test", "static", "dynamic", "bounded", "repository", "retrieval"]
    status: EvidenceStatus
    tool: str
    tool_version: str = ""
    rule: str = ""
    command: list[str] = Field(default_factory=list)
    exit_code: int | None = None
    artifact_sha256: str = ""
    summary: str = ""
    finding_id: str = ""


class SuggestionVerification(BaseModel):
    """Outcome of running ``suggestion`` in a sandbox.

    Attached to an :class:`InlineFinding` when ``--verify-suggestions``
    is enabled. ``status`` distinguishes verify-cmd PASS / FAIL from
    "could not apply" (skip) and "verifier crashed" (error). The
    PR-comment formatter renders a small green / red / yellow badge
    next to the suggestion based on this.
    """

    status: VerificationStatus
    verify_cmd: str
    duration_ms: int = 0
    reason: str = ""


class InlineFinding(BaseModel):
    """A single line-level review remark, intended for an inline PR comment.

    `suggestion` (if set) is the full replacement text rendered into a
    GitHub ```suggestion``` block. When the replacement spans more than one
    line, `start_line` should point at the first affected line and `line`
    at the last; GitHub treats `(start_line, line]` as the replaced range.
    """

    path: str
    line: int = Field(ge=1)
    severity: Severity = "info"
    comment: str
    suggestion: str | None = None
    start_line: int | None = Field(default=None, ge=1)
    original: str | None = None
    provenance: Provenance | None = None
    verification: SuggestionVerification | None = None
    reproducibility: Literal["stable", "low"] | None = None
    # Optional thematic bucket (security / correctness / …) used only to
    # group findings in the summary. Backward-compatible: a model that
    # never emits it leaves the field None and the By-category index is
    # simply omitted.
    category: FindingCategory | None = None
    evidence: list[Evidence] = Field(default_factory=list)
    finding_id: str = ""

    @model_validator(mode="after")
    def ensure_finding_id(self):
        if not self.finding_id:
            normalized_path = self.path.replace("\\", "/")
            normalized_comment = " ".join(self.comment.lower().split())
            identity = f"{normalized_path}:{self.start_line or self.line}:{self.line}:{self.category or ''}:{normalized_comment}"
            self.finding_id = hashlib.sha256(identity.encode()).hexdigest()[:20]
        return self

    @property
    def is_multiline(self) -> bool:
        return self.start_line is not None and self.start_line != self.line


class ReviewRequest(BaseModel):
    code_diff: str
    file_path: str | None = None
    steps: list[str] | None = None
    rag_enabled: bool = True
    rag_threshold: float = 0.7
    max_new_tokens: int = Field(default=32768, ge=1, le=32768)
    extra_rules: list[str] = Field(default_factory=list)


JobStatus = Literal["pending", "running", "done", "error", "cancelled"]


class ReviewJobSubmitResponse(BaseModel):
    job_id: str


class ReviewJobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    result: "ReviewResponse | None" = None
    error: str | None = None


class AskJobSubmitResponse(BaseModel):
    job_id: str


class AskJobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    result: str | None = None
    error: str | None = None


Verdict = Literal["approve", "request_changes", "comment"]


class JudgeVerdict(BaseModel):
    """Per-file decision from the ``JudgeStep``.

    The CLI aggregates verdicts across files and maps the result to a
    GitHub review ``event``: any ``request_changes`` wins, otherwise all
    ``approve`` collapses to ``APPROVE``, otherwise ``COMMENT``.
    """

    verdict: Verdict = "comment"
    score: int = Field(ge=0, le=10)
    reasons: list[str] = Field(default_factory=list)


class DiffEntropySummary(BaseModel):
    """Diff-shape summary attached to the consolidated review.

    Surfaces in the PR comment header when ``--diff-entropy`` is on.
    The framework intentionally does not block on a high score; the
    point is to make the PR's shape visible to human reviewers.
    """

    file_count: int = 0
    added_lines: int = 0
    removed_lines: int = 0
    dispersion_entropy: float = 0.0
    score: float = 0.0
    verdict: str = "focused"


class PersonaReview(BaseModel):
    """One persona's raw review output.

    Stored verbatim — no parsing — so a future analysis can mine the
    per-persona text directly. The conflict-finder step works off
    these.
    """

    persona: str
    output: str


class PersonaConflict(BaseModel):
    """One cross-persona tension surfaced by the conflict step.

    ``personas`` lists the two-or-more lenses that disagree;
    ``resolution`` is the suggested framing for the human reviewer's
    decision — explicitly NOT a winner pick, since pick-a-winner would
    defeat the point of surfacing the tension.
    """

    personas: list[str]
    summary: str
    resolution: str = ""


class DependencyUpgradeFinding(BaseModel):
    """One finding from the dependency-upgrade impact step.

    Each entry corresponds to one (package, old, new) tuple. ``severity``
    follows the same ``info`` / ``warning`` / ``error`` ladder used in
    :class:`InlineFinding` so the gate can score it uniformly.
    """

    file_path: str
    package: str
    old_version: str
    new_version: str
    ecosystem: str = "unknown"
    severity: Severity = "info"
    summary: str
    evidence: str = ""


class CounterfactualOption(BaseModel):
    """One alternative implementation proposed by the counterfactual step.

    For each finding flagged as a non-trivial design choice, the model
    is asked to surface *competing* implementations — not just "fix X"
    but "you could do A, B, or C, and here is the trade-off matrix".

    Per ``paper_rule.md``'s no-fabrication rule, neither the prompt nor
    this schema makes any empirical claim about how often the proposed
    options are useful. The mechanism is a design contribution; its
    end-to-end utility is future-work.
    """

    label: str
    rationale: str
    tradeoffs: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Free-form axis-name → impact map, e.g. "
            "{'performance': 'O(n) vs O(n log n)', "
            "'readability': 'one-liner vs explicit loop'}."
        ),
    )


PRTypeLiteral = Literal[
    "bugfix",
    "feature",
    "refactor",
    "docs",
    "chore",
    "unknown",
]


class PRClassification(BaseModel):
    """The PR-type-classifier's output.

    Attached to :class:`ReviewResponse` when ``--pr-classify`` is set.
    ``reason`` is the model's one-sentence justification; it's surfaced
    in the PR comment header for transparency but never used to
    re-classify the PR.
    """

    pr_type: PRTypeLiteral = "unknown"
    reason: str = ""


ApiDriftKind = Literal[
    "field_renamed",
    "field_removed",
    "type_changed",
    "path_changed",
    "method_changed",
    "other",
]


class ApiDriftFinding(BaseModel):
    """One cross-language API drift finding.

    Produced by the cross-language consistency step when a PR touches
    both backend (Python) and frontend (TypeScript / JavaScript) files
    and the model flags that the two sides have diverged. Always cites
    *two* paths (one each side); per-file findings live in
    :class:`InlineFinding` instead.
    """

    backend_path: str
    frontend_path: str
    kind: ApiDriftKind = "other"
    summary: str
    evidence: str = ""


class CounterfactualBlock(BaseModel):
    """A finding + its competing alternative implementations."""

    finding_index: int = Field(
        ge=0,
        description=(
            "0-based index into the inline_findings array this block "
            "elaborates on. Out-of-range entries are dropped by the parser."
        ),
    )
    options: list[CounterfactualOption] = Field(default_factory=list)


class ReviewResponse(BaseModel):
    code_diff: str
    rag_docs: list[str]
    steps: list[StepOutput]
    inline_findings: list[InlineFinding] = Field(default_factory=list)
    verdict: JudgeVerdict | None = None
    counterfactuals: list[CounterfactualBlock] = Field(default_factory=list)
    api_drift: list[ApiDriftFinding] = Field(default_factory=list)
    pr_classification: PRClassification | None = None
    dep_upgrades: list[DependencyUpgradeFinding] = Field(default_factory=list)
    persona_reviews: list[PersonaReview] = Field(default_factory=list)
    persona_conflicts: list[PersonaConflict] = Field(default_factory=list)
    diff_entropy: DiffEntropySummary | None = None

    def step_map(self) -> dict[str, str]:
        return {s.name: s.output for s in self.steps}


ReviewJobStatusResponse.model_rebuild()


__all__ = [
    "ApiDriftFinding",
    "ApiDriftKind",
    "AskRequest",
    "CitationKind",
    "CounterfactualBlock",
    "CounterfactualOption",
    "DependencyUpgradeFinding",
    "DiffEntropySummary",
    "FindingCategory",
    "InlineFinding",
    "JudgeVerdict",
    "PRClassification",
    "PRTypeLiteral",
    "PersonaConflict",
    "PersonaReview",
    "Provenance",
    "ProvenanceCitation",
    "AskJobStatusResponse",
    "AskJobSubmitResponse",
    "JobStatus",
    "RagRequest",
    "RagResponse",
    "ReviewJobStatusResponse",
    "ReviewJobSubmitResponse",
    "ReviewRequest",
    "ReviewResponse",
    "Severity",
    "StepOutput",
    "SuggestionVerification",
    "Verdict",
    "VerificationStatus",
]
