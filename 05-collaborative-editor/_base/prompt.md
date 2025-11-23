# Use Case 05 – Collaborative Text Editor (Quill)

## 1. Goal
Implement a minimal realtime collaborative text editor with a custom CRDT implementation, WebSocket synchronization, and persistence. Tests distributed systems knowledge and CRDT algorithm implementation.

## 2. Context & Constraints
- **Stack**: Node.js 20+, custom CRDT (no yjs/automerge libraries)
- **Server**: Listen on `127.0.0.1:8083`
- **Storage**: SQLite or file-based persistence
- **Out of scope**: Rich text formatting, user authentication, advanced UI
- **Time estimate**: High complexity (CRDT algorithm is challenging)

## 3. Requirements

### 3.1 Core (Must Have)
- **Server** with REST API and WebSocket
  - `GET /doc` - Returns current document text
  - `POST /doc/apply` - Applies operations to document
  - WebSocket endpoint for realtime collaboration
- **Custom CRDT** - Operation-based sequence CRDT
  - Support insert and delete operations
  - Lamport timestamps or vector clocks for causality tracking
  - Deterministic conflict resolution
  - Idempotent operations (safe to reapply)
- **Persistence**
  - Snapshot on startup
  - Operation log for replay
  - Compaction mechanism to prevent unbounded log growth
- **Simple web client** - Basic HTML/JS interface for editing

### 3.2 Stretch (Nice to Have)
- Multiple document support
- User cursors/presence indicators
- Undo/redo functionality
- Syntax highlighting

## 4. Quality Expectations
- **Architecture**: Clean separation between CRDT core, networking, and persistence
- **Testing**: Unit tests for CRDT operations; convergence tests; persistence tests
- **UX/UI**: Minimal but functional interface; smooth realtime updates
- **Documentation**: CRDT algorithm explanation; setup and verification steps

## 5. Acceptance Criteria

**AC1:** Server starts successfully on `127.0.0.1:8083`

**AC2:** HTTP operations work correctly
```bash
# Empty document initially
curl -s http://127.0.0.1:8083/doc | jq -r .text | wc -c | grep -Fx 0

# Apply operations via REST
curl -s -X POST http://127.0.0.1:8083/doc/apply \
  -H 'Content-Type: application/json' \
  -d '{"client":"A","ops":[{"type":"insert","pos":0,"text":"he"}],"ts":"1"}'

# Verify final text after multiple operations
curl -s http://127.0.0.1:8083/doc | jq -r .text | grep -Fx 'hello world'
```

**AC3:** Persistence - Document state survives server restart

**AC4:** Compaction - Endpoint to compact log without changing document content

## 6. Deliverables
- [ ] Working server with REST + WebSocket
- [ ] Custom CRDT implementation (no external CRDT libraries)
- [ ] Simple web client for editing
- [ ] Persistence with compaction
- [ ] Tests for CRDT logic and convergence
- [ ] README with setup and AC verification steps

## 7. Success Criteria
- CRDT correctly handles concurrent edits and converges
- All acceptance criteria pass
- Document state persists across restarts
- Compaction works without corrupting state
- Code is clean and well-tested
