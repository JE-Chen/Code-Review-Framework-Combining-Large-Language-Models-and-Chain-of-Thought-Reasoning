"""Versioned corpus selection for reproducible RAG experiments."""

from __future__ import annotations

import hashlib
import os

from datas.RAG_data.irrelevant_rules import irrelevant_rule_docs
from datas.RAG_data.rag_data import rule_docs as relevant_rule_docs

CORPORA: dict[str, tuple[str, ...]] = {
    "relevant": tuple(relevant_rule_docs),
    "irrelevant": tuple(irrelevant_rule_docs),
}


def active_corpus_name() -> str:
    name = os.environ.get("PRTHINKER_RAG_CORPUS", "relevant").strip().lower()
    if name not in CORPORA:
        choices = ", ".join(sorted(CORPORA))
        raise ValueError(f"Unknown PRTHINKER_RAG_CORPUS={name!r}; choose {choices}")
    return name


def active_rule_docs() -> tuple[str, ...]:
    return CORPORA[active_corpus_name()]


def corpus_digest(name: str | None = None) -> str:
    selected = active_corpus_name() if name is None else name
    payload = "\n\n---RULE---\n\n".join(CORPORA[selected]).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


if len(CORPORA["relevant"]) != len(CORPORA["irrelevant"]):
    raise RuntimeError("RAG negative-control corpus must match relevant corpus count")
