from __future__ import annotations

import uvicorn

from .api import app, create_app
from .config import settings


__all__ = ["app", "create_app"]


def main() -> None:
    uvicorn.run(
        "researcher.api:app",
        host="0.0.0.0",
        port=8000,
        factory=False,
        reload=False,
        log_level=settings.log_level.lower(),
    )
