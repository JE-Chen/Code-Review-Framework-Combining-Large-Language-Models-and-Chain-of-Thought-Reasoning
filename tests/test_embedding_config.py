"""Tests for codes.util.embedding_config (pure config, no ML deps)."""

from codes.util.embedding_config import (
    DEFAULT_EMB_MODEL,
    FALLBACK_THRESHOLD,
    LEGACY_QWEN_EMB_MODEL,
    RECOMMENDED_THRESHOLDS,
    active_emb_model,
    recommended_threshold,
    uses_sentence_transformers,
)


class TestActiveEmbModel:
    def test_defaults_to_embeddinggemma(self, monkeypatch):
        monkeypatch.delenv("EMB_MODEL", raising=False)
        assert active_emb_model() == DEFAULT_EMB_MODEL

    def test_env_override_wins(self, monkeypatch):
        monkeypatch.setenv("EMB_MODEL", LEGACY_QWEN_EMB_MODEL)
        assert active_emb_model() == LEGACY_QWEN_EMB_MODEL

    def test_env_override_arbitrary_model(self, monkeypatch):
        monkeypatch.setenv("EMB_MODEL", "org/some-new-model")
        assert active_emb_model() == "org/some-new-model"


class TestUsesSentenceTransformers:
    def test_default_model_uses_st(self):
        assert uses_sentence_transformers(DEFAULT_EMB_MODEL) is True

    def test_case_insensitive(self):
        assert uses_sentence_transformers("Google/EmbeddingGemma-300M") is True

    def test_qwen_uses_legacy_path(self):
        assert uses_sentence_transformers(LEGACY_QWEN_EMB_MODEL) is False

    def test_empty_string(self):
        assert uses_sentence_transformers("") is False


class TestRecommendedThreshold:
    def test_embeddinggemma_calibrated_value(self):
        assert recommended_threshold(DEFAULT_EMB_MODEL) == 0.32

    def test_legacy_qwen_value(self):
        assert recommended_threshold(LEGACY_QWEN_EMB_MODEL) == 0.7

    def test_unknown_model_falls_back(self):
        assert recommended_threshold("org/uncalibrated") == FALLBACK_THRESHOLD

    def test_empty_model_name_falls_back(self):
        assert recommended_threshold("") == FALLBACK_THRESHOLD

    def test_all_thresholds_are_valid_cosine_cutoffs(self):
        for model, value in RECOMMENDED_THRESHOLDS.items():
            assert 0.0 < value < 1.0, model
