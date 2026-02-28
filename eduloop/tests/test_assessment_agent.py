"""Unit tests for Assessment Agent."""

import pytest
import json
from agents.assessment_agent import AssessmentAgent, _safe_json_parse


@pytest.fixture
def dummy_rag():
    class R:
        def retrieve(self, topic, k=5, where=None):
            return [{"source": "ms", "text": "marking"}]
    return R()


@pytest.fixture
def assessment_agent(dummy_rag):
    return AssessmentAgent(minimax_api_key="", rag_vectordb=dummy_rag)


def test_safe_json_parse():
    assert _safe_json_parse('{"x":1}') == {"x": 1}
    assert _safe_json_parse("```{'x':2}```") is None
    assert _safe_json_parse("```json\n{\"x\":2}\n```") == {"x": 2}


def test_build_user_message():
    msg = AssessmentAgent._build_user_message(
        topic="Calc",
        question_text="Q?",
        student_answer="Ans",
        marking=[],
        papers=[],
    )
    assert "Topic: Calc" in msg
    assert "Student's Answer" in msg


def test_retrieve(assessment_agent):
    out = assessment_agent._retrieve("topic", doc_type="paper", k=1)
    assert out == [{"source": "ms", "text": "marking"}]
    assessment_agent.rag = None
    assert assessment_agent._retrieve("x") == []


def test_call_llm_no_api(assessment_agent):
    r = assessment_agent._call_llm("s", "u")
    assert r["status"] == "error"
    assert "No MiniMax API key" in r["error"]


def test_call_llm_success(assessment_agent):
    class DummyMsg:
        def __init__(self, t):
            self.text = t

    class DummyResp:
        def __init__(self, t):
            self.content = [DummyMsg(t)]

    fake_client = type(
        "C",
        (),
        {"messages": type("M", (), {"create": lambda self, **kw: DummyResp('{"score": 90}')})()},
    )()
    assessment_agent._client = fake_client
    out = assessment_agent._call_llm("s", "u")
    assert out == {"score": 90}


def test_evaluate_and_history(assessment_agent):
    assessment_agent._call_llm = lambda s, u: {"status": "success", "score_percentage": 75}
    assessment_agent.rag = type("R", (), {"retrieve": lambda self, *args, **kw: [{"source": "S", "text": "T"}]})()
    res = assessment_agent.evaluate("Area", "Q", "A", difficulty="foundational")
    assert res["topic"] == "Area"
    assert res["llm_response"]["status"] == "success"
    assert "assessment_id" in res
    hist = assessment_agent.get_history()
    assert hist and hist[0]["assessment_id"] == res["assessment_id"]

