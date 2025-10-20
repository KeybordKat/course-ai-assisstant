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

# API Keys (not needed for free local stack, but kept for compatibility)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

# Local LLM Settings (Ollama)
DEFAULT_LLM = os.getenv("DEFAULT_LLM", "ollama")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# LLM Parameters
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4096"))

# Vector DB Settings
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# Retrieval Settings
RELEVANCE_THRESHOLD = float(os.getenv("RELEVANCE_THRESHOLD", "0.3"))  # Minimum relevance score (0-1)

# Search Settings
SEARCH_ENGINE = os.getenv("SEARCH_ENGINE", "duckduckgo")

# Application Settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"


def validate_config():
    """Validate that required configuration is present."""
    # For local setup, we just need Ollama
    if DEFAULT_LLM == "ollama":
        print(f"✓ Using local LLM: {MODEL_NAME}")
    elif DEFAULT_LLM == "openai" and not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not found in environment")
    elif DEFAULT_LLM == "anthropic" and not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY not found in environment")

    # Create directories if they don't exist
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    VECTORDB_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    print("✓ Configuration validated")


if __name__ == "__main__":
    validate_config()
    print(f"\n📁 Project Configuration:")
    print(f"  Project root: {PROJECT_ROOT}")
    print(f"  PDF directory: {PDF_DIR}")
    print(f"  Vector DB: {VECTORDB_DIR}")
    print(f"\n🤖 LLM Settings:")
    print(f"  Provider: {DEFAULT_LLM}")
    print(f"  Model: {MODEL_NAME}")
    print(f"  Temperature: {TEMPERATURE}")
    print(f"  Max tokens: {MAX_TOKENS}")
    print(f"\n🔍 Search Settings:")
    print(f"  Search engine: {SEARCH_ENGINE}")
    print(f"\n📊 Vector DB Settings:")
    print(f"  Embedding model: {EMBEDDING_MODEL}")
    print(f"  Chunk size: {CHUNK_SIZE}")
    print(f"  Chunk overlap: {CHUNK_OVERLAP}")