"""Configuration management for the course AI assistant."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PDF_DIR = DATA_DIR / "pdfs"
VECTORDB_DIR = DATA_DIR / "vectordb"
CACHE_DIR = DATA_DIR / "cache"

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

# LLM Settings
DEFAULT_LLM = os.getenv("DEFAULT_LLM", "anthropic")
MODEL_NAME = os.getenv("MODEL_NAME", "claude-sonnet-4-20250514")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4096"))

# Vector DB Settings
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Application Settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"


def validate_config():
    """Validate that required configuration is present."""
    if DEFAULT_LLM == "openai" and not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not found in environment")
    if DEFAULT_LLM == "anthropic" and not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY not found in environment")
    if not TAVILY_API_KEY and not SERPAPI_KEY:
        print("Warning: No search API key found. Web search will not work.")

    # Create directories if they don't exist
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    VECTORDB_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    print("✓ Configuration validated")


if __name__ == "__main__":
    validate_config()
    print(f"Project root: {PROJECT_ROOT}")
    print(f"PDF directory: {PDF_DIR}")
    print(f"Using LLM: {DEFAULT_LLM} - {MODEL_NAME}")