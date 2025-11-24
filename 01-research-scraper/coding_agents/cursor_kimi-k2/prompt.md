# Use Case 01 – Research Paper Catalog (PaperTrail)

## 1. Goal
Build a research paper catalog with continuous autonomous ingestion, GraphRAG-based search, and multiple specialized views. The system should help researchers discover, analyze, and explore AI/ML papers through intelligent search, relationship mapping, and theory validation with real-time progress feedback during paper ingestion.

## 2. Context & Constraints
- **Stack/Language**: Python 3.11+ backend (FastAPI + litellm + sentence-transformers + tinydb + networkx), modern frontend (your choice - React/Vue/Svelte)
- **Managed by uv** - Use only uv commands like 'uv run' and 'uv add'
- **LLM Configuration**: litellm reads environment variables automatically. Only `DEFAULT_MODEL` and `DEFAULT_EMBEDDING_MODEL` need to get passed for LLM and embedding model config.
- **Fallback Strategy**:
  - **Embeddings**: If litellm embedding unavailable → automatically fall back to sentence-transformers default models (embeddings ALWAYS work)
  - **LLM**: If LLM unavailable → use placeholders (e.g., summary becomes `<summary>`), backfill when LLM becomes available
  - **Theory Mode**: Disabled when LLM unavailable (show clear message to user)
- **Data source**: arXiv papers (via API and links)
- **Out of scope**: GitHub repository scraping, non-research content, authentication/multi-user
- **Time estimate**: Full day project
- **⚠️ CRITICAL**: Manual testing with Playwright MCP is **MANDATORY** - you must actually run and test the application
- **⚠️ CRITICAL**: Extensive logging in both UI and terminal is **REQUIRED** for debugging and monitoring

Provided tools+data:
- .env with working credentials for LLM and embedding model communication and values
- **Playwright MCP for manual UI testing (REQUIRED - not optional)**

## 3. Requirements

### 3.1 Core (Must Have)

#### Paper Ingestion
- **Manual ingestion**: Accept arXiv links, fetch metadata and PDF content, generate embeddings
- **Continuous import**: Start multiple parallel arXiv import tasks that run continuously (24/7 while app is active)
  - Configurable check interval (every N seconds)
  - Filter options: arXiv category, semantic abstract matching, text search
  - Newest papers first
  - Skip already-known papers
  - Each task runs independently and can be started/stopped

#### Views
The application has **four distinct views**:

1. **Paper List View**: 
   - Filterable/sortable table of all papers
   - Columns: Title, Authors, Date, arXiv Category, Status (new/read/starred)
   - Quick actions: Star, Mark as read, Open detail view
   - Search bar with live filtering
   - Pagination

2. **Paper Detail View**:
   - Full metadata (title, authors, abstract, arXiv ID, publication date, categories)
   - AI-generated summary (key contributions, methodology, results, answered questions, possible further research possibilities)
   - Full text extraction/display
   - Similar papers section (vector similarity-based)
   - Relationship graph showing connected papers (citations, topic overlap, author connections)
   - Tags/keywords (auto-extracted and manual)
   - Notes section (user annotations)
   - Export options (BibTeX, PDF link, plain text summary)
   - Navigation to related papers

3. **Theory Mode View**:
   - Input field for hypothesis/theory statement
   - Search button to trigger analysis
   - Results split into two columns:
     - **Pro Arguments**: Papers supporting the theory with extensive natural language summaries
     - **Contra Arguments**: Papers contradicting the theory with extensive natural language summaries
   - Each result shows: paper title, relevance score, argument summary, key quotes
   - Export debate summary

4. **Dashboard View**: 
   - Total papers count, storage size
   - Papers by category (bar/pie chart)
   - Topic clusters visualization
   - Recent activity timeline
   - Continuous import task status (running tasks, papers imported today/week)
   - Collection growth over time

#### Search Modes
- **Cataloging mode**: Ingest papers and build knowledge base
- **Search mode**: Vector similarity search across papers (semantic query → ranked results)
- **Theory mode**: RAG-based argument discovery - analyze papers to find evidence for/against a given hypothesis

#### Technical Features
- **Real-time feedback**: WebSocket updates during paper processing and continuous imports
- **GraphRAG**: Build knowledge graph showing paper relationships (shared authors, citations, topic similarity)
- **Embeddings**: Generate and store embeddings for efficient semantic search
- **Resilience & Fallbacks**:
  - **Embedding fallback**: Auto-switch from litellm to sentence-transformers if embedding model unavailable
  - **LLM graceful degradation**: Store papers with placeholder fields (`<summary>`, `<keywords>`, etc.) when LLM unavailable
  - **Background backfill**: When LLM becomes available, automatically fill in missing summaries/analysis for papers with placeholders
  - **Theory mode gating**: Disable theory mode UI when LLM unavailable, show clear status message
  - **Error recovery**: Continuous import tasks should retry failed operations with exponential backoff
- **⚠️ Manual Testing**: Use Playwright MCP to test all views, interactions, and data flows - this is a CORE REQUIREMENT, not optional
- **⚠️ Extensive Logging**: 
  - **Backend/Terminal**: Structured logging for all operations (API calls, paper ingestion, embedding generation, search queries, errors, performance metrics, fallback activations)
  - **Frontend/UI**: Console logs for state changes, API calls, WebSocket events, user actions, errors, and service availability status
  - **Purpose**: Enable easy debugging, performance monitoring, and issue diagnosis during development and testing

### 3.2 Stretch (Nice to Have)
- Automatic paper recommendations based on collection analysis
- Citation network visualization (interactive graph)
- Batch import from arXiv search query results
- Email/webhook notifications when continuous import finds matching papers
- Advanced filters (date range, minimum citation count, specific authors)
- Full-text PDF search (beyond abstract/metadata)

## 4. Quality Expectations
- **Architecture**: Clean separation between ingestion, storage, retrieval, and presentation layers
- **Testing**: Test core retrieval and embedding logic
- **UX/UI**: Polished interface with clear navigation between views, responsive design
- **Documentation**: README with setup, usage examples for each mode

## 5. Process
- Configure litellm via environment variables (`DEFAULT_MODEL`, `DEFAULT_EMBEDDING_MODEL` - see .envtemplate)
- **Implement fallback mechanisms**: sentence-transformers for embeddings, placeholder system for LLM fields
- Design tinydb schema for papers (with placeholder support), embeddings, graph relationships, continuous import tasks, and backfill queue
- Choose networkx graph structure for paper relationships
- Plan LLM usage: paper summarization, relationship extraction, theory argument analysis
- **Implement comprehensive logging strategy** - structured logs in backend (Python logging), console logs in frontend, log levels (DEBUG/INFO/WARN/ERROR)
- Design the four views (Paper List, Detail, Theory Mode, Dashboard) with clear navigation
- Implement continuous import system with configurable filters and intervals
- Implement GraphRAG layer for relationship discovery
- Build Theory Mode with pro/contra argument extraction (with LLM availability check)
- **Implement background backfill worker** - automatically fills placeholders when LLM becomes available
- **⚠️ MANDATORY: MANUAL TESTING WITH PLAYWRIGHT MCP** - Actually run the app, test every view, verify data flows, test continuous imports, validate theory mode results, TEST FALLBACK SCENARIOS (disable LLM/embeddings and verify graceful degradation). Browser-based testing is NOT OPTIONAL.

## 6. Deliverables
- [ ] Working web application with backend API and frontend
- [ ] Paper ingestion system (manual and continuous) with real-time progress
- [ ] All four views implemented (List, Detail, Theory Mode, Dashboard)
- [ ] Continuous import system with configurable filters (category, semantic, text search)
- [ ] Theory mode with pro/contra argument extraction (with LLM availability gating)
- [ ] Search modes functional (cataloging, search, theory)
- [ ] GraphRAG-based relationship mapping in detail view
- [ ] **Fallback systems implemented**:
  - [ ] sentence-transformers fallback for embeddings
  - [ ] Placeholder system for LLM-generated fields when LLM unavailable
  - [ ] Background backfill worker to fill placeholders when LLM becomes available
  - [ ] Theory mode disabled with clear UI message when LLM unavailable
- [ ] **Extensive logging** - terminal logs for backend operations, browser console logs for frontend state/actions, fallback activations logged
- [ ] README with setup and usage guide
- [ ] Tests for core functionality (ingestion, search, embeddings, fallback scenarios)
- [ ] **⚠️ MANDATORY: Complete manual testing session using Playwright MCP** - documented evidence of testing all features including fallback scenarios

## 7. Success Criteria
- Can ingest papers from arXiv links with real-time feedback
- Can start/stop multiple continuous import tasks with different filters
- Continuous imports check periodically and skip known papers
- Search returns relevant results based on semantic similarity (works even when litellm embeddings unavailable via sentence-transformers fallback)
- Theory mode extracts and summarizes supporting and contradicting evidence (when LLM available)
- Theory mode shows clear disabled state with explanation when LLM unavailable
- Papers can be ingested even when LLM is unavailable (with placeholders like `<summary>`)
- Background worker automatically fills in placeholders when LLM becomes available
- Four views provide different valuable perspectives on the collection
- Paper detail view shows comprehensive metadata, summary (or placeholder), similar papers, and relationship graph
- Knowledge graph reveals meaningful paper relationships (authors, topics, citations)
- **Comprehensive logging in place** - terminal shows clear backend operation logs, browser console shows frontend state changes and API interactions, fallback activations clearly logged
- **⚠️ All features have been manually tested using Playwright MCP with browser automation** - no feature ships without real-world testing, including fallback scenarios (test with LLM disabled, test with embeddings disabled)
