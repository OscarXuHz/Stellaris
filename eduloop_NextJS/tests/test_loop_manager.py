"""Unit tests for core loop manager."""

import pytest
import json
from datetime import datetime
from core.loop_manager import LoopManager, SessionState


@pytest.fixture
def loop_manager():
    """Create a LoopManager instance for testing."""
    return LoopManager("test_session_001")


def test_initialization(loop_manager):
    assert loop_manager.session_id == "test_session_001"
    assert loop_manager.current_state == SessionState.INITIALIZED
    assert len(loop_manager.conversation_history) == 0


def test_initialize_session(loop_manager):
    student_data = {"name": "John Doe", "subjects": ["Mathematics"], "level": "intermediate"}
    result = loop_manager.initialize_session(student_data)
    assert result["status"] == "initialized"
    assert result["session_id"] == "test_session_001"
    assert loop_manager.current_state == SessionState.TEACHING


def test_state_transitions(loop_manager):
    loop_manager.initialize_session({"name": "Test"})
    teaching_data = {"summary": "something"}
    res = loop_manager.transition_to_assessment(teaching_data)
    assert res["state"] == SessionState.ASSESSMENT.value
    assessment_data = {"score": 85, "knowledge_gaps": ["X"]}
    res2 = loop_manager.transition_to_analysis(assessment_data)
    assert res2["state"] == SessionState.ANALYSIS.value


def test_feedback_loop(loop_manager):
    data = {"score": 70, "knowledge_gaps": ["a", "b"], "error_analysis": {"c": {"frequency": 2}}}
    feedback = loop_manager.process_feedback_loop(data)
    assert "identified_gaps" in feedback
    assert "recommended_topics" in feedback
    assert feedback["difficulty_adjustment"] in ["foundational", "intermediate", "advanced"]


def test_session_summary(loop_manager):
    loop_manager.initialize_session({"name": "Test"})
    summary = loop_manager.get_session_summary()
    assert summary["session_id"] == "test_session_001"
    assert "created_at" in summary
    assert summary["final_state"] == SessionState.TEACHING.value


def test_log_interaction(loop_manager):
    loop_manager.initialize_session({"name": "Test"})
    interaction = {"topic": "Math"}
    loop_manager.log_interaction("teaching_agent", interaction)
    assert len(loop_manager.conversation_history) == 1
    assert loop_manager.conversation_history[0]["agent"] == "teaching_agent"


def test_export_session_data(loop_manager):
    loop_manager.initialize_session({"name": "Test"})
    loop_manager.log_interaction("t", {"x": 1})
    exported = loop_manager.export_session_data()
    obj = json.loads(exported)
    assert obj["session_id"] == "test_session_001"
    assert "interaction_count" in obj


def test_static_helpers():
    assert LoopManager._generate_recommendations(["gap"]) == ["Review: gap"]
    assert LoopManager._calculate_difficulty_level({"score": 85}) == "advanced"
    assert LoopManager._calculate_difficulty_level({"score": 50}) == "foundational"
    errors = {"a": {"frequency": 1}, "b": {"frequency": 3}}
    pr = LoopManager._prioritize_areas(errors)
    assert pr[0][0] == "b"

