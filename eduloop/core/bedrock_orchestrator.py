"""AWS Bedrock agent integration for EduLoop orchestration."""

import json
from typing import Dict, Any, Optional
import boto3
from botocore.config import Config


class BedrockAgentOrchestrator:
    """
    Manages AWS Bedrock AgentCore for autonomous agent orchestration.
    Handles Teaching and Assessment agent deployment and communication.
    """
    
    def __init__(self, region: str = "us-east-1"):
        """Initialize Bedrock client and agent configuration."""
        config = Config(
            region_name=region,
            retries={'max_attempts': 3}
        )
        self.bedrock_runtime = boto3.client('bedrock-runtime', config=config)
        self.bedrock_agents = boto3.client('bedrock-agent', config=config)
        self.teaching_agent_id: Optional[str] = None
        self.assessment_agent_id: Optional[str] = None
    
    def invoke_teaching_agent(self, 
                             topic: str, 
                             level: str, 
                             student_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoke Teaching Agent to generate personalized lesson content.
        
        Args:
            topic: DSE curriculum topic
            level: Difficulty level (foundational, intermediate, advanced)
            student_context: Student profile and learning history
        
        Returns:
            Generated lesson content with multimedia elements
        """
        prompt = self._build_teaching_prompt(topic, level, student_context)
        
        response = self.bedrock_runtime.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20241022",
            body=json.dumps({"prompt": prompt, "max_tokens": 2000})
        )
        
        return self._parse_response(response)
    
    def invoke_assessment_agent(self,
                               topic: str,
                               student_response: str,
                               difficulty: str) -> Dict[str, Any]:
        """
        Invoke Assessment Agent to generate questions and evaluate responses.
        
        Args:
            topic: Topic being assessed
            student_response: Student's answer/response
            difficulty: Question difficulty level
        
        Returns:
            Assessment report with scoring and analysis
        """
        prompt = self._build_assessment_prompt(topic, student_response, difficulty)
        
        response = self.bedrock_runtime.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20241022",
            body=json.dumps({"prompt": prompt, "max_tokens": 2000})
        )
        
        return self._parse_response(response)
    
    def create_agent_handshake_protocol(self) -> Dict[str, Any]:
        """
        Define JSON protocol for Teaching-Assessment agent communication.
        Ensures seamless data exchange in the learning loop.
        """
        from config.prompts import COMMUNICATION_PROTOCOL
        return COMMUNICATION_PROTOCOL
    
    @staticmethod
    def _build_teaching_prompt(topic: str, level: str, context: Dict[str, Any]) -> str:
        """Build system prompt for Teaching Agent."""
        from config.prompts import get_teaching_system_prompt
        return get_teaching_system_prompt(topic, level, context)

    @staticmethod
    def _build_assessment_prompt(topic: str, response: str, difficulty: str) -> str:
        """Build system prompt for Assessment Agent."""
        from config.prompts import get_assessment_system_prompt
        return get_assessment_system_prompt(topic, response, difficulty)

    @staticmethod
    def _parse_response(response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Bedrock API response into structured format."""
        try:
            body = response['body'].read().decode('utf-8')
            parsed = json.loads(body)
            return parsed
        except Exception as e:
            return {"error": str(e), "raw_response": response}
    
    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Check status of deployed Bedrock agent."""
        try:
            response = self.bedrock_agents.get_agent(agentId=agent_id)
            return {
                "agent_id": agent_id,
                "status": response.get("agentStatus", "unknown"),
                "created_at": response.get("createdAt", ""),
                "updated_at": response.get("updatedAt", "")
            }
        except Exception as e:
            return {"error": str(e)}
