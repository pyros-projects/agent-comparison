# PaperTrail Architecture Plan

## High-Level Overview
- **Backend**: FastAPI application that exposes REST + WebSocket interfaces, orchestrates ingestion, search, theory mode, and background workers.
- **Frontend**: React (Vite) single-page app communicating with backend via JSON APIs + WebSockets for live progress.
- **Data Storage**: TinyDB for metadata, embeddings, tasks, notes; NetworkX persisted graph for relationships.
- **Embeddings**: Prefer litellm provider via DEFAULT_EMBEDDING_MODEL; fallback to sentence-transformers when litellm raises errors or env missing.
- **LLM Usage**: Summaries, tags, pro/contra arguments via litellm DEFAULT_MODEL; fallback writes placeholder text and enqueues backfill job.
- **GraphRAG**: Graph builder links papers based on shared authors, categories, vector similarity; exposed for detail + dashboard views.

## Key Components
1. **`researcher/config.py`**
   - Loads env vars, logging config, poll intervals, fallback flags.
2. **`researcher/logging.py`**
   - Structured logging setup (JSON friendly) for backend + WebSocket streaming.
3. **`researcher/models.py`**
   - Pydantic models for Paper, Task, TheoryQuery, GraphEdge, etc.
4. **`researcher/storage.py`**
   - TinyDB wrapper, indexes, helper methods, persistence for tasks + notes.
5. **`researcher/embeddings.py`**
   - `EmbeddingService` that tries litellm first, falls back to sentence-transformers, caches vector size metadata.
6. **`researcher/llm.py`**
   - `LLMService` with graceful degradation + placeholder tokens (`<summary>`, `<keywords>`...), publishes availability events.
7. **`researcher/graph.py`**
   - Maintains NetworkX `MultiDiGraph`, updates relationships after ingestion, supports graph queries for UI.
8. **`researcher/ingestion.py`**
   - Manual ingestion workflow, PDF fetch + extraction, metadata hydration via arXiv API.
   - Continuous import task manager with start/stop, interval loop, exponential backoff, filter config.
9. **`researcher/theory.py`**
   - Executes theory mode queries (pro/contra) if LLM available; otherwise surfaces disabled state message.
10. **`researcher/backfill.py`**
    - Background worker scanning TinyDB for placeholder fields, reruns LLM once available.
11. **`researcher/api.py`**
    - FastAPI routers for ingestion, search, tasks, theory, dashboard, notes; WebSocket endpoint for live updates.
12. **`researcher/main.py`**
    - Application factory (`create_app`) and CLI entry point for `uvicorn`.

## Frontend Views
- **List View**: Table with filters, search, pagination, quick actions; calls `/papers`, `/papers/{id}`.
- **Detail View**: Shows metadata, summary, tags, notes, similar papers, graph visualization (D3), export buttons.
- **Theory Mode**: Input + results columns; disables UI when `/status` reports LLM unavailable.
- **Dashboard**: Aggregations, charts (Recharts/Chart.js), import task status, activity timeline.

## Real-Time Feedback
- WebSocket channel `ws://.../ws/events` streaming ingestion progress, task status, fallback alerts, errors.
- Client writes console logs for state transitions + API calls; server logs structured JSON.

## Testing Strategy
- Pytest module for ingestion + fallback pieces using httpx mocking.
- Integration-style tests for search + embeddings.
- Documented manual Playwright scenarios covering all views + fallback toggles.
