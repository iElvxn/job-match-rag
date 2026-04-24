# Job Match RAG

A RAG (Retrieval-Augmented Generation) system that matches resumes to job postings using hybrid semantic search and LLM-powered analysis. Built as a course project for CSE 538 (NLP).

## How It Works

1. User uploads a resume (PDF)
2. Resume is parsed into plain text
3. Hybrid retrieval (BM25 + dense embeddings) searches 123K+ job postings
4. Cohere reranks top candidates to the most relevant chunks
5. Skills are extracted deterministically before hitting the LLM
6. GPT-4 generates a structured match analysis with exact quoted evidence from retrieved chunks
7. Results displayed in the Next.js frontend

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Next.js, TypeScript, Tailwind CSS |
| Backend | FastAPI (Python) |
| Vector DB | Pinecone (free tier) |
| Embeddings | OpenAI text-embedding-ada-002 |
| LLM | OpenAI GPT-4 |
| Reranking | Cohere Rerank API |
| PDF Parsing | PyPDF2 |
| Evaluation | RAGAS |

## Project Structure

```
job-match-rag/
├── frontend/                  # Next.js frontend
│   └── app/
├── backend/
│   ├── main.py                # FastAPI server
│   ├── rag/
│   │   ├── chunking.py        # Split job postings into semantic chunks
│   │   ├── indexing.py        # Embed + store chunks in Pinecone
│   │   ├── retrieval.py       # Hybrid BM25 + dense retrieval
│   │   ├── reranker.py        # Cohere reranking
│   │   ├── skill_extractor.py # Deterministic skill extraction
│   │   └── generation.py      # LLM analysis with evidence-span citations
│   ├── utils/
│   │   └── pdf_parser.py      # Resume PDF parsing
│   └── evaluation/
│       ├── ragas_eval.py      # RAGAS evaluation pipeline
│       └── ablation.py        # Ablation study conditions
├── data/                      # Dataset lives here (not tracked by git)
├── scripts/
│   └── download_data.py       # Download LinkedIn job postings from Kaggle
├── requirements.txt
└── .env                       # API keys (not tracked)
```

## Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- OpenAI API key
- Pinecone API key
- Cohere API key
- Kaggle account (for dataset download)

### Backend

```bash
python -m venv venv
source venv/Scripts/activate   # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt

cp .env.example .env
# Edit .env with your API keys
```

### Dataset

The dataset is the [LinkedIn Job Postings (2023-2024)](https://www.kaggle.com/datasets/arshkon/linkedin-job-postings) dataset from Kaggle (~123K job postings).

1. Create a Kaggle account and generate an API token (kaggle.com → Settings → API → Create New Token)
2. Place `kaggle.json` at `~/.kaggle/kaggle.json`
3. Run the download script:

```bash
python scripts/download_data.py
```

### Index Job Postings (one-time)

```bash
python scripts/run_indexing.py
```

### Run the Backend

```bash
uvicorn backend.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API

### `POST /analyze`

Upload a resume PDF and receive matched job postings with citation-grounded analysis.

**Request:** `multipart/form-data` with a `file` field (PDF)

**Response:**
```json
{
  "retrieved_jobs": [...],
  "skill_matrix": {...},
  "analysis": {...}
}
```

## Evaluation

- **RAGAS metrics** — faithfulness, answer relevancy, context precision, citation rate
- **Ablation study** — No RAG / Dense only / BM25 only / Hybrid / Hybrid + Rerank
