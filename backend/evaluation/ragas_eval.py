"""
RAGAS evaluation pipeline for the Job Match RAG system.

Evaluates generation quality by measuring how well the LLM output
is grounded in retrieved chunks. Runs on a set of test resumes and
produces per-resume and aggregate scores.

Metrics computed:
  - Faithfulness: are claims grounded in retrieved chunks?
  - Answer Relevancy: does output address the resume query?
  - Context Precision: are retrieved chunks actually used?
  - Context Recall: did retrieval capture needed information?
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from dotenv import load_dotenv
from ragas import evaluate
from ragas.metrics import (
    answer_relevancy,
    context_precision,
    context_recall,
    faithfulness,
)
from datasets import Dataset

load_dotenv()


def build_ragas_dataset(eval_records: list[dict]) -> Dataset:
    """
    Convert evaluation records into a HuggingFace Dataset for RAGAS.

    Each record must contain:
        question:  the resume text (serves as the "query")
        answer:    the LLM-generated analysis (JSON string)
        contexts:  list of retrieved chunk texts
        ground_truth: reference answer (optional — needed for context_recall)
    """
    return Dataset.from_dict({
        "question": [r["question"] for r in eval_records],
        "answer": [r["answer"] for r in eval_records],
        "contexts": [r["contexts"] for r in eval_records],
        "ground_truth": [r.get("ground_truth", "") for r in eval_records],
    })


def run_ragas_eval(eval_records: list[dict], output_path: str | None = None) -> dict:
    """
    Run RAGAS evaluation on a list of evaluation records.

    Args:
        eval_records: list of dicts with question/answer/contexts/ground_truth
        output_path: optional path to save results JSON

    Returns:
        dict with per-metric aggregate scores and per-sample breakdown
    """
    dataset = build_ragas_dataset(eval_records)

    metrics = [faithfulness, answer_relevancy, context_precision]
    # context_recall requires ground_truth — only include if provided
    if any(r.get("ground_truth") for r in eval_records):
        metrics.append(context_recall)

    result = evaluate(dataset=dataset, metrics=metrics)

    output = {
        "aggregate": {k: round(v, 4) for k, v in result.items() if isinstance(v, (int, float))},
        "per_sample": result.to_pandas().to_dict(orient="records"),
    }

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(output, f, indent=2, default=str)
        print(f"RAGAS results saved to {output_path}")

    return output


def format_analysis_as_answer(analysis: dict) -> str:
    """Convert the structured analysis dict to a flat string for RAGAS scoring."""
    return json.dumps(analysis, indent=2)


if __name__ == "__main__":
    # Quick smoke test with dummy data
    records = [
        {
            "question": "Software engineer with Python and AWS experience.",
            "answer": json.dumps({
                "matches": [{"job_id": "1", "title": "SWE", "company": "Acme",
                             "match_reasoning": "Resume mentions 'Python' matching job requirement 'Python experience'",
                             "evidence": {"resume": ["Python"], "job": ["Python experience"]},
                             "missing_alignment": []}],
                "skill_gaps": [],
                "recommendations": [],
            }),
            "contexts": ["Requirements: Python experience, AWS, Docker, Kubernetes"],
            "ground_truth": "The candidate matches the SWE role due to Python and AWS skills.",
        }
    ]
    results = run_ragas_eval(records)
    print(json.dumps(results["aggregate"], indent=2))
