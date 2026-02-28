"""Assessment Agent implementation for EduLoop."""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime


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
    
    def __init__(self, dse_curriculum_db):
        self.dse_curriculum_db = dse_curriculum_db
        self.generated_questions: List[Question] = []
        self.student_responses: List[Dict[str, Any]] = []
        self.assessment_reports: List[Dict[str, Any]] = []
    
    def generate_assessment(self,
                          topic: str,
                          num_questions: int,
                          difficulty: str,
                          question_types: List[str] = None) -> Dict[str, Any]:
        """
        Generate a set of assessment questions aligned with HKDSE syllabus.
        
        Args:
            topic: DSE curriculum topic
            num_questions: Number of questions to generate (3-5 typical)
            difficulty: Difficulty level (foundational, intermediate, advanced)
            question_types: Mix of question types (mcq, short_answer, long_answer)
        
        Returns:
            Assessment paper with questions and metadata
        """
        if question_types is None:
            question_types = ["short_answer", "long_answer"]
        
        questions = []
        total_marks = 0
        
        for i in range(num_questions):
            question = self._generate_single_question(
                topic, 
                difficulty, 
                question_types[i % len(question_types)],
                i + 1
            )
            questions.append(question)
            total_marks += question.marks_total
        
        assessment = {
            "assessment_id": self._generate_id(),
            "topic": topic,
            "difficulty": difficulty,
            "created_at": datetime.now().isoformat(),
            "questions": [q.__dict__ for q in questions],
            "total_marks": total_marks,
            "duration_minutes": 20 if num_questions <= 3 else 30,
            "dse_reference": f"HKDSE {topic} - Syllabus aligned"
        }
        
        self.generated_questions.extend(questions)
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
                                 question_id: str,
                                 student_answer: str,
                                 question_type: str) -> Dict[str, Any]:
        """
        Evaluate student response using HKDSE marking scheme.
        Provides detailed feedback and identifies misconceptions.
        """
        score = self._calculate_score(student_answer, question_type)
        error_analysis = self._analyze_errors(student_answer, question_type)
        
        evaluation = {
            "question_id": question_id,
            "student_answer": student_answer,
            "score": score,
            "marks_obtained": score.get("marks_obtained", 0),
            "marks_total": score.get("marks_total", 0),
            "percentage": (score.get("marks_obtained", 0) / score.get("marks_total", 1)) * 100,
            "error_analysis": error_analysis,
            "feedback": self._generate_feedback(error_analysis),
            "evaluated_at": datetime.now().isoformat()
        }
        
        self.student_responses.append(evaluation)
        return evaluation
    
    def generate_diagnostic_report(self,
                                  responses: List[Dict[str, Any]],
                                  topic: str) -> Dict[str, Any]:
        """
        Generate comprehensive diagnostic report showing knowledge gaps
        and misconception patterns.
        """
        total_marks = sum(r.get("marks_total", 0) for r in responses)
        obtained_marks = sum(r.get("marks_obtained", 0) for r in responses)
        
        # Aggregate error patterns
        all_errors = []
        knowledge_gaps = []
        
        for response in responses:
            errors = response.get("error_analysis", {})
            for error_type, count in errors.items():
                if error_type not in all_errors:
                    all_errors.append(error_type)
                
                if count > 0:
                    knowledge_gaps.append({
                        "area": error_type,
                        "frequency": count,
                        "severity": self._assess_severity(error_type)
                    })
        
        # Sort by frequency
        knowledge_gaps.sort(key=lambda x: x["frequency"], reverse=True)
        
        report = {
            "report_id": self._generate_id(),
            "topic": topic,
            "created_at": datetime.now().isoformat(),
            "performance": {
                "marks_obtained": obtained_marks,
                "marks_total": total_marks,
                "percentage": (obtained_marks / total_marks * 100) if total_marks > 0 else 0,
                "level": self._assess_level(obtained_marks, total_marks)
            },
            "knowledge_gaps": knowledge_gaps[:5],  # Top 5 areas
            "error_patterns": self._summarize_error_patterns(responses),
            "misconceptions": self._identify_misconceptions(responses),
            "recommendations": self._generate_recommendations(knowledge_gaps, topic),
            "next_steps": self._suggest_next_steps(obtained_marks, total_marks, knowledge_gaps)
        }
        
        self.assessment_reports.append(report)
        return report
    
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
        """Retrieve all generated assessments."""
        return [q.__dict__ for q in self.generated_questions]
    
    def get_reports(self) -> List[Dict[str, Any]]:
        """Retrieve all diagnostic reports."""
        return self.assessment_reports
