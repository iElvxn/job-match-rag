from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from backend.utils.pdf_parser import parse_resume
from backend.rag.indexing import get_index
from backend.rag.retrieval import load_bm25, hybrid_retrieve
from backend.rag.skill_extractor import get_skill_gap
from backend.rag.generation import generate_analysis

load_dotenv()

app = FastAPI(title="Job Match RAG")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

index = get_index()
bm25, chunks = load_bm25()
chunk_lookup = {c["chunk_id"]: c["text"] for c in chunks}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze")
async def analyze(file: UploadFile):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF.")

    try:
        resume_text = parse_resume(await file.read())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    results    = hybrid_retrieve(resume_text, index, bm25, chunks)
    skill_data = get_skill_gap(resume_text, results, chunk_lookup)
    analysis   = generate_analysis(resume_text, results, skill_data, chunk_lookup)

    # Pipeline grows here as components are built:
    # results = rerank(resume_text, results)

    return {
        "matches":    results,
        "skill_data": skill_data,
        "analysis":   analysis,
    }
