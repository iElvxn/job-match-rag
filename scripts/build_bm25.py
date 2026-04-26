import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from backend.rag.chunking import chunk_all_jobs
from backend.rag.retrieval import build_bm25

if __name__ == "__main__":
    print("Loading dataset...")
    df = pd.read_csv("data/linkedin_jobs/postings.csv")
    print(f"  {len(df):,} jobs loaded")

    print("Chunking jobs...")
    chunks = chunk_all_jobs(df)
    print(f"  {len(chunks):,} chunks produced")

    print("Building BM25 index...")
    build_bm25(chunks)
    print("Saved to data/bm25_index.pkl")
