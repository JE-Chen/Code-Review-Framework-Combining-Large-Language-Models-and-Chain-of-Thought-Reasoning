from codes.util.faiss_util import search_docs

def get_rag_docs(prompt: str, threshold: float = 0.7) -> list[str]:

    retrieved_docs, filtered_results = search_docs(
        query=prompt,
        threshold=threshold
    )
    return retrieved_docs