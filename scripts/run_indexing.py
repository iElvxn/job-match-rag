import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv

from backend.rag.chunking import chunk_all_jobs
from backend.rag.indexing import get_index, upsert_chunks, BATCH_SIZE_EMBED

load_dotenv()

CHECKPOINT_FILE = "data/indexing_checkpoint.json"

INCLUDE_KEYWORDS = [
    'software engineer', 'software developer', 'software architect',
    'backend engineer', 'frontend engineer', 'full stack', 'fullstack',
    'data engineer', 'data scientist', 'machine learning', 'ml engineer',
    'ai engineer', 'devops', 'platform engineer', 'site reliability',
    'cloud engineer', 'infrastructure engineer', 'security engineer',
    'network engineer', 'systems engineer', 'database engineer',
    'database administrator', 'data analyst', 'mobile engineer',
    'ios engineer', 'android engineer', 'python developer', 'java developer',
    'web developer', 'engineering manager', 'tech lead', 'research engineer',
    'computer vision', 'nlp engineer', 'applied scientist', 'qa engineer',
    'firmware engineer', 'embedded engineer', 'solutions architect',
]

EXCLUDE_KEYWORDS = [
    'mechanical', 'civil', 'electrical', 'chemical', 'structural',
    'manufacturing', 'industrial', 'environmental', 'aerospace',
    'hvac', 'plumbing', 'construction', 'financial', 'behavior analyst',
]


def prioritize_tech(df: pd.DataFrame) -> pd.DataFrame:
    """Sort tech jobs first, all others after. Ensures best coverage if run is interrupted."""
    title = df["title"].str.lower().fillna("")
    is_tech = title.str.contains("|".join(INCLUDE_KEYWORDS), na=False) & \
              ~title.str.contains("|".join(EXCLUDE_KEYWORDS), na=False)
    tech = df[is_tech]
    rest = df[~is_tech]
    return pd.concat([tech, rest], ignore_index=True)


def load_checkpoint() -> int:
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE) as f:
            return json.load(f).get("last_batch", 0)
    return 0


def save_checkpoint(batch_idx: int) -> None:
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump({"last_batch": batch_idx}, f)


def main(max_jobs: int | None = None):
    print("Loading dataset...")
    df = pd.read_csv("data/linkedin_jobs/postings.csv")
    print(f"  {len(df):,} total jobs")

    print("Prioritizing tech jobs...")
    df = prioritize_tech(df)

    if max_jobs:
        df = df.head(max_jobs)
        print(f"  Capped to {len(df):,} jobs (--max-jobs {max_jobs})")

    print("Chunking jobs...")
    chunks = chunk_all_jobs(df)
    print(f"  {len(chunks):,} chunks produced")

    print("Connecting to Pinecone...")
    index = get_index()

    start_batch = load_checkpoint()
    if start_batch > 0:
        print(f"Resuming from batch {start_batch}...")

    batches = range(0, len(chunks), BATCH_SIZE_EMBED)
    print("Embedding and uploading...")
    for i in tqdm(batches, initial=start_batch, total=len(batches)):
        if i < start_batch:
            continue
        batch = chunks[i : i + BATCH_SIZE_EMBED]
        upsert_chunks(batch, index)
        save_checkpoint(i + BATCH_SIZE_EMBED)

    os.remove(CHECKPOINT_FILE)
    stats = index.describe_index_stats()
    print(f"\nDone. Vectors in index: {stats.total_vector_count:,}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-jobs", type=int, default=None,
                        help="Cap number of jobs to index (default: all)")
    args = parser.parse_args()
    main(max_jobs=args.max_jobs)
