# Use Case 08: Git-Based Wiki (WikiGit)

**A content management system using Git as storage, demonstrating creative architecture, version control integration, and collaborative editing workflows.**

## The Challenge

Build a wiki system that uses Git as its database backend. Every page is a markdown file, every edit is a commit, and all Git features (branches, history, diffs, merges) are exposed through a user-friendly web interface.

The challenge tests unconventional architecture patterns, deep Git API integration, diff visualization, and collaborative editing workflows—all while maintaining the simplicity expected of a wiki.

See [`_base/prompt.md`](_base/prompt.md) for the complete specification.

## What This Tests

### Creative Architecture & Storage Patterns
Using Git as a database is unconventional and tests:
- **Thinking outside the box**: Not defaulting to traditional databases
- **Understanding Git internals**: Commits, trees, blobs, refs
- **Leveraging existing tools**: Git already solves versioning, why rebuild it?
- **Trade-off analysis**: When is Git-as-DB appropriate vs. inappropriate?
- **Architectural creativity**: Novel solutions to common problems

This tests whether agents can think beyond standard CRUD patterns.

### Git API Integration & Mastery
Deep Git integration requires:
- **libgit2 bindings**: Using pygit2 or nodegit effectively
- **Git object model**: Understanding trees, blobs, commits, refs
- **Programmatic operations**: Creating commits, branches, merges via API
- **Concurrent access**: Handling multiple processes/users safely
- **Performance**: Efficient Git operations for web apps

This goes far beyond basic `git add/commit/push` commands.

### Diff Visualization & Comparison
Visual diff features test:
- **Diff algorithms**: Understanding how diffs are computed
- **Presentation**: Making diffs readable and useful
- **Multiple formats**: Side-by-side, unified, word-level
- **Syntax highlighting**: In diffs and rendered code blocks
- **UI/UX design**: Clear presentation of changes

### Version Control UX Design
Exposing Git features to non-technical users tests:
- **Abstraction**: Making Git concepts accessible
- **Branching UX**: Draft/publish workflows
- **Conflict resolution**: Helping users merge changes
- **History navigation**: Intuitive access to old versions
- **Restore operations**: Undoing changes safely

Can the agent make Git's power usable without Git's complexity?

### Collaborative Editing Workflows
Multiple users editing concurrently tests:
- **Conflict detection**: Knowing when edits collide
- **Three-way merge**: Resolving conflicts programmatically
- **Merge UI**: Visual interface for conflict resolution
- **Optimistic concurrency**: Edit detection without locking
- **User communication**: Clear messaging about conflicts

### Full-Text Search Implementation
Search across Git repositories tests:
- **Indexing strategies**: Building search indices
- **Performance**: Fast search despite version history
- **Relevance ranking**: Ordering results meaningfully
- **Index maintenance**: Keeping index in sync with commits
- **Search scope**: Current version vs. all history

### Markdown Processing & Rendering
Wiki functionality requires:
- **CommonMark compliance**: Standard markdown rendering
- **Extensions**: Tables, footnotes, task lists
- **Wiki links**: `[[Page Name]]` style linking
- **Front matter**: YAML metadata parsing
- **Syntax highlighting**: Code blocks in multiple languages
- **Security**: XSS prevention in user content

### Web Application Development
Building the interface tests:
- **Backend framework**: Flask, FastAPI, or Express
- **RESTful API design**: Clean endpoints for operations
- **Frontend**: Markdown editor, preview, navigation
- **Real-time preview**: Live markdown rendering
- **Responsive design**: Works on mobile and desktop

## Why This Use Case?

This task was chosen because it tests **creative problem-solving** and **unconventional architectures**:

1. **Git as database** - Novel use of existing technology
2. **Version control UX** - Making complex features accessible
3. **Collaborative editing** - Conflict resolution without OT/CRDT
4. **Full-stack** - Backend Git integration + frontend wiki UI
5. **Production concerns** - Concurrent access, performance, search

An agent that handles this well demonstrates:

- **Architectural creativity**: Thinking beyond standard patterns
- **Git expertise**: Deep understanding of version control
- **UX design**: Making technical features user-friendly
- **Full-stack skills**: Backend integration + frontend polish
- **Problem-solving**: Handling concurrency, conflicts, search

This is fundamentally different from other use cases:
- **vs. Collaborative Editor**: Git merging vs. CRDT synchronization
- **vs. Research Scraper**: Novel storage vs. traditional database
- **vs. Job Orchestrator**: Content management vs. task orchestration
- **vs. Code Migration**: Version control integration vs. code transformation

## Evaluation Focus

When reviewing implementations, pay attention to:

### Git Integration Quality
- Are Git operations correct and safe?
- Is the repository structure clean?
- Are commits meaningful with good messages?
- Does branching/merging work correctly?
- Can you inspect the Git repo directly (it's valid)?

### UI/UX Design
- Is the wiki interface intuitive?
- Can non-technical users use it easily?
- Is the markdown editor pleasant to use?
- Are diffs clearly visualized?
- Is navigation logical?

### Version Control Features
- Does history browsing work well?
- Can you view any old version?
- Is diff comparison useful?
- Does branching make sense for drafts?
- Is conflict resolution understandable?

### Search Quality
- Is search fast and accurate?
- Are results ranked well?
- Does it scale to many pages?
- Is the search UI clear?
- Are snippets with highlights helpful?

### Collaborative Editing
- Does it detect concurrent edits?
- Is the conflict UI usable?
- Can users merge changes successfully?
- Are conflicts explained clearly?
- Does the merge preserve both sides' work?

### Code Quality
- Is the Git integration code clean?
- Is error handling robust?
- Is the architecture modular?
- Are operations safe (no data loss)?
- Is concurrent access handled?

### Performance
- Are page loads fast?
- Is search responsive?
- Does history load efficiently?
- Are diffs generated quickly?
- Can it handle hundreds of pages?

### Acceptance Criteria
- Do all 7 ACs pass exactly as specified?
- Can the curl commands run successfully?
- Does the Git repo have correct structure?
- Do branches and merges work?
- Is search functional?

## Technical Constraints

- **Python 3.11+** or **Node.js 20+** for backend
- **pygit2** (Python) or **nodegit** (Node.js) for Git integration
- **Markdown renderer**: CommonMark compliant
- **Web framework**: Flask, FastAPI, or Express
- **Search**: Whoosh, elasticsearch, or similar
- **Exact AC compliance**: Must pass all curl tests
- **Valid Git repo**: All operations create valid Git history

## Starting Point

The `_base` folder contains:
- Complete task specification in `prompt.md`
- Basic `pyproject.toml` with Python 3.11 requirement and CLI entry point
- `.python-version` for version management
- `.gitignore` for Python artifacts and test repos
- No implementation code (agent builds from scratch)

The minimal scaffolding gives the agent freedom to design the architecture and choose the best Git integration approach.

Copy `_base` to your test folder and let your agent work from the `prompt.md` specification.
