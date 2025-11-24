# PaperTrail - Research Paper Catalog with GraphRAG

A comprehensive research paper catalog system with continuous autonomous ingestion, GraphRAG-based search, and multiple specialized views for AI/ML researchers.

## Quick Start

1. Install dependencies: `uv sync`
2. Configure environment: `cp .envtemplate .env` and edit credentials
3. Start backend: `uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000`
4. Install frontend: `cd frontend && npm install && npm run dev`

Visit http://localhost:3000 to access the application.

## Features

- **Paper Ingestion**: Manual and continuous arXiv ingestion
- **GraphRAG**: Relationship mapping between papers
- **Theory Mode**: Analyze hypotheses with evidence
- **Four Views**: Papers list, details, theory mode, dashboard
- **Fallback System**: Graceful degradation when LLM unavailable

## Environment Variables

Required:
- DEFAULT_MODEL: LLM model name (e.g., gpt-3.5-turbo)
- DEFAULT_EMBEDDING_MODEL: Embedding model (e.g., text-embedding-3-small)
- OPENAI_API_KEY: Your API key

## Testing

Use Playwright MCP to test all features:
- Paper ingestion with real-time feedback
- Search functionality
- Theory mode analysis
- Fallback system testing
