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


def get_skill_gap(resume_text: str, results: list[dict], chunk_lookup: dict[str, str]) -> dict:
    """
    Compare skills in the resume against skills required by retrieved job chunks.

    Args:
        resume_text: raw resume text
        results: hybrid_retrieve output (list of chunk dicts with chunk_id)
        chunk_lookup: mapping of chunk_id -> chunk text, built from BM25 chunks at startup

    Returns dict with resume_skills, job_skills, and gaps.
    """
    resume_skills = extract_skills(resume_text)

    job_text = " ".join(chunk_lookup.get(r["chunk_id"], "") for r in results)
    job_skills = extract_skills(job_text)

    return {
        "resume_skills": sorted(resume_skills),
        "job_skills": sorted(job_skills),
        "gaps": sorted(job_skills - resume_skills),
    }
