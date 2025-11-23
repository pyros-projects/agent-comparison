# Use Case 06: Job Orchestrator (Orpheus)

**An event-driven job orchestration system demonstrating distributed architecture, async processing, retry logic, and real-time monitoring.**

## The Challenge

Build a complete job orchestration platform from scratch with separate API and worker services. The system must handle job submission, queuing, execution with retry logic, persistence, and provide a real-time monitoring dashboard.

The challenge tests microservice architecture patterns, event-driven design, WebSocket real-time updates, and production-ready error handling—all without external queue services (Redis, RabbitMQ), using only SQLite for coordination.

See [`_base/prompt.md`](_base/prompt.md) for the complete specification.

## What This Tests

### Distributed System Architecture
Building separate API and worker services tests:
- Microservice design patterns
- Service separation and boundaries
- Inter-process communication via database
- Coordination without a message broker
- Graceful startup and shutdown of multiple services

### Event-Driven Design
The polling-based worker and WebSocket updates test:
- Event-driven architecture patterns
- Asynchronous job processing
- Real-time event broadcasting
- Decoupling producers (API) from consumers (worker)
- State transition management

### Queue & Job Management
Implementing a job queue on SQLite tests:
- Queue semantics (FIFO, priorities)
- Job state machines (pending → in_progress → done/failed)
- Atomic state transitions to prevent race conditions
- Idempotency (preventing duplicate job execution)
- Job registry and type dispatching

### Retry Logic & Error Handling
The retry requirement tests:
- Exponential backoff implementation
- Retry counting and max attempts
- Transient vs. permanent failure handling
- Error logging and diagnostics
- Graceful degradation

### WebSocket Real-Time Communication
Live dashboard updates test:
- WebSocket server implementation in FastAPI
- Broadcasting events to multiple clients
- Client-side WebSocket handling
- Real-time UI updates without polling
- Connection management (connect, disconnect, reconnect)

### Database-Backed Coordination
Using SQLite as the coordination layer tests:
- Schema design for job metadata
- Transaction handling for consistency
- Row-level locking for concurrency control
- Query optimization for polling
- Migration and initialization strategies

### FastAPI & Python Backend
Building the API service tests:
- FastAPI framework proficiency
- REST API design and implementation
- Template rendering (Jinja2)
- Static file serving
- CORS and middleware configuration

### Frontend Integration
The dashboard tests:
- HTML/CSS/JavaScript for monitoring UI
- WebSocket client implementation
- Real-time data visualization
- Responsive table design
- User experience for operations monitoring

### Production Patterns
The production-ready requirement tests:
- Process management (running multiple services)
- Configuration management
- Logging and observability
- Health checks and monitoring
- Deployment readiness

## Why This Use Case?

This task was chosen because it tests **system design and architecture** rather than algorithm implementation:

1. **Microservice patterns** - Separate API and worker processes
2. **Event-driven coordination** - Without external message brokers
3. **Real-time updates** - WebSocket integration
4. **Production concerns** - Retry, error handling, health checks
5. **Full-stack** - Backend API + worker + frontend dashboard

An agent that handles this well demonstrates:

- **Architectural thinking**: Designing systems with multiple components
- **Distributed systems**: Coordination, consistency, failure handling
- **Production mindset**: Retry logic, health checks, logging
- **Full-stack skills**: API + worker + real-time frontend
- **Practical engineering**: Solving real problems without over-engineering

This is fundamentally different from other use cases:
- **vs. Research Scraper**: Event-driven backend vs. RAG frontend
- **vs. Collaborative Editor**: Job queue vs. CRDT synchronization
- **vs. Puzzle Game**: System architecture vs. creative game design
- **vs. Image Generation**: Distributed services vs. ML training

## Evaluation Focus

When reviewing implementations, pay attention to:

### Architecture & Separation
- Are API and worker cleanly separated?
- Can they run independently?
- Is the interface between them well-defined?
- Is the code organized logically (api/, worker/, shared/)?
- Could you add a second worker easily?

### Job Queue Implementation
- Is the queue mechanism sound (no double execution)?
- Are state transitions atomic?
- Is polling efficient?
- Can it handle concurrent workers (bonus)?
- Is the job registry extensible?

### Retry Logic
- Does exponential backoff work correctly?
- Are retries counted properly?
- Is max_retries enforced?
- Are transient errors retried but permanent ones not?
- Is retry state persisted?

### WebSocket Real-Time Updates
- Do updates appear instantly on the dashboard?
- Are all connected clients notified?
- Does the connection handle disconnects gracefully?
- Is the update format clear and useful?
- Does it scale to many jobs?

### Acceptance Criteria
- Do all 7 ACs pass exactly as specified?
- Can you run the curl commands successfully?
- Do jobs complete within 30 seconds?
- Are results correct (sum=5000050000, count=5)?
- Does the dashboard update live?

### Code Quality
- Is the code clean and well-structured?
- Are concerns properly separated?
- Is error handling comprehensive?
- Are database operations safe (transactions)?
- Is the code documented?

### Testing
- Are there unit tests for jobs?
- Are API endpoints tested?
- Is retry logic tested?
- Are edge cases covered?
- Is there a test harness for ACs?

### Dashboard & UX
- Is the dashboard clear and useful?
- Do updates appear smoothly?
- Is job information complete?
- Is the UI responsive?
- Can you easily see job status at a glance?

### Production Readiness
- Can services be started easily?
- Is configuration externalized?
- Are logs helpful for debugging?
- Do health checks work?
- Could this run in production?

## Technical Constraints

- **Python 3.11+** for both API and worker
- **FastAPI** for the API service
- **SQLite** for persistence and coordination
- **WebSocket** for real-time dashboard updates
- **Separate processes** for API and worker
- **Exact AC compliance** (must pass all curl tests)
- **No external services** (no Redis, RabbitMQ, etc.)

## Starting Point

The `_base` folder contains:
- Complete task specification in `prompt.md`
- Basic `pyproject.toml` with Python 3.11 requirement
- `.python-version` for Python version management
- `.gitignore` for common Python artifacts
- No implementation code (agent builds from scratch)

This provides minimal scaffolding while requiring the agent to design and implement all services, database schema, job logic, and real-time dashboard.

Copy `_base` to your test folder and let your agent work from the `prompt.md` specification.
