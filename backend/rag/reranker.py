import os

import cohere
from dotenv import load_dotenv

load_dotenv()

co = cohere.Client(os.getenv("COHERE_API_KEY", ""))


def rerank(
    resume_text: str,
    results: list[dict],
    chunk_lookup: dict[str, str],
    top_k: int = 15,
) -> list[dict]:
    """
    Rerank retrieved chunks using Cohere Rerank API.

    Takes the top-30 hybrid-retrieved chunks and reranks them by relevance
    to the resume using a cross-encoder model. Returns the top_k most
    relevant chunks.

    Args:
        resume_text: raw resume text used as the query
        results: hybrid_retrieve output (list of dicts with chunk_id, score, metadata)
        chunk_lookup: mapping of chunk_id -> chunk text
        top_k: number of top results to return after reranking

    Returns:
        Reranked list of result dicts, trimmed to top_k, with updated scores.
    """
    if not results:
        return []

    # Build the documents list for Cohere — use chunk text as the document
    documents = []
    valid_results = []
    for r in results:
        text = chunk_lookup.get(r["chunk_id"], "")
        if text.strip():
            documents.append(text)
            valid_results.append(r)

    if not documents:
        return results[:top_k]

    response = co.rerank(
        model="rerank-v3.5",
        query=resume_text,
        documents=documents,
        top_n=min(top_k, len(documents)),
    )

    reranked = []
    for hit in response.results:
        original = valid_results[hit.index]
        reranked.append({
            "chunk_id": original["chunk_id"],
            "score": hit.relevance_score,
            "metadata": original["metadata"],
        })

    return reranked
