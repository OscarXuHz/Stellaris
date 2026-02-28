"""Protocol definition for Teaching-Assessment agent handshake."""

AGENT_HANDSHAKE_PROTOCOL = {
    "version": "1.0",
    "description": "JSON protocol for autonomous Teaching and Assessment agent communication",
    
    "teaching_to_assessment": {
        "lesson_id": "string - unique lesson identifier",
        "topic": "string - curriculum topic being taught",
        "difficulty_level": "foundational|intermediate|advanced",
        "content": {
            "key_concepts": ["list of main concepts covered"],
            "learning_objectives": ["what students should learn"],
            "misconceptions_addressed": ["common errors explained"],
            "dse_coverage": "which HKDSE papers this covers"
        },
        "audio_narration": {
            "url": "string - link to TTS audio",
            "language": "english|cantonese|mixed",
            "duration_seconds": "integer"
        },
        "student_context": {
            "previous_performance": "0-100 percentage",
            "learning_style": "visual|auditory|mixed",
            "preferred_language": "english|cantonese"
        }
    },
    
    "assessment_to_teaching": {
        "assessment_id": "string - unique assessment identifier",
        "topic": "string - topic assessed",
        "student_performance": {
            "score": "0-100",
            "marks_obtained": "integer",
            "marks_total": "integer",
            "hkdse_level": "Level 1-5**"
        },
        "knowledge_gaps": [
            {
                "area": "string - specific topic gap",
                "frequency": "integer - how many times shown",
                "severity": "low|medium|high"
            }
        ],
        "error_analysis": {
            "conceptual_errors": "integer count",
            "calculation_errors": "integer count",
            "incomplete_answers": "integer count",
            "notation_errors": "integer count"
        },
        "misconceptions_identified": [
            "string - specific misconception pattern"
        ],
        "recommendations": {
            "next_topic_difficulty": "foundational|intermediate|advanced",
            "focus_areas": ["top areas to review"],
            "estimated_time_to_mastery": "string - e.g., '1-2 hours'"
        }
    },
    
    "shared_session_context": {
        "session_id": "string - persistent session identifier",
        "student_id": "string - anonymous student identifier",
        "timestamp": "ISO 8601 format",
        "learning_path_metadata": {
            "completed_topics": ["topic1", "topic2"],
            "current_focus": "string - current topic",
            "overall_progress": "0-100 percentage"
        }
    },
    
    "example_teaching_payload": {
        "lesson_id": "lesson_20240228_123456_abc12345",
        "topic": "Quadratic Equations",
        "difficulty_level": "intermediate",
        "content": {
            "key_concepts": ["Standard form", "Discriminant", "Roots", "Factoring"],
            "learning_objectives": [
                "Solve quadratic equations by factoring",
                "Use the quadratic formula",
                "Understand the discriminant"
            ],
            "misconceptions_addressed": [
                "Forgetting to rearrange to standard form",
                "Sign errors in the quadratic formula"
            ],
            "dse_coverage": "Paper 1, 2 - worth 5-8 marks per paper"
        },
        "audio_narration": {
            "url": "https://minimax.api/audio/lesson_12345.mp3",
            "language": "cantonese",
            "duration_seconds": 720
        },
        "student_context": {
            "previous_performance": 72,
            "learning_style": "visual",
            "preferred_language": "cantonese"
        }
    },
    
    "example_assessment_payload": {
        "assessment_id": "assess_20240228_123457_def67890",
        "topic": "Quadratic Equations",
        "student_performance": {
            "score": 75,
            "marks_obtained": 15,
            "marks_total": 20,
            "hkdse_level": "Level 5"
        },
        "knowledge_gaps": [
            {
                "area": "Quadratic Formula Application",
                "frequency": 2,
                "severity": "medium"
            },
            {
                "area": "Discriminant Interpretation",
                "frequency": 1,
                "severity": "low"
            }
        ],
        "error_analysis": {
            "conceptual_errors": 1,
            "calculation_errors": 2,
            "incomplete_answers": 0,
            "notation_errors": 1
        },
        "misconceptions_identified": [
            "Signs in quadratic formula application",
            "When to use discriminant vs. factoring"
        ],
        "recommendations": {
            "next_topic_difficulty": "intermediate",
            "focus_areas": [
                "Quadratic Formula - practice more examples",
                "Discriminant - review theory and applications"
            ],
            "estimated_time_to_mastery": "1 hour focused practice"
        }
    }
}

# Export for use in other modules
if __name__ == "__main__":
    import json
    print(json.dumps(AGENT_HANDSHAKE_PROTOCOL, indent=2))
