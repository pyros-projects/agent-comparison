"""PaperTrail - Research paper catalog with GraphRAG and semantic search."""

from researcher.main import app

def main() -> None:
    """Entry point for the application."""
    import uvicorn
    from researcher.config import settings
    
    uvicorn.run(
        "researcher.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
