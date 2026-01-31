from codes.with_vector_database.utils.faiss_util import search_docs

def get_rag_docs(prompt: str, filter_by_threshold: bool = False, threshold: float = 0.7) -> dict:

    retrieved_docs, filtered_results = search_docs(
        query=prompt,
        filter_by_threshold=filter_by_threshold,
        threshold=threshold
    )
    return retrieved_docs