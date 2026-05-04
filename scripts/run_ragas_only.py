"""
Run RAGAS evaluation on existing ablation_raw.json without re-running ablation.
Uses gpt-4o-mini to keep costs low.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from backend.evaluation.ablation import RETRIEVAL_CONDITIONS, PROMPTING_CONDITIONS
from backend.evaluation.ragas_eval import run_ragas_eval, format_analysis_as_answer

RESULTS_DIR = os.path.join("backend", "evaluation", "results")
RAW_FILE = os.path.join(RESULTS_DIR, "ablation_raw.json")


def main():
    print(f"Loading ablation results from {RAW_FILE}...")
    with open(RAW_FILE) as f:
        data = json.load(f)

    valid = [r for r in data if "error" not in r]
    print(f"  {len(valid)} valid results loaded")

    ragas_all = {}

    for ret_cond in RETRIEVAL_CONDITIONS:
        for prompt_cond in PROMPTING_CONDITIONS:
            condition_key = f"{ret_cond}_{prompt_cond}"
            subset = [r for r in valid
                      if r["retrieval_condition"] == ret_cond
                      and r["prompting_condition"] == prompt_cond
                      and r.get("contexts")]

            if not subset:
                print(f"  {condition_key}: skipped (no_rag or no contexts)")
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
                result = run_ragas_eval(
                    records,
                    output_path=os.path.join(RESULTS_DIR, f"ragas_{condition_key}.json"),
                )
                ragas_all[condition_key] = result["aggregate"]
                print(f"    -> {result['aggregate']}")
            except Exception as e:
                print(f"    RAGAS failed for {condition_key}: {e}")

    out = os.path.join(RESULTS_DIR, "ragas_consolidated.json")
    with open(out, "w") as f:
        json.dump(ragas_all, f, indent=2)
    print(f"\nSaved to {out}")

    # Print summary table
    print("\n=== RAGAS Faithfulness by Retrieval Condition (structured prompting) ===")
    for ret in RETRIEVAL_CONDITIONS:
        key = f"{ret}_structured"
        scores = ragas_all.get(key, {})
        faith = scores.get("faithfulness", "N/A")
        cp = scores.get("context_precision", "N/A")
        print(f"  {ret:<20} faithfulness={faith}  context_precision={cp}")

    print("\n=== RAGAS Faithfulness by Prompting Strategy (hybrid_rerank) ===")
    for prompt in PROMPTING_CONDITIONS:
        key = f"hybrid_rerank_{prompt}"
        scores = ragas_all.get(key, {})
        faith = scores.get("faithfulness", "N/A")
        print(f"  {prompt:<15} faithfulness={faith}")


if __name__ == "__main__":
    main()
