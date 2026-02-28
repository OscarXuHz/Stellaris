"""Unit tests for core loop manager."""

import pytest
from datetime import datetime
from core.loop_manager import LoopManager, SessionState


@pytest.fixture
def loop_manager():
    """Create a LoopManager instance for testing."""
    return LoopManager("test_session_001")


def test_initialization(loop_manager):
    """Test LoopManager initialization."""
    assert loop_manager.session_id == "test_session_001"
    assert loop_manager.current_state == SessionState.INITIALIZED
    assert len(loop_manager.conversation_history) == 0


def test_initialize_session(loop_manager):
    """Test session initialization."""
    student_data = {
        "name": "John Doe",
        "subjects": ["Mathematics"],
        "level": "intermediate"
    }
    
    result = loop_manager.initialize_session(student_data)
    
    assert result["status"] == "initialized"
    assert result["session_id"] == "test_session_001"
    assert loop_manager.current_state == SessionState.TEACHING


def test_state_transitions(loop_manager):
    """Test state machine transitions."""
    loop_manager.initialize_session({"name": "Test"})
    
    # Teaching -> Assessment
    teaching_data = {"summary": "Taught linear equations"}
    result = loop_manager.transition_to_assessment(teaching_data)
    assert result["state"] == SessionState.ASSESSMENT.value
    
    # Assessment -> Analysis
    assessment_data = {"score": 85, "knowledge_gaps": ["Quadratic equations"]}
    result = loop_manager.transition_to_analysis(assessment_data)
    assert result["state"] == SessionState.ANALYSIS.value


def test_feedback_loop(loop_manager):
    """Test feedback loop processing."""
    assessment_data = {
        "score": 70,
        "knowledge_gaps": ["Function composition", "Trigonometry"],
        "error_analysis": {
            "conceptual_error": 2,
            "calculation_error": 1
        }
    }
    
    feedback = loop_manager.process_feedback_loop(assessment_data)
    
    assert "identified_gaps" in feedback
    assert "recommended_topics" in feedback
    assert feedback["difficulty_adjustment"] in ["foundational", "intermediate", "advanced"]


def test_session_summary(loop_manager):
    """Test session summary generation."""
    loop_manager.initialize_session({"name": "Test Student"})
    summary = loop_manager.get_session_summary()
    
    assert summary["session_id"] == "test_session_001"
    assert "created_at" in summary
    assert summary["final_state"] == SessionState.TEACHING.value


def test_log_interaction(loop_manager):
    """Test interaction logging."""
    loop_manager.initialize_session({"name": "Test"})
    
    interaction_data = {
        "topic": "Mathematics",
        "type": "lesson"
    }
    
    loop_manager.log_interaction("teaching_agent", interaction_data)
    
    assert len(loop_manager.conversation_history) == 1
    assert loop_manager.conversation_history[0]["agent"] == "teaching_agent"
