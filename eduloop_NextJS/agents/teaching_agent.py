"""Teaching Agent — calls MiniMax (Anthropic-compatible API) with RAG context.

Flow
────
1.  Retrieve relevant chunks from the ChromaDB vector store (curriculum,
    past papers, marking schemes).
2.  Build the system prompt via ``config.prompts.get_teaching_system_prompt``.
3.  Pack the RAG context into the user message.
4.  Call MiniMax-M2.5 through the Anthropic SDK.
5.  Parse the structured JSON reply that follows COMMUNICATION_PROTOCOL.
6.  Return the lesson dict to the frontend.
"""

from __future__ import annotations

import json
import uuid
import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional

import anthropic                                  # MiniMax Anthropic-compat SDK

from config.prompts import get_teaching_system_prompt
from config.config import MiniMaxConfig


# ── helpers ──────────────────────────────────────────────────────────

def _safe_json_parse(text: str) -> Optional[Dict[str, Any]]:
    """Try to extract a JSON object from an LLM response string."""
    # The model *should* respond with pure JSON, but sometimes wraps it
    # in markdown fences or adds preamble text.
    text = text.strip()
    # Strip markdown code fences
    if text.startswith("```"):
        first_nl = text.index("\n") if "\n" in text else 3
        text = text[first_nl + 1:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Attempt to find the first '{' and last '}'
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                return None
    return None


# ── TeachingAgent ────────────────────────────────────────────────────

class TeachingAgent:
    """Generates personalised lessons by sending RAG context to MiniMax-M2.5."""

    def __init__(self, minimax_api_key: str, rag_vectordb):
        self.api_key = minimax_api_key or ""
        self.rag = rag_vectordb
        self.session_lessons: List[Dict[str, Any]] = []

        # Anthropic client pointing at MiniMax's endpoint
        self._client: Optional[anthropic.Anthropic] = None
        if self.api_key:
            self._client = anthropic.Anthropic(
                api_key=self.api_key,
                base_url=MiniMaxConfig.MINIMAX_BASE_URL,
                timeout=90.0,   # MiniMax-M2.5 extended thinking can take up to ~90s
            )
        self._model = MiniMaxConfig.MINIMAX_TEXT_MODEL  # e.g. "MiniMax-M2.5"

    # ── public API ───────────────────────────────────────────────────

    def generate_lesson(
        self,
        topic: str,
        level: str,
        student_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate a full lesson by calling MiniMax with RAG context.

        Returns a dict whose ``"content"`` follows the communication-protocol
        schema defined in ``config/prompts.py``.
        """

        # 1. Retrieve RAG context ────────────────────────────────────
        curriculum_chunks = self._retrieve(topic, doc_type="curriculum", k=5)
        paper_chunks      = self._retrieve(topic, doc_type="paper", k=5)
        marking_chunks    = self._retrieve(topic, doc_type="marking_scheme", k=3)
        all_chunks = curriculum_chunks + paper_chunks + marking_chunks

        # 2. Build the student context for the system prompt ─────────
        student_context = {
            "level": level,
            "learning_style": student_profile.get("learning_style", "visual"),
            "previous_knowledge_gaps": student_profile.get("knowledge_gaps", []),
            "preferred_language": student_profile.get("language", "English"),
        }

        # 3. System prompt (from the communication protocol) ─────────
        system_prompt = get_teaching_system_prompt(topic, level, student_context)

        # 4. User message = RAG context + instruction ────────────────
        user_message = self._build_user_message(topic, level,
                                                 curriculum_chunks,
                                                 paper_chunks,
                                                 marking_chunks)

        # 5. Call MiniMax via Anthropic SDK ──────────────────────────
        llm_output = self._call_llm(system_prompt, user_message)

        # 6. Package into lesson dict ────────────────────────────────
        lesson = self._package_lesson(topic, level, llm_output, all_chunks)
        self.session_lessons.append(lesson)
        return lesson

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
        level: str,
        curriculum: List[Dict],
        papers: List[Dict],
        marking: List[Dict],
    ) -> str:
        """Pack all RAG chunks into a structured user message."""
        sections: List[str] = []

        sections.append(f"## Topic: {topic}  |  Level: {level}\n")

        # Curriculum context
        if curriculum:
            sections.append("### Curriculum Material (from HKDSE syllabus PDFs)")
            for i, c in enumerate(curriculum, 1):
                src = c.get("source", "?")
                sections.append(f"**[Chunk {i} — {src}]**\n{c.get('text', '')}\n")

        # Past-paper questions
        if papers:
            sections.append("### Past-Paper Questions")
            for i, p in enumerate(papers, 1):
                meta = p.get("metadata", {})
                label = f"DSE {meta.get('year', '?')} {meta.get('paper', '')}"
                sections.append(f"**[{label} — {p.get('source', '')}]**\n{p.get('text', '')}\n")

        # Marking schemes
        if marking:
            sections.append("### Marking Schemes")
            for i, m in enumerate(marking, 1):
                sections.append(f"**[MS — {m.get('source', '')}]**\n{m.get('text', '')}\n")

        sections.append(
            "\n---\n"
            "Using the DSE material above, generate the lesson JSON as specified "
            "in your system prompt.  Ensure every content_block is grounded in the "
            "retrieved material.  Do NOT invent questions that aren't in the data."
        )
        return "\n\n".join(sections)

    # ── LLM call ─────────────────────────────────────────────────────

    def _call_llm(self, system_prompt: str, user_message: str) -> Dict[str, Any]:
        """Call MiniMax-M2.5 via the Anthropic SDK.  Gracefully degrade."""
        if not self._client:
            return self._fallback_no_api(user_message)

        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=4096,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )

            # Extract only TextBlocks — skip ThinkingBlock / RedactedThinkingBlock
            reply_text = ""
            for block in response.content:
                if getattr(block, "type", None) == "text":
                    reply_text += block.text

            parsed = _safe_json_parse(reply_text)
            if parsed:
                return parsed
            else:
                # LLM answered but not valid JSON — wrap its text
                return {
                    "status": "success",
                    "content_blocks": [
                        {"type": "concept", "text": reply_text}
                    ],
                    "constructive_advice": "",
                    "learning_objectives": [],
                    "suggested_questions_for_assessment": [],
                    "_raw": True,
                }

        except anthropic.AuthenticationError:
            return {
                "status": "error",
                "error": "Invalid MiniMax API key. Set MINIMAX_API_KEY in your .env file.",
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"LLM call failed: {e}",
                "_traceback": traceback.format_exc(),
            }

    @staticmethod
    def _fallback_no_api(user_message: str) -> Dict[str, Any]:
        """Returned when no API key is configured — shows RAG context only."""
        return {
            "status": "error",
            "error": (
                "No MiniMax API key configured.  "
                "Set MINIMAX_API_KEY in your .env file to enable AI-generated lessons.  "
                "Showing raw RAG data instead."
            ),
            "content_blocks": [
                {"type": "concept", "text": user_message},
            ],
            "constructive_advice": "",
            "learning_objectives": [],
            "suggested_questions_for_assessment": [],
        }

    # ── packaging ────────────────────────────────────────────────────

    @staticmethod
    def _package_lesson(
        topic: str,
        level: str,
        llm_output: Dict[str, Any],
        all_chunks: List[Dict],
    ) -> Dict[str, Any]:
        """Wrap LLM output + metadata into the final lesson dict."""
        return {
            "lesson_id": f"lesson_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}",
            "topic": topic,
            "level": level,
            "created_at": datetime.now().isoformat(),
            "llm_response": llm_output,                       # ← protocol-shaped JSON
            "dse_references": list({c.get("source", "?") for c in all_chunks}),
            "rag_chunks_used": len(all_chunks),
        }

    # ── question LaTeX formatter ──────────────────────────────────────────────

    def format_question_latex(self, raw_text: str, topic: str) -> str:
        """Send raw OCR question text to MiniMax for LaTeX cleanup."""
        if not self._client or not raw_text.strip():
            return raw_text

        system = (
            "You are a HKDSE Mathematics typesetter. "
            "You receive raw OCR-extracted text from scanned past-paper PDFs. "
            "Your ONLY tasks:\n"
            "1. Clean OCR artefacts (misread characters, broken words, stray symbols).\n"
            "2. Reformat ALL mathematical expressions in LaTeX:\n"
            "   - Inline: $expression$\n"
            "   - Display/block: $$expression$$\n"
            "3. Preserve the original question wording and numbering exactly.\n"
            "4. Return ONLY the cleaned markdown — no JSON, no explanation, no commentary.\n\n"
            "LaTeX examples:\n"
            "  Quadratic: $ax^2 + bx + c = 0$\n"
            "  Solution: $$x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}$$\n"
            "  Fraction: $\\frac{3}{4}$, power: $x^n$, subscript: $x_1$\n"
            "  Trig: $\\sin\\theta$, log: $\\log_a x$, abs: $|x|$\n"
            "  Matrix: $$\\begin{pmatrix} a & b \\\\ c & d \\end{pmatrix}$$"
        )

        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=1024,
                system=system,
                messages=[
                    {"role": "user", "content": f"Topic: {topic}\n\nRaw OCR text:\n\n{raw_text}"}
                ],
            )
            return (
                "".join(b.text for b in response.content if hasattr(b, "text"))
                or raw_text
            )
        except Exception:
            return raw_text

    # ── session helpers ──────────────────────────────────────────────

    def get_lesson_history(self) -> List[Dict[str, Any]]:
        return self.session_lessons

    def export_lesson(self, lesson_id: str) -> Optional[str]:
        lesson = next(
            (l for l in self.session_lessons if l["lesson_id"] == lesson_id),
            None,
        )
        return json.dumps(lesson, indent=2) if lesson else None
