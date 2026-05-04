"""
Run retrieval-only evaluation on stress-test resumes.

Skips the GPT-4.1 generation step — only embeds, retrieves, and computes
skill recall. Free except for negligible Pinecone + Cohere usage (free tier).

Outputs results in the same format as ablation_raw.json so they can be
combined with existing data for skill recall analysis.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from backend.rag.retrieval import (
    dense_retrieve, bm25_retrieve, reciprocal_rank_fusion, load_bm25,
)
from backend.rag.reranker import rerank
from backend.rag.indexing import get_index
from backend.utils.pdf_parser import parse_resume

TEST_DIR = "backend/evaluation/test_resumes"
STRESS_NAMES = [
    "sparse_minimal", "sparse_grad",
    "vocab_abbreviated", "vocab_casual",
    "cross_bioinformatics", "cross_fintech",
    "niche_rust_blockchain", "niche_embedded",
]
OUT_FILE = "backend/evaluation/results/retrieval_stress.json"


def retrieve_for_condition(condition, resume_text, index, bm25, chunks, chunk_lookup):
    if condition == "no_rag":
        return []
    elif condition == "bm25_only":
        return bm25_retrieve(resume_text, bm25, chunks, k=30)
    elif condition == "dense_only":
        return dense_retrieve(resume_text, index, k=30)
    elif condition == "hybrid":
        d = dense_retrieve(resume_text, index, k=30)
        b = bm25_retrieve(resume_text, bm25, chunks, k=30)
        return reciprocal_rank_fusion(d, b)
    elif condition == "hybrid_rerank":
        d = dense_retrieve(resume_text, index, k=30)
        b = bm25_retrieve(resume_text, bm25, chunks, k=30)
        fused = reciprocal_rank_fusion(d, b)
        return rerank(resume_text, fused, chunk_lookup, top_k=15)
    return []


def main():
    print("Loading BM25 index...")
    bm25, chunks = load_bm25()
    chunk_lookup = {c["chunk_id"]: c["text"] for c in chunks}

    print("Connecting to Pinecone...")
    index = get_index()

    conditions = ["no_rag", "bm25_only", "dense_only", "hybrid", "hybrid_rerank"]
    results = []

    for resume_name in STRESS_NAMES:
        path = os.path.join(TEST_DIR, f"{resume_name}.pdf")
        if not os.path.exists(path):
            print(f"  Skipping {resume_name} — not found")
            continue

        with open(path, "rb") as f:
            resume_text = parse_resume(f.read())
        print(f"\n{resume_name} ({len(resume_text)} chars)")

        for cond in conditions:
            res = retrieve_for_condition(cond, resume_text, index, bm25, chunks, chunk_lookup)
            contexts = [chunk_lookup.get(r["chunk_id"], r.get("text", "")) for r in res]
            results.append({
                "resume_name": f"{resume_name}.pdf",
                "resume_text": resume_text,
                "retrieval_condition": cond,
                "prompting_condition": "n/a",  # no generation
                "contexts": contexts,
                "num_chunks_retrieved": len(contexts),
            })
            print(f"  {cond:<20} → {len(contexts)} chunks")

    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    with open(OUT_FILE, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved {len(results)} retrieval results to {OUT_FILE}")


if __name__ == "__main__":
    main()
