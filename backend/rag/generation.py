import json

from openai import OpenAI

client = OpenAI()

MAX_JOBS = 10        # top unique jobs to include in the prompt
MAX_CHUNK_WORDS = 150  # truncate each chunk to keep token cost manageable

SYSTEM_PROMPT = """You are a career advisor analyzing resume-job fit.
You will be given a resume, extracted skills, and a list of retrieved job postings.
Respond with valid JSON only, using exactly this schema:

{
  "matches": [
    {
      "job_id": "string",
      "title": "string",
      "company": "string",
      "match_reasoning": "1-2 sentences explaining why this job fits the resume",
      "citations": ["exact quoted phrase from the job description"]
    }
  ],
  "skill_gaps": ["skill1", "skill2"],
  "recommendations": ["one concrete suggestion per gap"]
}

Rules:
- citations must be EXACT phrases copied from the job description — do not paraphrase
- do not invent skills or experience not present in the resume
- skill_gaps should match the extracted gaps provided, do not add new ones"""

def _truncate(text: str, max_words: int) -> str:
    words = text.split()
    return " ".join(words[:max_words]) + ("..." if len(words) > max_words else "")

def _group_by_job(results: list[dict], chunk_lookup: dict[str, str]) -> list[dict]:
    """Merge chunks by job_id, keeping the highest-scoring chunk text per job."""
    jobs = {}
    for result in results:
        job_id = result["metadata"].get("job_id", "")
        if job_id not in jobs or result["score"] > jobs[job_id]["score"]:
            jobs[job_id] = {
                "job_id":    job_id,
                "title":     result["metadata"].get("title", ""),
                "company":   result["metadata"].get("company", ""),
                "location":  result["metadata"].get("location", ""),
                "score":     result["score"],
                "text":      chunk_lookup.get(result["chunk_id"], ""),
            }
    return sorted(jobs.values(), key=lambda x: x["score"], reverse=True)[:MAX_JOBS]

def _build_prompt(resume_text: str, jobs: list[dict], skill_data: dict) -> str:
    resume_section = f"RESUME:\n{_truncate(resume_text, 500)}"
    
    skills_section = (
        f"EXTRACTED SKILLS:\n"
        f"  Resume skills: {', '.join(skill_data['resume_skills']) or 'none detected'}\n"
        f"  Skill gaps:    {', '.join(skill_data['gaps']) or 'none detected'}"
    )
    
    jobs_section = "JOB POSTINGS:"
    for i, job in enumerate(jobs, 1):
        jobs_section += (
            f"\n\n[{i}] {job['title']} at {job['company']} ({job['location']})\n"
            f"Job ID: {job['job_id']}\n"
            f"{_truncate(job['text'], MAX_CHUNK_WORDS)}"
        )

    return f"{resume_section}\n\n{skills_section}\n\n{jobs_section}"
    
def generate_analysis(resume_text: str, results: list[dict], skill_data: dict, chunk_lookup: dict[str, str]) -> dict:
    """
    Generate structured job match analysis using GPT-4o.

    Returns a dict with top job matches, match reasoning, skill gaps,
    and evidence-span citations sourced directly from retrieved chunks.
    """
    jobs = _group_by_job(results, chunk_lookup)
    prompt = _build_prompt(resume_text, jobs, skill_data)
    
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