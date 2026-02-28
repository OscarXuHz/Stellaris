"""AWS Bedrock AgentCore — Orchestration Layer for EduLoop's Dual-Agent System.

This module wraps AWS Bedrock's ``InvokeAgent`` / ``InvokeModel`` APIs to
provide the intelligent routing layer between EduLoop's Teaching Agent and
Assessment Agent.

Architecture
────────────
┌──────────────┐     ┌─────────────────────────┐     ┌──────────────────┐
│   Student     │ ──▶ │  Bedrock AgentCore       │ ──▶ │  Teaching Agent   │
│   (Next.js)   │     │  (Intent Classification  │     │  (MiniMax + RAG)  │
│               │ ◀── │   + Session Management   │ ──▶ │                  │
│               │     │   + State Machine)        │     │  Assessment Agent │
└──────────────┘     └─────────────────────────┘     │  (MiniMax + RAG)  │
                                                       └──────────────────┘

The Bedrock layer handles:
1.  Intent classification (teach / assess / chat) via Claude on Bedrock
2.  Session state management across the learning loop
3.  Feedback forwarding between Assessment → Teaching agents
4.  Learning loop state machine: TEACH → ASSESS → REPORT → TEACH
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError, NoCredentialsError

from config.config import AWSConfig

logger = logging.getLogger(__name__)


# ── Loop state machine ──────────────────────────────────────────────

class LoopState(str, Enum):
    """Learning loop states managed by the orchestrator."""
    IDLE       = "idle"
    TEACHING   = "teaching"
    ASSESSING  = "assessing"
    REVIEWING  = "reviewing"     # Feedback forwarding phase
    COMPLETED  = "completed"


# ── Session ─────────────────────────────────────────────────────────

class BedrockSession:
    """Tracks a student's learning loop session state."""

    def __init__(self, session_id: str | None = None):
        self.session_id = session_id or f"session_{uuid.uuid4().hex[:12]}"
        self.state: LoopState = LoopState.IDLE
        self.current_topic: str = ""
        self.loop_count: int = 0
        self.history: List[Dict[str, Any]] = []
        self.teaching_output: Optional[Dict[str, Any]] = None
        self.assessment_report: Optional[Dict[str, Any]] = None
        self.knowledge_gaps: List[str] = []
        self.mastery_scores: Dict[str, float] = {}
        self.created_at: str = datetime.now().isoformat()
        self.updated_at: str = self.created_at

    def transition(self, new_state: LoopState) -> None:
        """Transition to a new loop state with validation."""
        valid_transitions = {
            LoopState.IDLE:      [LoopState.TEACHING],
            LoopState.TEACHING:  [LoopState.ASSESSING, LoopState.IDLE],
            LoopState.ASSESSING: [LoopState.REVIEWING, LoopState.IDLE],
            LoopState.REVIEWING: [LoopState.TEACHING, LoopState.COMPLETED],
            LoopState.COMPLETED: [LoopState.IDLE, LoopState.TEACHING],
        }
        allowed = valid_transitions.get(self.state, [])
        if new_state not in allowed:
            logger.warning(
                "Invalid state transition %s → %s (allowed: %s)",
                self.state, new_state, allowed,
            )
        self.state = new_state
        self.updated_at = datetime.now().isoformat()
        if new_state == LoopState.TEACHING:
            self.loop_count += 1

    def record_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Append an event to session history."""
        self.history.append({
            "event": event_type,
            "state": self.state.value,
            "loop": self.loop_count,
            "timestamp": datetime.now().isoformat(),
            "data": data,
        })

    def to_dict(self) -> Dict[str, Any]:
        """Serialise session for storage or API response."""
        return {
            "session_id": self.session_id,
            "state": self.state.value,
            "current_topic": self.current_topic,
            "loop_count": self.loop_count,
            "knowledge_gaps": self.knowledge_gaps,
            "mastery_scores": self.mastery_scores,
            "history_length": len(self.history),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


# ── Intent Classification Prompt (used by Bedrock Claude) ───────────

BEDROCK_CLASSIFIER_PROMPT = """\
You are the intent classifier for EduLoop's Dual-Agent Learning System.

Given a student message and session context, classify the intent and extract
relevant information. You MUST respond with valid JSON only.

AGENTS:
1. Teaching Agent — generates personalised lessons, explanations, examples
2. Assessment Agent — generates questions, evaluates answers, diagnoses gaps

SESSION CONTEXT:
- Current state: {state}
- Current topic: {topic}
- Loop count: {loop_count}
- Knowledge gaps: {gaps}

CLASSIFICATION RULES:
- "teach": Student wants to learn, asks conceptual questions, requests explanations
- "assess": Student wants to practice, check answers, or be tested
- "feedback_loop": Assessment just completed — forward gaps to Teaching Agent for remediation
- "direct": General conversation, greetings, meta-questions

Respond with:
{{
  "intent": "teach" | "assess" | "feedback_loop" | "direct",
  "confidence": 0.0-1.0,
  "topic": "<extracted or inferred topic>",
  "sub_topic": "<specific sub-topic if identifiable>",
  "difficulty_adjustment": "easier" | "same" | "harder" | null,
  "reasoning": "<brief explanation of classification>"
}}
"""


# ── Bedrock Orchestrator ────────────────────────────────────────────

class BedrockOrchestrator:
    """AWS Bedrock AgentCore orchestration layer.

    Manages the closed-loop learning cycle:
        TEACH → ASSESS → REVIEW (feedback) → TEACH …

    Uses Bedrock's ``invoke_model`` for intent classification and
    session-aware routing between the Teaching and Assessment agents.
    """

    def __init__(
        self,
        region: str | None = None,
        model_id: str | None = None,
        teaching_agent=None,
        assessment_agent=None,
    ):
        self.region = region or AWSConfig.AWS_REGION
        self.model_id = model_id or AWSConfig.BEDROCK_MODEL_ID
        self.teaching_agent = teaching_agent
        self.assessment_agent = assessment_agent

        # Active sessions keyed by session_id
        self._sessions: Dict[str, BedrockSession] = {}

        # Initialise Bedrock runtime client
        self._client = None
        try:
            boto_config = BotoConfig(
                region_name=self.region,
                retries={"max_attempts": 3, "mode": "adaptive"},
                connect_timeout=10,
                read_timeout=120,
            )
            self._client = boto3.client(
                "bedrock-runtime",
                config=boto_config,
                region_name=self.region,
                aws_access_key_id=AWSConfig.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWSConfig.AWS_SECRET_ACCESS_KEY,
            )
            logger.info(
                "AWS Bedrock client initialised — region=%s model=%s",
                self.region, self.model_id,
            )
        except (NoCredentialsError, ClientError) as e:
            logger.warning("AWS Bedrock client init failed (non-fatal): %s", e)
            self._client = None

    @property
    def is_available(self) -> bool:
        """Whether the Bedrock client is ready."""
        return self._client is not None

    # ── Session management ───────────────────────────────────────────

    def get_or_create_session(self, session_id: str | None = None) -> BedrockSession:
        """Retrieve an existing session or create a new one."""
        if session_id and session_id in self._sessions:
            return self._sessions[session_id]
        session = BedrockSession(session_id)
        self._sessions[session.session_id] = session
        return session

    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all active sessions (for debugging / admin)."""
        return [s.to_dict() for s in self._sessions.values()]

    # ── Core orchestration ───────────────────────────────────────────

    def route(
        self,
        message: str,
        session_id: str | None = None,
        topic: str = "",
        history: list | None = None,
    ) -> Dict[str, Any]:
        """Route a student message through the Bedrock orchestration layer.

        This is the main entry point.  It:
        1.  Classifies intent via Bedrock Claude
        2.  Manages session state transitions
        3.  Invokes the appropriate agent
        4.  Handles feedback-loop forwarding
        5.  Returns the unified response

        Returns
        -------
        dict with keys: ``reply``, ``agent_used``, ``session``, ``loop_state``,
        ``bedrock_classification``, ``extra``.
        """
        session = self.get_or_create_session(session_id)
        if topic:
            session.current_topic = topic

        # ── 1. Classify intent via Bedrock ───────────────────────────
        classification = self._classify_intent(message, session)
        intent = classification.get("intent", "direct")
        confidence = classification.get("confidence", 0.5)
        inferred_topic = classification.get("topic") or session.current_topic or topic

        session.record_event("intent_classified", {
            "message": message[:200],
            "intent": intent,
            "confidence": confidence,
            "topic": inferred_topic,
        })

        # ── 2. Execute based on intent ───────────────────────────────
        if intent == "teach":
            session.transition(LoopState.TEACHING)
            result = self._invoke_teaching(inferred_topic, session, classification)

        elif intent == "assess":
            session.transition(LoopState.ASSESSING)
            result = self._invoke_assessment(message, inferred_topic, session, classification)

        elif intent == "feedback_loop":
            session.transition(LoopState.REVIEWING)
            result = self._handle_feedback_loop(session)

        else:
            # Direct response — use Bedrock Claude for conversational reply
            result = self._direct_reply(message, session, history or [])

        # Attach orchestration metadata
        result["session"] = session.to_dict()
        result["loop_state"] = session.state.value
        result["bedrock_classification"] = classification
        result["bedrock_model"] = self.model_id
        result["orchestrated_by"] = "aws_bedrock_agentcore"

        return result

    # ── Intent classification via Bedrock ────────────────────────────

    def _classify_intent(
        self, message: str, session: BedrockSession,
    ) -> Dict[str, Any]:
        """Use Bedrock Claude to classify the student's intent."""
        if not self._client:
            # Fallback: keyword-based classification
            return self._fallback_classify(message)

        system_prompt = BEDROCK_CLASSIFIER_PROMPT.format(
            state=session.state.value,
            topic=session.current_topic or "not set",
            loop_count=session.loop_count,
            gaps=", ".join(session.knowledge_gaps) if session.knowledge_gaps else "none identified",
        )

        try:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 512,
                "system": system_prompt,
                "messages": [
                    {"role": "user", "content": message},
                ],
            })

            response = self._client.invoke_model(
                modelId=self.model_id,
                contentType="application/json",
                accept="application/json",
                body=body,
            )

            response_body = json.loads(response["body"].read())
            reply_text = ""
            for block in response_body.get("content", []):
                if block.get("type") == "text":
                    reply_text += block["text"]

            # Parse JSON classification
            parsed = self._safe_json_parse(reply_text)
            if parsed and "intent" in parsed:
                return parsed

            return {"intent": "direct", "confidence": 0.3, "reasoning": "parse_failure"}

        except (ClientError, Exception) as e:
            logger.warning("Bedrock classify failed: %s — using fallback", e)
            return self._fallback_classify(message)

    def _fallback_classify(self, message: str) -> Dict[str, Any]:
        """Rule-based fallback when Bedrock is unavailable."""
        msg = message.lower()
        if any(kw in msg for kw in ["teach", "learn", "explain", "what is", "how to", "lesson", "show me"]):
            return {"intent": "teach", "confidence": 0.7, "reasoning": "keyword_match"}
        if any(kw in msg for kw in ["test", "quiz", "practice", "check", "evaluate", "assess", "answer"]):
            return {"intent": "assess", "confidence": 0.7, "reasoning": "keyword_match"}
        return {"intent": "direct", "confidence": 0.5, "reasoning": "no_keyword_match"}

    # ── Agent invocations ────────────────────────────────────────────

    def _invoke_teaching(
        self,
        topic: str,
        session: BedrockSession,
        classification: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Invoke the Teaching Agent with optional gap-aware context."""
        if not self.teaching_agent:
            return {"reply": "Teaching Agent not available.", "agent_used": "error"}

        # Build student profile from session data (personalisation)
        student_profile = {
            "knowledge_gaps": session.knowledge_gaps,
            "mastery_scores": session.mastery_scores,
            "loop_count": session.loop_count,
            "difficulty_adjustment": classification.get("difficulty_adjustment"),
        }

        try:
            lesson = self.teaching_agent.generate_lesson(
                topic=topic,
                level="intermediate",
                student_profile=student_profile,
            )
            session.teaching_output = lesson
            session.record_event("teaching_completed", {
                "topic": topic,
                "blocks": len(lesson.get("llm_response", {}).get("content_blocks", [])),
            })

            # Format response
            llm = lesson.get("llm_response", {})
            parts = [f"**Lesson: {topic}**\n"]
            for block in llm.get("content_blocks", []):
                btype = block.get("type", "concept")
                parts.append(f"**{btype.replace('_', ' ').title()}**\n{block.get('text', '')}")
            advice = llm.get("constructive_advice", "")
            if advice:
                parts.append(f"\n**Tutor's Advice:** {advice}")

            return {
                "reply": "\n\n".join(parts),
                "agent_used": "teaching",
                "extra": lesson,
            }
        except Exception as e:
            logger.error("Teaching Agent error: %s", e)
            return {"reply": f"Teaching Agent error: {e}", "agent_used": "teaching"}

    def _invoke_assessment(
        self,
        message: str,
        topic: str,
        session: BedrockSession,
        classification: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Invoke the Assessment Agent."""
        if not self.assessment_agent:
            return {"reply": "Assessment Agent not available.", "agent_used": "error"}

        try:
            result = self.assessment_agent.evaluate(
                topic=topic,
                question_text=message,
                student_answer=message,
                difficulty="intermediate",
            )
            session.assessment_report = result

            # Extract knowledge gaps for the feedback loop
            llm = result.get("llm_response", {})
            diag = llm.get("diagnostic_report", {})
            gaps = diag.get("knowledge_gaps", [])
            if gaps:
                session.knowledge_gaps = list(set(session.knowledge_gaps + gaps))

            # Update mastery scores
            score = llm.get("score_percentage")
            if score is not None:
                session.mastery_scores[topic] = score

            session.record_event("assessment_completed", {
                "topic": topic,
                "score": score,
                "gaps_found": gaps,
            })

            # Format response
            parts = ["**AI Evaluation**\n"]
            if score is not None:
                parts.append(f"**Score: {score}%**")
            strengths = diag.get("strengths", [])
            if strengths:
                parts.append("**Strengths:**\n" + "\n".join(f"  - {s}" for s in strengths))
            if gaps:
                parts.append("**Knowledge Gaps:**\n" + "\n".join(f"  - {g}" for g in gaps))
            feedback = diag.get("constructive_feedback", "")
            if feedback:
                parts.append(f"**Feedback:** {feedback}")

            # Check if we should trigger feedback loop
            if gaps and session.loop_count > 0:
                parts.append(
                    "\n*[Bedrock Orchestrator: Gaps detected — triggering feedback loop "
                    "to Teaching Agent for targeted remediation]*"
                )

            return {
                "reply": "\n\n".join(parts),
                "agent_used": "assessment",
                "extra": result,
            }
        except Exception as e:
            logger.error("Assessment Agent error: %s", e)
            return {"reply": f"Assessment Agent error: {e}", "agent_used": "assessment"}

    def _handle_feedback_loop(self, session: BedrockSession) -> Dict[str, Any]:
        """Forward assessment gaps back to Teaching Agent for remediation.

        This is the core of EduLoop's closed-loop learning cycle:
            Assessment report → extract gaps → Teaching Agent re-teaches
        """
        if not session.knowledge_gaps:
            session.transition(LoopState.COMPLETED)
            return {
                "reply": "No knowledge gaps detected — great work! You've mastered this topic.",
                "agent_used": "orchestrator",
            }

        gap_topic = session.knowledge_gaps[0]  # Focus on the most recent gap
        session.record_event("feedback_loop_triggered", {
            "gaps": session.knowledge_gaps,
            "focus": gap_topic,
            "loop": session.loop_count,
        })

        # Transition back to teaching with gap-aware context
        session.transition(LoopState.TEACHING)
        return self._invoke_teaching(
            topic=f"{session.current_topic} — Remediation: {gap_topic}",
            session=session,
            classification={"difficulty_adjustment": "easier"},
        )

    def _direct_reply(
        self,
        message: str,
        session: BedrockSession,
        history: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        """Generate a conversational reply via Bedrock Claude."""
        if not self._client:
            return {
                "reply": "I'm here to help with HKDSE Mathematics! Ask me to teach a topic or assess your work.",
                "agent_used": "orchestrator",
            }

        try:
            messages = [{"role": h["role"], "content": h["content"]} for h in history[-8:]]
            messages.append({"role": "user", "content": message})

            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1024,
                "system": (
                    "You are EduLoop, a friendly HKDSE Mathematics study companion. "
                    "You coordinate two AI agents: a Teaching Agent and an Assessment Agent. "
                    "Keep responses concise and encouraging. Use LaTeX for math: $inline$ or $$block$$."
                ),
                "messages": messages,
            })

            response = self._client.invoke_model(
                modelId=self.model_id,
                contentType="application/json",
                accept="application/json",
                body=body,
            )
            response_body = json.loads(response["body"].read())
            reply = "".join(
                b["text"] for b in response_body.get("content", [])
                if b.get("type") == "text"
            )
            return {"reply": reply, "agent_used": "orchestrator"}

        except Exception as e:
            logger.warning("Bedrock direct reply failed: %s", e)
            return {
                "reply": "I'm here to help with HKDSE Mathematics! What would you like to learn?",
                "agent_used": "orchestrator",
            }

    # ── Utility ──────────────────────────────────────────────────────

    @staticmethod
    def _safe_json_parse(text: str) -> Optional[Dict[str, Any]]:
        """Extract a JSON object from LLM text."""
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

    def get_session_report(self, session_id: str) -> Dict[str, Any]:
        """Generate a comprehensive session report for the student."""
        session = self._sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}

        return {
            **session.to_dict(),
            "history": session.history,
            "teaching_output": session.teaching_output,
            "assessment_report": session.assessment_report,
            "feedback_loops_completed": session.loop_count,
            "generated_at": datetime.now().isoformat(),
            "orchestrator": "aws_bedrock_agentcore",
            "model": self.model_id,
        }
