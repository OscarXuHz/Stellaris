"""Unit tests for Teaching Agent."""

import pytest
from agents.teaching_agent import TeachingAgent


@pytest.fixture
def teaching_agent():
    """Create a TeachingAgent instance for testing."""
    return TeachingAgent("test_key", rag_vectordb=None)


def test_lesson_generation(teaching_agent):
    """Test lesson generation."""
    student_profile = {
        "name": "Test Student",
        "level": "intermediate",
        "learning_style": "visual"
    }
    
    # Mock RAG retrieval
    mock_curriculum = [
        {"source": "DSE Curriculum", "content": "Lesson content here"}
    ]
    
    # Temporarily set mock materials
    teaching_agent.rag_vectordb = type('obj', (object,), {
        'retrieve': lambda topic, k: mock_curriculum
    })()
    
    lesson = teaching_agent.generate_lesson(
        topic="Linear Equations",
        level="intermediate",
        student_profile=student_profile
    )
    
    assert lesson["topic"] == "Linear Equations"
    assert lesson["level"] == "intermediate"
    assert "lesson_id" in lesson
    assert "content" in lesson
    assert "audio" in lesson


def test_lesson_structure(teaching_agent):
    """Test lesson content structure."""
    lesson_content = teaching_agent._create_lesson_structure(
        "Polynomials",
        "intermediate",
        []
    )
    
    assert "introduction" in lesson_content
    assert "main_content" in lesson_content
    assert "worked_examples" in lesson_content
    assert "key_points" in lesson_content
    assert "common_mistakes" in lesson_content


def test_audio_generation(teaching_agent):
    """Test audio narration setup."""
    student_profile = {
        "preferred_language": "cantonese",
        "voice_preference": "friendly"
    }
    
    lesson_content = {
        "introduction": "Introduction text",
        "main_content": "Main content",
        "key_points": ["Point 1", "Point 2"]
    }
    
    audio = teaching_agent._generate_audio_narration(lesson_content, student_profile)
    
    assert audio["language"] == "cantonese"
    assert audio["voice_tone"] == "friendly"
    assert "narration_script" in audio


def test_lesson_history(teaching_agent):
    """Test lesson history tracking."""
    assert len(teaching_agent.get_lesson_history()) == 0
    
    # Generate mock lesson
    mock_lesson = {
        "lesson_id": "test_123",
        "topic": "Test Topic"
    }
    teaching_agent.session_lessons.append(mock_lesson)
    
    assert len(teaching_agent.get_lesson_history()) == 1
    assert teaching_agent.get_lesson_history()[0]["lesson_id"] == "test_123"
