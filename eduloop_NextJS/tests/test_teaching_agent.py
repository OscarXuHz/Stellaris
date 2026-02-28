"""Unit tests for Teaching Agent."""

import pytest
import json
from agents.teaching_agent import TeachingAgent, _safe_json_parse


@pytest.fixture
def dummy_rag():
    """Simple stub implementing the retrieve interface."""
    class R:
        def __init__(self):
            self.calls = []
        def retrieve(self, topic, k=5, where=None):
            self.calls.append((topic, k, where))
            return [{"source": "src", "text": "content"}]
    return R()


@pytest.fixture
def teaching_agent(dummy_rag):
    """Create a TeachingAgent with a dummy RAG database."""
    # pass empty API key to trigger fallback behaviour in some tests
    return TeachingAgent(minimax_api_key="", rag_vectordb=dummy_rag)


def test_safe_json_parse():
    """Ensure _safe_json_parse handles plain JSON, fenced blocks, and junk."""
    assert _safe_json_parse('{"foo":1}') == {"foo": 1}
    assert _safe_json_parse("```json\n{\"bar\":2}\n```") == {"bar": 2}
    assert _safe_json_parse("no json here") is None


def test_build_user_message():
    """Verify that the user message contains topic, level and instructions."""
    msg = TeachingAgent._build_user_message(
        topic="Algebra",
        level="intermediate",
        curriculum=[],
        papers=[],
        marking=[],
    )
    assert "Topic: Algebra" in msg
    assert "generate the lesson JSON" in msg


def test_retrieve_methods(teaching_agent, dummy_rag):
    """_retrieve should safely call the RAG client and handle errors."""
    # valid call
    result = teaching_agent._retrieve("topic", doc_type="curriculum", k=2)
    assert result == [{"source": "src", "text": "content"}]
    assert dummy_rag.calls[-1] == ("topic", 2, {"document_type": "curriculum"})

    # RAG raising exception -> returns empty
    class Broken:
        def retrieve(self, *args, **kwargs):
            raise RuntimeError("boom")
    teaching_agent.rag = Broken()
    assert teaching_agent._retrieve("t") == []

    # RAG is None -> empty list
    teaching_agent.rag = None
    assert teaching_agent._retrieve("anything") == []


def test_call_llm_no_api(teaching_agent):
    """Without an API key, _call_llm should return an error dict."""
    out = teaching_agent._call_llm("sys", "user")
    assert out["status"] == "error"
    assert "No MiniMax API key" in out["error"]


def test_call_llm_success(monkeypatch, teaching_agent):
    """Simulate a successful anthropic client response."""
    class DummyMsg:
        def __init__(self, text):
            self.text = text

    class DummyResp:
        def __init__(self, text):
            self.content = [DummyMsg(text)]

    fake_client = type(
        "C",
        (),
        {"messages": type("M", (), {"create": lambda self, **kw: DummyResp('{"hello": "world"}')})()},
    )()

    teaching_agent._client = fake_client
    teaching_agent._model = "dummy"
    out = teaching_agent._call_llm("sys", "usr")
    assert out == {"hello": "world"}


def test_generate_lesson_and_history(teaching_agent):
    """End-to-end lesson generation utilising stubbed llm and rag."""
    teaching_agent._call_llm = lambda s, u: {"status": "success", "content_blocks": []}
    teaching_agent.rag = type("R", (), {"retrieve": lambda self, *args, **kw: [{"source": "A", "text": "T"}]})()
    lesson = teaching_agent.generate_lesson(
        topic="T", level="L", student_profile={"learning_style": "visual"}
    )
    assert lesson["topic"] == "T"
    assert lesson["llm_response"]["status"] == "success"
    assert "lesson_id" in lesson

    history = teaching_agent.get_lesson_history()
    assert history and history[0]["lesson_id"] == lesson["lesson_id"]

    exported = teaching_agent.export_lesson(lesson["lesson_id"])
    assert isinstance(exported, str)
    assert json.loads(exported)["topic"] == "T"
    assert teaching_agent.export_lesson("nonexistent") is None

