import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

logger = logging.getLogger("finnews_ai.config")

# Resolve directories
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

BACKEND_ENV = BASE_DIR / ".env"
ROOT_ENV = PROJECT_ROOT / ".env"

def _load_env_files() -> str:
    """
    Loads environment files with proper precedence:
    1. Load root .env (if present)
    2. Load backend/.env (if present) with override=True so backend/.env takes precedence.
    Returns a human-readable description of active env sources.
    """
    loaded_files = []
    
    # Load root .env first
    if ROOT_ENV.is_file():
        load_dotenv(dotenv_path=ROOT_ENV, override=False)
        loaded_files.append(f"root (.env: {ROOT_ENV})")

    # Load backend/.env with override=True to guarantee it takes precedence
    if BACKEND_ENV.is_file():
        load_dotenv(dotenv_path=BACKEND_ENV, override=True)
        loaded_files.append(f"backend (backend/.env: {BACKEND_ENV})")

    if not loaded_files:
        load_dotenv()
        return "system environment or local working directory"

    return " & ".join(loaded_files)

# Perform initial load
_active_source = _load_env_files()

class Settings:
    """Application settings loaded from environment variables."""
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "").strip()
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "").strip()
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b").strip() or "qwen/qwen3.8-27b"
    ACTIVE_SOURCE: str = _active_source

    @classmethod
    def reload(cls):
        """Reload environment variables if changed at runtime."""
        cls.ACTIVE_SOURCE = _load_env_files()
        cls.NEWS_API_KEY = os.getenv("NEWS_API_KEY", "").strip()
        cls.GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
        cls.GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip() or "llama-3.3-70b-versatile"
        logger.info("Configuration reloaded from %s", cls.ACTIVE_SOURCE)

    @classmethod
    def get_active_env_file(cls) -> str:
        """Returns the primary .env path being used."""
        if BACKEND_ENV.is_file():
            return str(BACKEND_ENV)
        elif ROOT_ENV.is_file():
            return str(ROOT_ENV)
        return "None found"

    @classmethod
    def has_news_key(cls) -> bool:
        """Checks if a valid, non-placeholder NewsAPI key is set."""
        val = cls.NEWS_API_KEY
        if not val:
            return False
        if val in ("your_newsapi_key_here", "your_api_key_here") or val.startswith("your_"):
            return False
        return True

    @classmethod
    def has_groq_key(cls) -> bool:
        """Checks if a valid, non-placeholder Groq API key is set."""
        val = cls.GROQ_API_KEY
        if not val:
            return False
        if val in ("your_groq_api_key_here", "your_api_key_here") or val.startswith("your_"):
            return False
        return True

    @classmethod
    def get_safe_status(cls) -> Dict[str, Any]:
        """Returns non-sensitive configuration diagnostics for debugging."""
        return {
            "active_env_file": cls.get_active_env_file(),
            "backend_env_exists": BACKEND_ENV.is_file(),
            "root_env_exists": ROOT_ENV.is_file(),
            "news_api_key_configured": cls.has_news_key(),
            "groq_api_key_configured": cls.has_groq_key(),
            "groq_model": cls.GROQ_MODEL,
        }

settings = Settings()

