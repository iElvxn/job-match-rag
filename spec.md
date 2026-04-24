# Job Match RAG - Project Specification

## Overview

A full-stack RAG (Retrieval-Augmented Generation) system that matches a
user's resume against a corpus of 50K+ real job postings. The system
retrieves the most semantically similar job posting chunks and generates
a citation-grounded match analysis using an LLM. Every claim in the
generated output is explicitly traced back to specific retrieved chunks
with exact quoted text, making hallucination structurally impossible and
retrieval genuinely essential.

---

## Problem Statement

Job seekers struggle to efficiently identify which roles they are best
suited for across thousands of postings. Generic LLMs can suggest job
types but cannot:
- Return real specific job postings a user can apply to
- Ground claims in verifiable current job market data
- Provide evidence-based skill gap analysis cited to exact source text
- Synthesize patterns across multiple real job postings simultaneously
- Count skill frequencies deterministically without hallucination

This system solves all five problems through genuine RAG architecture
with chunk-level retrieval, hybrid search, structured skill extraction,
and citation-grounded generation.

---

## System Architecture

```
User uploads resume (PDF)
        ↓
FastAPI Backend
        ↓
PDF Parser (PyPDF2)
        ↓
Skill Extractor (pre-LLM structured extraction)
        ↓
Embedding Model (OpenAI text-embedding-ada-002)
        ↓
Hybrid Retrieval (BM25 + Dense) → top 30-50 chunks
        ↓
Reranker (Cohere Rerank API) → top 10-15 chunks
        ↓
Chunk Grouper → top 5 jobs with relevant chunks
        ↓
Structured Skill Matrix (deterministic pre-computation)
        ↓
LLM (GPT-4) with evidence-span citation prompt
        ↓
Structured JSON analysis with exact quoted evidence
        ↓
Next.js Frontend
```

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Frontend | Next.js + TypeScript + Tailwind CSS | Team already knows it |
| Backend | FastAPI (Python) | Industry standard for ML backends |
| Vector Database | Pinecone (free tier) | Purpose-built for vector search, no infra setup |
| Embeddings | OpenAI text-embedding-ada-002 | Strong semantic representation |
| LLM | OpenAI GPT-4 | Best instruction following for citation requirements |
| PDF Parsing | PyPDF2 | Simple, reliable, no external dependencies |
| RAG Framework | LangChain | Connects all pipeline components |
| Reranking | Cohere Rerank API (free tier) | Two-stage retrieval improves precision significantly |
| Evaluation | RAGAS | Industry standard RAG evaluation framework |
| Dataset | LinkedIn Job Postings (Kaggle) | 50K+ real jobs, rich structured fields, no scraping |

---

## Dataset

**Primary:** LinkedIn Job Postings dataset (Kaggle)
- 50K+ real job postings
- Fields: title, company, location, description, required skills,
  salary, experience level

**Indexing strategy:**
- Each job posting split into semantic chunks before indexing
- Full chunk text used for embedding generation
- Structured fields stored as Pinecone metadata

---

## Project Structure

```
job-match-rag/
├── frontend/
│   ├── components/
│   │   ├── ResumeUpload.tsx
│   │   ├── JobMatches.tsx
│   │   └── SkillGapCard.tsx
│   └── pages/
│       └── index.tsx
├── backend/
│   ├── main.py
│   ├── rag/
│   │   ├── indexing.py
│   │   ├── chunking.py
│   │   ├── retrieval.py
│   │   ├── reranker.py
│   │   ├── skill_extractor.py
│   │   └── generation.py
│   ├── utils/
│   │   ├── pdf_parser.py
│   │   └── preprocessor.py
│   └── evaluation/
│       ├── ragas_eval.py
│       └── ablation.py
├── data/
│   └── linkedin_jobs.csv
├── scripts/
│   └── run_indexing.py
├── requirements.txt
└── README.md
```

---

## Core Components

### 1. PDF Parser (`utils/pdf_parser.py`)

**Responsibility:** Extract and clean text from uploaded resume PDFs

**Input:** PDF file upload
**Output:** Clean normalized resume text string

**Requirements:**
- Handle various PDF formats and layouts
- Strip headers, footers, and formatting artifacts
- Normalize whitespace and special characters
- Return plain text suitable for embedding and skill extraction

**Why PyPDF2:**
Simple and reliable with no external service dependencies. For a course
project scope, it handles standard PDF resumes without the overhead of
a dedicated document parsing service.

---

### 2. Chunking Pipeline (`rag/chunking.py`)

**Responsibility:** Split job postings into semantic chunks before indexing

**Input:** Full job posting text and structured fields
**Output:** List of chunks with metadata

**Chunk types per job posting:**
```python
chunks = [
    {
        "chunk_id": "job_123_required",
        "job_id": "job_123",
        "chunk_type": "required_qualifications",
        "text": "5+ years Python experience, Kubernetes...",
        "metadata": {
            "title": "Senior SWE",
            "company": "Google",
            "chunk_type": "required_qualifications"
        }
    },
    {
        "chunk_id": "job_123_preferred",
        "job_id": "job_123",
        "chunk_type": "preferred_qualifications",
        "text": "Experience with ML systems preferred...",
    },
    {
        "chunk_id": "job_123_responsibilities",
        "job_id": "job_123",
        "chunk_type": "responsibilities",
        "text": "Design and implement distributed systems...",
    }
]
```

**Why chunk-level instead of document-level retrieval:**
Embedding a full job description (500-2000 words) produces a single
averaged vector that represents everything and nothing precisely. A
resume mentioning "Python" needs to match against the specific
qualifications section of a job, not a diluted average of the entire
posting including company boilerplate and benefits. Chunk-level
retrieval means the LLM sees only directly relevant evidence, reduces
noise in reasoning, and makes claims like "Kubernetes appears in 4/5
jobs" actually reliable because the match is precise not approximate.

---

### 3. Indexing Pipeline (`rag/indexing.py`)

**Responsibility:** One-time indexing of all job chunks into Pinecone

**Input:** linkedin_jobs.csv
**Output:** Populated Pinecone index with chunk-level vectors

**Requirements:**
- Load and preprocess all job postings
- Split each posting into semantic chunks
- Generate embeddings for each chunk
- Store in Pinecone with full metadata
- Handle rate limiting with batch processing
- Log progress and errors

**Why index at chunk level:**
Retrieval precision is determined at index time. If you index whole
documents you can never recover chunk-level precision at query time.
Getting this right once during indexing pays dividends throughout the
entire pipeline.

---

### 4. Skill Extractor (`rag/skill_extractor.py`)

**Responsibility:** Deterministically extract skills from resume and job
chunks BEFORE passing to LLM

**Input:** Resume text, list of retrieved job chunks
**Output:** Structured skill matrix

**Output structure:**
```python
skill_matrix = {
    "resume_skills": ["Python", "AWS", "React", "REST APIs"],
    "job_skill_matrix": {
        "job_123": {
            "title": "Senior SWE",
            "company": "Google",
            "required_skills": ["Python", "Kubernetes", "AWS"],
            "preferred_skills": ["ML experience", "GCP"]
        },
        "job_456": {
            "title": "ML Engineer",
            "company": "Meta",
            "required_skills": ["Python", "PyTorch", "AWS"],
            "preferred_skills": ["Kubernetes"]
        }
    },
    "skill_frequency": {
        "Python": {"count": 5, "jobs": ["job_123", "job_456", ...]},
        "Kubernetes": {"count": 4, "jobs": ["job_123", ...]},
        "PyTorch": {"count": 2, "jobs": ["job_456", ...]}
    },
    "resume_job_overlap": {
        "job_123": {
            "matched": ["Python", "AWS"],
            "missing": ["Kubernetes"],
            "match_score": 72
        }
    }
}
```

**Why extract skills before generation:**
Without pre-extraction, the LLM must simultaneously read text, identify
skills, count occurrences across multiple jobs, and generate analysis.
This is too much to ask reliably. LLMs make counting errors and can
hallucinate skill frequencies. By extracting skills programmatically
first, counting becomes deterministic not probabilistic. When the system
says "Python appears in 5/5 retrieved jobs" that is a computed fact not
an LLM guess. This is the single most effective way to prevent
hallucination on quantitative claims.

---

### 5. Retrieval Pipeline (`rag/retrieval.py`)

**Responsibility:** Find the most relevant job chunks for a given resume
using hybrid retrieval

**Input:** Resume text, k_candidates (default=30)
**Output:** Top ranked chunks grouped by job

**Retrieval strategy - Hybrid (BM25 + Dense):**

```python
def hybrid_retrieve(resume_text, k=30):
    # Dense retrieval - semantic similarity
    dense_results = pinecone.query(
        vector=embed(resume_text),
        top_k=k
    )

    # BM25 retrieval - keyword matching
    bm25_results = bm25_index.search(
        query=resume_text,
        top_k=k
    )

    # Combine with Reciprocal Rank Fusion
    combined = reciprocal_rank_fusion(
        dense_results,
        bm25_results
    )

    return combined[:k]
```

**Why hybrid over pure dense retrieval:**
The job matching domain is extremely keyword-sensitive. A resume listing
"React" needs to match job postings requiring "React.js" or "ReactJS".
A resume mentioning "k8s" needs to match jobs requiring "Kubernetes".
Pure embedding-based retrieval can miss these exact skill matches because
embeddings capture meaning not exact tokens. BM25 captures exact keyword
matches that embeddings miss. Hybrid combines both, achieving higher
recall than either alone. This is particularly important for technical
skill matching where exact terminology matters.

**Why hybrid is the default not just an ablation condition:**
In production RAG systems for technical domains, hybrid retrieval
consistently outperforms pure dense retrieval. We include pure BM25 and
pure dense in the ablation to prove this empirically, but use hybrid as
default because the theoretical justification is strong and the
implementation cost is low.

---

### 6. Reranker (`rag/reranker.py`)

**Responsibility:** Rerank top 30-50 retrieved chunks to top 10-15
using Cohere Rerank API

**Input:** Resume text, list of 30-50 candidate chunks
**Output:** Top 10-15 reranked chunks

**Why two-stage retrieval with reranking:**
First-stage retrieval (embedding search) optimizes for speed across
50K+ chunks. It is good at recall but imprecise at ranking. Reranking
is a second pass that optimizes for relevance using a more powerful
cross-encoder model that directly compares the query against each
candidate. Two-stage retrieval consistently outperforms single-stage
because each stage does what it is good at. Cohere Rerank has a free
tier making this a high-value low-cost addition that meaningfully
improves retrieval quality.

---

### 7. Generation Pipeline (`rag/generation.py`)

**Responsibility:** Generate evidence-span citation-grounded analysis
using retrieved chunks and pre-computed skill matrix

**Input:** Resume text, grouped job chunks, skill matrix
**Output:** Structured JSON with exact quoted evidence

**Prompt structure:**
```
You are a career analyst. Every claim you make must
include an exact quoted span from the retrieved job
chunks below. If you cannot quote it, do not say it.

PRE-COMPUTED SKILL MATRIX (deterministic facts):
{skill_matrix}

RETRIEVED JOB CHUNKS:
Chunk 1 [job_123 - Google Senior SWE - required_qualifications]:
"5+ years Python experience, proficiency in Kubernetes,
 distributed systems design, REST API development"

Chunk 2 [job_456 - Meta ML Engineer - required_qualifications]:
"Strong Python skills, PyTorch experience, production ML
 systems, experimentation frameworks"

[Chunks 3-15 follow same format]

CANDIDATE RESUME:
{resume_text}

Generate the following JSON. For every skill claim,
include the exact quoted text from the chunk above.
For frequency claims, use the pre-computed skill matrix.
For missing data, state explicitly what was not found.

{
  "matched_jobs": [
    {
      "rank": 1,
      "job_id": "job_123",
      "title": "Senior SWE",
      "company": "Google",
      "match_score": 85,
      "match_evidence": [
        {
          "skill": "Python",
          "resume_evidence": "your resume mentions Python",
          "job_evidence": "job_123 chunk 1: '5+ years Python experience'"
        }
      ],
      "salary": "not found in retrieved chunks",
      "location": "New York, NY"
    }
  ],
  "skill_analysis": {
    "strong_matches": [
      {
        "skill": "Python",
        "frequency": "5/5 retrieved jobs",
        "source": "pre-computed skill matrix",
        "sample_evidence": "job_123: '5+ years Python experience'"
      }
    ],
    "skill_gaps": [
      {
        "skill": "Kubernetes",
        "frequency": "4/5 retrieved jobs",
        "priority": "high",
        "evidence": [
          "job_123: 'proficiency in Kubernetes'",
          "job_789: 'container orchestration (Kubernetes) required'"
        ]
      }
    ]
  },
  "market_patterns": {
    "universal_requirements": [
      {
        "skill": "Python",
        "evidence": "appears in 5/5 retrieved jobs per skill matrix"
      }
    ],
    "common_requirements": [...],
    "emerging_requirements": [...]
  },
  "uncertainty_flags": [
    "Salary not found in 3/5 retrieved job chunks",
    "Experience requirements inconsistent across postings (2-7 years)",
    "Tech stack not specified in job_456 retrieved chunks"
  ],
  "learning_roadmap": [
    {
      "skill": "Kubernetes",
      "rationale": "appears in 4/5 retrieved jobs",
      "evidence": "job_123: 'proficiency in Kubernetes required'",
      "personalized_path": "Based on your existing AWS experience,
                            start with EKS (Kubernetes on AWS) as
                            a direct extension of skills you have"
    }
  ]
}

RULES:
- Every skill claim must include exact quoted text from chunks
- Use pre-computed skill matrix for all frequency counts
- Never invent text not present in retrieved chunks
- When data is missing, add to uncertainty_flags explicitly
- Match scores must derive from skill matrix overlap data
- Do not use outside knowledge about any company or role
```

**Why evidence spans over simple citations:**
Citing "Job 1" is weak because citations can be fabricated. Requiring
exact quoted text from retrieved chunks makes hallucination immediately
auditable. If the LLM quotes text that does not exist in the retrieved
chunks, it is detectable by anyone. This turns the system from
"probably grounded" to "verifiably grounded."

**Why the LLM cannot function without retrieval:**
The prompt requires chunk IDs, exact chunk quotes, and counts from the
pre-computed skill matrix. Without retrieved chunks there are no chunk
IDs to reference, no text to quote, and no skill matrix to reason from.
The output format is literally impossible to produce without retrieval.

**Why explicit uncertainty flagging:**
Silent hallucination is worse than acknowledged uncertainty. If salary
is not in the retrieved chunks, guessing a range is a hallucination
that damages user trust. Saying "salary not found in retrieved chunks"
is honest and maintains the integrity of the grounding guarantee.

---

### 8. FastAPI Backend (`backend/main.py`)

**Responsibility:** API layer orchestrating the full RAG pipeline

**Endpoints:**

```
POST /analyze
  Input: PDF file upload
  Output: {
    "retrieved_jobs": [...],
    "skill_matrix": {...},
    "analysis": {...}
  }

GET /health
  Output: {"status": "ok"}
```

**Pipeline execution order:**
```python
@app.post("/analyze")
async def analyze(file: UploadFile):
    # Step 1: Parse resume
    resume_text = parse_resume(file)

    # Step 2: Hybrid retrieval (top 30 chunks)
    candidate_chunks = hybrid_retrieve(resume_text, k=30)

    # Step 3: Rerank (top 10-15 chunks)
    reranked_chunks = rerank(resume_text, candidate_chunks)

    # Step 4: Group chunks by job
    grouped_jobs = group_by_job(reranked_chunks)

    # Step 5: Extract skills deterministically
    skill_matrix = extract_skills(resume_text, grouped_jobs)

    # Step 6: Generate citation-grounded analysis
    analysis = generate(resume_text, reranked_chunks, skill_matrix)

    return {
        "retrieved_jobs": grouped_jobs,
        "skill_matrix": skill_matrix,
        "analysis": analysis
    }
```

---

### 9. Frontend (`frontend/`)

**Responsibility:** Clean simple UI for resume upload and results display

**Components:**

`ResumeUpload.tsx`
- Drag and drop PDF upload
- File validation (PDF only, size limit)
- Loading state during processing

`JobMatches.tsx`
- Display top 5 matched job postings
- Match score with evidence tooltip
- Company, title, location, salary
- Apply Now button
- Uncertainty flags displayed clearly

`SkillGapCard.tsx`
- Strong matches with quoted evidence spans
- Skill gaps with priority and quoted evidence
- Market patterns (universal/common/emerging)
- Personalized learning roadmap
- Uncertainty and absence flags

---

## Evaluation Framework

### Layer 1: Retrieval Quality

**Goal:** Are the retrieved chunks actually relevant to the resume?

**Ground truth generation:**
Use GPT-4 to label relevance of chunk/resume pairs (0-3 scale)
for 30 test resumes

**Metrics:**
- Precision@K (K=5,10,15)
- Recall
- F1 Score
- NDCG
- MRR (Mean Reciprocal Rank)

**Why these metrics over accuracy:**
The dataset contains 50K+ job postings meaning only a tiny fraction
are relevant to any given resume. Accuracy would be artificially high
(99%+) even if the system retrieves nothing useful because of class
imbalance. Precision, Recall, and F1 measure actual retrieval quality
independent of class distribution. NDCG additionally rewards systems
that rank more relevant chunks higher.

---

### Layer 2: Generation Quality

**Goal:** Is the LLM output grounded in retrieved chunks?

**Tool:** RAGAS framework

**Metrics:**
- Faithfulness — are claims grounded in retrieved chunks?
- Answer Relevancy — does output address the resume?
- Context Precision — are retrieved chunks actually used?
- Context Recall — did retrieval capture needed information?
- Citation Rate — percentage of claims with exact quoted evidence
- Hallucination Rate — claims not traceable to retrieved chunks

**Why faithfulness is the most critical metric:**
Your system's core value proposition is grounded verifiable analysis.
Faithfulness directly measures whether the LLM is reasoning from
retrieved content or hallucinating. A high faithfulness score is the
strongest possible evidence that your system is genuine RAG.

---

### Layer 3: Ablation Study

**Goal:** Empirically prove each design decision improves performance

**Conditions:**

| Condition | Description |
|---|---|
| No RAG baseline | LLM only, no retrieved context |
| Dense only | Embedding-based retrieval, no BM25 |
| BM25 only | Keyword retrieval, no embeddings |
| Hybrid no rerank | BM25 + dense, no reranking |
| Hybrid + rerank | Full system (primary) |
| Document-level | Full documents not chunks |
| Chunk-level | Chunks (primary) |

**Why run this many conditions:**
Each condition isolates one design decision. This lets you make specific
claims like "hybrid retrieval improves Precision@5 by X% over dense
alone" or "chunk-level retrieval improves faithfulness by Y% over
document-level." These specific claims are what distinguish a serious
evaluation from a vague comparison.

**Results table to produce:**

| Metric | No RAG | Dense | BM25 | Hybrid | Hybrid+Rerank |
|---|---|---|---|---|---|
| Faithfulness | - | - | - | - | - |
| Citation Rate | - | - | - | - | - |
| Hallucination Rate | - | - | - | - | - |
| Precision@5 | - | - | - | - | - |
| Human Score (1-5) | - | - | - | - | - |

---

### Layer 4: Human Evaluation

**Goal:** Is the system actually useful to real people?

**Protocol:**
- 15 different resumes
- 3 human raters evaluate outputs blindly
- Raters do not know which condition they are rating

**Rubric (1-5 scale):**
1. Are retrieved jobs relevant to the resume?
2. Are matched skills accurate?
3. Are skill gaps correct?
4. Are quoted evidence spans believable?
5. Would you use this in your job search?
6. Do you trust the analysis?

**Statistical analysis:**
- Cohen's Kappa for inter-annotator agreement
- Two-sample t-test for RAG vs no RAG significance
- p-value threshold: 0.05

**Why blind evaluation:**
Raters knowing which output is RAG vs no RAG introduces bias. Blind
evaluation ensures scores reflect genuine quality differences not
expectation effects.

---

### Layer 5: Error Analysis

**Goal:** Document and categorize system failures honestly

**Failure categories:**

1. Retrieval failures
   - Wrong chunks retrieved
   - Root cause: sparse resume, niche skills, vocabulary mismatch

2. Generation failures
   - LLM quotes text not in retrieved chunks
   - Inconsistent JSON structure
   - Citation format errors

3. Edge cases
   - Very short resumes (insufficient signal for embedding)
   - Career changers (mixed domain signals confuse retrieval)
   - Highly specialized roles (insufficient dataset coverage)

4. Absence handling failures
   - Missing salary data not flagged
   - Inconsistent experience requirements not surfaced

**Why document failures:**
Honest error analysis demonstrates intellectual rigor. Professors and
symposium judges are more impressed by a team that understands system
limitations than one that only reports successes. It also shows you
understand the gap between a research prototype and a production system.

---

## Why This Is Genuine RAG

**The critical test:**
Remove the retrieval step. Can the system produce the same output format?

No. Because:
- There are no chunk IDs to reference
- There is no text to quote as evidence spans
- There is no skill matrix (computed from retrieved chunks)
- There are no job-specific counts or frequencies
- The output format is structurally impossible without retrieval

This is the strongest possible guarantee that retrieval is essential
not decorative.

---

## Why This Is Better Than Just Asking An LLM

| Capability | LLM Alone | This System |
|---|---|---|
| Real job postings to apply to | ❌ | ✅ |
| Current job market data | ❌ | ✅ |
| Verifiable grounded claims | ❌ | ✅ |
| Exact quoted evidence spans | ❌ | ✅ |
| Deterministic skill frequency counts | ❌ | ✅ |
| Explicit uncertainty flagging | ❌ | ✅ |
| Search across 50K+ postings instantly | ❌ | ✅ |
| Hallucination structurally prevented | ❌ | ✅ |
| Auditable reasoning | ❌ | ✅ |

---

## Key Design Decisions With Intuition

### Chunk-level over document-level retrieval

**Decision:** Split each job posting into required qualifications,
preferred qualifications, and responsibilities chunks before indexing.

**Intuition:** Embedding a full 2000-word job description averages the
meaning of everything including company boilerplate, benefits, and
equal opportunity statements. The resume needs to match against the
specific qualifications section not an averaged representation of the
whole document. Chunk-level retrieval is like finding the right page
in a book instead of just the right book.

---

### Hybrid retrieval as default

**Decision:** Combine BM25 keyword search with dense embedding search
using Reciprocal Rank Fusion.

**Intuition:** Technical skill matching is simultaneously semantic and
exact. "Machine learning" and "ML" mean the same thing semantically
and embeddings handle this well. But "React" and "React.js" are exact
tokens that embeddings might handle inconsistently. BM25 catches exact
matches that embeddings miss. Hybrid gets the best of both worlds.

---

### Two-stage retrieval with reranking

**Decision:** Retrieve 30 candidate chunks then rerank to top 10-15
using Cohere before passing to LLM.

**Intuition:** Embedding search is fast but approximate. It is like a
broad filter that gets you in the right neighborhood. Reranking is a
precise second pass that directly compares the resume against each
candidate chunk using a more powerful model. Two-stage is standard in
production search systems because each stage does what it is best at —
speed first, precision second.

---

### Structured skill extraction before generation

**Decision:** Programmatically extract and count skills from resume and
job chunks before passing to LLM.

**Intuition:** Asking an LLM to simultaneously read 15 chunks, identify
all skills, count occurrences across jobs, and generate analysis is too
much to do reliably. LLMs make arithmetic and counting errors. By
pre-computing the skill matrix deterministically, counting becomes a
fact not a guess. The LLM then focuses on reasoning and language which
is what it does best.

---

### Evidence spans over simple citations

**Decision:** Require exact quoted text from retrieved chunks rather
than just job number references.

**Intuition:** Citing "Job 1" is unverifiable because the LLM can
fabricate a citation to a real job ID. Quoting exact text from a
retrieved chunk is auditable because anyone can check whether the
quoted text exists in the retrieved content. Evidence spans turn
hallucination from invisible to immediately detectable.

---

### Explicit uncertainty flagging

**Decision:** When data is missing or inconsistent, explicitly flag it
rather than fill in with guesses.

**Intuition:** Silent hallucination is worse than acknowledged
uncertainty. If salary is not in the retrieved chunks, guessing a
salary range is a hallucination that damages user trust. Saying
"salary not found in retrieved postings" is honest and maintains the
integrity of the grounding guarantee. Real RAG systems do not guess
when they do not know.

---

### GPT-4 over GPT-3.5

**Decision:** Use GPT-4 for generation despite higher cost.

**Intuition:** The prompt requires complex instruction following —
producing structured JSON, maintaining citation format across 15+
chunks, following uncertainty rules, and generating personalized
reasoning simultaneously. GPT-3.5 is inconsistent at this level of
instruction complexity. GPT-4 is significantly more reliable at
following multi-constraint prompts which is essential when the output
format is the foundation of your evaluation.

---

### Pinecone over pgvector

**Decision:** Use Pinecone managed vector database over pgvector with
PostgreSQL.

**Intuition:** pgvector requires setting up and managing a PostgreSQL
instance, configuring the extension, and handling index management
manually. Pinecone is a managed service with a free tier that works
out of the box. For a research prototype with a 5-week timeline,
infrastructure setup time is better spent on the RAG pipeline itself.
Both are legitimate production choices — Pinecone just has lower
operational overhead for this scope.

---

## Timeline

| Week | Tasks |
|---|---|
| Now → Mar 30 | Finalize proposal, professor approval |
| Mar 30 → Apr 6 | Dataset download, cleaning, chunking, indexing |
| Apr 6 → Apr 13 | Hybrid retrieval, reranker, skill extractor |
| Apr 13 → Apr 20 | Generation pipeline, prompt engineering, FastAPI |
| Apr 20 → Apr 27 | Frontend, RAGAS evaluation, ablation study |
| Apr 27 → May 4 | Human evaluation, error analysis, writeup, polish |

---

## Team Split

| Person 1 | Person 2 |
|---|---|
| Data cleaning + chunking + indexing | PDF parser + FastAPI setup |
| Hybrid retrieval + reranker | Skill extractor + generation |
| Ablation study | RAGAS evaluation |
| Frontend | Human evaluation + error analysis |

---

## Environment Variables

```
OPENAI_API_KEY=
PINECONE_API_KEY=
PINECONE_ENV=
PINECONE_INDEX_NAME=job-postings
COHERE_API_KEY=
```

---

## Priority Implementation Order

Given 5 weeks and 2 people, implement in this order:

**Must implement (core system):**
1. PDF parser
2. Chunking pipeline
3. Hybrid retrieval
4. Skill extractor
5. Evidence-span generation prompt
6. Uncertainty flagging
7. FastAPI backend
8. Basic frontend

**Implement after core is working:**
9. Reranker (Cohere) — defer until pre-evaluation; skip for initial end-to-end pipeline
10. RAGAS evaluation
11. Ablation study
12. Human evaluation

**Implement if ahead of schedule:**
13. Resume language alignment suggestions
14. Polished frontend UI
15. Extended error analysis
