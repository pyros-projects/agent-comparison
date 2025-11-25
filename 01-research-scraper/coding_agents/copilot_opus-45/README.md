# PaperTrail - Research Paper Catalog

A sophisticated research paper management system with GraphRAG-based search, continuous arXiv imports, and theory analysis capabilities.

## Features

- **📚 Paper Management**: Import, organize, and annotate research papers from arXiv
- **🔍 Semantic Search**: Find papers using natural language queries powered by embeddings
- **🕸️ Knowledge Graph**: Explore paper relationships and discover connections
- **🧪 Theory Mode**: Test hypotheses against your paper collection (requires LLM)
- **🔄 Continuous Import**: Autonomous paper discovery from arXiv categories
- **📊 Dashboard**: Visualize your collection with statistics and trends
- **💾 Graceful Degradation**: Works offline with fallback systems

## Architecture

### Backend (Python/FastAPI)
- **FastAPI** - High-performance async web framework
- **LiteLLM** - Unified LLM interface (OpenAI, Azure, etc.)
- **sentence-transformers** - Fallback embeddings when LLM unavailable
- **TinyDB** - JSON-based document database
- **NetworkX** - Knowledge graph for paper relationships

### Frontend (React/TypeScript)
- **React 18** with TypeScript
- **Vite** - Fast development build tool
- **Tailwind CSS** - Utility-first styling
- **Recharts** - Data visualization
- **WebSocket** - Real-time progress updates

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 20+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. **Clone and install backend dependencies:**
```bash
cd /path/to/project
uv sync
```

2. **Install frontend dependencies:**
```bash
cd frontend
npm install
```

3. **Set up environment variables (optional):**
```bash
# Create .env file in project root
cp .env.example .env

# Configure LLM (optional - system works without it)
DEFAULT_MODEL=gpt-4o-mini
DEFAULT_EMBEDDING_MODEL=text-embedding-3-small
AZURE_API_KEY=your-api-key
AZURE_API_BASE=https://your-endpoint.openai.azure.com
```

### Running the Application

1. **Start the backend:**
```bash
uv run researcher
# Or: uv run uvicorn researcher.api.app:app --reload --host 0.0.0.0 --port 8010
```

2. **Start the frontend (in another terminal):**
```bash
cd frontend
npm run dev
```

3. **Open the application:**
   - Frontend: http://localhost:5173
   - API docs: http://localhost:8000/docs

## Usage

### Paper Views

1. **Dashboard** (`/`): Overview of your collection with stats, charts, and recent activity
2. **Paper List** (`/papers`): Browse, search, and manage all papers
3. **Paper Detail** (`/papers/:id`): Full paper view with summary, relationships, and notes
4. **Theory Mode** (`/theory`): Test hypotheses (requires LLM)
5. **Imports** (`/imports`): Configure continuous import tasks

### Manual Paper Ingestion

Click "Ingest Paper" from the Paper List or Dashboard and enter an arXiv URL:
```
https://arxiv.org/abs/2301.00000
```

### Continuous Import

1. Go to **Imports** → **New Import Task**
2. Configure:
   - Name: "AI Papers"
   - Category: cs.AI
   - Semantic query (optional): "transformer architectures"
   - Check interval: 60 seconds
3. Click **Start** to begin autonomous import

### Theory Mode

1. Go to **Theory Mode**
2. Enter a hypothesis: "Attention mechanisms outperform RNNs for sequence modeling"
3. Click **Analyze Theory**
4. Review supporting and contradicting evidence from your papers

> ⚠️ Theory Mode requires an active LLM connection

## API Endpoints

### Papers
- `GET /api/papers` - List papers with pagination and filters
- `POST /api/papers` - Ingest new paper from arXiv URL
- `GET /api/papers/:id` - Get paper details
- `PATCH /api/papers/:id` - Update paper (status, notes, tags)
- `DELETE /api/papers/:id` - Delete paper
- `GET /api/papers/:id/similar` - Get similar papers by embedding
- `GET /api/papers/:id/related` - Get related papers from graph
- `GET /api/papers/:id/graph` - Get paper's subgraph
- `GET /api/papers/:id/bibtex` - Export BibTeX citation

### Search
- `POST /api/search/semantic` - Semantic search by embedding
- `GET /api/search/text` - Full-text search
- `POST /api/search/theory` - Theory analysis (requires LLM)
- `GET /api/search/theory/status` - Check theory mode availability

### Imports
- `GET /api/imports` - List import tasks
- `POST /api/imports` - Create import task
- `POST /api/imports/:id/start` - Start task
- `POST /api/imports/:id/stop` - Stop task
- `DELETE /api/imports/:id` - Delete task

### Dashboard
- `GET /api/dashboard` - Get stats, activity, clusters, growth
- `GET /api/dashboard/status` - System status (LLM/embedding availability)
- `GET /api/dashboard/graph` - Full knowledge graph

### WebSocket
- `WS /api/ws` - Real-time updates for imports and backfill

## Fallback Systems

PaperTrail is designed to work without an LLM connection:

| Feature | With LLM | Without LLM |
|---------|----------|-------------|
| Paper summary | AI-generated | Placeholder |
| Keywords | AI-extracted | Placeholder |
| Theory Mode | Full analysis | Disabled |
| Semantic search | ✅ Works | ✅ Works (sentence-transformers) |
| Paper import | ✅ Works | ✅ Works |
| Knowledge graph | ✅ Works | ✅ Works |

When LLM becomes available, a **backfill worker** automatically fills in placeholder content.

## Testing

Run the test suite:
```bash
uv run pytest tests/ -v
```

Run specific test file:
```bash
uv run pytest tests/test_database.py -v
```

## Data Storage

All data is stored in `~/.papertrail/` by default:
- `papers.json` - Paper database
- `embeddings.json` - Embedding store
- `graph.gml` - Knowledge graph
- `import_tasks.json` - Import task configurations

Configure data directory:
```bash
export PAPERTRAIL_DATA_DIR=/custom/path
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEFAULT_MODEL` | LiteLLM model for text generation | `gpt-4o-mini` |
| `DEFAULT_EMBEDDING_MODEL` | LiteLLM model for embeddings | `text-embedding-3-small` |
| `AZURE_API_KEY` | Azure OpenAI API key | - |
| `AZURE_API_BASE` | Azure OpenAI endpoint | - |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `PAPERTRAIL_DATA_DIR` | Data storage directory | `~/.papertrail` |

## Logging

Extensive logging is enabled throughout the application:
- Backend: Console output with timestamps and levels
- Frontend: Console logging for all API calls and WebSocket events

View backend logs by adjusting level:
```python
# In researcher/config.py
Config.LOG_LEVEL = "DEBUG"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `uv run pytest`
5. Submit a pull request

## License

MIT License - See LICENSE file for details.
