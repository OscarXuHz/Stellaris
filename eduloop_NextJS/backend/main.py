"""FastAPI backend for EduLoop — wraps the Python agents as REST endpoints.

Run from the eduloop_NextJS/ root:
    uvicorn backend.main:app --reload --port 8000
"""

from __future__ import annotations

import sys
import os
from pathlib import Path

# Ensure project root (eduloop_NextJS/) is on sys.path
# and is the working directory so relative paths (./data/vector_db) resolve.
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
os.chdir(_ROOT)

from dotenv import load_dotenv
load_dotenv(_ROOT / ".env")

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any

from agents.teaching_agent import TeachingAgent
from agents.assessment_agent import AssessmentAgent
from knowledge_base.rag_retriever import DSERetriever
from config.config import DatabaseConfig, MiniMaxConfig

# ── App ────────────────────────────────────────────────────────────────
app = FastAPI(title="EduLoop API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    # Allow Next.js dev server on any typical port
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Singletons (initialised once at startup) ──────────────────────────
rag: DSERetriever | None = None
teaching_agent: TeachingAgent | None = None
assessment_agent: AssessmentAgent | None = None


@app.on_event("startup")
async def startup() -> None:
    global rag, teaching_agent, assessment_agent

    import os
    os.environ.setdefault("HF_HUB_OFFLINE", "1")          # Skip HF network check
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

    rag = DSERetriever(
        persist_directory=DatabaseConfig.VECTOR_DB_PATH,
        collection_name=DatabaseConfig.CHROMA_COLLECTION,
        embedding_model=DatabaseConfig.EMBEDDING_MODEL,
    )
    api_key = MiniMaxConfig.MINIMAX_API_KEY or ""
    teaching_agent  = TeachingAgent(minimax_api_key=api_key, rag_vectordb=rag)
    assessment_agent = AssessmentAgent(minimax_api_key=api_key, rag_vectordb=rag)
    print(f"✅  EduLoop API ready — MiniMax key {'SET' if api_key else 'NOT SET'}")


# ── Request models ─────────────────────────────────────────────────────
class TeachRequest(BaseModel):
    topic: str
    level: str = "intermediate"
    student_profile: dict[str, Any] = {}


class AssessRequest(BaseModel):
    topic: str
    question_text: str
    student_answer: str
    difficulty: str = "intermediate"


class FormatRequest(BaseModel):
    raw_text: str
    topic: str


# ── Endpoints ──────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "rag_ready": rag is not None}


@app.post("/api/teach")
async def teach(req: TeachRequest):
    """Generate a structured lesson for a given topic."""
    if teaching_agent is None:
        raise HTTPException(503, "Agents not yet initialised")
    try:
        lesson = teaching_agent.generate_lesson(
            topic=req.topic,
            level=req.level,
            student_profile=req.student_profile,
        )
        return lesson
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/questions")
async def get_questions(
    topic: str = Query(..., description="DSE topic"),
    n: int = Query(3, ge=1, le=10, description="Number of questions"),
):
    """Retrieve past-paper questions and matching marking schemes from the RAG store."""
    if rag is None:
        raise HTTPException(503, "RAG not yet initialised")
    try:
        papers  = rag.retrieve(topic, k=n, where={"document_type": "paper"})
        marking = rag.retrieve(topic, k=n, where={"document_type": "marking_scheme"})
        if not papers:
            papers = rag.retrieve(topic, k=n)
        return {"questions": papers[:n], "marking": marking[:n]}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/format-questions")
async def format_questions(requests: list[FormatRequest]):
    """Batch-format raw OCR question texts into clean LaTeX markdown via MiniMax."""
    if teaching_agent is None:
        raise HTTPException(503, "Agents not yet initialised")
    formatted = []
    for r in requests:
        text = teaching_agent.format_question_latex(r.raw_text, r.topic)
        formatted.append({"original": r.raw_text, "formatted": text})
    return {"formatted": formatted}


@app.post("/api/assess")
async def assess(req: AssessRequest):
    """Evaluate a student's answer via MiniMax and return a diagnostic report."""
    if assessment_agent is None:
        raise HTTPException(503, "Agents not yet initialised")
    try:
        result = assessment_agent.evaluate(
            topic=req.topic,
            question_text=req.question_text,
            student_answer=req.student_answer,
            difficulty=req.difficulty,
        )
        return result
    except Exception as e:
        raise HTTPException(500, str(e))
