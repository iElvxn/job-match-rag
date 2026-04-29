from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from backend.utils.pdf_parser import parse_resume
from backend.rag.indexing import get_index
from backend.rag.retrieval import load_bm25, hybrid_retrieve
from backend.rag.skill_extractor import get_skill_gap, compute_market_intelligence
from backend.rag.generation import generate_analysis

load_dotenv()

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Job Match RAG")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
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
@limiter.limit("3/minute")
async def analyze(request: Request, file: UploadFile):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF.")

    try:
        resume_text = parse_resume(await file.read())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    results      = hybrid_retrieve(resume_text, index, bm25, chunks)
    market_intel = compute_market_intelligence(results, chunk_lookup)
    skill_data   = get_skill_gap(resume_text, results, chunk_lookup, market_intel)
    analysis     = generate_analysis(resume_text, results, skill_data, chunk_lookup, market_intel)

    # Enrich analysis matches with real computed scores and description text
    resume_skills_set = set(skill_data["resume_skills"])
    job_skills_map = market_intel.get("job_skills_map", {})

    # Best chunk per job: highest RRF score determines which chunk text to show
    job_best_chunk: dict[str, tuple[float, str]] = {}
    for r in results:
        jid = r["metadata"].get("job_id", "")
        if jid not in job_best_chunk or r["score"] > job_best_chunk[jid][0]:
            job_best_chunk[jid] = (r["score"], r["chunk_id"])

    for match in analysis.get("matches", []):
        jid = match.get("job_id", "")
        job_skills = set(job_skills_map.get(jid, []))
        _, chunk_id = job_best_chunk.get(jid, (0, ""))
        match["rrf_score"]    = round(job_best_chunk.get(jid, (0,))[0], 4)
        match["skill_overlap"] = round(
            len(resume_skills_set & job_skills) / len(job_skills), 2
        ) if job_skills else 0.0
        match["description"] = chunk_lookup.get(chunk_id, "")

    # Pipeline grows here as components are built:
    # results = rerank(resume_text, results)

    return {
        "matches":      results,
        "skill_data":   skill_data,
        "market_intel": market_intel,
        "analysis":     analysis,
    }
