from typing import Any

import faiss
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel

from codes.with_vector_database.utils.rules import rule_docs

# 載入 Qwen 的 embedding 模型與 tokenizer
emb_model = AutoModel.from_pretrained("Qwen/Qwen3-Embedding-4B", trust_remote_code=True)
emb_tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-Embedding-4B", trust_remote_code=True)


def get_embedding(text: str) -> np.ndarray:
    inputs = emb_tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        emb = emb_model(**inputs).last_hidden_state.mean(dim=1)
    emb = emb[0].cpu().numpy().astype("float32")
    # L2 normalize，確保內積等於 cosine 相似度
    faiss.normalize_L2(emb.reshape(1, -1))
    return emb

# 初始化階段 (只做一次)
init_distance = get_embedding("test").shape[0]
cpu_index = faiss.IndexFlatIP(init_distance)
res = faiss.StandardGpuResources()
gpu_index = faiss.index_cpu_to_gpu(res, 0, cpu_index)

doc_embeddings = [get_embedding(d) for d in rule_docs]
doc_embeddings = np.array(doc_embeddings).astype("float32")
faiss.normalize_L2(doc_embeddings)
gpu_index.add(doc_embeddings)

# 查詢階段 (每次查詢只做這段)
def search_docs(query: str, filter_by_threshold: bool = False, threshold:float = 0.7, k: int = 15):
    q_emb = get_embedding(query).reshape(1, -1).astype("float32")
    faiss.normalize_L2(q_emb)
    distance, indices = gpu_index.search(q_emb, k=k)

    if filter_by_threshold:
        threshold = threshold
        filtered_results = [
            {"doc": rule_docs[idx], "score": score}
            for idx, score in zip(indices[0], distance[0]) if score >= threshold
        ]
        return [r["doc"] for r in filtered_results], filtered_results
    else:
        return [rule_docs[idx] for idx in indices[0]], None
