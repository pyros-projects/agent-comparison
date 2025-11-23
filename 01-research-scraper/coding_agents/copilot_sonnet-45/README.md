# PaperTrail - Research Paper Catalog

A research paper catalog with continuous autonomous ingestion, GraphRAG-based search, and multiple specialized views. Built with FastAPI backend and React frontend.

## Features

- **Paper Ingestion**: Manual arXiv link input and continuous autonomous monitoring
- **GraphRAG**: Knowledge graph showing paper relationships (authors, citations, topics)
- **Semantic Search**: Vector similarity-based paper discovery
- **Theory Mode**: RAG-based argument discovery for hypothesis validation
- **Four Specialized Views**:
  - **Dashboard**: Statistics, charts, continuous import management
  - **Paper List**: Filterable/sortable catalog with status management
  - **Paper Detail**: Comprehensive metadata, AI summaries, relationships, notes
  - **Theory Mode**: Pro/contra argument analysis for hypothesis validation
- **Real-time Updates**: WebSocket-based progress tracking
- **Resilient Architecture**: Graceful degradation when LLM/embeddings unavailable

## Quick Start

### 1. Install Dependencies

```bash
# Backend dependencies
uv sync

# Frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Configure Environment

```bash
# Copy template and edit with your credentials
cp .envtemplate .env
```

Required environment variables:
- `DEFAULT_MODEL`: LLM model (e.g., `azure/gpt-4.1` or `openai/gpt-4`)
- `DEFAULT_EMBEDDING_MODEL`: Embedding model (e.g., `azure/text-embedding-3-small`)
- Plus corresponding API keys (see `.envtemplate`)

### 3. Run the Application

**Option A: Run both backend and frontend together**
```bash
# Terminal 1: Start backend
uv run uvicorn researcher.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start frontend
cd frontend && npm run dev
```

**Option B: Build and run production**
```bash
# Build frontend
cd frontend && npm run build && cd ..

# Run backend (serves frontend automatically)
uv run uvicorn researcher.main:app --host 0.0.0.0 --port 8000
```

### 4. Access the Application

- **Development**: http://localhost:3000 (frontend dev server)
- **Production**: http://localhost:8000 (backend serves built frontend)
- **API Docs**: http://localhost:8000/docs

## Usage Guide

### Adding Papers

1. Navigate to **Papers** view
2. Enter arXiv URL or ID (e.g., `2103.12345` or `https://arxiv.org/abs/2103.12345`)
3. Click "Add Paper" - watch real-time progress
4. Paper is automatically:
   - Downloaded and text extracted
   - Embedded for semantic search
   - Analyzed by LLM (if available)
   - Added to knowledge graph

### Continuous Import

1. Go to **Dashboard**
2. Create a new import task:
   - Name it (e.g., "CS.AI Papers")
   - Optional: Filter by arXiv category (e.g., `cs.AI`)
   - Click "Create Task"
3. Task runs every 5 minutes, importing new matching papers
4. Monitor progress and imported count in dashboard

### Semantic Search

1. Use the search bar in **Papers** view
2. Enter natural language query (e.g., "transformers for image processing")
3. Results ranked by semantic similarity

### Theory Mode

1. Navigate to **Theory Mode**
2. Enter your hypothesis (e.g., "Attention mechanisms improve model interpretability")
3. Click "Analyze Hypothesis"
4. View pro/contra arguments with:
   - Relevance scores
   - AI-generated summaries
   - Key quotes from papers
5. Export analysis as text file

### Paper Details

Click any paper to view:
- Full metadata and abstract
- AI-generated summary and key contributions
- Similar papers (by embeddings)
- Related papers (by graph relationships)
- Personal notes
- Export options (BibTeX, PDF link)

## Fallback Strategy

PaperTrail is designed to work even when services are unavailable:

### Embedding Fallback
- **Primary**: litellm with configured embedding model
- **Fallback**: sentence-transformers (automatic, always works)
- Papers can always be ingested and searched

### LLM Graceful Degradation
- **When Available**: Full AI summaries, analysis, theory mode
- **When Unavailable**: 
  - Papers stored with `<summary>` placeholders
  - Added to backfill queue
  - Automatically processed when LLM becomes available
  - Theory mode disabled with clear message

### Background Backfill Worker
- Monitors backfill queue continuously
- Processes papers with placeholders when LLM becomes available
- No manual intervention needed

## Architecture

```
┌─────────────────────────────────────────────┐
│            React Frontend (Vite)            │
│  Dashboard │ Papers │ Detail │ Theory       │
└──────────────────┬──────────────────────────┘
                   │ REST API + WebSocket
┌──────────────────┴──────────────────────────┐
│          FastAPI Backend (Python)           │
│  ┌────────────────────────────────────────┐ │
│  │  Services Layer                        │ │
│  │  • Ingestion  • Search  • Graph        │ │
│  │  • LLM        • Embeddings • Backfill  │ │
│  └────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────┐ │
│  │  Data Layer (TinyDB)                   │ │
│  │  • Papers  • Embeddings  • Graph       │ │
│  │  • Tasks   • Backfill Queue            │ │
│  └────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

**Tech Stack:**
- **Backend**: FastAPI, litellm, sentence-transformers, TinyDB, NetworkX
- **Frontend**: React, Vite, Recharts, Axios
- **Data Sources**: arXiv API, PyPDF2 for text extraction
- **Real-time**: WebSocket for progress updates

## Testing

```bash
# Run core functionality tests
uv run pytest tests/test_core.py -v

# Test with LLM disabled (validates fallback)
# Remove DEFAULT_MODEL from .env temporarily
uv run pytest tests/test_core.py -v
```

## Project Structure

```
researcher/
├── src/researcher/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── config.py            # Configuration
│   ├── database.py          # TinyDB wrapper
│   ├── embeddings.py        # Embedding service (with fallback)
│   ├── llm.py               # LLM service (with graceful degradation)
│   ├── ingestion.py         # arXiv ingestion
│   ├── search.py            # Search and theory mode
│   ├── graph.py             # GraphRAG service
│   ├── continuous_import.py # Background import tasks
│   ├── backfill.py          # Background backfill worker
│   └── logger.py            # Logging setup
├── frontend/
│   ├── src/
│   │   ├── main.jsx         # React entry point
│   │   ├── App.jsx          # Main app component
│   │   ├── api.js           # API client
│   │   ├── websocket.js     # WebSocket hook
│   │   └── views/           # View components
│   │       ├── DashboardView.jsx
│   │       ├── PaperListView.jsx
│   │       ├── PaperDetailView.jsx
│   │       └── TheoryModeView.jsx
│   ├── package.json
│   └── vite.config.js
├── tests/
│   └── test_core.py         # Core functionality tests
├── data/                    # Created at runtime (TinyDB storage)
├── pyproject.toml
└── README.md
```

## Comprehensive Logging

Both backend and frontend include extensive logging:

**Backend (Terminal):**
- Service initialization and availability
- Paper ingestion progress
- Search operations and results
- Fallback activations
- Background worker activities
- All errors with stack traces

**Frontend (Browser Console):**
- Component lifecycle
- API calls and responses
- WebSocket messages
- User actions
- State changes
- Service availability status

Check browser DevTools console and terminal output for detailed operation logs.

## Troubleshooting

### LLM Not Working
- Check `.env` has correct `DEFAULT_MODEL` and API keys
- Papers will still be ingested with placeholders
- Backfill worker will process them when LLM becomes available

### Embeddings Not Working
- Should automatically fall back to sentence-transformers
- Check terminal logs for "Fallback embedding model loaded"
- All functionality still works, just uses different embedding model

### Papers Not Appearing
- Check terminal for ingestion errors
- Verify arXiv ID is valid
- Check WebSocket connection status in UI

### Continuous Import Not Running
- Ensure task is active (green status)
- Check task interval and filters
- Monitor backend logs for import activity

## Development

```bash
# Run backend with auto-reload
uv run uvicorn researcher.main:app --reload

# Run frontend with hot-reload
cd frontend && npm run dev

# Build frontend for production
cd frontend && npm run build
```

## License

MIT
