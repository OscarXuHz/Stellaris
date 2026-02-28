"""Orchestrator Agent — coordinates between Teaching and Assessment agents.

The Orchestrator receives user messages, decides which specialist agent
to invoke (or responds directly), and returns a unified reply.

Flow
────
1.  Receive a user message + optional conversation history + topic.
2.  Use MiniMax-M2.5 to decide: teach / assess / direct-reply.
3.  Invoke TeachingAgent or AssessmentAgent as needed.
4.  Return the combined response with agent attribution.
"""

from __future__ import annotations

import json
import traceback
from typing import Any, Dict, List, Optional

import anthropic

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


# ── Orchestrator System Prompt ────────────────────────────────────────

ORCHESTRATOR_SYSTEM_PROMPT = """\
You are the **Orchestrator** of the EduLoop Dual-Agent Mastery Learning System for HKDSE Mathematics.

You coordinate between two specialist agents:
1. **Teaching Agent** — Generates structured, personalised lessons on HKDSE Math topics using RAG-grounded curriculum content.
2. **Assessment Agent** — Evaluates student answers against official HKDSE marking schemes and provides diagnostic feedback.

Your responsibilities:
- Understand what the student is asking for.
- If the student wants to **learn about a topic**, **asks a conceptual question**, or wants **explanations / examples**, you invoke the Teaching Agent.
- If the student wants to **check their answer**, **submit work for grading**, or asks **"is this correct?"**, you invoke the Assessment Agent.
- If the student is having a **general conversation** (greetings, meta-questions about the system, motivation, study advice), you respond directly without invoking either agent.

LATEX FORMATTING (CRITICAL — MUST FOLLOW):
- ALL mathematical expressions, equations, formulas, and symbols MUST be written in LaTeX.
- Use single dollar signs for inline math: $ax^2 + bx + c = 0$
- Use double dollar signs for display/block math:
  $$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$
- NEVER write equations in plain text.

TONE:
- Friendly, encouraging, and supportive — you are the student's study companion.
- Clear and concise.
- Culturally relevant to Hong Kong students preparing for DSE.

You MUST respond with valid JSON:
{
  "action": "teach" | "assess" | "direct",
  "reply": "<your direct reply if action is 'direct', or empty string>",
  "teach_topic": "<topic to teach if action is 'teach', else null>",
  "assess_data": {
    "question_text": "<the question if action is 'assess'>",
    "student_answer": "<the student's answer if action is 'assess'>"
  } | null
}
"""


# ── OrchestratorAgent ────────────────────────────────────────────────

class OrchestratorAgent:
    """Coordinates user chat messages between Teaching and Assessment agents."""

    def __init__(
        self,
        minimax_api_key: str,
        teaching_agent,
        assessment_agent,
    ):
        self.api_key = minimax_api_key or ""
        self.teaching_agent = teaching_agent
        self.assessment_agent = assessment_agent

        self._client: Optional[anthropic.Anthropic] = None
        if self.api_key:
            self._client = anthropic.Anthropic(
                api_key=self.api_key,
                base_url=MiniMaxConfig.MINIMAX_BASE_URL,
                timeout=90.0,
            )
        self._model = MiniMaxConfig.MINIMAX_TEXT_MODEL

    # ── public API ───────────────────────────────────────────────────

    def chat(
        self,
        message: str,
        topic: str = "",
        history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Process a user chat message and return a response.

        Parameters
        ----------
        message : str
            The user's latest message.
        topic : str
            The current topic context (may be empty).
        history : list[dict]
            Previous messages in ``[{"role": "user"|"assistant", "content": ...}]`` format.

        Returns
        -------
        dict with keys: ``reply``, ``agent_used``, ``extra`` (optional agent output).
        """
        if not self._client:
            return {
                "reply": "No MiniMax API key configured. Set MINIMAX_API_KEY in your .env file.",
                "agent_used": "error",
            }

        history = history or []

        # ── Step 1: Ask the LLM to decide which agent to invoke ──────
        decision = self._decide(message, topic, history)

        action = decision.get("action", "direct")

        # ── Step 2: Execute the decision ─────────────────────────────
        if action == "teach":
            return self._handle_teach(decision, topic)
        elif action == "assess":
            return self._handle_assess(decision, topic)
        else:
            # Direct reply from orchestrator
            return {
                "reply": decision.get("reply", "I'm here to help with HKDSE Mathematics! Ask me anything."),
                "agent_used": "orchestrator",
            }

    # ── decision LLM call ────────────────────────────────────────────

    def _decide(
        self,
        message: str,
        topic: str,
        history: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        """Call MiniMax to decide which agent to invoke."""
        messages: List[Dict[str, str]] = []

        # Include recent history (last 10 turns max)
        for h in history[-10:]:
            messages.append({"role": h["role"], "content": h["content"]})

        # Current user message with topic context
        user_content = message
        if topic:
            user_content = f"[Current topic context: {topic}]\n\n{message}"
        messages.append({"role": "user", "content": user_content})

        try:
            response = self._client.messages.create(  # type: ignore[union-attr]
                model=self._model,
                max_tokens=2048,
                system=ORCHESTRATOR_SYSTEM_PROMPT,
                messages=messages,
            )

            reply_text = ""
            for block in response.content:
                if getattr(block, "type", None) == "text":
                    reply_text += block.text

            parsed = _safe_json_parse(reply_text)
            if parsed and "action" in parsed:
                return parsed

            # Fallback: treat as direct reply
            return {"action": "direct", "reply": reply_text}

        except Exception as e:
            return {
                "action": "direct",
                "reply": f"Sorry, I encountered an error: {e}",
            }

    # ── handler: teach ───────────────────────────────────────────────

    def _handle_teach(self, decision: Dict, topic: str) -> Dict[str, Any]:
        """Invoke the Teaching Agent and format a chat-friendly response."""
        teach_topic = decision.get("teach_topic") or topic or "General HKDSE Mathematics"

        try:
            lesson = self.teaching_agent.generate_lesson(
                topic=teach_topic,
                level="intermediate",
                student_profile={},
            )
            llm = lesson.get("llm_response", {})

            # Build a readable reply from the lesson content blocks
            parts: List[str] = []
            parts.append(f"📘 **Lesson: {teach_topic}**\n")

            for block in llm.get("content_blocks", []):
                btype = block.get("type", "concept")
                emoji = {
                    "introduction": "📖",
                    "concept": "📘",
                    "example": "📝",
                    "common_pitfall": "⚠️",
                    "summary": "✅",
                }.get(btype, "📘")
                parts.append(f"{emoji} **{btype.replace('_', ' ').title()}**\n{block.get('text', '')}")

            advice = llm.get("constructive_advice", "")
            if advice:
                parts.append(f"\n💬 **Tutor's Advice:** {advice}")

            objectives = llm.get("learning_objectives", [])
            if objectives:
                obj_str = "\n".join(f"  ✓ {o}" for o in objectives)
                parts.append(f"\n🎯 **Learning Objectives:**\n{obj_str}")

            return {
                "reply": "\n\n".join(parts),
                "agent_used": "teaching",
                "extra": lesson,
            }

        except Exception as e:
            return {
                "reply": f"I tried to generate a lesson but encountered an error: {e}",
                "agent_used": "teaching",
            }

    # ── handler: assess ──────────────────────────────────────────────

    def _handle_assess(self, decision: Dict, topic: str) -> Dict[str, Any]:
        """Invoke the Assessment Agent and format a chat-friendly response."""
        assess_data = decision.get("assess_data") or {}
        question = assess_data.get("question_text", "")
        answer = assess_data.get("student_answer", "")
        assess_topic = topic or "General HKDSE Mathematics"

        if not answer:
            return {
                "reply": "I'd like to evaluate your answer, but I didn't find a clear answer to assess. Could you write out your working and answer?",
                "agent_used": "orchestrator",
            }

        try:
            result = self.assessment_agent.evaluate(
                topic=assess_topic,
                question_text=question,
                student_answer=answer,
                difficulty="intermediate",
            )
            llm = result.get("llm_response", {})

            parts: List[str] = []
            parts.append("📊 **AI Evaluation**\n")

            score = llm.get("score_percentage")
            if score is not None:
                parts.append(f"**Score: {score}%**")

            diag = llm.get("diagnostic_report", {})
            strengths = diag.get("strengths", [])
            if strengths:
                parts.append("✅ **Strengths:**\n" + "\n".join(f"  • {s}" for s in strengths))

            gaps = diag.get("knowledge_gaps", [])
            if gaps:
                parts.append("⚠️ **Knowledge Gaps:**\n" + "\n".join(f"  • {g}" for g in gaps))

            feedback = diag.get("constructive_feedback", "")
            if feedback:
                parts.append(f"💬 **Feedback:** {feedback}")

            misconception = diag.get("misconception_analysis", "")
            if misconception:
                parts.append(f"🔍 **Misconception:** {misconception}")

            rec = llm.get("next_step_recommendation", {})
            if rec:
                action = rec.get("action", "")
                focus = rec.get("focus_topics_for_teacher", rec.get("focus_topics", []))
                parts.append(f"\n📌 **Next Step:** {action} — focus on: {', '.join(focus)}")

            return {
                "reply": "\n\n".join(parts),
                "agent_used": "assessment",
                "extra": result,
            }

        except Exception as e:
            return {
                "reply": f"I tried to evaluate your answer but encountered an error: {e}",
                "agent_used": "assessment",
            }
