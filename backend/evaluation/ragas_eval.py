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

# Pin to gpt-4o-mini — ~$0.15/1M input vs $2.50 for gpt-4o.
# Boost max_tokens above the default so verdict generation doesn't truncate
# (default gets cut off when verifying many statements at once).
_openai_client = OpenAI()
_ragas_llm = llm_factory("gpt-4o-mini", client=_openai_client, max_tokens=4096)
faithfulness.llm = _ragas_llm


def format_analysis_as_answer(analysis: dict) -> str:
    """
    Extract only the high-level claims that need verification for RAGAS faithfulness.

    Faithfulness measures whether claims in the answer are supported by the
    retrieved contexts. We include only:
      - match_reasoning: the natural-language claim that needs verification
      - skill_gap names: the asserted skill gap claims

    We deliberately exclude evidence spans — they are either direct excerpts
    from the contexts (trivially grounded) or excerpts from the resume (not
    accessible to RAGAS since it only sees the contexts). Including them
    inflates statement count and hits LLM max_tokens limits.

    We limit to the top 3 matches to keep statement count manageable.
    """
    lines = []
    for match in (analysis.get("matches") or [])[:3]:
        reasoning = match.get("match_reasoning", "")
        if reasoning:
            lines.append(reasoning)
    for gap in (analysis.get("skill_gaps") or [])[:5]:
        if isinstance(gap, str):
            lines.append(f"Skill gap: {gap}")
        elif isinstance(gap, dict) and gap.get("skill"):
            lines.append(f"Skill gap: {gap['skill']}")
    return " ".join(lines) if lines else "No grounded claims found."


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
