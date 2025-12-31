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

def search_docs(query: str, filter_by_threshold: bool = False, k: int = 15) -> tuple[list[Any], list[Any]] | tuple[list[Any], None]:
    # 先算出 embedding 的維度
    distance = get_embedding("test").shape[0]

    # 建立 CPU IndexFlatIP（內積）
    cpu_index = faiss.IndexFlatIP(distance)

    # 把 Index 搬到 GPU
    res = faiss.StandardGpuResources()  # 建立 GPU 資源
    gpu_index = faiss.index_cpu_to_gpu(res, 0, cpu_index)  # 0 代表使用第一張 GPU

    # 對每個文件算 embedding
    doc_embeddings = [get_embedding(d) for d in rule_docs]
    doc_embeddings = np.array(doc_embeddings).astype("float32")
    faiss.normalize_L2(doc_embeddings)  # 再次確保所有文件向量正規化
    gpu_index.add(doc_embeddings)

    q_emb = get_embedding(query).reshape(1, -1)
    faiss.normalize_L2(q_emb)

    # 搜尋前 K 筆（在 GPU 上）
    distance, indices = gpu_index.search(q_emb, k=k)

    if filter_by_threshold:
        # 相似度閾值
        threshold = 0.7
        filtered_results = []
        for index, score in zip(indices[0], distance[0]):
            if score >= threshold:  # 內積 = cosine，相似度越大越好
                filtered_results.append({"doc": rule_docs[indices], "score": score})

        retrieved_docs = [r["doc"] for r in filtered_results]
        return retrieved_docs, filtered_results
    else:
        retrieved_docs = []
        for index in indices[0]:
            retrieved_docs.append(rule_docs[index])
        return retrieved_docs, None