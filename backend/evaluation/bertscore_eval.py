"""
BERTScore evaluation for the Job Match RAG system.

Compares generated analysis text against reference summaries using
contextual embeddings. Unlike RAGAS (which measures retrieval grounding),
BERTScore measures semantic similarity of the output to a reference —
useful for comparing prompting strategies against a gold-standard output.

Metrics: Precision, Recall, F1 (per-sample and aggregate)
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from bert_score import score as bert_score


def run_bertscore_eval(
    candidates: list[str],
    references: list[str],
    output_path: str | None = None,
) -> dict:
    """
    Compute BERTScore between candidate outputs and reference summaries.

    Args:
        candidates: list of generated analysis strings (one per test resume)
        references: list of reference/gold-standard analysis strings
        output_path: optional path to save results JSON

    Returns:
        dict with aggregate and per-sample precision, recall, F1
    """
    P, R, F1 = bert_score(
        candidates,
        references,
        lang="en",
        model_type="microsoft/deberta-xlarge-mnli",
        verbose=True,
    )

    per_sample = [
        {"precision": round(p, 4), "recall": round(r, 4), "f1": round(f, 4)}
        for p, r, f in zip(P.tolist(), R.tolist(), F1.tolist())
    ]

    output = {
        "aggregate": {
            "precision": round(P.mean().item(), 4),
            "recall": round(R.mean().item(), 4),
            "f1": round(F1.mean().item(), 4),
        },
        "per_sample": per_sample,
    }

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(output, f, indent=2)
        print(f"BERTScore results saved to {output_path}")

    return output


def analysis_to_text(analysis: dict) -> str:
    """
    Flatten a structured analysis dict into plain text for BERTScore.

    Extracts match reasoning, skill gaps, and recommendations into a
    readable paragraph so BERTScore compares semantic content rather
    than JSON syntax.
    """
    parts = []

    for match in analysis.get("matches", []):
        parts.append(
            f"Job: {match.get('title', '')} at {match.get('company', '')}. "
            f"{match.get('match_reasoning', '')}"
        )

    for gap in analysis.get("skill_gaps", []):
        parts.append(
            f"Skill gap: {gap.get('skill', '')} "
            f"(frequency: {gap.get('frequency', 'unknown')})"
        )

    for rec in analysis.get("recommendations", []):
        parts.append(
            f"Recommendation: learn {rec.get('skill', '')} — {rec.get('action', '')}"
        )

    return " ".join(parts) if parts else json.dumps(analysis)


if __name__ == "__main__":
    # Quick smoke test
    cands = ["The candidate matches the SWE role due to Python and AWS skills."]
    refs = ["The resume shows strong Python and AWS experience relevant to the SWE position."]
    results = run_bertscore_eval(cands, refs)
    print(json.dumps(results["aggregate"], indent=2))
