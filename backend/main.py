from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from backend.utils.pdf_parser import parse_resume

load_dotenv()

app = FastAPI(title="Job Match RAG")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


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

    # Pipeline grows here as components are built:
    # chunks   = hybrid_retrieve(resume_text)
    # chunks   = rerank(resume_text, chunks)
    # skills   = extract_skills(resume_text, chunks)
    # analysis = generate(resume_text, chunks, skills)

    return {"resume_text": resume_text}
