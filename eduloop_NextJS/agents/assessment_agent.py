"""Assessment Agent — calls MiniMax (Anthropic-compatible API) for evaluation.

Flow
────
1.  Receive the student's answer and the topic.
2.  Retrieve relevant marking-scheme and past-paper chunks from RAG.
3.  Build the system prompt via ``config.prompts.get_assessment_system_prompt``.
4.  Pack the student answer + RAG context into the user message.
5.  Call MiniMax-M2.5 through the Anthropic SDK.
6.  Parse the structured JSON reply that follows COMMUNICATION_PROTOCOL.
7.  Return the diagnostic report to the frontend / loop manager.
"""

from __future__ import annotations

import json
import uuid
import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional

import anthropic

from config.prompts import get_assessment_system_prompt
from config.config import MiniMaxConfig


# ── helpers ──────────────────────────────────────────────────────────

def _safe_json_parse(text: str) -> Optional[Dict[str, Any]]:
    """Try to extract a JSON object from an LLM response string."""
    text = text.strip()
    if text.startswith("```"):
        first_nl = text.index("\n") if "\n" in text else 3
        text = text[first_nl + 1:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                return None
    return None


# ── AssessmentAgent ──────────────────────────────────────────────────

class AssessmentAgent:
    """Evaluates student responses by sending them + marking schemes to MiniMax."""

    def __init__(self, minimax_api_key: str, rag_vectordb):
        self.api_key = minimax_api_key or ""
        self.rag = rag_vectordb
        self.assessment_history: List[Dict[str, Any]] = []

        self._client: Optional[anthropic.Anthropic] = None
        if self.api_key:
            self._client = anthropic.Anthropic(
                api_key=self.api_key,
                base_url=MiniMaxConfig.MINIMAX_BASE_URL,
            )
        self._model = MiniMaxConfig.MINIMAX_TEXT_MODEL

    # ── public API ───────────────────────────────────────────────────

    def evaluate(
        self,
        topic: str,
        question_text: str,
        student_answer: str,
        difficulty: str = "intermediate",
    ) -> Dict[str, Any]:
        """Evaluate a single student answer via MiniMax.

        Returns a dict following the ``assessment_to_orchestrator`` schema
        from ``config/prompts.py``.
        """

        # 1. Retrieve relevant marking schemes & papers from RAG ─────
        marking_chunks = self._retrieve(topic, doc_type="marking_scheme", k=5)
        paper_chunks   = self._retrieve(topic, doc_type="paper", k=3)

        # 2. System prompt (communication protocol) ──────────────────
        system_prompt = get_assessment_system_prompt(
            topic, student_answer, difficulty,
        )

        # 3. User message = question + answer + RAG marking schemes ──
        user_message = self._build_user_message(
            topic, question_text, student_answer, marking_chunks, paper_chunks,
        )

        # 4. Call MiniMax ────────────────────────────────────────────
        llm_output = self._call_llm(system_prompt, user_message)

        # 5. Package ────────────────────────────────────────────────
        result = {
            "assessment_id": f"assess_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}",
            "topic": topic,
            "difficulty": difficulty,
            "created_at": datetime.now().isoformat(),
            "student_answer": student_answer,
            "llm_response": llm_output,
            "rag_chunks_used": len(marking_chunks) + len(paper_chunks),
        }
        self.assessment_history.append(result)
        return result

    # ── RAG retrieval ────────────────────────────────────────────────

    def _retrieve(
        self, topic: str, doc_type: str | None = None, k: int = 5,
    ) -> List[Dict[str, Any]]:
        if self.rag is None:
            return []
        where = {"document_type": doc_type} if doc_type else None
        try:
            return self.rag.retrieve(topic, k=k, where=where)
        except Exception:
            try:
                return self.rag.retrieve(topic, k=k)
            except Exception:
                return []

    # ── prompt construction ──────────────────────────────────────────

    @staticmethod
    def _build_user_message(
        topic: str,
        question_text: str,
        student_answer: str,
        marking: List[Dict],
        papers: List[Dict],
    ) -> str:
        sections: List[str] = []

        sections.append(f"## Topic: {topic}\n")
        sections.append(f"### Question\n{question_text}\n")
        sections.append(f"### Student's Answer\n{student_answer}\n")

        if marking:
            sections.append("### Official Marking Schemes (from HKDSE)")
            for i, m in enumerate(marking, 1):
                src = m.get("source", "?")
                sections.append(f"**[MS {i} — {src}]**\n{m.get('text', '')}\n")

        if papers:
            sections.append("### Related Past-Paper Content")
            for i, p in enumerate(papers, 1):
                meta = p.get("metadata", {})
                label = f"DSE {meta.get('year', '?')} {meta.get('paper', '')}"
                sections.append(f"**[{label}]**\n{p.get('text', '')}\n")

        sections.append(
            "\n---\n"
            "Evaluate the student's answer against the marking schemes above.  "
            "Respond with the JSON format specified in your system prompt."
        )
        return "\n\n".join(sections)

    # ── LLM call ─────────────────────────────────────────────────────

    def _call_llm(self, system_prompt: str, user_message: str) -> Dict[str, Any]:
        if not self._client:
            return {
                "status": "error",
                "error": (
                    "No MiniMax API key configured.  "
                    "Set MINIMAX_API_KEY in your .env file to enable AI assessment."
                ),
            }

        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=4096,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )

            reply_text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    reply_text += block.text

            parsed = _safe_json_parse(reply_text)
            if parsed:
                return parsed
            else:
                return {
                    "status": "success",
                    "diagnostic_report": {
                        "strengths": [],
                        "knowledge_gaps": [],
                        "constructive_feedback": reply_text,
                        "misconception_analysis": "",
                    },
                    "_raw": True,
                }

        except anthropic.AuthenticationError:
            return {
                "status": "error",
                "error": "Invalid MiniMax API key.  Check MINIMAX_API_KEY in .env.",
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"LLM call failed: {e}",
                "_traceback": traceback.format_exc(),
            }

    # ── session helpers ──────────────────────────────────────────────

    def get_history(self) -> List[Dict[str, Any]]:
        return self.assessment_history
