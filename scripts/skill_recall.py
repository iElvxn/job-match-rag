"""
Compute Skill Recall@K from existing ablation_raw.json.

Skill Recall measures retrieval quality: of all skills in the resume,
what percentage appear in the top-K retrieved job chunks?

Higher recall = retrieval found jobs that actually require what the resume offers.
This metric is deterministic, free, and directly answers "did we find relevant jobs?"
"""
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.rag.skill_extractor import extract_skills

RESULTS_FILE = "backend/evaluation/results/ablation_raw.json"
STRESS_FILE = "backend/evaluation/results/retrieval_stress.json"
OUT_FILE = "backend/evaluation/results/skill_recall.json"


def compute_skill_overlap(resume_text: str, contexts: list[str]) -> dict:
    """
    Compute skill recall, precision, F1 for one resume + retrieved chunks.

    Recall    = |resume_skills ∩ job_skills| / |resume_skills|
    Precision = |resume_skills ∩ job_skills| / |job_skills|
    F1        = harmonic mean
    """
    resume_skills = extract_skills(resume_text)
    if not resume_skills:
        return {"recall": 0.0, "precision": 0.0, "f1": 0.0,
                "n_resume_skills": 0, "n_job_skills": 0, "n_matched": 0}

    job_text = " ".join(contexts)
    job_skills = extract_skills(job_text)

    matched = resume_skills & job_skills
    recall = len(matched) / len(resume_skills) if resume_skills else 0.0
    precision = len(matched) / len(job_skills) if job_skills else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

    return {
        "recall": recall,
        "precision": precision,
        "f1": f1,
        "n_resume_skills": len(resume_skills),
        "n_job_skills": len(job_skills),
        "n_matched": len(matched),
    }


def main():
    print(f"Loading {RESULTS_FILE}...")
    with open(RESULTS_FILE) as f:
        data = json.load(f)
    print(f"  {len(data)} ablation results loaded")

    if os.path.exists(STRESS_FILE):
        with open(STRESS_FILE) as f:
            stress = json.load(f)
        data.extend(stress)
        print(f"  +{len(stress)} stress-test retrieval results loaded")

    print("Computing skill overlap for each result...")

    # Group by retrieval condition (skill recall is independent of prompting strategy
    # since prompting only affects the LLM output, not what was retrieved)
    by_retrieval = defaultdict(list)
    seen = set()
    for r in data:
        # Dedupe — same retrieval result regardless of prompting strategy
        key = (r["resume_name"], r["retrieval_condition"])
        if key in seen:
            continue
        seen.add(key)

        overlap = compute_skill_overlap(r["resume_text"], r["contexts"])
        overlap["resume_name"] = r["resume_name"]
        overlap["retrieval_condition"] = r["retrieval_condition"]
        by_retrieval[r["retrieval_condition"]].append(overlap)

    # Aggregate per condition
    print("\n" + "=" * 70)
    print("Skill Recall by Retrieval Condition (n=15 resumes per condition)")
    print("=" * 70)
    print(f"{'Condition':<18} {'Recall':>8} {'Precision':>11} {'F1':>8} {'AvgChunks':>12}")
    print("-" * 70)

    aggregate = {}
    order = ["no_rag", "bm25_only", "dense_only", "hybrid", "hybrid_rerank"]
    for cond in order:
        rows = by_retrieval.get(cond, [])
        if not rows:
            continue
        n = len(rows)
        avg_recall = sum(r["recall"] for r in rows) / n
        avg_prec = sum(r["precision"] for r in rows) / n
        avg_f1 = sum(r["f1"] for r in rows) / n
        avg_jobskills = sum(r["n_job_skills"] for r in rows) / n
        aggregate[cond] = {
            "n": n,
            "avg_recall": round(avg_recall, 4),
            "avg_precision": round(avg_prec, 4),
            "avg_f1": round(avg_f1, 4),
            "avg_n_job_skills": round(avg_jobskills, 1),
        }
        print(f"{cond:<18} {avg_recall:>8.3f} {avg_prec:>11.3f} {avg_f1:>8.3f} {avg_jobskills:>12.1f}")

    # Per-resume breakdown for stress-test resumes
    print("\n" + "=" * 70)
    print("Stress-test resumes — recall across conditions")
    print("=" * 70)
    print(f"{'Resume':<28} {'BM25':>7} {'Dense':>7} {'Hyb':>7} {'H+Rrnk':>8}")
    print("-" * 70)
    stress_keywords = ["sparse", "vocab", "cross", "niche"]
    bm25_by = {r["resume_name"]: r["recall"] for r in by_retrieval.get("bm25_only", [])}
    dense_by = {r["resume_name"]: r["recall"] for r in by_retrieval.get("dense_only", [])}
    hyb_by = {r["resume_name"]: r["recall"] for r in by_retrieval.get("hybrid", [])}
    rer_by = {r["resume_name"]: r["recall"] for r in by_retrieval.get("hybrid_rerank", [])}
    for resume in sorted(bm25_by):
        if not any(k in resume for k in stress_keywords):
            continue
        b, d, h, r = bm25_by[resume], dense_by.get(resume, 0), hyb_by.get(resume, 0), rer_by.get(resume, 0)
        print(f"{resume:<28} {b:>7.3f} {d:>7.3f} {h:>7.3f} {r:>8.3f}")

    # Aggregate just over stress resumes
    print("\n" + "=" * 70)
    print("Stress-test resumes only — aggregate")
    print("=" * 70)
    print(f"{'Condition':<18} {'Recall':>8} {'Precision':>11} {'F1':>8}")
    print("-" * 70)
    for cond in order:
        rows = [r for r in by_retrieval.get(cond, [])
                if any(k in r["resume_name"] for k in stress_keywords)]
        if not rows:
            continue
        n = len(rows)
        avg_r = sum(r["recall"] for r in rows) / n
        avg_p = sum(r["precision"] for r in rows) / n
        avg_f = sum(r["f1"] for r in rows) / n
        print(f"{cond:<18} {avg_r:>8.3f} {avg_p:>11.3f} {avg_f:>8.3f}")

    # Save
    output = {
        "aggregate": aggregate,
        "per_sample": {cond: rows for cond, rows in by_retrieval.items()},
    }
    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    with open(OUT_FILE, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved to {OUT_FILE}")


if __name__ == "__main__":
    main()
