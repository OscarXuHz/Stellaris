"""Unit tests for Assessment Agent."""

import pytest
import json
from agents.assessment_agent import AssessmentAgent, QuestionDifficulty
from config.config import Config


@pytest.fixture
def assessment_agent():
    """Create an AssessmentAgent instance for testing."""
    cfg = Config()
    return AssessmentAgent(cfg, dse_curriculum_db=None)


def test_assessment_generation(assessment_agent):
    """Test assessment generation from a lesson dict."""
    lesson = {
        "lesson_id": "lesson_001",
        "topic": "Quadratic Equations",
        "difficulty_level": "intermediate"
    }
    assessment = assessment_agent.generate_assessment(lesson, num_questions=3)

    assert assessment["topic"] == "Quadratic Equations"
    assert assessment["difficulty"] == "intermediate"
    assert len(assessment["questions"]) == 3
    assert assessment["total_marks"] > 0


def test_student_evaluation(assessment_agent):
    """Test evaluation of a generated assessment."""
    lesson = {"lesson_id": "lesson_002", "topic": "Polynomials", "difficulty_level": "foundational"}
    assessment = assessment_agent.generate_assessment(lesson, num_questions=2)
    # create perfect answers using the correct_answer field
    answers = []
    for q in assessment["questions"]:
        answers.append({"question_id": q["question_id"], "answer_text": q.get("correct_answer")})
    results = assessment_agent.evaluate_student_response(assessment["assessment_id"], answers)

    assert results["assessment_id"] == assessment["assessment_id"]
    assert "total_score" in results
    assert "percentage" in results
    assert "dse_level" in results


def test_diagnostic_report(assessment_agent):
    """Test diagnostic report creation from results dict."""
    results = {
        "total_score": 9,
        "percentage": 75.0,
        "dse_level": "Level 5",
        "student_answers": [
            {"question_id": "Q1", "score": 6, "marks": 6, "topic": "A"},
            {"question_id": "Q2", "score": 3, "marks": 6, "topic": "B"}
        ],
        "recommendations": ["practice more"],
        "gaps": ["B"]
    }
    report = assessment_agent.generate_diagnostic_report("assess_test", results)

    assert "performance_summary" in report
    assert report["dse_level_mapping"] == "Level 5"


def test_level_assessment(assessment_agent):
    """Test HKDSE level assessment utility."""
    assert assessment_agent._assess_level(85, 100) == "Level 5*"
    assert assessment_agent._assess_level(70, 100) == "Level 5"
    assert assessment_agent._assess_level(60, 100) == "Level 4"
    assert assessment_agent._assess_level(30, 100) == "Below Level 3"


def test_error_analysis(assessment_agent):
    """Test error analysis utility."""
    errors = assessment_agent._analyze_errors("I forgot the formula", "short_answer")
    assert isinstance(errors, dict)
    assert any(v > 0 for v in errors.values())


def test_recommendations_generation(assessment_agent):
    """Test recommendation generation logic."""
    gaps = [
        {"area": "Quadratic Equations", "frequency": 3, "severity": "high"},
        {"area": "Factoring", "frequency": 2, "severity": "medium"}
    ]
    recommendations = assessment_agent._generate_recommendations(gaps, "Mathematics")
    assert recommendations
    assert any("Quadratic" in rec for rec in recommendations)


def test_severity_assessment(assessment_agent):
    """Test error severity assessment."""
    assert assessment_agent._assess_severity("conceptual_misunderstanding") == "high"
    assert assessment_agent._assess_severity("notation_error") == "low"


def test_generate_question_via_llm(assessment_agent, monkeypatch):
    """Ensure _generate_question uses Minimax LLM output."""
    sample_output = {
        "question_text": "What is 2+2?",
        "type": "mcq",
        "options": ["2", "3", "4", "5"],
        "correct_answer": "4",
        "marks": 1,
        "explanation": "basic addition",
        "marking_scheme": {"correct_answer": 1}
    }
    def fake_call(prompt, system_prompt=None):
        return json.dumps(sample_output)

    monkeypatch.setattr(assessment_agent, "_call_minimax_llm", fake_call)
    q = assessment_agent._generate_question("Math", "foundational", "Math Foundation", "Paper 1")
    assert q["question_text"] == "What is 2+2?"
    assert q["correct_answer"] == "4"
    assert q["marks"] == 1


def test_score_question_via_llm(assessment_agent, monkeypatch):
    """Ensure _score_question consults LLM for non-MCQ responses."""
    question = {
        "question_id": "q1",
        "type": "short_answer",
        "question_text": "Explain 2+2",
        "correct_answer": "4",
        "marks": 2,
        "marking_scheme": {"correct_answer": 2}
    }
    def fake_call(prompt, system_prompt=None):
        return json.dumps({"score": 2, "is_correct": True})

    monkeypatch.setattr(assessment_agent, "_call_minimax_llm", fake_call)
    score, correct = assessment_agent._score_question(question, "4")
    assert score == 2 and correct


def test_llm_misconceptions(assessment_agent, monkeypatch):
    """LLM should return a list of misconceptions when available."""
    topics = ["Quadratics", "Polynomials"]
    def fake_call(prompt, system_prompt=None):
        return json.dumps(["Misunderstanding A", "Misunderstanding B"])
    monkeypatch.setattr(assessment_agent, "_call_minimax_llm", fake_call)
    results = assessment_agent._analyze_misconceptions([{"topic": t} for t in topics])
    assert "Misunderstanding A" in results


def test_llm_recommendations(assessment_agent, monkeypatch):
    """LLM should be used to generate recommendations if configured."""
    def fake_call(prompt, system_prompt=None):
        return json.dumps(["Do extra problems", "Review notes"])
    monkeypatch.setattr(assessment_agent, "_call_minimax_llm", fake_call)
    recs = assessment_agent._recommend_next_topics(50, ["topic1"])
    assert "Do extra problems" in recs
