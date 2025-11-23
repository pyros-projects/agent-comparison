"""Configuration management using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False
    )
    
    # LiteLLM Configuration
    default_model: Optional[str] = None
    default_embedding_model: Optional[str] = None
    
    # Azure OpenAI (if used)
    azure_api_key: Optional[str] = None
    azure_api_base: Optional[str] = None
    azure_api_version: Optional[str] = None
    
    # OpenAI (if used)
    openai_api_key: Optional[str] = None
    
    # Application settings
    db_path: str = "data/papertrail.json"
    embeddings_db_path: str = "data/embeddings.json"
    graph_db_path: str = "data/graph.json"
    tasks_db_path: str = "data/tasks.json"
    backfill_db_path: str = "data/backfill.json"
    
    # Fallback models
    fallback_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000


settings = Settings()
