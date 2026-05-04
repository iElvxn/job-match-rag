"""
Run BERTScore on existing ablation results, using hybrid_rerank+structured
output as the reference (best system) and comparing all other conditions
against it.

Free, local, no API calls.
"""
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.evaluation.bertscore_eval import run_bertscore_eval, analysis_to_text

RAW_FILE = "backend/evaluation/results/ablation_raw.json"
OUT_FILE = "backend/evaluation/results/bertscore_consolidated.json"
REF_RETRIEVAL = "hybrid_rerank"
REF_PROMPTING = "structured"


def main():
    print(f"Loading {RAW_FILE}...")
    with open(RAW_FILE) as f:
        data = json.load(f)
    print(f"  {len(data)} ablation results loaded")

    # Build reference: hybrid_rerank + structured per resume
    refs = {
        r["resume_name"]: analysis_to_text(r["analysis"])
        for r in data
        if r["retrieval_condition"] == REF_RETRIEVAL
        and r["prompting_condition"] == REF_PROMPTING
    }
    print(f"  {len(refs)} reference outputs (using {REF_RETRIEVAL}+{REF_PROMPTING})")

    # Group results by condition
    by_cond = defaultdict(list)
    for r in data:
        key = f"{r['retrieval_condition']}_{r['prompting_condition']}"
        by_cond[key].append(r)

    # Compute BERTScore for each condition vs reference
    aggregate = {}
    ref_key = f"{REF_RETRIEVAL}_{REF_PROMPTING}"

    for cond_key in sorted(by_cond):
        if cond_key == ref_key:
            continue
        rows = by_cond[cond_key]
        # Match each row to its reference by resume name
        valid = [(r, refs[r["resume_name"]]) for r in rows if r["resume_name"] in refs]
        if not valid:
            print(f"  {cond_key}: skipped (no reference)")
            continue

        candidates = [analysis_to_text(r["analysis"]) for r, _ in valid]
        references = [ref for _, ref in valid]

        print(f"\n{cond_key} ({len(candidates)} samples)...")
        try:
            result = run_bertscore_eval(
                candidates, references,
                output_path=os.path.join(
                    os.path.dirname(OUT_FILE),
                    f"bertscore_{cond_key}.json"
                ),
            )
            aggregate[cond_key] = result["aggregate"]
            print(f"  → P={result['aggregate']['precision']:.3f}  "
                  f"R={result['aggregate']['recall']:.3f}  "
                  f"F1={result['aggregate']['f1']:.3f}")
        except Exception as e:
            print(f"  Error: {e}")

    with open(OUT_FILE, "w") as f:
        json.dump(aggregate, f, indent=2)
    print(f"\nSaved to {OUT_FILE}")

    # Summary table
    print("\n" + "=" * 70)
    print(f"BERTScore vs {REF_RETRIEVAL}+{REF_PROMPTING} reference")
    print("=" * 70)
    print(f"{'Condition':<35} {'Prec':>8} {'Recall':>8} {'F1':>8}")
    print("-" * 70)
    for cond in sorted(aggregate):
        a = aggregate[cond]
        print(f"{cond:<35} {a['precision']:>8.3f} {a['recall']:>8.3f} {a['f1']:>8.3f}")


if __name__ == "__main__":
    main()
