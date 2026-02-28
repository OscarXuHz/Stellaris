"""Assessment Agent implementation for EduLoop."""

from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import json
import logging
import random
import requests
from datetime import datetime

from config.config import Config, MiniMaxConfig
from utils.helpers import generate_entity_id, save_json, load_json, calculate_percentage, get_dse_level

# configure logger for this module
logger = logging.getLogger(__name__)


class QuestionDifficulty(Enum):
    """Question difficulty levels aligned with HKDSE."""
    FOUNDATIONAL = "foundational"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


@dataclass
class Question:
    """Structure for HKDSE examination question."""
    id: str
    topic: str
    difficulty: QuestionDifficulty
    question_text: str
    question_type: str  # mcq, short_answer, long_answer
    correct_answer: str
    marking_scheme: Dict[str, int]  # Points for different parts
    dse_paper: str  # Paper 1 or Paper 2
    marks_total: int


class AssessmentAgent:
    """
    Generates syllabus-aligned assessments and provides diagnostic feedback.
    Implements automatic scoring based on HKDSE marking schemes.
    """
    
    def __init__(self, config: Config, dse_curriculum_db: Optional[Any] = None) -> None:
        """
        Initialize the assessment agent.

        Args:
            config: Configuration object (contains API keys, etc.)
            dse_curriculum_db: Optional database for curriculum/question lookup
        """
        self.config = config
        self.dse_curriculum_db = dse_curriculum_db
        # history stores full assessment objects
        self.assessment_history: List[Dict[str, Any]] = []
        # reports generated after evaluations
        self.report_history: List[Dict[str, Any]] = []
        # Minimax LLM credentials and endpoints
        self.minimax_api_key = MiniMaxConfig.MINIMAX_API_KEY
        self.minimax_group_id = MiniMaxConfig.MINIMAX_GROUP_ID
        self.minimax_base_url = MiniMaxConfig.MINIMAX_BASE_URL
        self.minimax_llm_url = getattr(MiniMaxConfig, 'MINIMAX_LLM_URL', f"{self.minimax_base_url}/llm")
        logger.info("AssessmentAgent initialized with config and optional curriculum DB")
    
    def _call_minimax_llm(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Perform a request to the Minimax LLM endpoint.

        Args:
            prompt: User prompt to send to the model.
            system_prompt: Optional system-level instruction.
        Returns:
            Text output from the model or empty string on failure.
        """
        if not self.minimax_api_key:
            logger.warning("No Minimax API key configured; skipping LLM request")
            return ""
        url = self.minimax_llm_url
        headers = {
            "Authorization": f"Bearer {self.minimax_api_key}",
            "Content-Type": "application/json"
        }
        payload: Dict[str, Any] = {
            "model": MiniMaxConfig.MINIMAX_TEXT_MODEL,
            "input": prompt,
            "group_id": self.minimax_group_id,
            "max_tokens": 1500,
            "temperature": 0.7
        }
        if system_prompt:
            payload["system_prompt"] = system_prompt
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, dict):
                if "output" in data:
                    return data["output"]
                if "choices" in data and isinstance(data["choices"], list):
                    return "".join(c.get("text", "") for c in data["choices"])
                if "reply" in data:
                    return data["reply"]
            return json.dumps(data)
        except Exception as e:
            logger.error(f"Minimax LLM request failed: {e}")
            return ""

    def generate_assessment(self, lesson: Dict[str, Any], num_questions: int = 5) -> Dict[str, Any]:
        """
        Create an assessment based on a lesson produced by TeachingAgent.

        Args:
            lesson: Lesson dictionary containing topic, difficulty_level, subject, etc.
            num_questions: Number of questions to include (default 5)

        Returns:
            A structured assessment dict ready for delivery.
        """
        topic = lesson.get("topic")
        difficulty = lesson.get("difficulty_level") or lesson.get("difficulty", "foundational")
        subject = lesson.get("subject", "")
        paper = lesson.get("paper")

        # for now all questions adopt the same difficulty
        distribution = [difficulty] * num_questions

        questions: List[Dict[str, Any]] = []
        total_marks = 0
        for idx in range(num_questions):
            qdiff = distribution[idx]
            question = self._generate_question(topic, qdiff, subject, paper)
            questions.append(question)
            total_marks += question.get("marks", 0)

        assessment = {
            "assessment_id": generate_entity_id("assess"),
            "lesson_id": lesson.get("lesson_id"),
            "topic": topic,
            "difficulty": difficulty,
            "subject": subject,
            "paper": paper,
            "questions": questions,
            "total_marks": total_marks,
            "time_allowed_minutes": num_questions * 2,
            "instructions": f"Answer all {num_questions} questions in {num_questions*2} minutes."
        }
        self.assessment_history.append(assessment)
        return assessment
    
    def _generate_single_question(self,
                                 topic: str,
                                 difficulty: str,
                                 question_type: str,
                                 question_num: int) -> Question:
        """Generate a single assessment question."""
        difficulty_enum = QuestionDifficulty(difficulty)
        
        if question_type == "mcq":
            marks = 1
        elif question_type == "short_answer":
            marks = 4 if difficulty_enum == QuestionDifficulty.FOUNDATIONAL else 6
        else:  # long_answer
            marks = 8 if difficulty_enum == QuestionDifficulty.ADVANCED else 6
        
        return Question(
            id=f"Q{question_num}",
            topic=topic,
            difficulty=difficulty_enum,
            question_text=self._create_question_text(topic, difficulty_enum, question_type),
            question_type=question_type,
            correct_answer="Sample correct answer",
            marking_scheme=self._create_marking_scheme(question_type, marks),
            dse_paper="Paper 1" if question_num % 2 == 1 else "Paper 2",
            marks_total=marks
        )
    
    def evaluate_student_response(self,
                                   assessment_id: str,
                                   student_answers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate a full assessment submission.

        Args:
            assessment_id: ID returned by generate_assessment
            student_answers: list of {question_id, answer_text, time_taken?}

        Returns:
            Results dict containing scores, gaps, misconceptions, and feedback.
        """
        assessment = next((a for a in self.assessment_history if a["assessment_id"] == assessment_id), None)
        if assessment is None:
            raise ValueError(f"Assessment {assessment_id} not found")

        question_map = {q["question_id"]: q for q in assessment["questions"]}
        scored = []
        incorrect_questions = []
        total_score = 0

        for ans in student_answers:
            qid = ans.get("question_id")
            answer_text = ans.get("answer_text")
            question = question_map.get(qid)
            if not question:
                continue
            score, is_correct = self._score_question(question, answer_text)
            total_score += score
            scored.append({
                "question_id": qid,
                "answer_text": answer_text,
                "score": score,
                "is_correct": is_correct,
                "marks": question.get("marks")
            })
            if not is_correct:
                incorrect_questions.append(question)

        percentage = calculate_percentage(total_score, assessment.get("total_marks", 0))
        dse_level = get_dse_level(percentage)
        gaps = [q["topic"] for q in incorrect_questions]
        misconceptions = self._analyze_misconceptions(incorrect_questions)
        feedback_summary = f"You scored {total_score}/{assessment.get('total_marks')} ({percentage:.1f}%)."
        recommendations = self._recommend_next_topics(percentage, gaps)

        results = {
            "assessment_id": assessment_id,
            "student_answers": scored,
            "total_score": total_score,
            "percentage": percentage,
            "dse_level": dse_level,
            "gaps": gaps,
            "misconceptions": misconceptions,
            "feedback_summary": feedback_summary,
            "recommendations": recommendations
        }

        # store diagnostic report as well
        results["diagnostic_report"] = self.generate_diagnostic_report(assessment_id, results)
        return results
    
    def generate_diagnostic_report(self,
                                   assessment_id: str,
                                   results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build a diagnostic report based on evaluation results.

        Args:
            assessment_id: ID of the assessment just scored
            results: Dictionary returned by evaluate_student_response
        """
        total = results.get("total_score", 0)
        possible = next((a["total_marks"] for a in self.assessment_history if a["assessment_id"] == assessment_id), 0)
        percentage = results.get("percentage", 0)
        dse_level = results.get("dse_level", "")

        strengths = [q["topic"] for q in results.get("student_answers", [])
                     if q.get("score", 0) >= 0.8 * q.get("marks", 1)]
        weaknesses = results.get("gaps", [])

        report = {
            "report_id": generate_entity_id("report"),
            "assessment_id": assessment_id,
            "performance_summary": f"Scored {total}/{possible} ({percentage:.1f}% – {dse_level})",
            "score_breakdown": results.get("student_answers", []),
            "dse_level_mapping": dse_level,
            "strengths": strengths,
            "areas_for_improvement": weaknesses,
            "recommended_focus": results.get("recommendations", []),
        }
        self.report_history.append(report)
        return report

    # --- additional helpers for lesson-based workflow ---
    def _generate_question(self, topic: str, difficulty: str,
                           subject: str, paper: Optional[str] = None) -> Dict[str, Any]:
        """Generate a realistic HKDSE-style question via Minimax LLM.

        If the LLM call fails or returns unparsable output, fall back to a
        simple placeholder question.
        """
        qid = generate_entity_id("q")
        # decide a question type randomly to send in prompt
        qtype = random.choice(["mcq", "short_answer", "long_answer"])
        prompt = (
            f"Create an HKDSE {qtype} question in {subject} on the topic "
            f"'{topic}', at {difficulty} difficulty, for {paper or 'any paper'}. "
            "Return the result in JSON with keys: question_text, type, options (if mcq), "
            "correct_answer, marks, explanation, marking_scheme."
        )
        raw = self._call_minimax_llm(prompt)
        question: Dict[str, Any]
        try:
            question = json.loads(raw)
        except Exception:
            logger.warning("Failed to parse LLM question response, using placeholder")
            question = {}
        # ensure required fields
        if not question.get("question_text"):
            question = {}
        if not question:
            # fallback placeholder
            question_type = qtype
            marks = 1 if question_type == "mcq" else 5
            options = []
            correct = "A"
            if question_type == "mcq":
                options = ["A", "B", "C", "D"]
                correct = random.choice(options)
            question = {
                "question_text": f"{difficulty.capitalize()} question on {topic}",
                "type": question_type,
                "options": options,
                "correct_answer": correct,
                "marks": marks,
                "explanation": "",
                "marking_scheme": {}
            }
        # attach metadata identifiers
        question.update({
            "question_id": qid,
            "topic": topic,
            "difficulty": difficulty,
            "subject": subject,
            "paper": paper
        })
        return question

    def _score_question(self, question: Dict[str, Any],
                        student_answer: Union[str, Any]) -> Tuple[float, bool]:
        """Score one question, return (score, is_correct)."""
        if question.get("type") == "mcq":
            is_correct = student_answer == question.get("correct_answer")
            return (question.get("marks", 0) if is_correct else 0, is_correct)
        # open-ended: delegate to LLM
        prompt = (
            f"Grade the following HKDSE response.\n"
            f"Question: {question.get('question_text')}\n"
            f"Correct answer: {question.get('correct_answer')}\n"
            f"Marking scheme: {json.dumps(question.get('marking_scheme', {}))}\n"
            f"Student answer: {student_answer}\n"
            "Provide output JSON with the fields 'score' and 'is_correct'."
        )
        raw = self._call_minimax_llm(prompt)
        try:
            result = json.loads(raw)
            score = float(result.get("score", 0))
            is_correct = bool(result.get("is_correct", score >= question.get("marks", 0)))
            return (score, is_correct)
        except Exception:
            logger.warning("LLM scoring failed, falling back to simple heuristic")
            is_correct = question.get("topic", "").lower() in str(student_answer).lower()
            return (question.get("marks", 0) if is_correct else 0, is_correct)

    def _analyze_misconceptions(self, incorrect_questions: List[Dict[str, Any]]) -> List[str]:
        """Infer misconceptions from missed questions.

        If MiniMax LLM is available, ask it to summarize common misconceptions.
        """
        if self.minimax_api_key and incorrect_questions:
            topics = ", ".join(q.get("topic", "") for q in incorrect_questions)
            prompt = (
                f"Given the following missed question topics: {topics}, list the likely misconceptions "
                "students exhibit. Respond with a JSON array of strings."
            )
            raw = self._call_minimax_llm(prompt)
            try:
                mis = json.loads(raw)
                if isinstance(mis, list):
                    return mis
            except Exception:
                logger.debug("LLM returned non-json for misconceptions")
        # fallback
        return [f"Review concept for {q.get('topic')}" for q in incorrect_questions]

    def _recommend_next_topics(self, percentage: float, gaps: List[str]) -> List[str]:
        """Suggest next focus areas based on performance.

        Optionally consult the LLM for personalized advice.
        """
        if self.minimax_api_key:
            prompt = (
                f"Student scored {percentage:.1f}% and struggled with {', '.join(gaps)}. "
                "Recommend next topics or actions in a JSON array."
            )
            raw = self._call_minimax_llm(prompt)
            try:
                recs = json.loads(raw)
                if isinstance(recs, list) and recs:
                    return recs
            except Exception:
                logger.debug("LLM gave invalid recommendations, using heuristic")
        # fallback heuristic
        if percentage >= 80:
            return ["advance topic"]
        elif percentage >= 60:
            return ["reinforce current topic"]
        else:
            return ["review fundamentals"]
    
    @staticmethod
    def _create_question_text(topic: str, difficulty: QuestionDifficulty, q_type: str) -> str:
        """Create question text based on topic and difficulty."""
        difficulty_indicator = {
            QuestionDifficulty.FOUNDATIONAL: "basic",
            QuestionDifficulty.INTERMEDIATE: "intermediate",
            QuestionDifficulty.ADVANCED: "complex"
        }
        return f"[{difficulty_indicator[difficulty]} {q_type.replace('_', ' ')} on {topic}]"
    
    @staticmethod
    def _create_marking_scheme(question_type: str, total_marks: int) -> Dict[str, int]:
        """Create marking scheme breakdown."""
        if question_type == "mcq":
            return {"correct_answer": total_marks}
        elif question_type == "short_answer":
            return {
                "correct_working": total_marks // 2,
                "correct_answer": total_marks - total_marks // 2
            }
        else:  # long_answer
            return {
                "understanding": total_marks // 3,
                "working": total_marks // 3,
                "final_answer": total_marks - 2 * (total_marks // 3)
            }
    
    @staticmethod
    def _calculate_score(student_answer: str, question_type: str) -> Dict[str, int]:
        """Calculate score based on student answer."""
        # Simplified scoring (to be replaced with actual matching logic)
        score = 3 if len(student_answer) > 20 else 1
        marks_total = 4 if question_type == "short_answer" else 6
        return {
            "marks_obtained": min(score, marks_total),
            "marks_total": marks_total
        }
    
    @staticmethod
    def _analyze_errors(answer: str, question_type: str) -> Dict[str, int]:
        """Analyze errors in student response."""
        errors = {}
        answer_lower = answer.lower()
        
        # Common error patterns
        error_patterns = {
            "calculation_error": ["forgot", "wrong number", "miscalculated"],
            "conceptual_misunderstanding": ["confused", "mixed up", "incorrect formula"],
            "incomplete_answer": ["partial", "missing steps", "no explanation"],
            "notation_error": ["wrong notation", "symbol error"]
        }
        
        for error_type, keywords in error_patterns.items():
            errors[error_type] = sum(1 for kw in keywords if kw in answer_lower)
        
        return errors
    
    @staticmethod
    def _generate_feedback(error_analysis: Dict[str, int]) -> str:
        """Generate personalized feedback based on error analysis."""
        primary_errors = [k for k, v in error_analysis.items() if v > 0]
        
        if not primary_errors:
            return "Excellent work! Your answer demonstrates solid understanding."
        
        feedback = "Areas to improve: "
        feedback += ", ".join(primary_errors).replace("_", " ")
        feedback += ". Review the concept and try similar problems."
        
        return feedback
    
    @staticmethod
    def _assess_severity(error_type: str) -> str:
        """Assess severity of error type."""
        severity_map = {
            "conceptual_misunderstanding": "high",
            "calculation_error": "medium",
            "incomplete_answer": "medium",
            "notation_error": "low"
        }
        return severity_map.get(error_type, "medium")
    
    @staticmethod
    def _assess_level(marks_obtained: int, marks_total: int) -> str:
        """Assess HKDSE level based on marks."""
        if marks_total == 0:
            return "Not assessed"
        percentage = (marks_obtained / marks_total) * 100
        if percentage >= 90:
            return "Level 5**"
        elif percentage >= 80:
            return "Level 5*"
        elif percentage >= 70:
            return "Level 5"
        elif percentage >= 60:
            return "Level 4"
        elif percentage >= 50:
            return "Level 3"
        else:
            return "Below Level 3"
    
    @staticmethod
    def _summarize_error_patterns(responses: List[Dict[str, Any]]) -> List[str]:
        """Summarize common error patterns across responses."""
        all_errors = {}
        for response in responses:
            errors = response.get("error_analysis", {})
            for error_type, count in errors.items():
                all_errors[error_type] = all_errors.get(error_type, 0) + count
        
        return sorted(all_errors.items(), key=lambda x: x[1], reverse=True)[:3]
    
    @staticmethod
    def _identify_misconceptions(responses: List[Dict[str, Any]]) -> List[str]:
        """Identify systematic misconceptions from multiple responses."""
        misconceptions = set()
        for response in responses:
            errors = response.get("error_analysis", {})
            if errors.get("conceptual_misunderstanding", 0) > 0:
                misconceptions.add("Conceptual gap identified - review fundamentals")
        
        return list(misconceptions)
    
    @staticmethod
    def _generate_recommendations(gaps: List[Dict], topic: str) -> List[str]:
        """Generate specific recommendations for improvement."""
        if not gaps:
            return ["Continue practicing at advanced level"]
        
        recommendations = []
        for gap in gaps[:3]:
            recommendations.append(f"Review: {gap['area']} - {gap['severity']} priority")
        
        recommendations.append(f"Attempt more {topic} practice problems from past papers")
        return recommendations
    
    @staticmethod
    def _suggest_next_steps(marks: int, total: int, gaps: List[Dict]) -> Dict[str, Any]:
        """Suggest next learning steps based on performance."""
        percentage = (marks / total * 100) if total > 0 else 0
        
        if percentage >= 80:
            next_topic_difficulty = "advanced"
            action = "Advance to more complex topics"
        elif percentage >= 60:
            next_topic_difficulty = "intermediate"
            action = "Reinforce current topic with more practice"
        else:
            next_topic_difficulty = "foundational"
            action = "Review fundamentals of this topic"
        
        return {
            "performance_level": percentage,
            "recommended_difficulty": next_topic_difficulty,
            "recommended_action": action,
            "practice_recommendation": "Complete 5-10 additional problems before moving on",
            "time_to_mastery_estimate": "1-2 hours of focused practice"
        }
    
    @staticmethod
    def _generate_id() -> str:
        """Generate unique assessment ID."""
        from datetime import datetime
        import uuid
        return f"assess_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
    
    def get_assessment_history(self) -> List[Dict[str, Any]]:
        """Retrieve all generated assessments from history."""
        return self.assessment_history
    
    def get_reports(self) -> List[Dict[str, Any]]:
        """Retrieve all diagnostic reports created."""
        return self.report_history
