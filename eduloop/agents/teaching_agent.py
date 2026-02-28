"""Teaching Agent implementation for EduLoop."""

from typing import Dict, Any, Optional, List
import json
from datetime import datetime


class TeachingAgent:
    """
    Specializes in generating personalized, multi-modal lesson content.
    Integrates with MiniMax API for audio generation and RAG for DSE curriculum.
    """
    
    def __init__(self, minimax_api_key: str, rag_vectordb):
        self.minimax_api_key = minimax_api_key
        self.rag_vectordb = rag_vectordb
        self.session_lessons = []
        self.dse_knowledge_base = None
    
    def generate_lesson(self, 
                       topic: str, 
                       level: str,
                       student_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive, personalized lesson with multiple modalities.
        
        Args:
            topic: DSE curriculum topic
            level: Difficulty level
            student_profile: Student learning preferences and history
        
        Returns:
            Lesson content with text, audio, and visual suggestions
        """
        # Retrieve DSE curriculum material via RAG
        curriculum_material = self.rag_vectordb.retrieve(topic, k=5)
        
        # Generate lesson content
        lesson_content = self._create_lesson_structure(topic, level, curriculum_material)
        
        # Generate audio narration (via MiniMax)
        audio_content = self._generate_audio_narration(lesson_content, student_profile)
        
        # Compile complete lesson package
        complete_lesson = {
            "lesson_id": self._generate_id(),
            "topic": topic,
            "level": level,
            "created_at": datetime.now().isoformat(),
            "content": lesson_content,
            "audio": audio_content,
            "learning_objectives": self._extract_objectives(lesson_content),
            "estimated_duration": 20,  # minutes
            "key_concepts": self._extract_key_concepts(lesson_content),
            "dse_references": [m.get("source") for m in curriculum_material]
        }
        
        self.session_lessons.append(complete_lesson)
        return complete_lesson
    
    def _create_lesson_structure(self, 
                                topic: str, 
                                level: str,
                                curriculum_material: List[Dict]) -> Dict[str, Any]:
        """
        Create structured lesson with introduction, explanation, examples, and practice.
        """
        return {
            "introduction": self._generate_introduction(topic, level),
            "main_content": self._generate_main_content(topic, curriculum_material),
            "worked_examples": self._generate_examples(topic, level),
            "key_points": self._generate_key_points(topic),
            "common_mistakes": self._generate_misconceptions(topic),
            "dse_exam_tips": self._generate_exam_tips(topic, level)
        }
    
    def _generate_introduction(self, topic: str, level: str) -> str:
        """Generate engaging introduction to topic."""
        return f"""Welcome to today's lesson on {topic}. 
        
At the {level} level, you'll learn:
- Core concepts and definitions
- Practical applications in HKDSE exams
- Problem-solving strategies

By the end of this lesson, you should be able to tackle Paper 1 and Paper 2 questions on {topic}."""
    
    def _generate_main_content(self, topic: str, materials: List[Dict]) -> str:
        """Generate main teaching content from curriculum materials."""
        content_parts = []
        for material in materials:
            content_parts.append(material.get("content", ""))
        return "\n\n".join(content_parts)
    
    def _generate_examples(self, topic: str, level: str) -> List[Dict[str, str]]:
        """Generate worked examples at appropriate difficulty level."""
        return [
            {
                "number": 1,
                "question": f"Example question on {topic} ({level} level)",
                "solution_steps": "Step-by-step solution",
                "explanation": "Why this approach works",
                "common_error": "Common mistake to avoid"
            }
        ]
    
    def _generate_key_points(self, topic: str) -> List[str]:
        """Extract and summarize key points for retention."""
        return [
            f"Key concept 1 about {topic}",
            f"Key concept 2 about {topic}",
            f"Key concept 3 about {topic}"
        ]
    
    def _generate_misconceptions(self, topic: str) -> List[Dict[str, str]]:
        """Identify and explain common misconceptions."""
        return [
            {
                "misconception": "Incorrect understanding",
                "correction": "Correct understanding",
                "explanation": "Why this matters for HKDSE"
            }
        ]
    
    def _generate_exam_tips(self, topic: str, level: str) -> Dict[str, Any]:
        """Generate HKDSE exam-specific tips and strategies."""
        return {
            "paper_focus": "Which paper(s) test this topic",
            "marks_allocation": "Typical marks for questions",
            "time_management": "Recommended time per question",
            "strategy": "Approach to solve efficiently",
            "level_5_tips": "What examiners look for in Level 5 answers" if level == "advanced" else ""
        }
    
    def _generate_audio_narration(self, 
                                 lesson_content: Dict[str, Any],
                                 student_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate audio narration using MiniMax TTS.
        Supports Cantonese and English for local relevance.
        """
        language = student_profile.get("preferred_language", "english")
        voice_tone = student_profile.get("voice_preference", "friendly")
        
        return {
            "narration_script": self._prepare_audio_script(lesson_content),
            "language": language,
            "voice_tone": voice_tone,
            "estimated_duration": 12,  # minutes
            "status": "pending_generation",  # To be filled after MiniMax API call
            "audio_url": None  # Will be populated after TTS generation
        }
    
    @staticmethod
    def _prepare_audio_script(lesson_content: Dict[str, Any]) -> str:
        """Prepare script for text-to-speech conversion."""
        parts = [
            lesson_content.get("introduction", ""),
            lesson_content.get("main_content", ""),
            "Key points: " + ", ".join(lesson_content.get("key_points", []))
        ]
        return "\n\n".join(parts)
    
    @staticmethod
    def _extract_objectives(lesson_content: Dict[str, Any]) -> List[str]:
        """Extract learning objectives from lesson content."""
        intro = lesson_content.get("introduction", "")
        # Parse objectives from introduction (simplified)
        return [
            "Understand core concepts",
            "Apply to HKDSE exam questions",
            "Solve practice problems correctly"
        ]
    
    @staticmethod
    def _extract_key_concepts(lesson_content: Dict[str, Any]) -> List[str]:
        """Extract key concepts for quick reference."""
        return lesson_content.get("key_points", [])
    
    @staticmethod
    def _generate_id() -> str:
        """Generate unique lesson ID."""
        from datetime import datetime
        import uuid
        return f"lesson_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
    
    def get_lesson_history(self) -> List[Dict[str, Any]]:
        """Retrieve lesson history for session."""
        return self.session_lessons
    
    def export_lesson(self, lesson_id: str) -> Optional[str]:
        """Export lesson as JSON for storage and sharing."""
        lesson = next((l for l in self.session_lessons if l["lesson_id"] == lesson_id), None)
        if lesson:
            return json.dumps(lesson, indent=2)
        return None
