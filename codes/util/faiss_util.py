"""Local FAISS RAG index over the global rule documents.

The embedding model is selected by ``EMB_MODEL`` (default
``google/embeddinggemma-300m`` — see ``codes.util.embedding_config``).
EmbeddingGemma loads through sentence-transformers because its embedding
stack appends Dense projections and query/document prompts after pooling;
the legacy Qwen path keeps the original bare-AutoModel mean pooling so
``EMB_MODEL=Qwen/Qwen3-Embedding-4B`` reproduces the historical index
exactly (cosine threshold 0.7 era).
"""

import os
from typing import List, Tuple

import faiss
import numpy as np
import torch

from codes.util.embedding_config import (
    active_emb_model,
    recommended_threshold,
    uses_sentence_transformers,
)
from datas.RAG_data.rag_data import rule_docs

# =========================
# Env config
# =========================
USE_FAISS_GPU = os.getenv("USE_FAISS_GPU", "0") == "1"
TORCH_USE_CUDA = torch.cuda.is_available()

USE_GPU = USE_FAISS_GPU and TORCH_USE_CUDA

DEVICE = "cuda" if USE_GPU else "cpu"
MODEL_NAME = active_emb_model()
RECOMMENDED_THRESHOLD = recommended_threshold(MODEL_NAME)
MAX_LENGTH = 2048

print(f"[RAG] FAISS GPU = {USE_FAISS_GPU}, torch cuda = {TORCH_USE_CUDA}")
print(f"[RAG] Using device: {DEVICE}")
print(f"[RAG] Embedding model: {MODEL_NAME}")

# =========================
# Embedding backends
# =========================
if uses_sentence_transformers(MODEL_NAME):
    from sentence_transformers import SentenceTransformer

    _st_model = SentenceTransformer(MODEL_NAME, device=DEVICE)

    def get_embedding(text: str) -> np.ndarray:
        """Symmetric (document-space) embedding.

        Used by the learned-corpora stores (dismissed / accepted), which
        embed stored examples and incoming findings with the SAME
        function so both sides share one similarity space.
        """
        return _encode_documents([text])[0]

    def _encode_documents(texts: List[str]) -> np.ndarray:
        emb = _st_model.encode_document(list(texts))
        return np.asarray(emb, dtype="float32")

    def _encode_query(text: str) -> np.ndarray:
        emb = _st_model.encode_query([text])
        return np.asarray(emb, dtype="float32")[0]

else:
    from transformers import AutoModel, AutoTokenizer

    emb_tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME,
        trust_remote_code=True,
    )

    emb_model = AutoModel.from_pretrained(
        MODEL_NAME,
        trust_remote_code=True,
    ).to(DEVICE)
    emb_model.eval()

    @torch.no_grad()
    def get_embedding(text: str) -> np.ndarray:
        inputs = emb_tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=MAX_LENGTH,
        ).to(DEVICE)

        outputs = emb_model(**inputs)
        last_hidden = outputs.last_hidden_state
        attention_mask = inputs["attention_mask"].unsqueeze(-1)

        pooled = (last_hidden * attention_mask).sum(dim=1) / attention_mask.sum(dim=1)
        emb = pooled[0].float().cpu().numpy().astype("float32")

        # cosine similarity
        faiss.normalize_L2(emb.reshape(1, -1))
        return emb

    def _encode_documents(texts: List[str]) -> np.ndarray:
        return np.stack([get_embedding(t) for t in texts])

    def _encode_query(text: str) -> np.ndarray:
        return get_embedding(text)



# =========================
# Build FAISS index
# =========================
doc_embeddings = _encode_documents(list(rule_docs))
dim = doc_embeddings.shape[1]

cpu_index = faiss.IndexFlatIP(dim)

if USE_GPU:
    res = faiss.StandardGpuResources()
    index = faiss.index_cpu_to_gpu(res, 0, cpu_index)
else:
    index = cpu_index

index.add(doc_embeddings)

print(f"[RAG] FAISS index ready, total docs = {index.ntotal}")


# =========================
# Query
# =========================
def search_docs(
    query: str,
    k: int = 15,
    threshold: float | None = None
) -> Tuple[List[str], List[dict]]:
    q_emb = _encode_query(query).reshape(1, -1)

    scores, indices = index.search(q_emb, k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue
        if threshold is not None and score < threshold:
            continue

        results.append({
            "doc": rule_docs[idx],
            "score": float(score)
        })

    return [r["doc"] for r in results], results
