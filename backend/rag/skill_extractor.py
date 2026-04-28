import re

from rapidfuzz import fuzz, process

SKILLS = [
    # Languages
    "python", "java", "javascript", "typescript", "go", "rust", "c++", "c#",
    "ruby", "swift", "kotlin", "scala", "bash", "sql",
    # Frameworks / Libraries
    "react", "angular", "vue", "django", "flask", "fastapi", "spring", "node.js",
    "express", "next.js", "pytorch", "tensorflow", "scikit-learn", "keras",
    "hugging face", "langchain", "pandas", "numpy", "opencv", "nltk", "spacy",
    # Databases
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "dynamodb",
    "cassandra", "sqlite", "snowflake", "bigquery",
    # Cloud
    "aws", "gcp", "azure", "lambda", "ec2", "s3",
    # DevOps / Infra
    "docker", "kubernetes", "terraform", "jenkins", "github actions", "ansible",
    # Tools / Concepts
    "git", "linux", "rest", "graphql", "grpc", "kafka", "spark", "airflow", "dbt",
    # Methodologies
    "agile", "scrum", "kanban", "jira", "product management",
    "stakeholder management", "technical writing", "data analysis", "system design",
]

_PATTERNS = {
    skill: re.compile(rf"\b{re.escape(skill)}\b", re.IGNORECASE)
    for skill in SKILLS
}

_FUZZY_THRESHOLD = 85


def extract_skills(text: str) -> set[str]:
    """Return the set of known skills found in the text using exact and fuzzy matching."""
    matched = set()

    # Exact match first
    for skill, pattern in _PATTERNS.items():
        if pattern.search(text):
            matched.add(skill)

    # Fuzzy match on tokens not already covered by exact match
    tokens = set(re.findall(r"\b\w[\w.+#-]*\b", text.lower()))
    unmatched_tokens = tokens - matched
    for token in unmatched_tokens:
        result = process.extractOne(token, SKILLS, scorer=fuzz.ratio)
        if result and result[1] >= _FUZZY_THRESHOLD:
            matched.add(result[0])

    return matched


def compute_market_intelligence(results: list[dict], chunk_lookup: dict[str, str]) -> dict:
    """
    Compute per-skill frequency across retrieved jobs before calling the LLM.

    Groups chunks by job_id first to avoid double-counting multi-chunk jobs,
    then runs extract_skills once per unique job.

    Returns skill_frequency sorted by count descending, total job count,
    and pre-formatted market_summary strings for injection into the LLM prompt.
    """
    job_texts: dict[str, str] = {}
    for r in results:
        jid = r["metadata"].get("job_id", "")
        job_texts[jid] = job_texts.get(jid, "") + " " + chunk_lookup.get(r["chunk_id"], "")

    total_jobs = len(job_texts)

    skill_counts: dict[str, list[str]] = {}
    for jid, text in job_texts.items():
        for skill in extract_skills(text):
            skill_counts.setdefault(skill, []).append(jid)

    skill_frequency = {
        skill: {"count": len(job_ids), "job_ids": job_ids}
        for skill, job_ids in sorted(skill_counts.items(), key=lambda x: len(x[1]), reverse=True)
    }

    return {
        "skill_frequency": skill_frequency,
        "total_jobs": total_jobs,
        "market_summary": [
            f"{skill}: {d['count']}/{total_jobs} matched jobs"
            for skill, d in skill_frequency.items()
        ],
    }


def get_skill_gap(
    resume_text: str,
    results: list[dict],
    chunk_lookup: dict[str, str],
    market_intel: dict | None = None,
) -> dict:
    """
    Compare skills in the resume against skills required by retrieved job chunks.

    Args:
        resume_text: raw resume text
        results: hybrid_retrieve output (list of chunk dicts with chunk_id)
        chunk_lookup: mapping of chunk_id -> chunk text, built from BM25 chunks at startup
        market_intel: optional output of compute_market_intelligence, used to sort gaps by frequency

    Returns dict with resume_skills, job_skills, and gaps sorted by job frequency.
    """
    resume_skills = extract_skills(resume_text)

    if market_intel:
        # Derive job_skills from market intel — already computed per-job and grounded
        # in retrieved postings. This ensures gaps are strictly retrieval-driven.
        freq = market_intel["skill_frequency"]
        job_skills = set(freq.keys())
        raw_gaps = job_skills - resume_skills
        gaps_sorted = sorted(raw_gaps, key=lambda s: freq[s]["count"], reverse=True)
    else:
        job_text = " ".join(chunk_lookup.get(r["chunk_id"], "") for r in results)
        job_skills = extract_skills(job_text)
        raw_gaps = job_skills - resume_skills
        gaps_sorted = sorted(raw_gaps)

    return {
        "resume_skills": sorted(resume_skills),
        "job_skills":    sorted(job_skills),
        "gaps":          gaps_sorted,
    }
