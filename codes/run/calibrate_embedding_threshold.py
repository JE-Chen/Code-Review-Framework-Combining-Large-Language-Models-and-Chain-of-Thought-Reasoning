"""Calibrate the RAG cosine threshold for a new embedding model.

The qwen3-era retriever used Qwen3-Embedding-4B (mean pooling, no prompt)
with threshold 0.7. When swapping to google/embeddinggemma-300m the score
distribution shifts, so 0.7 is no longer meaningful. This script embeds
the 19 rule docs and the 44 code_to_detect queries with BOTH models,
records which docs the old model retrieves at 0.7, then sweeps thresholds
for the new model and picks the one whose retrieved sets best match
(highest mean Jaccard overlap). Writes a markdown report.

Run inside the training image (CPU is fine, no GPU needed):
    docker run --rm -v <repo>:/workspace -v docker_hf-cache:/workspace/.hf_cache \
        -e PYTHONPATH=/workspace -w /workspace prthinker-gemma4-train \
        python codes/run/calibrate_embedding_threshold.py
"""

import datetime
import os
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer

from datas.RAG_data.rag_data import rule_docs

OLD_MODEL = "Qwen/Qwen3-Embedding-4B"
NEW_MODEL = os.environ.get("NEW_EMB_MODEL", "google/embeddinggemma-300m")
OLD_THRESHOLD = 0.7
DATA_ROOT = Path("/workspace/datas/code_to_detect")
REPORT_PATH = Path(
    os.environ.get(
        "REPORT_PATH", "/workspace/codes/run/embedding_threshold_calibration.md"
    )
)
MAX_LENGTH = 2048
SWEEP = np.arange(0.30, 0.96, 0.01)



def _log(*parts: object) -> None:
    print(datetime.datetime.now(), *parts, flush=True)


def _load(model_name: str):
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = AutoModel.from_pretrained(model_name, trust_remote_code=True)
    model.eval()
    return tokenizer, model


@torch.no_grad()
def _embed(tokenizer, model, text: str) -> np.ndarray:
    """Mean-pool + L2-normalize, mirroring codes/util/faiss_util.py."""
    inputs = tokenizer(
        text,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=MAX_LENGTH,
    )
    outputs = model(**inputs)
    mask = inputs["attention_mask"].unsqueeze(-1)
    pooled = (outputs.last_hidden_state * mask).sum(dim=1) / mask.sum(dim=1)
    emb = pooled[0].float().cpu().numpy().astype("float32")
    return emb / (np.linalg.norm(emb) + 1e-12)


def _collect_queries() -> list[tuple[str, str]]:
    cases = []
    for sub in ("bad_data", "code_diff", "only_code"):
        for src in ("ChatGPT", "Copilot"):
            directory = DATA_ROOT / sub / "Python" / src
            for f in sorted(directory.iterdir()):
                if f.is_file():
                    cases.append((f"{sub}/{src}/{f.name}", f.read_text("utf-8")))
    return cases


def _score_matrix(tokenizer, model, queries, docs, q_prefix="", d_prefix=""):
    doc_embs = np.stack([_embed(tokenizer, model, d_prefix + d) for d in docs])
    rows = []
    for name, text in queries:
        rows.append(doc_embs @ _embed(tokenizer, model, q_prefix + text))
        _log("embedded query", name)
    return np.stack(rows)  # [n_queries, n_docs] cosine scores


def _retrieved(scores: np.ndarray, threshold: float) -> list[set[int]]:
    return [set(np.flatnonzero(row >= threshold).tolist()) for row in scores]


def _pair_f1(old_sets: list[set[int]], new_sets: list[set[int]]) -> float:
    """Micro-F1 over (query, doc) retrieval pairs, old model as truth.

    Empty-vs-empty agreement contributes nothing, so "retrieve nothing"
    cannot win degenerately (most queries retrieve no rule at 0.7 with
    the old model — a naive Jaccard rewards always-empty with ~0.75).
    """
    tp = sum(len(a & b) for a, b in zip(old_sets, new_sets))
    fp = sum(len(b - a) for a, b in zip(old_sets, new_sets))
    fn = sum(len(a - b) for a, b in zip(old_sets, new_sets))
    if tp == 0:
        return 0.0
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    return 2 * precision * recall / (precision + recall)


def main() -> None:
    queries = _collect_queries()
    _log(len(queries), "queries,", len(rule_docs), "rule docs")

    cache = REPORT_PATH.with_suffix(".old-scores.npy")
    if cache.exists():
        _log("Reusing cached OLD-model scores from", cache)
        old_scores = np.load(cache)
    else:
        _log("Loading OLD model", OLD_MODEL)
        old_tok, old_model = _load(OLD_MODEL)
        old_scores = _score_matrix(old_tok, old_model, queries, rule_docs)
        del old_model
        np.save(cache, old_scores)
    old_sets = _retrieved(old_scores, OLD_THRESHOLD)

    # The new model goes through sentence-transformers, NOT bare AutoModel:
    # EmbeddingGemma's ST stack adds two Dense projections after pooling
    # plus the built-in query/document prompts, and production must use
    # the same path or this calibration is meaningless.
    from sentence_transformers import SentenceTransformer

    new_cache = REPORT_PATH.with_suffix(".new-scores.npy")
    if new_cache.exists():
        _log("Reusing cached NEW-model scores from", new_cache)
        new_scores = np.load(new_cache)
    else:
        _log("Loading NEW model", NEW_MODEL)
        st_model = SentenceTransformer(NEW_MODEL)
        doc_embs = st_model.encode_document(list(rule_docs))
        query_embs = st_model.encode_query([text for _, text in queries])
        new_scores = np.asarray(query_embs) @ np.asarray(doc_embs).T
        np.save(new_cache, new_scores)

    results = []
    for t in SWEEP:
        new_sets = _retrieved(new_scores, float(t))
        f1 = _pair_f1(old_sets, new_sets)
        avg_k = float(np.mean([len(s) for s in new_sets]))
        results.append((float(t), f1, avg_k))
    old_avg_k = float(np.mean([len(s) for s in old_sets]))
    # Best pair-F1; ties broken by retrieved-count closest to the old model.
    best = max(results, key=lambda r: (r[1], -abs(r[2] - old_avg_k)))

    rows = "\n".join(
        f"| {t:.2f} | {f:.3f} | {k:.1f} |" for t, f, k in results
    )
    REPORT_PATH.write_text(
        f"# Embedding threshold calibration — {datetime.date.today()}\n\n"
        f"Old: `{OLD_MODEL}` @ {OLD_THRESHOLD} (avg {old_avg_k:.1f} docs/query)\n"
        f"New: `{NEW_MODEL}`\n\n"
        f"## Recommended threshold: **{best[0]:.2f}** "
        f"(pair F1 {best[1]:.3f}, avg {best[2]:.1f} docs/query)\n\n"
        f"| threshold | pair F1 vs old | avg docs/query |\n"
        f"|:---:|:---:|:---:|\n{rows}\n\n"
        f"Old-model score range: [{old_scores.min():.3f}, {old_scores.max():.3f}] · "
        f"New-model score range: [{new_scores.min():.3f}, {new_scores.max():.3f}]\n",
        encoding="utf-8",
    )
    _log("Report written to", REPORT_PATH, "recommended threshold:", best[0])


if __name__ == "__main__":
    main()
