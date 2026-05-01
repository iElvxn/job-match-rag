import json

from openai import OpenAI

client = OpenAI()

MAX_JOBS = 10
MAX_CHUNK_WORDS = 150

SYSTEM_PROMPT = """You are a retrieval-augmented career advisor.

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
- If a job requires significantly more experience than the resume demonstrates (e.g. "5+ years" when the resume shows internships or <2 years), you MUST reflect this in missing_alignment and lower your confidence in the match. Do NOT rationalize seniority mismatches away.

3. EXPERIENCE LEVEL (MANDATORY CHECK)
- Before including any match, check whether the job's required years of experience aligns with the resume.
- If the job title or description contains "Senior", "Staff", "Principal", "Lead", "Director", or requires "5+ years" / "7+ years" / "10+ years" and the resume does not demonstrate equivalent experience, add it to missing_alignment with job_requirement set to the exact experience phrase and reason set to what the resume actually shows.
- Do NOT exclude these jobs entirely — include them in matches but surface the gap clearly.

4. SKILL GAPS (RETRIEVAL-DRIVEN)
- ONLY include skills that appear in retrieved job postings
- Use the MARKET INTELLIGENCE section for frequency counts — do NOT compute yourself
- Each skill must include exact quoted evidence from job descriptions

5. RECOMMENDATIONS
- Must be derived ONLY from identified skill gaps
- Must reference job demand frequency from MARKET INTELLIGENCE
- Must be actionable (e.g., build X, learn Y, implement Z)

6. NO HALLUCINATIONS
- Do NOT invent skills, experience, or job requirements

7. OUTPUT FORMAT
- Return ONLY valid JSON, no extra text
"""


def generate_analysis(
    resume_text: str,
    results: list[dict],
    skill_data: dict,
    chunk_lookup: dict[str, str],
    market_intel: dict | None = None,
) -> dict:
    """
    Generate structured job match analysis using GPT-4.1.

    Returns a dict with top job matches, match reasoning, skill gaps,
    and evidence-span citations sourced directly from retrieved chunks.
    """
    jobs = _group_by_job(results, chunk_lookup)
    prompt = _build_prompt(resume_text, jobs, skill_data, market_intel)

    response = client.chat.completions.create(
        model="gpt-4.1",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
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
    skill_data: dict,
    market_intel: dict | None,
) -> str:
    resume_section = f"RESUME:\n{_truncate(resume_text, 1500)}" #ima test with out truncating
    
    skills_section = (
        f"EXTRACTED SKILLS:\n"
        f"  Resume skills: {', '.join(skill_data['resume_skills']) or 'none detected'}\n"
        f"  Skill gaps:    {', '.join(skill_data['gaps'][:20]) or 'none detected'}"
    )

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

    sections = [resume_section, skills_section]
    if market_section:
        sections.append(market_section)
    sections.append(jobs_section)

    return "\n\n".join(sections)
