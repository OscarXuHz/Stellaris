"""Utility functions for EduLoop."""

import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_session_id() -> str:
    """Generate unique session ID."""
    return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"


def generate_entity_id(prefix: str) -> str:
    """Generate unique entity ID with prefix."""
    return f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"


def save_json(data: Dict[str, Any], filepath: str) -> bool:
    """Save data as JSON file."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved to {filepath}")
        return True
    except Exception as e:
        logger.error(f"Failed to save {filepath}: {str(e)}")
        return False


def load_json(filepath: str) -> Optional[Dict[str, Any]]:
    """Load data from JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Loaded from {filepath}")
        return data
    except Exception as e:
        logger.error(f"Failed to load {filepath}: {str(e)}")
        return None


def calculate_percentage(obtained: float, total: float) -> float:
    """Calculate percentage safely."""
    if total == 0:
        return 0.0
    return (obtained / total) * 100


def get_dse_level(percentage: float) -> str:
    """Map percentage to HKDSE level."""
    if percentage >= 90:
        return "Level 5**"
    elif percentage >= 80:
        return "Level 5*"
    elif percentage >= 70:
        return "Level 5"
    elif percentage >= 60:
        return "Level 4"
    elif percentage >= 50:
        return "Level 3"
    elif percentage >= 40:
        return "Level 2"
    else:
        return "Level 1"


def format_timestamp(iso_string: str) -> str:
    """Format ISO timestamp to readable format."""
    try:
        dt = datetime.fromisoformat(iso_string)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return iso_string


def merge_dicts(base: Dict, updates: Dict) -> Dict:
    """Recursively merge two dictionaries."""
    result = base.copy()
    for key, value in updates.items():
        if isinstance(value, dict) and key in result and isinstance(result[key], dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


class SessionManager:
    """Manage session data persistence."""
    
    def __init__(self, session_dir: str = "./data/sessions"):
        self.session_dir = session_dir
        self._ensure_directory(session_dir)
    
    def save_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Save session data."""
        filepath = f"{self.session_dir}/{session_id}.json"
        return save_json(data, filepath)
    
    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load session data."""
        filepath = f"{self.session_dir}/{session_id}.json"
        return load_json(filepath)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session data."""
        import os
        filepath = f"{self.session_dir}/{session_id}.json"
        try:
            os.remove(filepath)
            logger.info(f"Deleted session {session_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {str(e)}")
            return False
    
    def list_sessions(self) -> List[str]:
        """List all saved sessions."""
        import os
        try:
            files = os.listdir(self.session_dir)
            return [f.replace('.json', '') for f in files if f.endswith('.json')]
        except:
            return []
    
    @staticmethod
    def _ensure_directory(path: str) -> None:
        """Ensure directory exists."""
        import os
        os.makedirs(path, exist_ok=True)
