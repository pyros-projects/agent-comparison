# PaperTrail

PaperTrail is a research paper catalog that ingests arXiv links, builds semantic search indexes, and exposes specialized views (List, Detail, Theory Mode, Dashboard) with GraphRAG insights and real-time telemetry.

## Requirements
- Python 3.12+
- Node 20+ for the React frontend
- `uv` for Python dependency management (install via https://github.com/astral-sh/uv)

## Backend (FastAPI)
1. Install dependencies:
   ```bash
   uv sync
   ```
2. Run the API + background workers:
   ```bash
   uv run researcher
   ```
3. Environment:
   - Copy `.envtemplate` to `.env` and set `DEFAULT_MODEL` / `DEFAULT_EMBEDDING_MODEL` if you have litellm credentials.
   - When LLM/embeddings are unavailable the service auto-falls back to placeholders + sentence-transformers.

## Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```
The dev server proxies `/api` and `/ws` traffic to the FastAPI backend.

## Testing
Automated tests cover storage filtering and LLM fallback logic:
```bash
uv run pytest
```

**Manual testing with Playwright MCP is mandatory** as outlined in `prompt.md`. Validate:
- Manual ingestion flow with WebSocket progress
- Continuous import task lifecycle and dashboard metrics
- Paper detail view (graph, similar papers, notes, exports)
- Theory mode both when LLM is available and unavailable (disabled UI messaging)
- Fallback scenarios (disable DEFAULT_MODEL/DEFAULT_EMBEDDING_MODEL)

## Folder Structure
- `src/researcher`: FastAPI app, ingestion pipelines, GraphRAG, fallbacks, WebSocket events
- `frontend`: React SPA implementing the four required views
- `docs/architecture.md`: High-level design notes
- `tests`: Pytest coverage for core logic

## Logging
- Backend uses structured JSON logs (see `researcher/logging.py`).
- Frontend logs every API call and WebSocket event to the browser console for easier correlation.

## Next Steps
- Expand automated coverage for ingestion + graph generation.
- Implement PDF text search and richer relationship visualization.
- Capture Playwright MCP run artifacts per the prompt requirements.
