# Use Case 01: Research Scraper

**A complex RAG application with autonomous data collection, graph-based exploration, and multi-modal interaction.**

## The Challenge

Build a research catalog database that autonomously discovers, analyzes, and organizes AI-related research papers. The application must operate in multiple modes:

- **Cataloging Mode** - Continuously search for, download, and analyze new papers using LLMs
- **Search Mode** - Browse papers via a filterable Paper List View and dive deep into individual papers via Paper Detail View with comprehensive analysis, relationship graphs, and similar paper recommendations
- **Theory Mode** - Validate theories by finding supporting/opposing evidence in the catalog
- **Dashboard** - High-level visualization of catalog statistics, research clusters, and ingestion activity

See [`_base/prompt.md`](_base/prompt.md) for the complete specification.

## Requirements

- .env with working credentials/litellm env vars for LLM and embedding model communication https://docs.litellm.ai/docs/providers
- playwright mcp for manual UI testing https://github.com/microsoft/playwright-mcp
- uv installed https://docs.astral.sh/uv/getting-started/installation/

## What This Tests

### Long-Running Background Processes
The cataloging mode runs indefinitely until stopped by the user. This tests whether the agent can:
- Design appropriate async/background task architectures
- Implement progress tracking and state management
- Handle graceful shutdown and resumption
- Provide real-time feedback to users during long operations

### GraphRAG Implementation
The task requires building a graph-based retrieval system on top of a simple database (TinyDB). This evaluates:
- Understanding of graph data structures and RAG concepts
- Ability to implement clustering and similarity detection
- Cross-linking related papers
- Semantic search and relationship mapping

### Multi-Mode Application Design
Three distinct interaction modes test architectural flexibility:
- Can the agent design a coherent navigation structure?
- How does state management work across different modes?
- Is the architecture extensible for future modes?

### LLM Integration & Orchestration
Heavy use of LLMs for analysis (summarization, tagging, scoring) tests:
- Proper use of `litellm` with provided configuration
- Prompt engineering for consistent, structured outputs
- Error handling and retry logic for LLM calls
- Cost awareness and efficient API usage

### Web Scraping & Data Collection
Autonomous discovery from arXiv and other research sources requires:
- Implementing robust scraping logic
- Handling different data sources and formats
- Rate limiting and respectful crawling
- Data validation and cleaning

### Modern Full-Stack Development
The requirement for a Vite + React frontend with Python backend tests:
- Clean separation of concerns (API design)
- Modern SPA patterns and state management
- Real-time updates (websockets or polling)
- Professional UI/UX with status bars and dashboards

### Rich UI/UX Design
The Paper List and Paper Detail views test:
- Effective data presentation and information hierarchy
- Interactive filtering, sorting, and navigation
- Visual relationship graphs and cluster visualizations
- Smooth transitions between list and detail views
- Responsive design and layout patterns
- Balancing information density with readability

### Database Design Without Guardrails
Using TinyDB (a simple JSON database) instead of a full-featured DB tests:
- Schema design from scratch
- Indexing and query optimization strategies
- Graph layer implementation on top of simple key-value storage
- Data consistency without ACID guarantees

## Why This Use Case?

This task was chosen because it combines **multiple complex subsystems** that must work together coherently:

1. **Background workers** (scraping/ingestion)
2. **LLM orchestration** (analysis pipeline)
3. **Database layer** (with graph semantics)
4. **API layer** (backend endpoints)
5. **Frontend UI** (multiple views and modes)
6. **Real-time feedback** (status and progress)

It's realistic — this mirrors real-world applications like research tools, content aggregators, or knowledge management systems. An agent that handles this well demonstrates:

- Ability to break down complex requirements
- Strong architectural decision-making
- Full-stack development competence
- Understanding of production concerns (state, errors, performance)
- UX awareness (feedback, navigation, visualization)

## Evaluation Focus

When reviewing implementations, pay attention to:

### Architecture
- How are background tasks managed? (Threading, async, queues?)
- How is state shared between frontend and backend?
- Is the codebase modular and maintainable?
- Are there clear boundaries between components?

### LLM Usage
- Are prompts well-structured and consistent?
- Is error handling robust for LLM failures?
- Are costs considered (caching, batching)?
- Are results validated and parsed correctly?

### Data & Search
- How is the graph structure implemented?
- Is similarity search effective?
- Can the system handle 100s or 1000s of items?
- Are queries efficient?

### UX & Polish
- Is real-time feedback clear and helpful?
- Are the different modes intuitive to navigate?
- Is the Paper List View effective for browsing and filtering?
- Does the Paper Detail View present information clearly and comprehensively?
- Do the relationship graphs and similarity recommendations work well?
- Is the UI responsive and pleasant to use?
- Are filtering and sorting options intuitive and useful?

### Code Quality
- Is the code clean, documented, and idiomatic?
- Are dependencies managed properly with `uv`?
- Can the project be set up and run easily?
- Are there tests (even basic ones)?

## Technical Constraints

- **Python backend** managed with `uv` (already initialized)
- **Vite + React frontend** for modern SPA experience
- **litellm** for LLM calls (configuration provided in `.env`)
- **TinyDB** for storage (with custom graph layer on top)
- **Playwright MCP tools** for frontend testing

## Starting Point

The `_base` folder contains:
- Complete task specification in `prompt.md`
- Initialized Python project with `uv` configuration
- Minimal boilerplate code
- `.env.template` for required API keys

Copy `_base` to your test folder and let your agent work from the `prompt.md` specification.
