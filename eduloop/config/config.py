"""Environment configuration for EduLoop."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")


class AWSConfig:
    """AWS Bedrock configuration."""
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022")


class MiniMaxConfig:
    """MiniMax API configuration."""
    MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY")
    MINIMAX_GROUP_ID = os.getenv("MINIMAX_GROUP_ID")
    MINIMAX_BASE_URL = os.getenv("MINIMAX_BASE_URL", "https://api.minimaxi.com/v1")
    MINIMAX_TEXT_MODEL = os.getenv("MINIMAX_TEXT_MODEL", "abab6-advanced")
    MINIMAX_AUDIO_VOICE = os.getenv("MINIMAX_AUDIO_VOICE", "male-cantonese")


class StreamlitConfig:
    """Streamlit frontend configuration."""
    PAGE_TITLE = "EduLoop DSE"
    PAGE_ICON = "📚"
    LAYOUT = "wide"
    INITIAL_SIDEBAR_STATE = "expanded"


class DatabaseConfig:
    """Database and persistence configuration."""
    VECTOR_DB_TYPE = os.getenv("VECTOR_DB_TYPE", "chroma")  # chroma, pinecone, etc.
    VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./data/vector_db")
    SESSION_DB_PATH = os.getenv("SESSION_DB_PATH", "./data/sessions")


class DSEConfig:
    """HKDSE curriculum and exam configuration."""
    SYLLABUSES = ["Math Foundation", "Math I", "Math II"]
    TOPICS = {
        "Math Foundation": ["Quadratic Equations", "Functions", "Geometry", "Trigonometry", "Statistics"],
        "Math I": ["Calculus", "Probability", "Binomial Distribution", "Differentiation Application"],
        "Math II": ["Matrix Algebra", "Vectors", "Integration", "Mathematical Induction"]
    }
    PAPER_TYPES = ["Paper 1", "Paper 2"]
    MAX_MARKS_PER_PAPER = 100
    TOTAL_EXAM_TIME_MINUTES = 150


def get_config():
    """Get active configuration based on environment."""
    return Config()
