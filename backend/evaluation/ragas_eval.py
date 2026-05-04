"""
RAGAS evaluation pipeline for the Job Match RAG system.

Evaluates generation quality using faithfulness — whether LLM claims
are grounded in retrieved chunks. Uses gpt-4o-mini to keep costs low.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from dotenv import load_dotenv
from openai import OpenAI
from ragas import evaluate
from ragas.llms import llm_factory
from ragas.metrics import faithfulness
from datasets import Dataset

load_dotenv()

# Pin to gpt-4o-mini — ~$0.15/1M input vs $2.50 for gpt-4o
_openai_client = OpenAI()
_ragas_llm = llm_factory("gpt-4o-mini", client=_openai_client)
faithfulness.llm = _ragas_llm


def format_analysis_as_answer(analysis: dict) -> str:
    """
    Extract only the grounded text claims from the analysis for RAGAS scoring.

    Faithfulness checks whether claims in the answer are supported by the
    retrieved contexts. We include only the match reasoning and evidence
    spans — not metadata like job_id or company — to keep token count low
    and focus evaluation on the actual grounded claims.
    """
    lines = []
    for match in analysis.get("matches", []):
        reasoning = match.get("match_reasoning", "")
        if reasoning:
            lines.append(f"Match reasoning: {reasoning}")
        for span in match.get("evidence", {}).get("job", []):
            lines.append(f"Job evidence: {span}")
        for span in match.get("evidence", {}).get("resume", []):
            lines.append(f"Resume evidence: {span}")
        for m in match.get("missing_alignment", []):
            req = m.get("job_requirement", "") if isinstance(m, dict) else str(m)
            if req:
                lines.append(f"Missing requirement: {req}")
    for gap in analysis.get("skill_gaps", []):
        if isinstance(gap, str):
            lines.append(f"Skill gap: {gap}")
        elif isinstance(gap, dict):
            lines.append(f"Skill gap: {gap.get('skill', '')}")
    return "\n".join(lines) if lines else "No grounded claims found."


def build_ragas_dataset(eval_records: list[dict]) -> Dataset:
    return Dataset.from_dict({
        "question":  [r["question"] for r in eval_records],
        "answer":    [r["answer"] for r in eval_records],
        "contexts":  [r["contexts"] for r in eval_records],
    })


def run_ragas_eval(eval_records: list[dict], output_path: str | None = None) -> dict:
    """
    Run RAGAS faithfulness evaluation on a list of records.

    Args:
        eval_records: list of dicts with question / answer / contexts keys
        output_path:  optional path to save results JSON

    Returns:
        dict with aggregate scores and per-sample breakdown
    """
    dataset = build_ragas_dataset(eval_records)

    result = evaluate(dataset=dataset, metrics=[faithfulness], llm=_ragas_llm)

    # EvaluationResult.to_pandas() is the stable API in RAGAS 0.4.x
    df = result.to_pandas()
    aggregate = {col: round(float(df[col].mean()), 4)
                 for col in df.columns
                 if df[col].dtype.kind == "f"}

    output = {
        "aggregate": aggregate,
        "per_sample": df.to_dict(orient="records"),
    }

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(output, f, indent=2, default=str)
        print(f"    saved → {output_path}")

    return output


if __name__ == "__main__":
    # Smoke test — run this before spending API credits
    records = [
        {
            "question": "Software engineer with Python and AWS experience.",
            "answer": (
                "Match reasoning: Resume mentions Python matching job requirement.\n"
                "Job evidence: 5+ years Python experience required.\n"
                "Resume evidence: Python, Flask, REST APIs."
            ),
            "contexts": ["Requirements: Python experience, AWS, Docker, Kubernetes"],
        }
    ]
    result = run_ragas_eval(records)
    print("Smoke test aggregate:", result["aggregate"])
