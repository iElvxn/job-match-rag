"""
Compute citation rate and skill gap metrics from ablation_raw.json.
Outputs a table ready to paste into the poster/report.
"""
import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

RESULTS_FILE = "backend/evaluation/results/ablation_raw.json"


def has_citation(match: dict) -> bool:
    ev = match.get("evidence", {})
    return bool(ev.get("resume")) and bool(ev.get("job"))


def citation_rate(results: list[dict]) -> float:
    total, cited = 0, 0
    for r in results:
        for match in r["analysis"].get("matches", []):
            total += 1
            if has_citation(match):
                cited += 1
    return cited / total if total else 0.0


def avg_gaps(results: list[dict]) -> float:
    counts = [r["num_skill_gaps"] for r in results]
    return sum(counts) / len(counts) if counts else 0.0


def avg_matches(results: list[dict]) -> float:
    counts = [len(r["analysis"].get("matches", [])) for r in results]
    return sum(counts) / len(counts) if counts else 0.0


def main():
    with open(RESULTS_FILE) as f:
        data = json.load(f)

    # Group by (retrieval_condition, prompting_condition)
    groups: dict[str, list] = {}
    for r in data:
        key = f"{r['retrieval_condition']}_{r['prompting_condition']}"
        groups.setdefault(key, []).append(r)

    # Aggregate per retrieval condition (across prompting strategies)
    ret_groups: dict[str, list] = {}
    for r in data:
        key = r["retrieval_condition"]
        ret_groups.setdefault(key, []).append(r)

    print("\n=== By Retrieval Condition (all prompting strategies combined) ===")
    print(f"{'Condition':<20} {'N':>4} {'Cit%':>6} {'AvgGaps':>8} {'AvgMatches':>11}")
    print("-" * 55)
    order = ["no_rag", "bm25_only", "dense_only", "hybrid", "hybrid_rerank"]
    for cond in order:
        results = ret_groups.get(cond, [])
        cr = citation_rate(results) * 100
        ag = avg_gaps(results)
        am = avg_matches(results)
        print(f"{cond:<20} {len(results):>4} {cr:>5.1f}% {ag:>8.1f} {am:>11.1f}")

    print("\n=== By Prompting Strategy (hybrid_rerank only) ===")
    print(f"{'Strategy':<20} {'N':>4} {'Cit%':>6} {'AvgGaps':>8} {'AvgMatches':>11}")
    print("-" * 55)
    for prompt in ["zero_shot", "structured", "few_shot"]:
        key = f"hybrid_rerank_{prompt}"
        results = groups.get(key, [])
        cr = citation_rate(results) * 100
        ag = avg_gaps(results)
        am = avg_matches(results)
        print(f"{prompt:<20} {len(results):>4} {cr:>5.1f}% {ag:>8.1f} {am:>11.1f}")

    print("\n=== Full Condition Grid ===")
    print(f"{'Condition':<35} {'Cit%':>6} {'AvgGaps':>8}")
    print("-" * 52)
    for key in sorted(groups):
        results = groups[key]
        cr = citation_rate(results) * 100
        ag = avg_gaps(results)
        print(f"{key:<35} {cr:>5.1f}% {ag:>8.1f}")


if __name__ == "__main__":
    main()
