"""Configuration management for PaperTrail."""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("papertrail")


class Config:
    """Application configuration."""

    # Base paths
    BASE_DIR = Path(__file__).parent.parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    DB_PATH = DATA_DIR / "papers.json"
    EMBEDDINGS_PATH = DATA_DIR / "embeddings"

    # LLM Configuration
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "")
    DEFAULT_EMBEDDING_MODEL = os.getenv("DEFAULT_EMBEDDING_MODEL", "")

    # Fallback embedding model (sentence-transformers)
    FALLBACK_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION = 384  # Dimension for all-MiniLM-L6-v2

    # API Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))

    # Import Configuration
    DEFAULT_CHECK_INTERVAL = 60  # seconds
    MAX_PAPERS_PER_FETCH = 20  # Reduced to avoid rate limits
    ARXIV_RATE_LIMIT = 5.0  # seconds between requests (arXiv recommends 3+)

    # Placeholders for missing LLM content
    PLACEHOLDER_SUMMARY = "<summary>"
    PLACEHOLDER_KEYWORDS = "<keywords>"
    PLACEHOLDER_ANALYSIS = "<analysis>"

    @classmethod
    def ensure_dirs(cls) -> None:
        """Ensure data directories exist."""
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.EMBEDDINGS_PATH.mkdir(parents=True, exist_ok=True)
        logger.info(f"Data directory: {cls.DATA_DIR}")
        logger.info(f"Database path: {cls.DB_PATH}")

    @classmethod
    def has_llm_config(cls) -> bool:
        """Check if LLM is configured."""
        return bool(cls.DEFAULT_MODEL)

    @classmethod
    def has_embedding_config(cls) -> bool:
        """Check if litellm embedding model is configured."""
        return bool(cls.DEFAULT_EMBEDDING_MODEL)


# Ensure directories exist on import
Config.ensure_dirs()
