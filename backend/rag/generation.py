import json

from openai import OpenAI

client = OpenAI()

MAX_JOBS = 10
MAX_CHUNK_WORDS = 150

# ---------------------------------------------------------------------------
# Prompting strategies
# ---------------------------------------------------------------------------

# Strategy 1: Zero-shot — no skill matrix, no market intelligence, minimal
# instructions. Serves as the baseline to measure the value of structured
# context injection.

ZERO_SHOT_SYSTEM = """You are a career advisor. Analyze the candidate's resume against the retrieved job postings.

Return valid JSON in this exact schema:

{
  "matches": [
    {
      "job_id": "string",
      "title": "string",
      "company": "string",
      "match_reasoning": "Explain why this job matches the resume",
      "evidence": {
        "resume": ["relevant phrases from the resume"],
        "job": ["relevant phrases from the job description"]
      },
      "missing_alignment": [
        {
          "job_requirement": "requirement from job description",
          "reason": "not found in resume"
        }
      ]
    }
  ],
  "skill_gaps": [
    {
      "skill": "string",
      "evidence": ["phrases from job descriptions showing this requirement"],
      "frequency": "how often this skill appears across the jobs"
    }
  ],
  "recommendations": [
    {
      "skill": "string",
      "frequency": "how often this appears",
      "reason": "why this matters",
      "action": "what to do about it"
    }
  ]
}

Return ONLY valid JSON, no extra text.
"""

# Strategy 2: Structured + Market Intelligence — the current production
# prompt. Pre-computed skill matrix and market frequency counts are injected
# so the LLM doesn't have to count or guess. Evidence-span citation rules
# enforce grounding.

STRUCTURED_SYSTEM = """You are a retrieval-augmented career advisor.

You MUST base ALL reasoning strictly on the provided resume and retrieved job postings.
Do NOT use prior knowledge.

Return valid JSON in this exact schema:

{
  "matches": [
    {
      "job_id": "string",
      "title": "string",
      "company": "string",
      "match_reasoning": "Concise explanation explicitly linking resume evidence to job requirements",
      "evidence": {
        "resume": ["exact phrases from the resume"],
        "job": ["exact phrases from the job description"]
      },
      "missing_alignment": [
        {
          "job_requirement": "exact phrase from job description",
          "reason": "not found in resume"
        }
      ]
    }
  ],
  "skill_gaps": [
    {
      "skill": "string",
      "evidence": ["exact phrases from job descriptions showing this requirement"],
      "frequency": "use the frequency from MARKET INTELLIGENCE section — do not compute yourself"
    }
  ],
  "recommendations": [
    {
      "skill": "string",
      "frequency": "X/Y jobs — copy from MARKET INTELLIGENCE",
      "reason": "which types of roles require this and why it matters",
      "action": "specific project or task to build this skill (e.g. deploy X using Y on Z)"
    }
  ]
}

STRICT RULES:

1. GROUNDING (MANDATORY)
- Every claim MUST be supported by evidence from:
  (a) the resume AND
  (b) retrieved job descriptions
- Use exact quotes only. No paraphrasing.

2. MATCH REASONING
- Must explicitly connect resume evidence → job requirement
- Do NOT give generic explanations.

3. SKILL GAPS (RETRIEVAL-DRIVEN)
- ONLY include skills that appear in retrieved job postings
- Use the MARKET INTELLIGENCE section for frequency counts — do NOT compute yourself
- Each skill must include exact quoted evidence from job descriptions

4. RECOMMENDATIONS
- Must be derived ONLY from identified skill gaps
- Must reference job demand frequency from MARKET INTELLIGENCE
- Must be actionable (e.g., build X, learn Y, implement Z)

5. NO HALLUCINATIONS
- Do NOT invent skills, experience, or job requirements

6. OUTPUT FORMAT
- Return ONLY valid JSON, no extra text
"""

# Strategy 3: Few-shot — includes a worked example of a correct match
# analysis so the model can pattern-match on citation style and depth.
# The example is synthetic and domain-neutral to avoid biasing towards
# specific skills.

FEW_SHOT_SYSTEM = """You are a retrieval-augmented career advisor.

You MUST base ALL reasoning strictly on the provided resume and retrieved job postings.
Do NOT use prior knowledge.

Below is an example of the expected output format and quality:

=== EXAMPLE INPUT ===
RESUME: Software engineer with 3 years of experience in Python and Django. Built REST APIs serving 10K+ RPM. Experience with PostgreSQL and Redis caching.

JOB POSTING [1]: Backend Engineer at Acme Corp
"Requirements: 3+ years Python experience, Django or Flask, PostgreSQL, experience with caching systems (Redis/Memcached), CI/CD pipelines"

EXTRACTED SKILLS:
  Resume skills: python, django, postgresql, redis, rest
  Skill gaps: flask, ci/cd

MARKET INTELLIGENCE:
  - python: 5/5 matched jobs
  - postgresql: 4/5 matched jobs
  - redis: 3/5 matched jobs
  - ci/cd: 3/5 matched jobs

=== EXAMPLE OUTPUT ===
{
  "matches": [
    {
      "job_id": "example_1",
      "title": "Backend Engineer",
      "company": "Acme Corp",
      "match_reasoning": "Resume states '3 years of experience in Python and Django' which directly satisfies the job requirement '3+ years Python experience, Django or Flask'. Resume mentions 'PostgreSQL and Redis caching' matching 'PostgreSQL, experience with caching systems (Redis/Memcached)'.",
      "evidence": {
        "resume": ["3 years of experience in Python and Django", "Built REST APIs serving 10K+ RPM", "PostgreSQL and Redis caching"],
        "job": ["3+ years Python experience, Django or Flask", "PostgreSQL", "experience with caching systems (Redis/Memcached)"]
      },
      "missing_alignment": [
        {
          "job_requirement": "CI/CD pipelines",
          "reason": "not found in resume"
        }
      ]
    }
  ],
  "skill_gaps": [
    {
      "skill": "ci/cd",
      "evidence": ["CI/CD pipelines"],
      "frequency": "3/5 matched jobs"
    }
  ],
  "recommendations": [
    {
      "skill": "ci/cd",
      "frequency": "3/5 matched jobs",
      "reason": "Required by backend and DevOps roles for deployment automation",
      "action": "Set up a GitHub Actions pipeline for an existing Django project with automated testing and Docker deployment"
    }
  ]
}

=== END EXAMPLE ===

Now analyze the ACTUAL resume and job postings below using the same format and rigor. Return valid JSON in the same schema. Use exact quotes from the actual data, not the example.

STRICT RULES:

1. GROUNDING (MANDATORY)
- Every claim MUST be supported by evidence from:
  (a) the resume AND
  (b) retrieved job descriptions
- Use exact quotes only. No paraphrasing.

2. MATCH REASONING
- Must explicitly connect resume evidence → job requirement
- Do NOT give generic explanations.

3. SKILL GAPS (RETRIEVAL-DRIVEN)
- ONLY include skills that appear in retrieved job postings
- Use the MARKET INTELLIGENCE section for frequency counts — do NOT compute yourself
- Each skill must include exact quoted evidence from job descriptions

4. RECOMMENDATIONS
- Must be derived ONLY from identified skill gaps
- Must reference job demand frequency from MARKET INTELLIGENCE
- Must be actionable (e.g., build X, learn Y, implement Z)

5. NO HALLUCINATIONS
- Do NOT invent skills, experience, or job requirements

6. OUTPUT FORMAT
- Return ONLY valid JSON, no extra text
"""

# Map strategy names to system prompts for easy lookup in ablation
STRATEGY_PROMPTS = {
    "zero_shot": ZERO_SHOT_SYSTEM,
    "structured": STRUCTURED_SYSTEM,
    "few_shot": FEW_SHOT_SYSTEM,
}


def generate_analysis(
    resume_text: str,
    results: list[dict],
    skill_data: dict,
    chunk_lookup: dict[str, str],
    market_intel: dict | None = None,
    strategy: str = "structured",
) -> dict:
    """
    Generate structured job match analysis using GPT-4.1.

    Args:
        resume_text: raw resume text
        results: retrieved chunk dicts
        skill_data: output of get_skill_gap()
        chunk_lookup: chunk_id -> chunk text mapping
        market_intel: output of compute_market_intelligence()
        strategy: prompting strategy — one of "zero_shot", "structured", "few_shot"

    Returns a dict with top job matches, match reasoning, skill gaps,
    and evidence-span citations sourced directly from retrieved chunks.
    """
    system_prompt = STRATEGY_PROMPTS.get(strategy, STRUCTURED_SYSTEM)
    jobs = _group_by_job(results, chunk_lookup)

    # Zero-shot intentionally omits skill data and market intel
    if strategy == "zero_shot":
        prompt = _build_prompt(resume_text, jobs, skill_data=None, market_intel=None)
    else:
        prompt = _build_prompt(resume_text, jobs, skill_data, market_intel)

    response = client.chat.completions.create(
        model="gpt-4.1",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": prompt},
        ],
        temperature=0,
    )

    return json.loads(response.choices[0].message.content)


# --- private helpers ---

def _group_by_job(results: list[dict], chunk_lookup: dict[str, str]) -> list[dict]:
    """Merge chunks by job_id, keeping the highest-scoring chunk text per job."""
    jobs = {}
    for result in results:
        job_id = result["metadata"].get("job_id", "")
        if job_id not in jobs or result["score"] > jobs[job_id]["score"]:
            jobs[job_id] = {
                "job_id":     job_id,
                "title":      result["metadata"].get("title", ""),
                "company":    result["metadata"].get("company", ""),
                "location":   result["metadata"].get("location", ""),
                "chunk_type": result["metadata"].get("chunk_type", ""),
                "score":      result["score"],
                "text":       chunk_lookup.get(result["chunk_id"], ""),
            }
    return sorted(jobs.values(), key=lambda x: x["score"], reverse=True)[:MAX_JOBS]


def _truncate(text: str, max_words: int) -> str:
    words = text.split()
    return " ".join(words[:max_words]) + ("..." if len(words) > max_words else "")


def _build_prompt(
    resume_text: str,
    jobs: list[dict],
    skill_data: dict | None,
    market_intel: dict | None,
) -> str:
    resume_section = f"RESUME:\n{_truncate(resume_text, 1500)}"

    # Skill data and market intel are omitted for the zero-shot strategy
    if skill_data:
        skills_section = (
            f"EXTRACTED SKILLS:\n"
            f"  Resume skills: {', '.join(skill_data['resume_skills']) or 'none detected'}\n"
            f"  Skill gaps:    {', '.join(skill_data['gaps'][:20]) or 'none detected'}"
        )
    else:
        skills_section = ""

    if market_intel and market_intel.get("market_summary"):
        top = market_intel["market_summary"][:15]
        intel_lines = "\n".join(f"  - {s}" for s in top)
        market_section = (
            f"MARKET INTELLIGENCE (computed deterministically — use these frequency counts exactly):\n"
            f"{intel_lines}"
        )
    else:
        market_section = ""

    jobs_section = "JOB POSTINGS:"
    for i, job in enumerate(jobs, 1):
        section_label = f" [{job['chunk_type']}]" if job.get("chunk_type") else ""
        jobs_section += (
            f"\n\n[{i}] {job['title']} at {job['company']} ({job['location']}){section_label}\n"
            f"Job ID: {job['job_id']}\n"
            f"{_truncate(job['text'], MAX_CHUNK_WORDS)}"
        )

    sections = [resume_section]
    if skills_section:
        sections.append(skills_section)
    if market_section:
        sections.append(market_section)
    sections.append(jobs_section)

    return "\n\n".join(sections)
