# Use Case 06 – Job Orchestrator (Orpheus)

## 1. Goal
Build an event-driven job orchestration system with separate API and worker services, retry logic, persistence, and a real-time monitoring dashboard. Tests distributed systems concepts without external queue services.

## 2. Context & Constraints
- **Stack/Language**: Python (FastAPI), use `uv` for package management
- **Architecture**: Separate API and worker processes
- **Storage**: SQLite (no external queue services)
- **Out of scope**: Multi-node deployment, complex job types, authentication
- **Time estimate**: Half to full day

## 3. Requirements

### 3.1 Core (Must Have)
- **API Service**: Submit jobs, query status, serve dashboard
- **Worker Service**: Separate process executing jobs from queue
- **Job types**: At least `sum_range(n)` and `wordcount(text)`
- **Retry logic**: Max retries (default 3), exponential backoff
- **Persistence**: SQLite for jobs, attempts, logs
- **Web dashboard**: Real-time updates via WebSocket
- **API endpoints**: POST /jobs, GET /jobs, GET /jobs/{id}, GET /, /ws

### 3.2 Stretch (Nice to Have)
- Job cancellation
- Scheduled/delayed jobs
- Job dependencies/chaining
- Metrics and monitoring

## 4. Quality Expectations
- **Architecture**: Clean separation between API and worker, proper state management
- **Testing**: Test job execution, retry logic, state transitions
- **UX/UI**: Clear dashboard showing job status and progress
- **Documentation**: README with setup and architecture explanation

## 6. Deliverables
- [ ] FastAPI server with REST + WebSocket
- [ ] Separate worker process
- [ ] SQLite persistence
- [ ] Web dashboard with live updates
- [ ] At least 2 job types
- [ ] Retry logic with exponential backoff
- [ ] Tests for core functionality
- [ ] README with setup instructions

## 7. Success Criteria
- Jobs execute successfully with proper state tracking
- Retry logic works correctly on failures
- Dashboard shows real-time job status
- Clean separation between API and worker
- System handles concurrent jobs properly
