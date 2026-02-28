"""Core orchestration module for EduLoop agents."""

from enum import Enum
from typing import Dict, Any, Optional
import json
from datetime import datetime


class SessionState(Enum):
    """State machine for learning session."""
    INITIALIZED = "initialized"
    TEACHING = "teaching"
    ASSESSMENT = "assessment"
    ANALYSIS = "analysis"
    FEEDBACK = "feedback"
    COMPLETED = "completed"


class LoopManager:
    """
    Manages the continuous feedback loop between Teaching and Assessment agents.
    Orchestrates session state, handles agent communication, and maintains learning context.
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.current_state = SessionState.INITIALIZED
        self.teaching_output: Dict[str, Any] = {}
        self.assessment_report: Dict[str, Any] = {}
        self.student_profile: Dict[str, Any] = {}
        self.conversation_history = []
        self.created_at = datetime.now().isoformat()
    
    def initialize_session(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize a new learning session with student profile."""
        self.student_profile = student_data
        self.current_state = SessionState.TEACHING
        return {
            "session_id": self.session_id,
            "status": "initialized",
            "state": self.current_state.value,
            "timestamp": datetime.now().isoformat()
        }
    
    def transition_to_teaching(self, topic: str, level: str) -> Dict[str, Any]:
        """Transition to teaching phase and prepare lesson content."""
        self.current_state = SessionState.TEACHING
        return {
            "state": self.current_state.value,
            "topic": topic,
            "level": level,
            "timestamp": datetime.now().isoformat()
        }
    
    def transition_to_assessment(self, teaching_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transition to assessment phase with teaching output."""
        self.teaching_output = teaching_data
        self.current_state = SessionState.ASSESSMENT
        return {
            "state": self.current_state.value,
            "teaching_summary": teaching_data.get("summary", ""),
            "timestamp": datetime.now().isoformat()
        }
    
    def transition_to_analysis(self, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transition to analysis phase for performance analysis."""
        self.assessment_report = assessment_data
        self.current_state = SessionState.ANALYSIS
        return {
            "state": self.current_state.value,
            "student_performance": assessment_data.get("score", 0),
            "timestamp": datetime.now().isoformat()
        }
    
    def process_feedback_loop(self, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process assessment results and generate feedback for next teaching iteration.
        This is the critical "handshake" between agents.
        """
        knowledge_gaps = assessment_data.get("knowledge_gaps", [])
        error_analysis = assessment_data.get("error_analysis", {})
        
        feedback_package = {
            "identified_gaps": knowledge_gaps,
            "misunderstanding_areas": error_analysis,
            "recommended_topics": self._generate_recommendations(knowledge_gaps),
            "difficulty_adjustment": self._calculate_difficulty_level(assessment_data),
            "focus_areas": self._prioritize_areas(error_analysis)
        }
        
        self.current_state = SessionState.FEEDBACK
        return feedback_package
    
    def log_interaction(self, agent: str, data: Dict[str, Any]) -> None:
        """Log agent interactions for session history."""
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "data": data,
            "session_state": self.current_state.value
        })
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Generate comprehensive session summary."""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "final_state": self.current_state.value,
            "student_profile": self.student_profile,
            "teaching_output": self.teaching_output,
            "assessment_report": self.assessment_report,
            "interaction_count": len(self.conversation_history),
            "total_duration": datetime.now().isoformat()
        }
    
    @staticmethod
    def _generate_recommendations(gaps: list) -> list:
        """Generate topic recommendations based on identified gaps."""
        # To be implemented with proper DSE curriculum mapping
        return [f"Review: {gap}" for gap in gaps]
    
    @staticmethod
    def _calculate_difficulty_level(assessment_data: Dict[str, Any]) -> str:
        """Calculate appropriate difficulty level for next lesson."""
        score = assessment_data.get("score", 0)
        if score > 80:
            return "advanced"
        elif score > 60:
            return "intermediate"
        else:
            return "foundational"
    
    @staticmethod
    def _prioritize_areas(error_analysis: Dict[str, Any]) -> list:
        """Prioritize focus areas based on error frequency and importance."""
        # Sort by frequency and DSE syllabus importance
        return sorted(error_analysis.items(), 
                     key=lambda x: x[1].get("frequency", 0), 
                     reverse=True)[:3]

    def export_session_data(self) -> str:
        """Export session data as JSON for persistent storage."""
        return json.dumps(self.get_session_summary(), indent=2)
