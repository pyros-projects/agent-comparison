# Contributing to Agent Comparison Suite

Thank you for your interest in contributing! This repository is designed to qualitatively compare coding agents and orchestration paradigms across diverse, realistic use cases.

## Table of Contents

- [Ways to Contribute](#ways-to-contribute)
- [Getting Started](#getting-started)
- [Contributing Agent Runs](#contributing-agent-runs)
- [Contributing New Use Cases](#contributing-new-use-cases)
- [Code Quality Standards](#code-quality-standards)
- [Evaluation Guidelines](#evaluation-guidelines)
- [Pull Request Process](#pull-request-process)
- [Community Guidelines](#community-guidelines)

---

## Ways to Contribute

There are two primary ways to contribute to this project:

1. **Add Agent/Orchestration Runs**: Execute a use case with a specific agent or orchestration paradigm and submit your results
2. **Add New Use Cases**: Design and propose new challenges that test different aspects of agent capabilities

Both types of contributions are valuable and help build a comprehensive comparison framework.

---

## Getting Started

### Prerequisites

- **Git**: Version control
- **Python 3.11+**: For Python-based use cases and tooling
- **Node.js 20+**: For JavaScript/TypeScript use cases
- **uv**: Python package manager (`pip install uv`)
- Familiarity with the agent or orchestration tool you plan to use

### Initial Setup

1. **Fork the repository** on GitHub
2. **Clone your fork locally:**
   ```bash
   git clone https://github.com/YOUR-USERNAME/agent-comparison.git
   cd agent-comparison
   ```
3. **Add upstream remote:**
   ```bash
   git remote add upstream https://github.com/pyros-projects/agent-comparison.git
   ```
4. **Explore existing use cases** to understand the structure and expectations

---

## Contributing Agent Runs

Agent runs demonstrate how a specific coding agent or orchestration paradigm handles a use case. Each run is isolated in its own folder.

### Quick Start with Setup Tool

The fastest way to start a new agent run is using the included setup tool:

```bash
python setup-run.py
```

This interactive CLI will:
- Show available use cases
- Let you choose coding agent vs. orchestration
- Optionally select an orchestration paradigm
- Create a properly structured folder
- Generate a git branch name
- Copy the base files
- Create a feature branch automatically

### Manual Setup

If you prefer manual setup:

1. **Choose a use case** (e.g., `01-research-scraper`)
2. **Copy the base folder:**
   ```bash
   cp -r 01-research-scraper/_base 01-research-scraper/coding_agents/my-agent-name
   ```
   Or for orchestration:
   ```bash
   cp -r 01-research-scraper/_base 01-research-scraper/orchestration/paradigm/agent-name
   ```
3. **Create a feature branch:**
   ```bash
   git checkout -b run/01-research-scraper/my-agent-name
   ```

### Working on Your Run

1. **Read the prompt carefully:**
   - Located at `_base/prompt.md`
   - Contains goal, requirements, constraints, and success criteria
   - Treat this as your specification

2. **Use your chosen agent/tool:**
   - Execute the task using your coding agent or orchestration approach
   - Keep all work **within your run folder**
   - Do not modify `_base/` or other runs

3. **Capture the process:**
   - If your tool supports session logs (like `.data/` folders), commit them
   - Document any manual interventions in `EVALUATION_REPORT_*.md`
   - Take screenshots of final UI/outputs

4. **Test thoroughly:**
   - Ensure all Core Requirements are met
   - Test Stretch Goals if implemented
   - Run any included test suites
   - Verify the application works end-to-end

5. **Complete evaluation:**
   - Copy the appropriate evaluation template:
     ```bash
     cp ../../EVALUATION_REPORT_CODING_AGENT.md ./EVALUATION_REPORT.md
     # or
     cp ../../../EVALUATION_REPORT_ORCHESTRATION.md ./EVALUATION_REPORT.md
     ```
   - Fill out all sections honestly:
     - Human interventions (context provided, guidance given)
     - Functional requirements completion
     - Code quality assessment
     - Overall scoring and observations

### What Makes a Good Agent Run

✅ **Do:**
- Follow the prompt requirements closely
- Document all human interventions transparently
- Include session logs if available (`.data/` folders, chat transcripts)
- Test the implementation thoroughly
- Complete the evaluation report honestly
- Keep dependencies scoped to your run folder
- Add a README if setup/usage is non-obvious

❌ **Don't:**
- Cherry-pick the best of multiple attempts (submit your first complete run)
- Modify the base prompt or requirements
- Touch other agents' runs
- Skip documenting manual interventions
- Inflate scores in evaluation

### Run Folder Structure

Your run folder should look like:

```
01-research-scraper/coding_agents/my-agent/
├── prompt.md                    # Copied from _base
├── pyproject.toml               # Copied from _base
├── EVALUATION_REPORT.md         # Your completed evaluation
├── README.md                    # Optional: setup/usage notes
├── .data/                       # Optional: session logs
│   └── 2024-11-23-session.md
├── src/                         # Your implementation
│   └── researcher/
│       ├── __init__.py
│       ├── main.py
│       └── ...
├── tests/                       # Your tests
└── ...                          # Other implementation files
```

---

## Contributing New Use Cases

New use cases expand the suite's coverage and test different agent capabilities. Great use cases are:

- **Realistic**: Mirrors real-world development tasks
- **Non-trivial**: Requires problem-solving, not just boilerplate
- **Focused**: Tests specific skills (e.g., system design, API integration, algorithm implementation)
- **Completable**: Achievable in 2-6 hours for a competent developer
- **Diverse**: Adds something the existing 14 use cases don't cover

### Before You Start

1. **Review existing use cases** to avoid duplication
2. **Identify the skill gap** your use case will test
3. **Consider implementation complexity** - should be challenging but reasonable
4. **Think about evaluation** - can success be assessed qualitatively?

### Use Case Creation Process

#### 1. Plan Your Use Case

Answer these questions:
- **What skill does this test?** (e.g., async programming, database design, algorithm optimization)
- **What's the end deliverable?** (CLI tool, web app, library, data pipeline)
- **What makes it interesting?** (novel constraints, integration challenges, performance requirements)
- **How will success be evaluated?** (functional criteria, quality expectations)

#### 2. Choose a Number

- Use the next available number (currently 15+)
- Format: `XX-descriptive-name` (e.g., `15-streaming-pipeline`)

#### 3. Create Directory Structure

```bash
mkdir -p XX-use-case-name/_base
mkdir -p XX-use-case-name/coding_agents
mkdir -p XX-use-case-name/orchestration
```

#### 4. Write the Prompt

Copy the template and fill it out:

```bash
cp PROMPT_TEMPLATE.md XX-use-case-name/_base/prompt.md
```

**Follow the 7-section structure:**

##### Section 1: Goal (3-5 lines)
Clear, concise pitch of what's being built.
```markdown
## Goal

Build a real-time WebSocket chat server supporting multiple rooms, user presence,
and message history. The system should handle 100+ concurrent connections and
persist chat history to SQLite.
```

##### Section 2: Context & Constraints
Technical stack, time estimate, hardware assumptions, scope boundaries.
```markdown
## Context & Constraints

**Stack**: Python 3.11+, WebSocket library of choice, SQLite  
**Time Estimate**: 3-4 hours  
**Scope**: Server-side only; assume clients exist  
**Constraints**: Must handle concurrent connections gracefully, store last 100 messages per room
```

##### Section 3: Requirements
Split into Core (must-have) and Stretch (nice-to-have).
```markdown
## Requirements

### Core Requirements
- [ ] WebSocket server accepting connections on configurable port
- [ ] Support for multiple chat rooms (create, join, leave)
- [ ] Real-time message broadcasting within rooms
- [ ] Persist messages to SQLite
- [ ] User presence tracking (online/offline status)

### Stretch Goals
- [ ] Private direct messages between users
- [ ] Typing indicators
- [ ] Message search/filtering
- [ ] Rate limiting per user
```

##### Section 4: Quality Expectations
Architecture, testing, UX, documentation standards.
```markdown
## Quality Expectations

**Architecture**: Clean separation between WebSocket handling, business logic, and persistence  
**Testing**: Unit tests for message handling, integration tests for WebSocket flows  
**Error Handling**: Graceful handling of disconnects, invalid messages, storage failures  
**Documentation**: README with setup, usage examples, architecture overview
```

##### Section 5: Process (if applicable)
Research or design steps for complex use cases.
```markdown
## Process

1. **Research**: Compare WebSocket libraries (websockets, aiohttp, Tornado)
2. **Design**: Sketch message protocol and room management logic
3. **Implement**: Start with basic connection handling, then add rooms and persistence
4. **Test**: Write tests as you go, verify concurrent connection handling
```

##### Section 6: Deliverables
Concrete checklist of what to submit.
```markdown
## Deliverables

- [ ] Working WebSocket server implementation
- [ ] SQLite schema and persistence layer
- [ ] Unit and integration tests (>70% coverage)
- [ ] README with setup and usage instructions
- [ ] Example client script demonstrating connections
```

##### Section 7: Success Criteria
3-5 indicators of a successful implementation.
```markdown
## Success Criteria

1. **Functionality**: Server handles 100+ concurrent connections across multiple rooms
2. **Reliability**: Messages are never lost, even during disconnects
3. **Code Quality**: Clean architecture, well-tested, properly handles edge cases
4. **Usability**: Clear README, easy to run and test locally
```

**Prompt Writing Tips:**
- Be **specific about requirements** but **flexible about implementation**
- Provide **context without prescribing solutions**
- Include **concrete acceptance criteria** where relevant (e.g., "support 100+ connections")
- Balance **clarity with creative freedom** - agents should problem-solve, not follow a recipe
- Keep it **concise** (30-50 lines ideal) - avoid over-prescription
- **Test different skills** than existing use cases

#### 5. Add Minimal Scaffolding

In `_base/`, include only essential boilerplate:

**For Python use cases:**
```toml
# pyproject.toml
[project]
name = "agent_comparison_XX_use_case"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = []

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = ["pytest>=7.0", "ruff>=0.1.0"]
```

**For Node.js use cases:**
```json
{
  "name": "agent-comparison-XX-use-case",
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "test": "vitest",
    "dev": "vite"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "vitest": "^1.0.0"
  }
}
```

**Include:**
- Basic `src/` directory structure (empty or minimal `__init__.py`)
- Config files if stack is predetermined (`.eslintrc`, `tsconfig.json`, etc.)
- `.gitignore` for the language/framework

**Don't include:**
- Implementation code
- Detailed examples or hints
- Step-by-step guides

#### 6. Create the README

Add `XX-use-case-name/README.md` explaining:

```markdown
# XX: Use Case Name

## What This Tests

- **Primary Skills**: [e.g., WebSocket handling, concurrent programming, state management]
- **Secondary Skills**: [e.g., database design, API design, error handling]
- **Complexity**: [Low/Medium/High]

## Why This Is Interesting

[2-3 sentences on what makes this challenging or valuable for comparison]

## Evaluation Criteria

When reviewing implementations, consider:

### Functional Completeness
- Are all Core Requirements met?
- How many Stretch Goals were completed?
- Does the implementation handle edge cases?

### Code Quality
- Is the architecture clean and maintainable?
- Are tests comprehensive and meaningful?
- Is error handling robust?

### Problem-Solving Approach
- How were design decisions made?
- Were appropriate libraries/patterns chosen?
- Is the solution over-engineered or under-engineered?

### Documentation
- Can someone else run and understand the code?
- Are setup instructions clear?
- Is the architecture documented?

## Expected Time Investment

**Typical**: 3-4 hours  
**Experienced developers**: 2-3 hours  
**Includes**: Research, implementation, testing, documentation
```

#### 7. Add Screenshots/Assets (if applicable)

For use cases with visual output:
```bash
mkdir -p docs/assets
# Add screenshots showing expected UI/output
```

Reference them in the README:
```markdown
## Expected Output

![Example Interface](../../docs/assets/XX-screenshot.png)
```

#### 8. Test Your Use Case

Before submitting:

1. **Attempt it yourself** (or have someone else try)
2. **Verify the prompt is clear** - no ambiguities or missing context
3. **Check time estimate** - is it actually achievable in the stated time?
4. **Ensure it's different** - does it test something the other 10 don't?
5. **Validate scaffolding** - is there enough to start but not too much?

#### 9. Update Root README

Add your use case to the list in `/README.md`:

```markdown
| 11 | [WebSocket Chat](11-websocket-chat) | Real-time chat server with rooms, presence, persistence | Python | Medium | 3-4h |
```

#### 10. Create a Pull Request

See [Pull Request Process](#pull-request-process) below.

### What Makes a Great Use Case

✅ **Good Examples:**
- **Database-backed REST API** - tests CRUD, validation, error handling, persistence
- **CLI data processing pipeline** - tests file I/O, streaming, error recovery, performance
- **Real-time collaborative editor** - tests CRDTs, concurrency, conflict resolution
- **Code analysis tool** - tests AST manipulation, pattern matching, refactoring logic

❌ **Avoid:**
- **Too simple**: "Build a TODO list" (too basic, well-worn)
- **Too complex**: "Build a distributed database" (not completable in reasonable time)
- **Too vague**: "Create a useful utility" (no clear success criteria)
- **Too prescriptive**: Step-by-step implementation guide (removes problem-solving)

### Use Case Checklist

Before submitting, verify:

- [ ] Directory structure created (`XX-name/_base/`, `/coding_agents/`, `/orchestration/`)
- [ ] Prompt follows `PROMPT_TEMPLATE.md` structure (7 sections)
- [ ] Prompt is clear, concise (30-50 lines), not overly prescriptive
- [ ] Core Requirements are specific and testable
- [ ] Stretch Goals are genuinely optional enhancements
- [ ] Minimal scaffolding in `_base/` (no implementation code)
- [ ] README explains what skills are tested and why it's interesting
- [ ] Time estimate is realistic (tested by attempting it yourself)
- [ ] Root README updated with use case entry
- [ ] Use case tests skills not heavily covered by existing cases

---

## Code Quality Standards

All contributions (agent runs and use cases) should follow these standards:

### Language-Specific Guidelines

**Python:**
- Python 3.11+ syntax and features
- Type hints for function signatures
- 4-space indentation
- Follow PEP 8 (use `ruff` or `black` for formatting)
- Modules: `snake_case.py`
- Classes: `PascalCase`
- Functions/variables: `snake_case`

**JavaScript/TypeScript:**
- ES modules (`import`/`export`)
- 2-space indentation
- Use `const`/`let`, avoid `var`
- TypeScript: strict mode, explicit types
- Components: `PascalCase`
- Functions/variables: `camelCase`
- Use ESLint/Prettier if configured

**General:**
- Clear, intention-revealing names
- Functions should do one thing
- Keep files focused and reasonably sized
- Comments for "why", not "what"
- No commented-out code in final submission

### Testing Expectations

- **Unit tests** for core logic and utilities
- **Integration tests** for key workflows
- **Coverage**: Aim for >70% on critical paths
- **Test naming**: Descriptive, follows convention (`test_*` for Python, `*.test.ts` for JS)
- **Assertions**: Clear failure messages
- **Mocking**: Use mocks/fakes for external dependencies in tests

### Documentation Standards

Every run should include:

1. **README** (if setup is non-obvious):
   - What was built
   - How to install dependencies
   - How to run the application
   - How to run tests
   - Any configuration needed

2. **Code comments** where logic is complex:
   - Why a particular approach was chosen
   - Gotchas or edge cases
   - TODO items for Stretch Goals (if applicable)

3. **EVALUATION_REPORT.md**:
   - Honest assessment of completion
   - Documentation of interventions
   - Scores and observations

### Architecture Expectations

- **Separation of concerns**: Business logic separate from I/O, UI, persistence
- **Dependency management**: Keep dependencies minimal and scoped to your run
- **Configuration**: Use environment variables or config files, not hardcoded values
- **Error handling**: Graceful failures, meaningful error messages
- **Security**: No committed secrets, tokens, API keys (use `.env.example` instead)

---

## Evaluation Guidelines

### For Agent Runs

Evaluation is qualitative and focuses on:

1. **Functional Completeness**:
   - Core Requirements met?
   - Stretch Goals attempted/completed?
   - Edge cases handled?

2. **Code Quality**:
   - Architecture: Clean separation, appropriate patterns
   - Testing: Coverage and quality of tests
   - Readability: Clear naming, appropriate comments
   - Error Handling: Robust and user-friendly

3. **Human Intervention**:
   - How much context was needed?
   - How much guidance was provided?
   - Were there manual fixes?

4. **Overall Execution**:
   - Time to completion
   - Number of iterations
   - Quality of problem-solving

Use the provided evaluation templates (`EVALUATION_REPORT_CODING_AGENT.md` or `EVALUATION_REPORT_ORCHESTRATION.md`) and fill them out honestly.

### For New Use Cases

Use cases are evaluated on:

1. **Clarity**: Is the prompt clear and unambiguous?
2. **Scope**: Is it completable in the stated time?
3. **Value**: Does it test skills not covered by other use cases?
4. **Quality**: Is the scaffolding appropriate (minimal but sufficient)?
5. **Realism**: Does it reflect real-world development tasks?

---

## Pull Request Process

### Creating Your PR

1. **Ensure your branch is up to date:**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat(use-case-XX): add agent-name run"
   # or
   git commit -m "feat: add use case XX - descriptive name"
   ```

3. **Push to your fork:**
   ```bash
   git push origin your-branch-name
   ```

4. **Open a PR on GitHub** from your fork to `pyros-projects/agent-comparison:main`

### PR Title Format

Follow Conventional Commits:

**For agent runs:**
```
feat(01-research-scraper): add codex-cli run
feat(03-image-gen): add orchestration/agent-swarm/gpt4 run
fix(02-text-gen): correct dependency in gemini-cli run
```

**For new use cases:**
```
feat: add use case 11 - websocket chat server
```

### PR Description Template

```markdown
## Type of Contribution
- [ ] Agent Run (coding agent or orchestration)
- [ ] New Use Case
- [ ] Documentation/Tooling Fix

## Summary
[Brief description of what you're adding]

## Use Case
**Number/Name**: 01 - Research Scraper  
**Agent/Paradigm**: Codex CLI / Agent Swarm + GPT-4

## Checklist

### For Agent Runs:
- [ ] All Core Requirements completed
- [ ] Tests written and passing
- [ ] EVALUATION_REPORT.md completed honestly
- [ ] Session logs included (if available)
- [ ] Changes scoped to my run folder only
- [ ] Dependencies are scoped (not repo-wide)

### For New Use Cases:
- [ ] Prompt follows PROMPT_TEMPLATE.md (7 sections)
- [ ] Prompt is clear and concise (~30-50 lines)
- [ ] Minimal scaffolding only (no implementation)
- [ ] README explains what's tested and why
- [ ] Time estimate is realistic (tested myself)
- [ ] Root README updated
- [ ] Tests a skill gap in existing use cases

## Testing Done
[Commands you ran, what you verified]

Example:
```bash
cd 01-research-scraper/coding_agents/my-agent
uv sync
uv run pytest
uv run python -m researcher.main --query "machine learning"
```

## Screenshots (if applicable)
[Add screenshots for UI-based use cases]

## Notes
[Anything reviewers should know - known limitations, interesting decisions, etc.]
```

### Review Process

1. **Automated checks** will run (if configured)
2. **Manual review** will assess:
   - Code quality and testing
   - Adherence to standards
   - Completeness of evaluation
   - Scope (changes only your run/use case)
3. **Feedback** may request changes
4. **Merge** once approved

### After Your PR is Merged

- Your run/use case is now part of the comparison suite
- Consider trying other use cases with different agents
- Share your experience and insights

---

## Community Guidelines

### Code of Conduct

- **Be respectful**: Constructive feedback only
- **Be honest**: Accurate evaluation and reporting
- **Be collaborative**: Help others when you can
- **Be transparent**: Document interventions and challenges

### Scope Discipline

**Critical for multi-contributor repos:**

- **Work in your own folder** - never modify other runs or `_base/`
- **Scoped dependencies** - install packages in your run, not repo-wide
- **Isolated branches** - one run or use case per branch
- **No cross-contamination** - don't copy/reference other agents' implementations

### Session Logs and Transparency

If your agent/tool generates session logs (e.g., `.data/` folders with conversation transcripts):

- **Do commit them** - valuable for understanding the process
- **Include context** - what prompts you gave, what guidance you provided
- **Document interventions** - if you manually fixed something, note it in EVALUATION_REPORT.md

### Honest Evaluation

This suite is for **qualitative comparison**, not competition. Honest reporting is essential:

- Submit your **first complete run**, not the best of multiple attempts
- Document **all human interventions** (context, prompts, fixes)
- Score **realistically** in evaluations
- Note **what went wrong** as well as what went right

### Getting Help

- **Questions about use cases?** Open an issue labeled `question`
- **Bug in setup tool?** Open an issue labeled `bug`
- **Stuck on implementation?** This is expected - document the challenge in your evaluation
- **Unclear prompt?** Open an issue suggesting clarifications

---

## Examples and References

### Example Agent Run PR
```
Title: feat(01-research-scraper): add cursor-composer run

Description:
Added a coding agent run using Cursor Composer on the Research Scraper use case.

Use Case: 01 - Research Scraper
Agent: Cursor with Composer mode

Checklist:
✓ All Core Requirements completed
✓ 2 of 4 Stretch Goals completed (graph view, filters)
✓ Tests passing (pytest, 75% coverage)
✓ EVALUATION_REPORT.md filled out
✓ Session logs in .data/ folder
✓ Changes scoped to run folder

Testing:
- Ran pytest suite: 12 passed
- Tested end-to-end with real arXiv queries
- Verified all three views render correctly

Notes:
- Agent struggled with graph visualization initially, needed guidance on library choice
- Documented in evaluation report
```

### Example New Use Case PR
```
Title: feat: add use case 11 - rate limiter library

Description:
New use case testing concurrency, algorithm implementation, and API design.

Summary:
Build a generic rate limiting library supporting multiple algorithms (token bucket, 
sliding window, etc.). Tests concurrent programming, algorithm correctness, and 
clean API design.

Checklist:
✓ Prompt follows template (7 sections, 42 lines)
✓ Minimal scaffolding (pyproject.toml only)
✓ README explains testing focus
✓ Time estimate realistic (3-4h, tested myself)
✓ Root README updated
✓ Tests algorithm implementation (not covered by other use cases)

Why This Use Case:
Current suite lacks low-level algorithm challenges and concurrency testing.
Rate limiting is a practical problem requiring correct algorithm implementation,
thread safety, and clean API design.

Testing:
- Attempted implementation myself in 3.5 hours
- Prompt is clear and unambiguous
- Core Requirements are achievable, Stretch Goals are genuinely optional
```

---

## Quick Reference

### Agent Run Workflow
```bash
# 1. Setup
python setup-run.py

# 2. Implement
cd XX-use-case/coding_agents/my-agent
# ... work on implementation ...

# 3. Test
uv run pytest  # or npm test

# 4. Evaluate
cp ../../EVALUATION_REPORT_CODING_AGENT.md ./EVALUATION_REPORT.md
# ... fill out evaluation ...

# 5. Submit
git add .
git commit -m "feat(XX-use-case): add my-agent run"
git push origin run/XX-use-case/my-agent
# ... open PR on GitHub ...
```

### New Use Case Workflow
```bash
# 1. Create structure
mkdir -p XX-use-case-name/{_base,coding_agents,orchestration}

# 2. Write prompt
cp PROMPT_TEMPLATE.md XX-use-case-name/_base/prompt.md
# ... fill out 7 sections ...

# 3. Add scaffolding
# Create minimal pyproject.toml or package.json in _base/

# 4. Document
# Create XX-use-case-name/README.md

# 5. Update root
# Add entry to README.md use case table

# 6. Test
# Attempt the use case yourself to validate

# 7. Submit
git checkout -b feat/use-case-XX-name
git add .
git commit -m "feat: add use case XX - descriptive name"
git push origin feat/use-case-XX-name
# ... open PR on GitHub ...
```

---

## Questions?

- **General questions**: Open an issue with label `question`
- **Prompt clarifications**: Open an issue referencing the use case
- **Tool bugs**: Open an issue with label `bug` and steps to reproduce
- **Use case suggestions**: Open an issue with label `enhancement` describing the idea

Thank you for contributing to the Agent Comparison Suite! Your runs and use cases help build a valuable resource for understanding agent capabilities across diverse real-world challenges.
