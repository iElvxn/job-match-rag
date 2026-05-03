"""
Ablation study for the Job Match RAG system.

Runs the same set of test resumes through multiple retrieval and prompting
configurations, collects outputs, and feeds them into RAGAS and BERTScore
evaluators to produce the comparison tables for the report.

Retrieval conditions (5):
    1. no_rag        — LLM only, no retrieved context
    2. bm25_only     — BM25 keyword retrieval only
    3. dense_only    — Dense embedding retrieval only
    4. hybrid        — BM25 + Dense with RRF fusion
    5. hybrid_rerank — Hybrid + Cohere reranking (full pipeline)

Prompting conditions (3):
    1. zero_shot     — No skill matrix or market intel
    2. structured    — Pre-computed skill matrix + market intel
    3. few_shot      — Structured + worked example in prompt
"""

import json
import os
import sys
import time
from itertools import product

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from dotenv import load_dotenv

load_dotenv()

from backend.rag.retrieval import dense_retrieve, bm25_retrieve, reciprocal_rank_fusion, load_bm25
from backend.rag.reranker import rerank
from backend.rag.indexing import get_index
from backend.rag.skill_extractor import get_skill_gap, compute_market_intelligence
from backend.rag.generation import generate_analysis
from backend.utils.pdf_parser import parse_resume

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")

RETRIEVAL_CONDITIONS = ["no_rag", "bm25_only", "dense_only", "hybrid", "hybrid_rerank"]
PROMPTING_CONDITIONS = ["zero_shot", "structured", "few_shot"]


def _retrieve(condition: str, resume_text: str, index, bm25, chunks, chunk_lookup) -> list[dict]:
    """Run retrieval for a given condition. Returns empty list for no_rag."""
    if condition == "no_rag":
        return []
    elif condition == "bm25_only":
        return bm25_retrieve(resume_text, bm25, chunks, k=30)
    elif condition == "dense_only":
        return dense_retrieve(resume_text, index, k=30)
    elif condition == "hybrid":
        dense_res = dense_retrieve(resume_text, index, k=30)
        bm25_res = bm25_retrieve(resume_text, bm25, chunks, k=30)
        return reciprocal_rank_fusion(dense_res, bm25_res)
    elif condition == "hybrid_rerank":
        dense_res = dense_retrieve(resume_text, index, k=30)
        bm25_res = bm25_retrieve(resume_text, bm25, chunks, k=30)
        fused = reciprocal_rank_fusion(dense_res, bm25_res)
        return rerank(resume_text, fused, chunk_lookup, top_k=15)
    else:
        raise ValueError(f"Unknown retrieval condition: {condition}")


def run_single(
    resume_text: str,
    retrieval_cond: str,
    prompting_cond: str,
    index,
    bm25,
    chunks: list[dict],
    chunk_lookup: dict[str, str],
) -> dict:
    """
    Run the pipeline for one resume under one retrieval + prompting condition.

    Returns a dict with the raw analysis output, retrieval results,
    skill data, and timing info.
    """
    t0 = time.time()

    results = _retrieve(retrieval_cond, resume_text, index, bm25, chunks, chunk_lookup)

    if results:
        market_intel = compute_market_intelligence(results, chunk_lookup)
        skill_data = get_skill_gap(resume_text, results, chunk_lookup, market_intel)
    else:
        market_intel = None
        skill_data = {"resume_skills": [], "job_skills": [], "gaps": []}

    analysis = generate_analysis(
        resume_text, results, skill_data, chunk_lookup, market_intel,
        strategy=prompting_cond,
    )

    elapsed = time.time() - t0

    return {
        "retrieval_condition": retrieval_cond,
        "prompting_condition": prompting_cond,
        "analysis": analysis,
        "num_chunks_retrieved": len(results),
        "num_resume_skills": len(skill_data.get("resume_skills", [])),
        "num_skill_gaps": len(skill_data.get("gaps", [])),
        "contexts": [chunk_lookup.get(r["chunk_id"], "") for r in results],
        "elapsed_seconds": round(elapsed, 2),
    }


def load_test_resumes(test_dir: str) -> list[dict]:
    """
    Load test resume PDFs from a directory.

    Returns list of dicts with 'name' and 'text' keys.
    """
    resumes = []
    for fname in sorted(os.listdir(test_dir)):
        if not fname.lower().endswith(".pdf"):
            continue
        path = os.path.join(test_dir, fname)
        with open(path, "rb") as f:
            text = parse_resume(f.read())
        resumes.append({"name": fname, "text": text})
        print(f"  Loaded {fname} ({len(text)} chars)")
    return resumes


def run_ablation(
    test_dir: str,
    retrieval_conditions: list[str] | None = None,
    prompting_conditions: list[str] | None = None,
    output_dir: str | None = None,
) -> list[dict]:
    """
    Run the full ablation study across all condition combinations.

    Args:
        test_dir: directory containing test resume PDFs
        retrieval_conditions: list of retrieval conditions to test (defaults to all 5)
        prompting_conditions: list of prompting conditions to test (defaults to all 3)
        output_dir: directory to save per-condition results (defaults to RESULTS_DIR)

    Returns:
        List of result dicts, one per (resume, retrieval, prompting) combination.
    """
    ret_conds = retrieval_conditions or RETRIEVAL_CONDITIONS
    prompt_conds = prompting_conditions or PROMPTING_CONDITIONS
    output_dir = output_dir or RESULTS_DIR
    os.makedirs(output_dir, exist_ok=True)

    print("Loading BM25 index...")
    bm25, chunks = load_bm25()
    chunk_lookup = {c["chunk_id"]: c["text"] for c in chunks}

    print("Connecting to Pinecone...")
    index = get_index()

    print(f"Loading test resumes from {test_dir}...")
    resumes = load_test_resumes(test_dir)
    print(f"  {len(resumes)} resumes loaded")

    total = len(resumes) * len(ret_conds) * len(prompt_conds)
    print(f"\nRunning {total} evaluations ({len(resumes)} resumes × {len(ret_conds)} retrieval × {len(prompt_conds)} prompting)...\n")

    all_results = []
    for i, (resume, ret_cond, prompt_cond) in enumerate(
        product(resumes, ret_conds, prompt_conds), 1
    ):
        label = f"[{i}/{total}] {resume['name']} | {ret_cond} | {prompt_cond}"
        print(f"{label}...", end=" ", flush=True)

        try:
            result = run_single(
                resume["text"], ret_cond, prompt_cond,
                index, bm25, chunks, chunk_lookup,
            )
            result["resume_name"] = resume["name"]
            result["resume_text"] = resume["text"]
            all_results.append(result)
            print(f"done ({result['elapsed_seconds']}s)")
        except Exception as e:
            print(f"FAILED: {e}")
            all_results.append({
                "resume_name": resume["name"],
                "retrieval_condition": ret_cond,
                "prompting_condition": prompt_cond,
                "error": str(e),
            })

    # Save raw results
    raw_path = os.path.join(output_dir, "ablation_raw.json")
    with open(raw_path, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\nRaw results saved to {raw_path}")

    # Build summary table
    _save_summary(all_results, output_dir)

    return all_results


def _save_summary(results: list[dict], output_dir: str) -> None:
    """Aggregate timing and retrieval stats per condition and save as CSV."""
    import csv
    from collections import defaultdict

    stats = defaultdict(lambda: {"count": 0, "total_time": 0, "total_chunks": 0, "total_gaps": 0})

    for r in results:
        if "error" in r:
            continue
        key = f"{r['retrieval_condition']}_{r['prompting_condition']}"
        stats[key]["count"] += 1
        stats[key]["total_time"] += r.get("elapsed_seconds", 0)
        stats[key]["total_chunks"] += r.get("num_chunks_retrieved", 0)
        stats[key]["total_gaps"] += r.get("num_skill_gaps", 0)

    summary_path = os.path.join(output_dir, "ablation_summary.csv")
    with open(summary_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["condition", "n", "avg_time_s", "avg_chunks", "avg_gaps"])
        for key, s in sorted(stats.items()):
            n = s["count"]
            writer.writerow([
                key, n,
                round(s["total_time"] / n, 2),
                round(s["total_chunks"] / n, 1),
                round(s["total_gaps"] / n, 1),
            ])
    print(f"Summary saved to {summary_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run ablation study")
    parser.add_argument("--test-dir", default="backend/evaluation/test_resumes",
                        help="Directory containing test resume PDFs")
    parser.add_argument("--retrieval", nargs="*", default=None,
                        help="Retrieval conditions to test (default: all)")
    parser.add_argument("--prompting", nargs="*", default=None,
                        help="Prompting conditions to test (default: all)")
    parser.add_argument("--output-dir", default=None,
                        help="Output directory for results")
    args = parser.parse_args()

    run_ablation(
        test_dir=args.test_dir,
        retrieval_conditions=args.retrieval,
        prompting_conditions=args.prompting,
        output_dir=args.output_dir,
    )
