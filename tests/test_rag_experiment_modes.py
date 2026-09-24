from __future__ import annotations

import pytest

from datas.RAG_data import corpora
from prthinker.rag import AllRulesRetriever


def test_negative_control_matches_relevant_document_count():
    assert len(corpora.CORPORA["irrelevant"]) == len(corpora.CORPORA["relevant"])
    assert len(corpora.CORPORA["relevant"]) == 19


def test_corpus_digest_is_stable_and_distinguishes_controls():
    relevant = corpora.corpus_digest("relevant")
    irrelevant = corpora.corpus_digest("irrelevant")
    assert len(relevant) == 64
    assert len(irrelevant) == 64
    assert relevant != irrelevant


def test_unknown_corpus_fails_closed(monkeypatch):
    monkeypatch.setenv("PRTHINKER_RAG_CORPUS", "typo")
    with pytest.raises(ValueError, match="Unknown PRTHINKER_RAG_CORPUS"):
        corpora.active_rule_docs()


def test_all_rules_retriever_uses_selected_corpus(monkeypatch):
    monkeypatch.setenv("PRTHINKER_RAG_CORPUS", "irrelevant")
    docs = AllRulesRetriever().retrieve("Python diff")
    assert docs == list(corpora.CORPORA["irrelevant"])
