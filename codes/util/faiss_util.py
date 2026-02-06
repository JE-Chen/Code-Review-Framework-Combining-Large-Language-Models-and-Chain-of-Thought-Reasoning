import os
from typing import List, Tuple

import faiss
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel

from datas.RAG_data.rag_data import rule_docs

# =========================
# Env config
# =========================
USE_FAISS_GPU = os.getenv("USE_FAISS_GPU", "0") == "1"
TORCH_USE_CUDA = torch.cuda.is_available()

USE_GPU = USE_FAISS_GPU and TORCH_USE_CUDA

DEVICE = "cuda" if USE_GPU else "cpu"
MODEL_NAME = "Qwen/Qwen3-Embedding-4B"

print(f"[RAG] FAISS GPU = {USE_FAISS_GPU}, torch cuda = {TORCH_USE_CUDA}")
print(f"[RAG] Using device: {DEVICE}")

# =========================
# Load embedding model
# =========================
emb_tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True
)

emb_model = AutoModel.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True
).to(DEVICE)
emb_model.eval()

# =========================
# Embedding function
# =========================
@torch.no_grad()
def get_embedding(text: str) -> np.ndarray:
    inputs = emb_tokenizer(
        text,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=2048
    ).to(DEVICE)

    outputs = emb_model(**inputs)
    last_hidden = outputs.last_hidden_state
    attention_mask = inputs["attention_mask"].unsqueeze(-1)

    pooled = (last_hidden * attention_mask).sum(dim=1) / attention_mask.sum(dim=1)
    emb = pooled[0].float().cpu().numpy().astype("float32")

    # cosine similarity
    faiss.normalize_L2(emb.reshape(1, -1))
    return emb

# =========================
# Build FAISS index
# =========================
dim = get_embedding("test").shape[0]

cpu_index = faiss.IndexFlatIP(dim)

if USE_GPU:
    res = faiss.StandardGpuResources()
    index = faiss.index_cpu_to_gpu(res, 0, cpu_index)
else:
    index = cpu_index

# =========================
# Ingest documents
# =========================
doc_embeddings = np.stack([get_embedding(d) for d in rule_docs])
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
    q_emb = get_embedding(query).reshape(1, -1)

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
