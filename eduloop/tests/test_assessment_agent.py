"""Unit tests for Assessment Agent."""

import pytest
from agents.assessment_agent import AssessmentAgent, QuestionDifficulty


@pytest.fixture
def assessment_agent():
    """Create an AssessmentAgent instance for testing."""
    return AssessmentAgent(dse_curriculum_db=None)


def test_assessment_generation(assessment_agent):
    """Test assessment generation."""
    assessment = assessment_agent.generate_assessment(
        topic="Quadratic Equations",
        num_questions=3,
        difficulty="intermediate"
    )
    
    assert assessment["topic"] == "Quadratic Equations"
    assert assessment["difficulty"] == "intermediate"
    assert len(assessment["questions"]) == 3
    assert assessment["total_marks"] > 0


def test_student_evaluation(assessment_agent):
    """Test student response evaluation."""
    evaluation = assessment_agent.evaluate_student_response(
        question_id="Q1",
        student_answer="The solution is x = 2",
        question_type="short_answer"
    )
    
    assert "score" in evaluation
    assert "error_analysis" in evaluation
    assert "feedback" in evaluation
    assert "marks_obtained" in evaluation


def test_diagnostic_report(assessment_agent):
    """Test diagnostic report generation."""
    responses = [
        {
            "question_id": "Q1",
            "marks_obtained": 6,
            "marks_total": 6,
            "error_analysis": {"calculation_error": 0}
        },
        {
            "question_id": "Q2",
            "marks_obtained": 3,
            "marks_total": 6,
            "error_analysis": {"conceptual_misunderstanding": 1}
        }
    ]
    
    report = assessment_agent.generate_diagnostic_report(responses, "Polynomials")
    
    assert report["topic"] == "Polynomials"
    assert "performance" in report
    assert "knowledge_gaps" in report
    assert "recommendations" in report
    assert report["performance"]["percentage"] == 75.0


def test_level_assessment(assessment_agent):
    """Test HKDSE level assessment."""
    # Excellent performance
    level = assessment_agent._assess_level(85, 100)
    assert level == "Level 5*"
    
    # Good performance
    level = assessment_agent._assess_level(70, 100)
    assert level == "Level 5"
    
    # Average performance
    level = assessment_agent._assess_level(60, 100)
    assert level == "Level 4"
    
    # Poor performance
    level = assessment_agent._assess_level(30, 100)
    assert level == "Below Level 3"


def test_error_analysis(assessment_agent):
    """Test error analysis."""
    errors = assessment_agent._analyze_errors("I forgot the formula", "short_answer")
    
    assert isinstance(errors, dict)
    assert "forgot" in str(errors).lower() or len(errors) > 0


def test_recommendations_generation(assessment_agent):
    """Test recommendation generation."""
    gaps = [
        {"area": "Quadratic Equations", "frequency": 3, "severity": "high"},
        {"area": "Factoring", "frequency": 2, "severity": "medium"}
    ]
    
    recommendations = assessment_agent._generate_recommendations(gaps, "Mathematics")
    
    assert len(recommendations) > 0
    assert any("Quadratic" in rec for rec in recommendations)


def test_severity_assessment(assessment_agent):
    """Test error severity assessment."""
    severity = assessment_agent._assess_severity("conceptual_misunderstanding")
    assert severity == "high"
    
    severity = assessment_agent._assess_severity("notation_error")
    assert severity == "low"
