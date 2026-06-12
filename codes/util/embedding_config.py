"""Embedding-model defaults for the local FAISS RAG stack.

Pure configuration and routing logic — no ML imports — so the runner
test suite can cover threshold resolution without torch / faiss
installed. The heavy loading lives in ``codes.util.faiss_util``.
"""

import os

DEFAULT_EMB_MODEL = "google/embeddinggemma-300m"
LEGACY_QWEN_EMB_MODEL = "Qwen/Qwen3-Embedding-4B"

# Calibrated 2026-06-12 — see codes/run/embedding_threshold_calibration.md.
# 0.32 is the pair-F1-optimal match to the qwen-era retrieval sets at 0.7;
# EmbeddingGemma's cosine scores run much lower than Qwen3-Embedding-4B's
# (observed max 0.395 vs 0.761), so 0.7 retrieves nothing on the new model.
RECOMMENDED_THRESHOLDS = {
    DEFAULT_EMB_MODEL: 0.32,
    LEGACY_QWEN_EMB_MODEL: 0.7,
}
FALLBACK_THRESHOLD = 0.7


def active_emb_model() -> str:
    """Embedding model the local FAISS index loads (EMB_MODEL overrides)."""
    return os.environ.get("EMB_MODEL", DEFAULT_EMB_MODEL)


def uses_sentence_transformers(model_name: str) -> bool:
    """EmbeddingGemma must go through sentence-transformers.

    Its embedding stack appends two Dense projections and built-in
    query/document prompts after pooling; bare AutoModel mean pooling
    produces vectors from a different space.
    """
    return "embeddinggemma" in model_name.lower()


def recommended_threshold(model_name: str) -> float:
    """Calibrated cosine threshold for ``model_name``.

    Unknown models fall back to 0.7 — the historical default — rather
    than failing, so an experimental EMB_MODEL is usable before it has
    been calibrated.
    """
    return RECOMMENDED_THRESHOLDS.get(model_name, FALLBACK_THRESHOLD)
