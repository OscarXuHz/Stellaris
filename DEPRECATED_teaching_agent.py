"""Teaching Agent implementation for EduLoop.

Generates personalized, multi-modal lesson content using RAG and MiniMax TTS.
Integrates with Config for API credentials and KnowledgeRetriever for curriculum access.
"""

import json
import logging
import os
import base64
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime

from config.config import Config, MiniMaxConfig
from utils.helpers import generate_entity_id, save_json, get_dse_level


# Configure logging
logger = logging.getLogger(__name__)


class TeachingAgent:
    """
    Generates personalized lessons using RAG-enhanced curriculum and MiniMax TTS.
    
    Integrates with:
    - KnowledgeRetriever: Retrieves relevant curriculum chunks via RAG
    - MiniMax API: Generates multilingual audio narration (Cantonese/English)
    - Config: Manages API credentials and model selection
    """
    
    def __init__(self, config: Config, retriever) -> None:
        """
        Initialize TeachingAgent with config and knowledge retriever.
        
        Args:
            config: Config instance with AWS Bedrock and MiniMax settings
            retriever: KnowledgeRetriever instance for curriculum access
        """
        self.config = config
        self.retriever = retriever
        self.lesson_history: List[Dict[str, Any]] = []
        self.minimax_api_key = MiniMaxConfig.MINIMAX_API_KEY
        self.minimax_group_id = MiniMaxConfig.MINIMAX_GROUP_ID
        self.minimax_base_url = MiniMaxConfig.MINIMAX_BASE_URL
        # LLM endpoint may differ from audio endpoint
        self.minimax_llm_url = getattr(MiniMaxConfig, 'MINIMAX_LLM_URL', f"{self.minimax_base_url}/llm")
        
        logger.info("TeachingAgent initialized with config and retriever")
    
    def generate_lesson(
        self,
        topic: str,
        level: str,
        subject: str,
        paper: Optional[str] = None,
        previous_gaps: Optional[List[str]] = None,
        student_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive lesson with RAG-retrieved curriculum and audio narration.
        
        Args:
            topic: DSE curriculum topic (e.g., "Quadratic Equations")
            level: Difficulty level ("foundational", "intermediate", "advanced")
            subject: DSE subject (e.g., "Math Foundation", "Math I", "Math II")
            paper: Optional specific exam paper ("Paper 1", "Paper 2")
            previous_gaps: Optional list of previously identified knowledge gaps
            student_context: Optional dict with learning preferences and history
        
        Returns:
            Lesson dict conforming to Teaching → Assessment protocol:
            - lesson_id: Unique identifier
            - topic, difficulty_level, subject: Lesson metadata
            - content: Dict with key_concepts, learning_objectives, misconceptions, dse_coverage
            - sections: List of content sections with optional audio narration
            - audio_narration: Dict with url, language, duration
            - student_context: Provided student info
            - created_at: ISO timestamp
        """
        logger.info(f"Generating lesson: topic={topic}, level={level}, subject={subject}")
        
        try:
            # Step 1: Retrieve curriculum chunks via RAG
            curriculum_chunks = self._retrieve_curriculum(topic, subject)
            
            # Step 2: Build detailed prompt for LLM
            gaps_text = "\n".join(previous_gaps) if previous_gaps else "None identified"
            prompt = self._build_lesson_prompt(
                context="\n\n".join(curriculum_chunks),
                level=level,
                gaps=gaps_text
            )
            
            # Step 3: Invoke LLM (placeholder for Bedrock integration)
            # TODO: Replace with actual Bedrock call when integrated
            llm_response = self._invoke_llm(prompt, topic, level)
            
            # Step 4: Parse LLM response into structured lesson
            lesson_structure = self._create_lesson_structure(llm_response)
            
            # Step 5: Generate audio narration for key sections
            language = student_context.get("preferred_language", "yue") if student_context else "yue"
            audio_narration = self._generate_audio_narration(
                text=lesson_structure.get("summary", ""),
                language=language
            )
            
            # Step 6: Construct final lesson dict
            lesson = {
                "lesson_id": lesson_structure.get("lesson_id"),
                "topic": topic,
                "difficulty_level": level,
                "subject": subject,
                "paper": paper,
                "content": {
                    "key_concepts": lesson_structure.get("objectives", []),
                    "learning_objectives": lesson_structure.get("objectives", []),
                    "misconceptions_addressed": self._extract_misconceptions(lesson_structure),
                    "dse_coverage": f"{subject} - {paper or 'Papers 1 & 2'}"
                },
                "sections": lesson_structure.get("sections", []),
                "summary": lesson_structure.get("summary", ""),
                "key_takeaways": lesson_structure.get("key_takeaways", []),
                "estimated_duration": lesson_structure.get("estimated_duration", 30),
                "difficulty": level,
                "audio_narration": audio_narration,
                "student_context": student_context or {},
                "created_at": datetime.now().isoformat()
            }
            
            self.lesson_history.append(lesson)
            logger.info(f"Lesson generated: {lesson['lesson_id']}")
            return lesson
            
        except Exception as e:
            logger.error(f"Error generating lesson: {str(e)}", exc_info=True)
            raise
    
    def _retrieve_curriculum(self, topic: str, subject: str) -> List[str]:
        """
        Retrieve relevant curriculum chunks via RAG retriever.
        
        Args:
            topic: Curriculum topic
            subject: DSE subject
        
        Returns:
            List of relevant text chunks from curriculum
        """
        try:
            query = f"{subject}: {topic}"
            chunks = self.retriever.get_relevant_chunks(
                query=query,
                subject=subject,
                top_k=5
            )
            logger.info(f"Retrieved {len(chunks)} curriculum chunks for {query}")
            return chunks
        except AttributeError:
            logger.warning("Retriever missing get_relevant_chunks method; using fallback")
            return [f"Curriculum content for {topic} in {subject}"]
        except Exception as e:
            logger.error(f"Error retrieving curriculum: {str(e)}")
            return []
    
    def _build_lesson_prompt(self, context: str, level: str, gaps: str) -> str:
        """
        Build a detailed prompt for LLM to generate lesson content.
        
        Args:
            context: Curriculum material from RAG
            level: Difficulty level for instruction tailoring
            gaps: Previous knowledge gaps to address
        
        Returns:
            Formatted prompt for LLM
        """
        level_guidance = {
            "foundational": "Assume no prior knowledge. Use simple language and concrete examples.",
            "intermediate": "Assume basic understanding. Introduce deeper concepts and connections.",
            "advanced": "Assume solid foundation. Focus on complex applications and exam-level rigor."
        }
        
        prompt = f"""Generate a comprehensive DSE lesson with the following structure:

CURRICULUM MATERIAL:
{context}

DIFFICULTY LEVEL: {level}
{level_guidance.get(level, level_guidance['foundational'])}

KNOWLEDGE GAPS TO ADDRESS:
{gaps}

Please provide the lesson in JSON format with these keys:
- objectives: List of learning objectives (3-5 items)
- sections: List of {{heading, content}} dicts covering the topic thoroughly
- key_takeaways: 3-5 key points students must remember
- summary: A concise summary for audio narration
- estimated_duration_minutes: 15-60 range based on complexity
- misconceptions: Common errors and corrections

Focus on HKDSE exam relevance and practical problem-solving strategies."""
        
        return prompt
    
    def _call_minimax_llm(self, prompt: str) -> str:
        """
        Low-level call to Minimax LLM endpoint.

        Args:
            prompt: Text prompt to send to the model.

        Returns:
            The generated string produced by the LLM.
        """
        if not self.minimax_api_key:
            logger.warning("Minimax API key not configured; skipping LLM call")
            return ""

        url = self.minimax_llm_url
        headers = {
            "Authorization": f"Bearer {self.minimax_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": MiniMaxConfig.MINIMAX_TEXT_MODEL,
            "input": prompt,
            "group_id": self.minimax_group_id,
            "max_tokens": 1500,
            "temperature": 0.7
        }
        try:
            logger.info(f"Sending prompt to MiniMax LLM ({url})")
            resp = requests.post(url, json=payload, headers=headers, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            # attempt to extract text
            if isinstance(data, dict):
                if "output" in data:
                    return data["output"]
                if "choices" in data and isinstance(data["choices"], list):
                    return "".join(c.get("text", "") for c in data["choices"])
                if "reply" in data:
                    return data["reply"]
            return json.dumps(data)
        except Exception as e:
            logger.error(f"Error calling MiniMax LLM: {e}")
            return ""

    def _invoke_llm(self, prompt: str, topic: str, level: str) -> str:
        """
        Invoke LLM (MiniMax) to generate lesson content.
        
        Args:
            prompt: Detailed instruction prompt
            topic: Curriculum topic (for context)
            level: Difficulty level (for context)
        
        Returns:
            LLM-generated lesson content (JSON string or structured text)
        """
        logger.info(f"Invoking MiniMax LLM for {topic} at {level} level")
        result = self._call_minimax_llm(prompt)
        if result:
            return result
        # fallback to placeholder if API fails
        logger.warning("Minimax LLM returned empty response, using placeholder")
        placeholder_response = {
            "objectives": [
                f"Understand the core concepts of {topic}",
                f"Apply {topic} to HKDSE exam questions",
                f"Solve complex {topic} problems efficiently"
            ],
            "sections": [
                {
                    "heading": "Introduction to " + topic,
                    "content": f"This section introduces {topic} with foundational definitions and context."
                },
                {
                    "heading": "Key Concepts and Theory",
                    "content": f"Explore the essential principles underlying {topic}."
                },
                {
                    "heading": "Worked Examples",
                    "content": f"Step-by-step solutions demonstrating {topic} problem-solving."
                },
                {
                    "heading": "Common Mistakes",
                    "content": f"Learn to avoid typical errors in {topic}."
                }
            ],
            "key_takeaways": [
                f"Core principle 1 of {topic}",
                f"Core principle 2 of {topic}",
                f"Exam-specific strategy for {topic}"
            ],
            "summary": f"Master {topic} with systematic approach and practice problems.",
            "estimated_duration_minutes": 25 if level == "foundational" else (40 if level == "intermediate" else 50),
            "misconceptions": [
                {"error": "Common error in step 1", "correction": "Correct approach"},
                {"error": "Common error in step 2", "correction": "Correct approach"}
            ]
        }
        return json.dumps(placeholder_response)
    
    def _generate_audio_narration(self, text: str, language: str = "yue") -> Dict[str, Any]:
        """
        Generate audio narration using MiniMax TTS API.
        
        Args:
            text: Text to convert to speech
            language: Language code ("yue" for Cantonese, "en" for English)
        
        Returns:
            Dict with audio_url, language, duration_seconds, base64_audio (optional)
        """
        if not self.minimax_api_key or not self.minimax_group_id:
            logger.warning("MiniMax credentials not configured; skipping audio generation")
            return {
                "url": None,
                "language": language,
                "duration_seconds": 0,
                "status": "skipped_no_credentials"
            }
        
        try:
            # Prepare MiniMax TTS request
            url = f"{self.minimax_base_url}/audio_generation"
            headers = {
                "Authorization": f"Bearer {self.minimax_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "group_id": self.minimax_group_id,
                "text": text[:2000],  # Truncate to API limit
                "voice_id": "male-cantonese" if language == "yue" else "male-english",
                "speed": 1.0,
                "pitch": 1.0
            }
            
            logger.info(f"Requesting audio generation from MiniMax for {language}")
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            audio_data = response.json()
            
            # Extract audio URL and metadata
            audio_url = audio_data.get("audio_url")
            duration = audio_data.get("duration_seconds", 0)
            
            # Optionally fetch and encode audio as base64
            audio_base64 = None
            if audio_url:
                try:
                    audio_response = requests.get(audio_url, timeout=10)
                    audio_response.raise_for_status()
                    audio_base64 = base64.b64encode(audio_response.content).decode()
                except Exception as e:
                    logger.warning(f"Could not fetch audio file: {str(e)}")
            
            logger.info(f"Audio generated: {duration}s, language={language}")
            return {
                "url": audio_url,
                "language": language,
                "duration_seconds": duration,
                "base64_audio": audio_base64,
                "status": "success"
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"MiniMax TTS API error: {str(e)}")
            return {
                "url": None,
                "language": language,
                "duration_seconds": 0,
                "status": f"error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error in audio generation: {str(e)}", exc_info=True)
            return {
                "url": None,
                "language": language,
                "duration_seconds": 0,
                "status": f"error: {str(e)}"
            }
    
    def _create_lesson_structure(self, raw_content: str) -> Dict[str, Any]:
        """
        Parse LLM output into structured lesson dictionary.
        
        Args:
            raw_content: JSON string from LLM output
        
        Returns:
            Structured lesson dict with all required keys
        """
        try:
            # Parse JSON if possible
            if raw_content.startswith("{"):
                lesson_data = json.loads(raw_content)
            else:
                # Fallback: parse markdown-like structure
                lesson_data = self._parse_markdown_structure(raw_content)
            
            # Ensure all required keys exist
            lesson_structure = {
                "lesson_id": generate_entity_id("lesson"),
                "title": lesson_data.get("title", "DSE Lesson"),
                "objectives": lesson_data.get("objectives", []),
                "sections": lesson_data.get("sections", []),
                "summary": lesson_data.get("summary", ""),
                "key_takeaways": lesson_data.get("key_takeaways", []),
                "estimated_duration": lesson_data.get("estimated_duration_minutes", 30),
                "difficulty": lesson_data.get("difficulty", "intermediate")
            }
            
            # Process sections to ensure audio fields
            processed_sections = []
            for section in lesson_structure.get("sections", []):
                processed_section = {
                    "heading": section.get("heading", ""),
                    "content": section.get("content", ""),
                    "audio_base64": section.get("audio_base64")  # Optional
                }
                processed_sections.append(processed_section)
            
            lesson_structure["sections"] = processed_sections
            
            logger.info(f"Lesson structure created: {lesson_structure['lesson_id']}")
            return lesson_structure
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse lesson JSON: {str(e)}")
            # Return minimal structure on parse error
            return {
                "lesson_id": generate_entity_id("lesson"),
                "title": "DSE Lesson",
                "objectives": [],
                "sections": [{"heading": "Content", "content": raw_content}],
                "summary": "",
                "key_takeaways": [],
                "estimated_duration": 30,
                "difficulty": "intermediate"
            }
        except Exception as e:
            logger.error(f"Unexpected error in lesson structure creation: {str(e)}")
            raise
    
    def _extract_misconceptions(self, lesson_structure: Dict[str, Any]) -> List[str]:
        """
        Extract misconceptions from lesson structure.
        
        Args:
            lesson_structure: Structured lesson dict
        
        Returns:
            List of misconception strings
        """
        misconceptions = []
        
        # Look for misconceptions field
        if "misconceptions" in lesson_structure:
            for item in lesson_structure["misconceptions"]:
                if isinstance(item, dict):
                    misconceptions.append(f"{item.get('error', '')} → {item.get('correction', '')}")
                else:
                    misconceptions.append(str(item))
        
        return misconceptions
    
    def _parse_markdown_structure(self, content: str) -> Dict[str, Any]:
        """
        Parse markdown-formatted lesson content into structured dict.
        
        Args:
            content: Markdown-formatted text
        
        Returns:
            Structured dict with lesson components
        """
        # Simple markdown parser for headings and sections
        sections = []
        current_section = None
        
        for line in content.split("\n"):
            if line.startswith("## "):
                if current_section:
                    sections.append(current_section)
                current_section = {
                    "heading": line.replace("## ", "").strip(),
                    "content": ""
                }
            elif current_section and line.strip():
                current_section["content"] += line + "\n"
        
        if current_section:
            sections.append(current_section)
        
        return {
            "objectives": [],
            "sections": sections,
            "key_takeaways": [],
            "summary": content[:200],
            "estimated_duration_minutes": 30
        }
    
    def get_lesson_history(self) -> List[Dict[str, Any]]:
        """Retrieve all generated lessons in current session."""
        return self.lesson_history
    
    def export_lesson(self, lesson_id: str, filepath: Optional[str] = None) -> Optional[str]:
        """
        Export lesson as JSON file.
        
        Args:
            lesson_id: ID of lesson to export
            filepath: Optional destination path (else returns JSON string)
        
        Returns:
            JSON string or filepath if saved
        """
        lesson = next((l for l in self.lesson_history if l.get("lesson_id") == lesson_id), None)
        
        if not lesson:
            logger.warning(f"Lesson {lesson_id} not found")
            return None
        
        if filepath:
            if save_json(lesson, filepath):
                logger.info(f"Lesson exported to {filepath}")
                return filepath
            else:
                return None
        else:
            return json.dumps(lesson, indent=2, ensure_ascii=False)
