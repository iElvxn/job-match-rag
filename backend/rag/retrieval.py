import pickle
from collections import defaultdict

from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-mpnet-base-v2")


def build_bm25(chunks: list[dict]) -> None:
    """Build a BM25 index over all job chunks and save it to disk."""
    tokenized = [c["text"].lower().split() for c in chunks]
    bm25 = BM25Okapi(tokenized)
    with open("data/bm25_index.pkl", "wb") as f:
        pickle.dump({"bm25": bm25, "chunks": chunks}, f)


def load_bm25() -> tuple[BM25Okapi, list[dict]]:
    """Load the pre-built BM25 index from disk. Call once at server startup."""
    with open("data/bm25_index.pkl", "rb") as f:
        data = pickle.load(f)
    return data["bm25"], data["chunks"]


def dense_retrieve(resume_text: str, index, k: int = 30) -> list[dict]:
    """Encode resume as a vector and retrieve the top-k semantically similar job chunks from Pinecone."""
    vector = model.encode(resume_text).tolist()
    results = index.query(vector=vector, top_k=k, include_metadata=True)
    return [
        {"chunk_id": m.id, "score": m.score, "metadata": m.metadata}
        for m in results.matches
    ]


def bm25_retrieve(resume_text: str, bm25, chunks: list[dict], k: int = 30) -> list[dict]:
    """Retrieve the top-k job chunks by BM25 keyword score against the resume text."""
    tokens = resume_text.lower().split()
    scores = bm25.get_scores(tokens)
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
    return [
        {"chunk_id": chunks[i]["chunk_id"], "score": float(scores[i]), "metadata": chunks[i]["metadata"]}
        for i in top_indices
    ]


def reciprocal_rank_fusion(dense_results: list[dict], bm25_results: list[dict], k: int = 60) -> list[dict]:
    """
    Merge dense and BM25 ranked lists using Reciprocal Rank Fusion (RRF).

    Each result is scored as sum(1 / (rank + k)) across both lists. The k=60
    constant dampens the impact of high ranks so a #1 result in one list doesn't
    completely dominate.
    """
    scores: dict[str, float] = defaultdict(float)
    metadata_map: dict[str, dict] = {}

    for rank, result in enumerate(dense_results):
        cid = result["chunk_id"]
        scores[cid] += 1 / (rank + k)
        metadata_map[cid] = result["metadata"]

    for rank, result in enumerate(bm25_results):
        cid = result["chunk_id"]
        scores[cid] += 1 / (rank + k)
        metadata_map[cid] = result.get("metadata", metadata_map.get(cid, {}))

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [
        {"chunk_id": cid, "score": score, "metadata": metadata_map[cid]}
        for cid, score in ranked[:30]
    ]


def hybrid_retrieve(resume_text: str, index, bm25, chunks: list[dict], k: int = 30) -> list[dict]:
    """Run dense and BM25 retrieval concurrently, then fuse results with RRF."""
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=2) as pool:
        f_dense = pool.submit(dense_retrieve, resume_text, index, k)
        f_bm25  = pool.submit(bm25_retrieve, resume_text, bm25, chunks, k)
        dense_res, bm25_res = f_dense.result(), f_bm25.result()
    return reciprocal_rank_fusion(dense_res, bm25_res)
