# Use Case 07: Code Migration Tool (CodeMorph)

**An automated code modernization tool demonstrating AST manipulation, code transformation, and test-driven refactoring.**

## The Challenge

Build a tool that automatically migrates Python 2.7 codebases to Python 3.12, preserving all functionality while modernizing syntax and patterns. The core challenge is implementing AST (Abstract Syntax Tree) transformations without using existing migration tools like 2to3.

The tool must analyze code, apply transformations, verify tests still pass, and generate comprehensive reports—demonstrating code comprehension, transformation logic, and quality assurance.

See [`_base/prompt.md`](_base/prompt.md) for the complete specification.

## What This Tests

### Code Analysis & Comprehension
Building a migration tool requires:
- **AST parsing and traversal**: Deep understanding of Python's syntax tree
- **Pattern recognition**: Identifying Python 2 idioms and anti-patterns
- **Semantic understanding**: Knowing what code *does*, not just what it looks like
- **Dependency analysis**: Understanding transformation ordering
- **Static analysis**: Detecting issues without execution

This tests whether agents can *read and understand* code, not just write it.

### AST Manipulation & Transformation
Implementing transformations tests:
- **AST modification**: Creating, updating, and replacing nodes
- **Code generation**: Converting AST back to source code
- **Formatting preservation**: Maintaining readability where possible
- **Edge case handling**: Dealing with complex or unusual syntax
- **Correctness**: Ensuring transformations preserve behavior

This requires low-level programming skills beyond typical application development.

### Test-Driven Refactoring
The verification requirement tests:
- **Test preservation**: Ensuring migrations don't break functionality
- **Before/after validation**: Running tests in different Python versions
- **Regression detection**: Identifying when migrations fail
- **Rollback capability**: Undoing changes when verification fails
- **Quality assurance mindset**: Using tests as contracts

### Tool & CLI Design
Building a professional CLI tool tests:
- **User experience**: Intuitive commands and flags
- **Dry-run modes**: Preview before applying changes
- **Backup mechanisms**: Safety features for users
- **Progress reporting**: Feedback during long operations
- **Error handling**: Helpful messages when things go wrong

### Documentation & Reporting
The reporting requirement tests:
- **Change documentation**: Explaining what was modified and why
- **Metrics generation**: Quantifying migration scope
- **Multiple formats**: Markdown, JSON, HTML reports
- **Actionable insights**: Highlighting manual review items
- **Communication skills**: Making technical changes understandable

### Language Feature Knowledge
Handling Python 2→3 migration requires knowing:
- **Version differences**: What changed between Python 2.7 and 3.12
- **Breaking changes**: Print, division, exceptions, unicode, iterators
- **Best practices**: Modern Python patterns (f-strings, type hints, pathlib)
- **Stdlib changes**: Module renames and reorganization
- **Compatibility concerns**: What works across versions

### Modular Architecture
The plugin architecture requirement tests:
- **Separation of concerns**: Analyzers, transformers, reporters
- **Extensibility**: Easy to add new transformation rules
- **Reusability**: Components usable independently
- **Testing**: Each rule testable in isolation
- **Maintainability**: Clean, documented code structure

## Why This Use Case?

This task was chosen because it tests **code transformation** rather than creation:

1. **Reading, not just writing** - Must understand existing code deeply
2. **Semantic preservation** - Changes syntax while keeping behavior identical
3. **AST mastery** - Low-level manipulation of code structure
4. **Tool building** - Creating something developers use, not end-users
5. **Quality verification** - Tests must pass before and after

An agent that handles this well demonstrates:

- **Deep language knowledge**: Understanding Python internals
- **Analytical skills**: Recognizing patterns and anti-patterns
- **Precision**: Transformations must be exact and correct
- **Testing culture**: Verification through automated tests
- **Tool craftsmanship**: Building developer-friendly CLIs
- **Metaprogramming**: Code that transforms code

This is fundamentally different from other use cases:
- **vs. Research Scraper**: Code transformation vs. data processing
- **vs. Puzzle Game**: Tool building vs. user-facing app
- **vs. Job Orchestrator**: Static analysis vs. runtime orchestration
- **vs. Collaborative Editor**: AST manipulation vs. text synchronization

## Evaluation Focus

When reviewing implementations, pay attention to:

### Transformation Correctness
- Do all required transformations work correctly?
- Are edge cases handled (nested prints, complex exceptions)?
- Is behavior preserved after migration?
- Do tests pass before and after?
- Are transformations idempotent (safe to run twice)?

### Code Quality
- Is the AST manipulation code clean and understandable?
- Are transformers modular and testable?
- Is the architecture plugin-based and extensible?
- Is error handling comprehensive?
- Are there helpful comments explaining complex logic?

### Test Corpus Quality
- Are the test files representative of real Python 2 code?
- Do they cover all required transformation types?
- Are tests meaningful (not just trivial)?
- Do tests actually verify behavior?
- Can tests run in both Python 2.7 and 3.12?

### Tool Usability
- Is the CLI intuitive and well-documented?
- Does dry-run mode work correctly?
- Are backups created properly?
- Is progress feedback helpful?
- Are error messages actionable?

### Reporting
- Are reports comprehensive and useful?
- Do they document all changes clearly?
- Are metrics accurate?
- Is the format readable?
- Are manual review items highlighted?

### Acceptance Criteria
- Do all 6 ACs pass exactly as specified?
- Can the bash commands run successfully?
- Do tests pass in both Python versions?
- Are backups created correctly?
- Are reports generated properly?

### Testing
- Are there unit tests for each transformation?
- Are integration tests comprehensive?
- Are edge cases tested?
- Is the tool itself well-tested?
- Do tests actually catch regressions?

### Performance
- Can it handle reasonably large codebases?
- Is analysis fast enough?
- Are transformations efficient?
- Does it scale to thousands of lines?

## Technical Constraints

- **Python 3.11+** for the tool itself
- **AST module** for parsing and transformation
- **No 2to3 or similar** - must implement transformations yourself
- **Test corpus** must work in Python 2.7 and 3.12 (after migration)
- **Exact AC compliance** - must pass all bash tests
- **Behavior preservation** - all tests must pass after migration

## Starting Point

The `_base` folder contains:
- Complete task specification in `prompt.md`
- Basic `pyproject.toml` with Python 3.11 requirement and CLI entry point
- `.python-version` for version management
- `.gitignore` for Python artifacts and test outputs
- No implementation code (agent builds from scratch)

The minimal scaffolding allows the agent to design the architecture while providing a standard Python project structure.

Copy `_base` to your test folder and let your agent work from the `prompt.md` specification.
