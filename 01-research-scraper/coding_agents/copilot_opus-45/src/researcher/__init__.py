"""PaperTrail - Research Paper Catalog with GraphRAG-based search."""

import uvicorn


def main() -> None:
    """Run the PaperTrail application."""
    uvicorn.run(
        "researcher.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )


__all__ = ["main"]
