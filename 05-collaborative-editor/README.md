# Use Case 05: Collaborative Editor (Quill)

**A realtime collaborative text editor with custom CRDT implementation, demonstrating distributed systems knowledge and low-level algorithm design.**

## The Challenge

Implement a minimal but production-ready collaborative text editor from scratch. The core requirement is building a custom CRDT (Conflict-free Replicated Data Type) that handles concurrent edits from multiple clients without conflicts.

The system must support realtime collaboration via WebSocket, persist state to disk, implement log compaction, and pass strict acceptance criteria tests via both REST API and WebSocket interfaces.

See [`_base/prompt.md`](_base/prompt.md) for the complete specification.

## What This Tests

### Distributed Systems & CRDT Knowledge
Implementing a custom CRDT tests deep understanding of:
- Conflict-free replicated data types and their guarantees
- Eventual consistency models
- Causal ordering (Lamport clocks or vector clocks)
- Operation-based vs. state-based CRDTs
- Idempotency and commutativity
- Convergence proofs (informal but sound reasoning)

This is **not** about using libraries—agents must implement the CRDT logic themselves, showing genuine algorithmic understanding.

### Concurrent Systems Design
Building a realtime collaborative system requires:
- Handling concurrent operations from multiple clients
- Ensuring operations can be applied in any order and converge
- Managing local vs. remote state
- Dealing with network delays and message reordering
- Implementing deterministic conflict resolution

### WebSocket & Realtime Architecture
The realtime aspect tests:
- WebSocket server implementation
- Broadcasting updates to all connected clients
- Managing client connections and disconnections
- Efficient message serialization
- Handling client-side and server-side state synchronization

### Persistence & State Management
The persistence requirement tests:
- Designing a durable operation log
- Implementing snapshot mechanisms
- Log compaction to prevent unbounded growth
- Recovery and replay from persisted state
- SQLite or file-based storage patterns

### REST API Design
The dual HTTP/WebSocket interface tests:
- Clean API design for headless testing
- Proper HTTP semantics (GET for reads, POST for writes)
- JSON request/response handling
- Separation of concerns (API vs. business logic)

### Test-Driven Development
The strict acceptance criteria test:
- Ability to write testable, verifiable software
- Understanding of test contracts and specifications
- Automated testing practices
- Headless testing via curl/HTTP
- Manual testing via WebSocket clients

### Low-Level Algorithm Implementation
Unlike high-level frameworks, this requires:
- Implementing data structures from scratch (operation sequences)
- Position tracking in mutable text
- Efficient insert/delete operations
- Reasoning about algorithmic correctness
- Performance considerations for text operations

### Node.js Backend Development
Building the server tests:
- Node.js proficiency (async I/O, events)
- npm ecosystem navigation (choosing appropriate libraries)
- Server architecture (Express or similar)
- File I/O and database operations
- Process management and startup

## Why This Use Case?

This task was chosen because it tests **fundamental computer science knowledge** rather than framework usage:

1. **True algorithmic work** - Must implement CRDT from scratch, not use libraries
2. **Distributed systems** - Requires understanding of consistency models
3. **Precise specifications** - Acceptance criteria are exact and testable
4. **Low-level thinking** - No high-level abstractions to hide behind
5. **Production concerns** - Persistence, compaction, restart recovery

An agent that handles this well demonstrates:

- **Deep CS fundamentals**: CRDTs, distributed systems, algorithms
- **Systems programming**: Concurrent operations, state management
- **Precision**: Meeting exact specifications with testable outputs
- **Backend proficiency**: Node.js, WebSocket, persistence
- **Problem decomposition**: Breaking complex system into manageable parts

This is fundamentally different from other use cases:
- **vs. Research Scraper**: Low-level algorithms instead of high-level orchestration
- **vs. Puzzle Game**: Precise specs instead of creative freedom
- **vs. Image Generation**: Distributed systems instead of ML
- **vs. Text Playground**: Production backend instead of educational frontend

## Evaluation Focus

When reviewing implementations, pay attention to:

### CRDT Correctness
- Does it actually converge under concurrent operations?
- Are operations correctly ordered using clocks?
- Is the implementation idempotent (safe to reapply ops)?
- Are edge cases handled (e.g., deleting already-deleted text)?
- Is the algorithm explained and justified?

### Acceptance Criteria
- Does it pass all five ACs exactly as specified?
- Can the curl commands be run successfully?
- Does WebSocket broadcast work correctly?
- Does persistence survive restarts?
- Does compaction preserve document state?

### Code Quality
- Is the CRDT implementation clean and understandable?
- Is the server code well-structured?
- Are concerns properly separated (CRDT, persistence, API, WebSocket)?
- Is error handling robust?
- Are there appropriate comments explaining the algorithm?

### Testing
- Are there unit tests for CRDT operations?
- Are convergence properties tested?
- Are there integration tests for the API?
- Is there a test harness for running ACs?
- Are edge cases covered?

### Performance
- Is text insertion/deletion efficient?
- Does compaction run in reasonable time?
- Can it handle documents of reasonable size?
- Are there any obvious performance bottlenecks?

### Documentation
- Is the CRDT algorithm explained clearly?
- Are setup steps precise and complete?
- Can someone run all ACs by following the README?
- Are design decisions documented?
- Is the clock/ordering mechanism explained?

### Production Readiness
- Would this work reliably in production?
- Is state properly persisted?
- Are errors handled gracefully?
- Can the server recover from crashes?
- Is the code maintainable?

## Technical Constraints

- **Node.js 20+** for server implementation
- **WebSocket** for realtime communication
- **SQLite or file-based** persistence
- **Custom CRDT** (no yjs, automerge, or similar)
- **REST API** at specified endpoints
- **Exact AC compliance** (must pass curl tests)
- **npm packages allowed** for utilities (not CRDT core)

## Starting Point

The `_base` folder contains:
- Complete task specification in `prompt.md`
- Basic `package.json` with Node 20 engine requirement
- `.gitignore` for node_modules and database files
- No implementation code (agent builds from scratch)

This gives a clean starting point while requiring the agent to implement all core logic, including the CRDT algorithm.

Copy `_base` to your test folder and let your agent work from the `prompt.md` specification.
