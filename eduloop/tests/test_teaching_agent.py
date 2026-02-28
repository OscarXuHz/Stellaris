"""Unit tests for Teaching Agent."""

import pytest
from agents.teaching_agent import TeachingAgent
from config.config import Config


@pytest.fixture
def teaching_agent():
    """Create a TeachingAgent instance for testing."""
    cfg = Config()
    # dummy retriever with required method signature
    retriever = type('R', (object,), {
        'get_relevant_chunks': lambda self, query, subject, top_k: []
    })()
    return TeachingAgent(cfg, retriever)


def test_lesson_generation(teaching_agent):
    """Test lesson generation."""
    student_profile = {
        "name": "Test Student",
        "level": "intermediate",
        "learning_style": "visual"
    }
    
    # Mock RAG retrieval
    mock_curriculum = [{"source": "DSE Curriculum", "content": "Lesson content here"}]
    teaching_agent.retriever = type('obj', (object,), {
        'get_relevant_chunks': lambda self, query, subject, top_k: mock_curriculum
    })()
    
    lesson = teaching_agent.generate_lesson(
        topic="Linear Equations",
        level="intermediate",
        subject="Math Foundation",
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
    mock_lesson = {"lesson_id": "test_123", "topic": "Test Topic"}
    teaching_agent.lesson_history.append(mock_lesson)
    
    assert len(teaching_agent.get_lesson_history()) == 1
    assert teaching_agent.get_lesson_history()[0]["lesson_id"] == "test_123"


def test_minimax_llm_call(teaching_agent, monkeypatch):
    """Ensure LLM helper returns expected text when API is mocked."""
    class DummyResp:
        def __init__(self, data):
            self._data = data
            self.status_code = 200
        def raise_for_status(self):
            pass
        def json(self):
            return self._data
    
    def fake_post(url, json, headers, timeout):
        # record url and payload for assertions
        assert url == teaching_agent.minimax_llm_url
        return DummyResp({"output": "{\"objectives\": []}"})

    monkeypatch.setattr(requests, "post", fake_post)
    result = teaching_agent._call_minimax_llm("dummy prompt")
    assert "objectives" in result
