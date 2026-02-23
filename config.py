"""
Configuration management for MedGemma AI Medical Triage System.
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project Root
PROJECT_ROOT = Path(__file__).parent
SRC_DIR = PROJECT_ROOT / "src"
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"
MODELS_DIR = PROJECT_ROOT / "models"

# Create directories if they don't exist
LOGS_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)
(MODELS_DIR / "cache").mkdir(exist_ok=True)


class ModelConfig:
    """Configuration for MedGemma model."""
    
    # Model selection
    MODEL_NAME: str = os.getenv("MODEL_NAME", "google/medgemma-2b")
    MODEL_CACHE_DIR: str = os.getenv("MODEL_CACHE_DIR", str(MODELS_DIR / "cache"))
    
    # Hugging Face
    HF_TOKEN: Optional[str] = os.getenv("HF_TOKEN")
    HF_HOME: str = os.getenv("HF_HOME", str(MODELS_DIR / "cache"))
    
    # Model parameters
    USE_GPU: bool = os.getenv("USE_GPU", "true").lower() == "true"
    MAX_LENGTH: int = int(os.getenv("MAX_LENGTH", "2048"))
    MAX_NEW_TOKENS: int = int(os.getenv("MAX_NEW_TOKENS", "512"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    TOP_P: float = 0.9
    TOP_K: int = 50
    
    # Performance
    LOAD_IN_8BIT: bool = False
    LOAD_IN_4BIT: bool = False
    USE_FLASH_ATTENTION: bool = False
    
    @classmethod
    def get_device(cls) -> str:
        """Get the device to use for inference."""
        if cls.USE_GPU:
            import torch
            return "cuda" if torch.cuda.is_available() else "cpu"
        return "cpu"


class AgentConfig:
    """Configuration for agent behavior."""
    
    MAX_ITERATIONS: int = int(os.getenv("MAX_AGENT_ITERATIONS", "10"))
    TIMEOUT: int = int(os.getenv("AGENT_TIMEOUT", "300"))
    RETRY_ATTEMPTS: int = 3
    RETRY_DELAY: float = 1.0


class TriageConfig:
    """Configuration for triage workflow."""
    
    # Conversation settings
    ENABLE_HISTORY: bool = os.getenv("ENABLE_CONVERSATION_HISTORY", "true").lower() == "true"
    MAX_TURNS: int = int(os.getenv("MAX_CONVERSATION_TURNS", "20"))
    
    # Urgency levels
    URGENCY_LEVELS = [
        "EMERGENCY",      # Immediate life-threatening
        "URGENT",         # Needs attention within hours
        "SEMI-URGENT",    # Needs attention within 1-2 days
        "NON-URGENT"      # Can wait for routine appointment
    ]
    
    # Care settings
    CARE_SETTINGS = [
        "Emergency Department (ER)",
        "Urgent Care Center",
        "Primary Care Physician",
        "Telemedicine Consultation",
        "Self-Care at Home"
    ]
    
    # Red flag symptoms (require immediate attention)
    # Legacy list - kept for backward compatibility
    RED_FLAGS = [
        "chest pain",
        "difficulty breathing",
        "severe bleeding",
        "altered consciousness",
        "severe head injury",
        "stroke symptoms",
        "severe allergic reaction",
        "suicidal thoughts",
        "seizure"
    ]
    
    # Critical red flags - Always EMERGENCY (life-threatening)
    # These are more specific to reduce false positives
    CRITICAL_RED_FLAGS = [
        "severe chest pain",
        "crushing chest pain",
        "crushing chest pressure",
        "chest pain radiating",
        "severe difficulty breathing",
        "cannot breathe",
        "blue lips",
        "cyanosis",
        "gasping for air",
        "stroke symptoms",
        "face drooping",
        "facial droop",
        "arm weakness",
        "arm paralysis",
        "speech difficulty",
        "slurred speech",
        "altered consciousness",
        "unresponsive",
        "severe confusion",
        "severe bleeding",
        "hemorrhage",
        "bleeding heavily",
        "severe allergic reaction",
        "anaphylaxis",
        "throat swelling",
        "severe head injury",
        "worst headache of life",
        "thunderclap headache",
        "suicidal thoughts",
        "seizure"
    ]
    
    # Warning flags - Concerning but context-dependent
    WARNING_FLAGS = [
        "chest discomfort",
        "chest pain",
        "high fever",
        "fever over 103",
        "103°f",
        "103 degrees",
        "fever 103",
        "severe abdominal pain",
        "moderate breathing difficulty",
        "shortness of breath",
        "severe injury",
        "severe pain",
        "persistent vomiting",
        "cannot keep fluids down",
        "can't keep food down",
        "can't keep fluids down",
        "extreme swelling",
        "extremely swollen",
        "purple discoloration",
        "turning purple",
        "can't bear weight",
        "can't put weight",
        "can't walk",
        "unable to walk",
        "pain getting worse",
        "progressively worse"
    ]
    
    # Severity keywords for context analysis
    # Enhanced with more specific phrases and negative indicators
    SEVERITY_KEYWORDS = {
        "critical": [
            "severe", "crushing", "worst", "sudden", "radiating",
            "intense", "unbearable", "excruciating", "life-threatening",
            "blue", "cyanosis", "unresponsive", "cannot breathe",
            "drooping", "paralyzed", "cannot speak", "hemorrhaging",
            "gasping", "worst ever", "cannot move", "won't stop bleeding",
            "throat swelling", "cannot swallow", "extreme", "acute"
        ],
        "high": [
            "significant", "extreme", "very painful", "getting worse",
            "rapidly", "spreading", "persistent", "worsening",
            "progressively worse", "increasingly", "very severe",
            "extremely swollen", "turning purple", "can't walk",
            "can't keep down"
        ],
        "moderate": [
            "moderate", "noticeable", "concerning", "uncomfortable",
            "increasing", "frequent", "persistent", "ongoing",
            "bothersome", "troublesome", "annoying"
        ],
        "low": [
            "mild", "slight", "minor", "occasional", "intermittent",
            "tolerable", "manageable", "slight", "little",
            "somewhat", "a bit", "goes away", "comes and goes",
            "improving", "better", "healing"
        ]
    }
    
    # Negative indicators that reduce severity
    NEGATION_KEYWORDS = [
        "no", "not", "without", "denies", "deny", "absent",
        "never", "neither", "none", "nothing"
    ]
    
    # Temporal indicators that suggest non-acute/historical
    TEMPORAL_KEYWORDS = [
        "history of", "previously", "past", "used to",
        "last year", "months ago", "years ago", "chronic"
    ]


class DemoConfig:
    """Configuration for demo application."""
    
    PORT: int = int(os.getenv("DEMO_PORT", "7860"))
    SHARE: bool = os.getenv("DEMO_SHARE", "false").lower() == "true"
    SERVER_NAME: str = "0.0.0.0"
    
    # UI settings
    THEME: str = "soft"
    TITLE: str = "MedGemma AI Medical Triage System"
    DESCRIPTION: str = """
    This intelligent triage system uses multiple AI agents powered by MedGemma 
    to assess your symptoms and recommend appropriate care.
    
    ⚠️ **Disclaimer**: This is a demonstration system for research purposes only. 
    It does NOT replace professional medical advice. For emergencies, call 911.
    """


class APIConfig:
    """Configuration for API (if enabled)."""
    
    HOST: str = os.getenv("API_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("API_PORT", "8000"))
    RELOAD: bool = os.getenv("DEBUG", "false").lower() == "true"


class LogConfig:
    """Configuration for logging."""
    
    LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", str(LOGS_DIR / "app.log"))
    FORMAT: str = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
    
    # Log rotation
    ROTATION: str = "100 MB"
    RETENTION: str = "30 days"
    COMPRESSION: str = "zip"


# Export all configs
__all__ = [
    "ModelConfig",
    "AgentConfig", 
    "TriageConfig",
    "DemoConfig",
    "APIConfig",
    "LogConfig",
    "PROJECT_ROOT",
    "SRC_DIR",
    "DATA_DIR",
    "LOGS_DIR",
    "MODELS_DIR"
]
