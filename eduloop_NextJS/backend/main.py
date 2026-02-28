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
from agents.orchestrator_agent import OrchestratorAgent
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
orchestrator_agent: OrchestratorAgent | None = None


@app.on_event("startup")
async def startup() -> None:
    global rag, teaching_agent, assessment_agent, orchestrator_agent

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
    orchestrator_agent = OrchestratorAgent(
        minimax_api_key=api_key,
        teaching_agent=teaching_agent,
        assessment_agent=assessment_agent,
    )
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


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    topic: str = ""
    history: list[ChatMessage] = []


# ── Endpoints ──────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "rag_ready": rag is not None}


@app.post("/api/teach")
def teach(req: TeachRequest):
    """Generate a structured lesson for a given topic.
    Defined as sync def so FastAPI runs it in a thread pool — prevents
    the blocking Anthropic SDK call from stalling the event loop.
    """
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
def get_questions(
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
def format_questions(requests: list[FormatRequest]):
    """Batch-format raw OCR question texts into clean LaTeX markdown via MiniMax.

    Questions are processed in parallel (ThreadPoolExecutor) to cut latency from
    N × ~15s  →  ~15s total (wall-clock).

    Each result now includes ``question`` (cleaned) and ``answer`` (separated).
    """
    if teaching_agent is None:
        raise HTTPException(503, "Agents not yet initialised")

    from concurrent.futures import ThreadPoolExecutor, as_completed
    import traceback as _tb

    def _fmt(r: FormatRequest) -> dict:
        try:
            result = teaching_agent.format_question_latex(r.raw_text, r.topic)  # type: ignore[union-attr]
            return {
                "original": r.raw_text,
                "formatted": result["question"],
                "answer": result.get("answer", ""),
            }
        except Exception:
            _tb.print_exc()
            return {"original": r.raw_text, "formatted": r.raw_text, "answer": ""}

    # Run all formatting calls concurrently (max 6 threads)
    with ThreadPoolExecutor(max_workers=min(len(requests), 6)) as pool:
        futures = {pool.submit(_fmt, r): i for i, r in enumerate(requests)}
        results: list[dict | None] = [None] * len(requests)
        for fut in as_completed(futures):
            results[futures[fut]] = fut.result()

    return {"formatted": results}


@app.post("/api/assess")
def assess(req: AssessRequest):
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


@app.post("/api/chat")
def chat(req: ChatRequest):
    """Chat with the Orchestrator, which coordinates Teaching + Assessment agents."""
    if orchestrator_agent is None:
        raise HTTPException(503, "Agents not yet initialised")
    try:
        history = [{"role": m.role, "content": m.content} for m in req.history]
        result = orchestrator_agent.chat(
            message=req.message,
            topic=req.topic,
            history=history,
        )
        return result
    except Exception as e:
        raise HTTPException(500, str(e))


# ── Paraphrase endpoint (for natural-sounding TTS) ─────────────────────

class ParaphraseRequest(BaseModel):
    raw_content: str
    topic: str = ""
    context: str = "lesson"  # "lesson" | "practice"


@app.post("/api/paraphrase")
def paraphrase(req: ParaphraseRequest):
    """Use MiniMax LLM to re-paraphrase content into natural spoken narration."""
    if teaching_agent is None or not teaching_agent._client:
        raise HTTPException(503, "Agents not yet initialised")
    try:
        system = (
            "You are a warm, encouraging HKDSE Mathematics tutor recording a voice-over narration. "
            "Take the following lesson/practice content and re-write it as natural, conversational spoken English — "
            "as if you are personally explaining it to a student sitting across from you.\n\n"
            "Rules:\n"
            "- Do NOT read content verbatim. Paraphrase it in your own words.\n"
            "- Replace ALL LaTeX/math notation with spoken equivalents (e.g. '$x^2$' → 'x squared', "
            "'$\\frac{a}{b}$' → 'a over b', '$$...$$' → describe the equation in words).\n"
            "- Keep it under 500 words so the audio is 2-3 minutes.\n"
            "- Use a supportive, encouraging tone. Add verbal cues: 'Now, here\'s the key idea...', "
            "'Let me walk you through this...', 'A common mistake students make is...'\n"
            "- Do NOT include any markdown, LaTeX, formatting, or JSON. Output ONLY the spoken text.\n"
            "- End with a brief motivational sentence."
        )
        user_msg = f"Topic: {req.topic}\nContext: {req.context}\n\nContent to paraphrase:\n\n{req.raw_content[:4000]}"

        response = teaching_agent._client.messages.create(
            model=teaching_agent._model,
            max_tokens=2048,
            system=system,
            messages=[{"role": "user", "content": user_msg}],
        )
        reply = "".join(
            b.text for b in response.content
            if getattr(b, "type", None) == "text"
        )
        return {"paraphrased": reply.strip()}
    except Exception as e:
        raise HTTPException(500, f"Paraphrase failed: {e}")


# ── MiniMax TTS + Video endpoints ──────────────────────────────────────

class TTSRequest(BaseModel):
    text: str
    voice_id: str = "English_Insightful_Speaker"
    speed: float = 1.0

class VideoRequest(BaseModel):
    prompt: str
    duration: int = 6


@app.post("/api/tts")
def text_to_speech(req: TTSRequest):
    """Generate speech audio via MiniMax T2A API. Returns hex-encoded mp3."""
    import urllib.request, json as _json

    api_key = MiniMaxConfig.MINIMAX_API_KEY
    if not api_key:
        raise HTTPException(503, "MiniMax API key not configured")

    payload = {
        "model": "speech-2.8-hd",
        "text": req.text,
        "stream": False,
        "language_boost": "English",
        "output_format": "hex",
        "voice_setting": {
            "voice_id": req.voice_id,
            "speed": req.speed,
            "vol": 1,
            "pitch": 0,
        },
        "audio_setting": {
            "sample_rate": 32000,
            "bitrate": 128000,
            "format": "mp3",
            "channel": 1,
        },
    }

    body = _json.dumps(payload).encode()
    http_req = urllib.request.Request(
        "https://api.minimax.io/v1/t2a_v2",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        resp = urllib.request.urlopen(http_req, timeout=60)
        data = _json.loads(resp.read())
        if data.get("base_resp", {}).get("status_code", -1) != 0:
            raise HTTPException(502, data.get("base_resp", {}).get("status_msg", "TTS failed"))
        audio_hex = data.get("data", {}).get("audio", "")
        extra = data.get("extra_info", {})
        return {
            "audio_hex": audio_hex,
            "audio_length_ms": extra.get("audio_length", 0),
            "format": extra.get("audio_format", "mp3"),
        }
    except urllib.error.URLError as e:
        raise HTTPException(502, f"TTS request failed: {e}")


@app.post("/api/video")
def generate_video(req: VideoRequest):
    """Create a MiniMax video generation task. Returns task_id for polling."""
    import urllib.request, json as _json

    api_key = MiniMaxConfig.MINIMAX_API_KEY
    if not api_key:
        raise HTTPException(503, "MiniMax API key not configured")

    payload = {
        "model": "MiniMax-Hailuo-2.3",
        "prompt": req.prompt,
        "prompt_optimizer": True,
        "duration": req.duration,
        "resolution": "768P",
    }

    body = _json.dumps(payload).encode()
    http_req = urllib.request.Request(
        "https://api.minimax.io/v1/video_generation",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        resp = urllib.request.urlopen(http_req, timeout=30)
        data = _json.loads(resp.read())
        if data.get("base_resp", {}).get("status_code", -1) != 0:
            raise HTTPException(502, data.get("base_resp", {}).get("status_msg", "Video generation failed"))
        return {"task_id": data.get("task_id", "")}
    except urllib.error.URLError as e:
        raise HTTPException(502, f"Video request failed: {e}")


@app.get("/api/video/{task_id}")
def get_video_status(task_id: str):
    """Poll the status of a MiniMax video generation task."""
    import urllib.request, json as _json

    api_key = MiniMaxConfig.MINIMAX_API_KEY
    if not api_key:
        raise HTTPException(503, "MiniMax API key not configured")

    url = f"https://api.minimax.io/v1/query/video_generation?task_id={task_id}"
    http_req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {api_key}"},
        method="GET",
    )
    try:
        resp = urllib.request.urlopen(http_req, timeout=15)
        data = _json.loads(resp.read())
        status = data.get("status", "unknown")
        file_id = data.get("file_id", "")
        # If done, also fetch the download URL
        download_url = ""
        if status == "Success" and file_id:
            dl_url = f"https://api.minimax.io/v1/files/retrieve?file_id={file_id}"
            dl_req = urllib.request.Request(
                dl_url,
                headers={"Authorization": f"Bearer {api_key}"},
                method="GET",
            )
            dl_resp = urllib.request.urlopen(dl_req, timeout=15)
            dl_data = _json.loads(dl_resp.read())
            download_url = dl_data.get("file", {}).get("download_url", "")
        return {
            "task_id": task_id,
            "status": status,
            "file_id": file_id,
            "download_url": download_url,
        }
    except urllib.error.URLError as e:
        raise HTTPException(502, f"Video status check failed: {e}")
