import re

import pandas as pd

# Section header patterns (chunk_type label)
SECTION_PATTERNS = [
    (re.compile(r"(?i)(requirements?|qualifications?|what you.ll need|you have|must have)[\s:]+"), "qualifications"),
    (re.compile(r"(?i)(responsibilities|what you.ll do|your role|essential functions|duties)[\s:]+"), "responsibilities"),
    (re.compile(r"(?i)(preferred|nice to have|bonus|plus|desired)[\s:]+"), "preferred"),
]

CHUNK_TOKEN_SIZE = 400
CHUNK_OVERLAP = 50


def chunk_job(row: dict) -> list[dict]:
    """Split one job posting row into chunks for indexing."""
    description = row.get("description") or ""
    description = description.strip()
    if not description:
        return []

    chunks = _section_chunks(description) or _fixed_chunks(description)

    job_id = str(row.get("job_id", ""))
    metadata = {
        "job_id":    job_id,
        "title":     row.get("title") or "",
        "company":   row.get("company_name") or "",
        "location":  row.get("location") or "",
    }

    return [
        {
            "chunk_id":   f"{job_id}_{c['chunk_type']}",
            "job_id":     job_id,
            "chunk_type": c["chunk_type"],
            "text":       c["text"],
            "metadata":   {**metadata, "chunk_type": c["chunk_type"]},
        }
        for c in chunks
        if c["text"].strip()
    ]


def chunk_all_jobs(df: pd.DataFrame) -> list[dict]:
    """Chunk every row in the dataframe. Used by the indexing pipeline."""
    all_chunks = []
    for _, row in df.iterrows():
        all_chunks.extend(chunk_job(row.to_dict()))
    return all_chunks


# --- private helpers ---

def _section_chunks(description: str) -> list[dict]:
    """
    Split description based on known section headers.
    Returns empty list if no sections are found, and falls back to fixed chunking.
    """
    # Find all section boundaries: (start_index, chunk_type)
    boundaries = []
    for pattern, chunk_type in SECTION_PATTERNS:
        for match in pattern.finditer(description):
            boundaries.append((match.end(), chunk_type))

    if not boundaries:
        return []

    boundaries.sort(key=lambda x: x[0])

    # Collect text per section
    sections: dict[str, list[str]] = {}
    for i, (start, chunk_type) in enumerate(boundaries):
        end = boundaries[i + 1][0] if i + 1 < len(boundaries) else len(description)
        text = description[start:end].strip()
        if text:
            sections.setdefault(chunk_type, []).append(text)

    # Merge duplicate section types into one chunk each
    return [
        {"chunk_type": chunk_type, "text": " ".join(texts)}
        for chunk_type, texts in sections.items()
    ]


def _fixed_chunks(description: str) -> list[dict]:
    """
    Split free-form description into overlapping token windows.
    Uses whitespace-split words as a proxy for tokens (close enough without tiktoken).
    """
    words = description.split()
    if not words:
        return []

    chunks = []
    start = 0
    idx = 0
    while start < len(words):
        end = min(start + CHUNK_TOKEN_SIZE, len(words))
        text = " ".join(words[start:end])
        chunks.append({"chunk_type": f"general_{idx}", "text": text})
        if end == len(words):
            break
        start += CHUNK_TOKEN_SIZE - CHUNK_OVERLAP
        idx += 1

    return chunks
