from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Runtime configuration sourced from environment variables."""

    model_config = SettingsConfigDict(env_file=('.env',), env_file_encoding='utf-8', case_sensitive=False)

    app_name: str = Field(default="PaperTrail")
    data_dir: Path = Field(default=Path("var/data"))
    attachments_dir: Path = Field(default=Path("var/attachments"))
    continuous_import_poll_seconds: int = Field(default=900, ge=30)
    continuous_import_batch_size: int = Field(default=10, ge=1)
    default_model: str | None = Field(default=None, validation_alias='DEFAULT_MODEL')
    default_embedding_model: str | None = Field(default=None, validation_alias='DEFAULT_EMBEDDING_MODEL')
    enable_litellm: bool = Field(default=True)
    enable_sentence_transformers: bool = Field(default=True)
    graph_similarity_threshold: float = Field(default=0.78, ge=0.0, le=1.0)
    log_level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR'] = Field(default='INFO')
    websocket_history: int = Field(default=200, ge=0)
    background_backfill_interval: int = Field(default=300, ge=30)

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.attachments_dir.mkdir(parents=True, exist_ok=True)


settings = AppSettings()
settings.ensure_dirs()
