# Job Match RAG

A RAG (Retrieval-Augmented Generation) system that matches resumes to job postings using semantic search and LLM-powered analysis. Built as a course project for CSE 538 (NLP).

## How It Works

1. User uploads a resume (PDF)
2. Resume is parsed into plain text
3. Resume text is embedded using OpenAI `text-embedding-ada-002`
4. Pinecone searches 50K+ job postings for the most semantically similar matches
5. Top 5 retrieved job postings are injected into an LLM prompt
6. GPT-4 generates a structured match analysis grounded strictly in retrieved postings
7. Results displayed in the Next.js frontend

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Next.js, TypeScript, Tailwind CSS |
| Backend | FastAPI (Python) |
| Vector DB | Pinecone (free tier) |
| Embeddings | OpenAI text-embedding-ada-002 |
| LLM | OpenAI GPT-4 |
| PDF Parsing | PyPDF2 |
| RAG Framework | LangChain |
| Evaluation | RAGAS |

## Project Structure

```
job-match-rag/
├── frontend/                # Next.js frontend
│   └── app/
├── backend/
│   ├── main.py              # FastAPI server
│   ├── rag/
│   │   ├── indexing.py       # Embed + store jobs in Pinecone
│   │   ├── retrieval.py      # Semantic search
│   │   └── generation.py     # LLM analysis with RAG
│   ├── utils/
│   │   ├── pdf_parser.py     # Resume PDF parsing
│   │   └── preprocessor.py   # Job posting text cleaning
│   └── evaluation/
│       ├── ragas_eval.py     # RAGAS evaluation pipeline
│       └── ablation.py       # Baseline comparisons
├── data/                     # Job posting dataset (not tracked)
├── scripts/
│   └── run_indexing.py       # One-time indexing script
├── requirements.txt
└── .env                      # API keys (not tracked)
```

## Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- OpenAI API key
- Pinecone API key

### Backend

```bash
# Create and activate virtual environment
python -m venv venv
source venv/Scripts/activate   # Windows
# source venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys

# Run the backend
uvicorn backend.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Indexing Job Data

Before using the system, index the job postings into Pinecone:

```bash
# Place linkedin_jobs.csv in data/
python scripts/run_indexing.py
```

## API

### `POST /analyze`

Upload a resume PDF and receive matched job postings with analysis.

**Request:** `multipart/form-data` with a `file` field (PDF)

**Response:**
```json
{
  "matches": [
    {
      "job_title": "...",
      "company": "...",
      "similarity_score": 0.92,
      "matched_skills": ["Python", "NLP", "..."],
      "description": "..."
    }
  ],
  "skill_gaps": ["..."],
  "recommendations": ["..."]
}
```

## Evaluation

The system is evaluated using:

- **RAGAS metrics** — faithfulness, answer relevancy, context precision
- **Ablation studies** — comparing dense retrieval (RAG) against no-retrieval baseline and BM25 retrieval
