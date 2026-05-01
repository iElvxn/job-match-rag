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


_YEARS_RE = re.compile(
    r"(\d+)\s*(?:\+|to|-)?\s*(\d+)?\s+years?",
    re.IGNORECASE,
)


def _years_to_seniority(years: int) -> str:
    if years <= 1:
        return "entry"
    if years <= 4:
        return "mid"
    if years <= 8:
        return "senior"
    return "staff"


def _extract_years(description: str) -> int | None:
    matches = []
    for m in _YEARS_RE.findall(description[:2000]):
        low  = int(m[0])
        high = int(m[1]) if m[1] else low
        matches.append(max(low, high))
    return max(matches) if matches else None


def _detect_seniority(title: str, description: str = "") -> str:
    t = title.lower()

    # Intern first — unambiguous even before staff/senior checks
    if any(kw in t for kw in ("intern", "internship", "co-op", "coop", "apprentice")):
        return "intern"

    # Staff / principal
    if any(kw in t for kw in ("principal", "distinguished", "fellow", "staff engineer")):
        return "staff"

    # Senior
    if any(kw in t for kw in ("senior", "sr.", "tech lead")) or "engineer iii" in t:
        return "senior"

    # Mid
    if "engineer ii" in t:
        return "mid"

    # Entry
    if any(kw in t for kw in ("junior", "jr.", "new grad", "associate")) or "engineer i" in t:
        return "entry"

    # Description fallback — parse years-of-experience requirements
    if description:
        years = _extract_years(description)
        if years is not None:
            return _years_to_seniority(years)

    return "unknown"


def chunk_job(row: dict) -> list[dict]:
    """Split one job posting row into chunks for indexing."""
    description = _safe(row.get("description")).strip()
    if not description:
        return []

    chunks = _section_chunks(description) or _fixed_chunks(description)

    job_id = str(row.get("job_id", ""))
    title  = _safe(row.get("title"))
    metadata = {
        "job_id":    job_id,
        "title":     title,
        "company":   _safe(row.get("company_name")),
        "location":  _safe(row.get("location")),
        "seniority": _detect_seniority(title, description),
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

def _safe(val) -> str:
    """Convert a value to string, treating NaN/None as empty string."""
    if val is None:
        return ""
    try:
        import math
        if math.isnan(val):
            return ""
    except TypeError:
        pass
    return str(val)

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
