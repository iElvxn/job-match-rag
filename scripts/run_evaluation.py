"""
Master evaluation script for the Job Match RAG system.

Orchestrates the full evaluation pipeline:
  1. Run ablation study across all conditions
  2. Feed outputs into RAGAS evaluation
  3. Feed outputs into BERTScore evaluation
  4. Produce consolidated results tables

Usage:
    python scripts/run_evaluation.py --test-dir backend/evaluation/test_resumes
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

load_dotenv()

from backend.evaluation.ablation import run_ablation, RETRIEVAL_CONDITIONS, PROMPTING_CONDITIONS
from backend.evaluation.ragas_eval import run_ragas_eval, format_analysis_as_answer
from backend.evaluation.bertscore_eval import run_bertscore_eval, analysis_to_text

RESULTS_DIR = os.path.join("backend", "evaluation", "results")


def main(test_dir: str, reference_dir: str | None = None):
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # ---- Step 1: Ablation study ----
    print("=" * 60)
    print("STEP 1: Running ablation study")
    print("=" * 60)
    ablation_results = run_ablation(
        test_dir=test_dir,
        output_dir=RESULTS_DIR,
    )

    # Filter out errors
    valid = [r for r in ablation_results if "error" not in r]
    if not valid:
        print("No valid results — aborting evaluation.")
        return

    # ---- Step 2: RAGAS evaluation per condition ----
    print("\n" + "=" * 60)
    print("STEP 2: Running RAGAS evaluation")
    print("=" * 60)

    ragas_all = {}
    for ret_cond in RETRIEVAL_CONDITIONS:
        for prompt_cond in PROMPTING_CONDITIONS:
            condition_key = f"{ret_cond}_{prompt_cond}"
            subset = [r for r in valid
                      if r["retrieval_condition"] == ret_cond
                      and r["prompting_condition"] == prompt_cond
                      and r.get("contexts")]  # skip no_rag (no contexts)

            if not subset:
                print(f"  {condition_key}: skipped (no contexts or no results)")
                continue

            print(f"  {condition_key}: evaluating {len(subset)} samples...")
            records = [
                {
                    "question": r["resume_text"],
                    "answer": format_analysis_as_answer(r["analysis"]),
                    "contexts": r["contexts"],
                }
                for r in subset
            ]

            try:
                ragas_result = run_ragas_eval(
                    records,
                    output_path=os.path.join(RESULTS_DIR, f"ragas_{condition_key}.json"),
                )
                ragas_all[condition_key] = ragas_result["aggregate"]
            except Exception as e:
                print(f"    RAGAS failed for {condition_key}: {e}")

    # Save consolidated RAGAS results
    with open(os.path.join(RESULTS_DIR, "ragas_consolidated.json"), "w") as f:
        json.dump(ragas_all, f, indent=2)

    # ---- Step 3: BERTScore evaluation ----
    print("\n" + "=" * 60)
    print("STEP 3: Running BERTScore evaluation")
    print("=" * 60)

    # Use the hybrid_rerank + structured condition as reference
    ref_key = "hybrid_rerank_structured"
    ref_results = [r for r in valid
                   if r["retrieval_condition"] == "hybrid_rerank"
                   and r["prompting_condition"] == "structured"]

    if not ref_results:
        # Fallback to hybrid + structured
        ref_key = "hybrid_structured"
        ref_results = [r for r in valid
                       if r["retrieval_condition"] == "hybrid"
                       and r["prompting_condition"] == "structured"]

    if ref_results:
        # Build reference texts from the best condition
        ref_texts = {r["resume_name"]: analysis_to_text(r["analysis"]) for r in ref_results}

        bertscore_all = {}
        for ret_cond in RETRIEVAL_CONDITIONS:
            for prompt_cond in PROMPTING_CONDITIONS:
                condition_key = f"{ret_cond}_{prompt_cond}"
                if condition_key == ref_key:
                    continue  # skip self-comparison

                subset = [r for r in valid
                          if r["retrieval_condition"] == ret_cond
                          and r["prompting_condition"] == prompt_cond
                          and r["resume_name"] in ref_texts]

                if not subset:
                    continue

                candidates = [analysis_to_text(r["analysis"]) for r in subset]
                references = [ref_texts[r["resume_name"]] for r in subset]

                print(f"  {condition_key} vs {ref_key}: {len(candidates)} samples...")
                try:
                    bs_result = run_bertscore_eval(
                        candidates, references,
                        output_path=os.path.join(RESULTS_DIR, f"bertscore_{condition_key}.json"),
                    )
                    bertscore_all[condition_key] = bs_result["aggregate"]
                except Exception as e:
                    print(f"    BERTScore failed for {condition_key}: {e}")

        with open(os.path.join(RESULTS_DIR, "bertscore_consolidated.json"), "w") as f:
            json.dump(bertscore_all, f, indent=2)
    else:
        print("  No reference results available — skipping BERTScore.")

    # ---- Step 4: Print summary ----
    print("\n" + "=" * 60)
    print("EVALUATION COMPLETE")
    print("=" * 60)
    print(f"\nResults saved to: {RESULTS_DIR}/")
    print("\nRAGAS aggregate scores:")
    for cond, scores in ragas_all.items():
        print(f"  {cond}: {scores}")

    print(f"\nAll result files:")
    for fname in sorted(os.listdir(RESULTS_DIR)):
        fpath = os.path.join(RESULTS_DIR, fname)
        size = os.path.getsize(fpath)
        print(f"  {fname} ({size:,} bytes)")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run full evaluation pipeline")
    parser.add_argument("--test-dir", default="backend/evaluation/test_resumes",
                        help="Directory containing test resume PDFs")
    args = parser.parse_args()

    main(test_dir=args.test_dir)
