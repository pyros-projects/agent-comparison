# Use Case 10: Novel AI Library Conceptualization & Implementation (Library Lab)

**Research the AI library landscape, identify gaps, conceptualize a novel library, and build a fully functional MVP.**

## The Challenge

Research the current AI/LLM Python library ecosystem, identify gaps and opportunities, conceptualize a novel library that would make developers excited, and implement a 100% functional MVP of the best idea. This is a two-phase challenge testing research capability, creative ideation, gap analysis, and rapid prototyping.

The task requires comprehensive web research, landscape analysis, creative brainstorming, rigorous self-evaluation, and implementation of a working proof-of-concept with clean API design and compelling documentation.

See [`_base/prompt.md`](_base/prompt.md) for the complete specification.

## What This Tests

### Research & Information Gathering
The landscape analysis requirement tests:
- **Web research capability**: Can the agent conduct genuine research across GitHub, PyPI, Reddit, HN, blogs?
- **Information synthesis**: Can it organize findings into coherent categories?
- **Pattern recognition**: Can it identify trends, common patterns, and emerging approaches?
- **Source quality**: Does it find current, relevant information from credible sources?
- **Breadth vs. depth**: Does it balance surveying the landscape with deep dives?

This tests whether agents can gather and synthesize real-world information, not just generate ideas from training data.

### Gap Analysis & Critical Thinking
The opportunity identification requirement tests:
- **Problem identification**: Can it recognize what's missing or broken?
- **Developer empathy**: Does it understand developer pain points and needs?
- **Market awareness**: Can it identify underserved use cases?
- **Technical insight**: Does it recognize technical gaps vs. just missing features?
- **Opportunity sizing**: Can it distinguish significant gaps from minor improvements?

This tests analytical thinking and understanding of developer ecosystems.

### Creative Ideation
The concept generation requirement tests:
- **Originality**: Can it generate genuinely novel ideas, not just variations of existing libraries?
- **Creativity**: Does it think beyond obvious solutions?
- **Vision**: Can it imagine what would delight developers?
- **Feasibility awareness**: Does it balance creativity with buildability?
- **Diversity**: Can it explore different directions and approaches?

This tests creative thinking—a rare capability to evaluate in coding agents.

### Self-Evaluation & Prioritization
The rating and selection requirement tests:
- **Rigor**: Does it evaluate ideas honestly and consistently?
- **Criteria application**: Can it apply multiple criteria systematically?
- **Judgment**: Does it select ideas with good potential?
- **Justification**: Can it articulate why one idea is better than others?
- **Trade-off understanding**: Does it balance novelty, feasibility, and delight?

This tests critical self-assessment and decision-making.

### API Design & Developer Experience
The implementation requirement tests:
- **Pythonic design**: Is the API intuitive and idiomatic?
- **Elegance**: Is the interface beautiful and delightful?
- **Consistency**: Are patterns used uniformly?
- **Type hints**: Are types used effectively for IDE support?
- **Error handling**: Are error messages helpful and clear?

This tests understanding of what makes APIs pleasant to use.

### Rapid Prototyping
Building a functional MVP tests:
- **Scope management**: Can it focus on core features vs. getting lost in details?
- **Implementation speed**: Can it build quickly while maintaining quality?
- **Priority identification**: Does it implement what matters most?
- **MVP thinking**: Does it understand "prove the concept" vs. "production-ready"?

### Documentation & Communication
The documentation requirement tests:
- **Compelling writing**: Does the README make you want to try it?
- **Clarity**: Are installation and usage instructions clear?
- **Examples**: Do they showcase the library's value effectively?
- **Technical writing**: Can it explain complex concepts simply?

### Full-Stack Library Development
Bringing it all together tests:
- **Package structure**: Proper Python package layout
- **Testing**: Meaningful tests that verify functionality
- **Dependencies**: Minimal, justified dependency choices
- **Installation**: Proper packaging with `pyproject.toml`
- **Code quality**: Clean, maintainable implementation

## Why This Use Case?

This task was chosen because it tests **the full ideation-to-implementation cycle** and **creative thinking**:

1. **Research capability** - Must gather real information, not just speculate
2. **Creative problem-solving** - Inventing new solutions, not implementing specs
3. **Self-direction** - No prescribed task; agent defines the goal
4. **Developer empathy** - Must understand what makes developers excited
5. **Rapid execution** - Proving concepts quickly with high quality

An agent that handles this well demonstrates:

- **Information gathering**: Conducting meaningful research beyond training data
- **Creative vision**: Imagining novel approaches and delightful experiences
- **Critical analysis**: Evaluating ideas rigorously and selecting winners
- **Execution excellence**: Building functional, well-designed MVPs quickly
- **API taste**: Understanding what makes libraries pleasant to use
- **Communication**: Writing documentation that excites and instructs

This is fundamentally different from other use cases:
- **vs. Research Scraper**: Creating new tools vs. building specified apps
- **vs. Collaborative Editor**: Inventing abstractions vs. implementing algorithms
- **vs. Code Migration**: Creative ideation vs. deterministic transformation
- **vs. LLM Roguelike**: Full research cycle vs. architecture-then-build

## Evaluation Focus

When reviewing implementations, pay attention to:

### Research Quality (Phase 1)
- Is the landscape analysis comprehensive (20-30+ libraries surveyed)?
- Are findings based on real, current information (GitHub, PyPI, discussions)?
- Does the analysis show understanding of the ecosystem?
- Are gaps identified legitimate and significant?
- Are underserved use cases clearly articulated?
- Are sources cited or referenced appropriately?

### Ideation Quality (Phase 1)
- Are the library concepts genuinely novel?
- Would developers actually be excited to use them?
- Do ideas explore diverse directions?
- Are concepts well-developed (not just vague ideas)?
- Do the ideas address identified gaps?
- Is there a "wow factor" to any of the concepts?

### Evaluation Rigor (Phase 1)
- Is the rating methodology thoughtful and consistent?
- Are criteria applied fairly across all ideas?
- Is the selection well-justified?
- Does the chosen idea have good potential?
- Are trade-offs explicitly considered?

### Functionality (Phase 2)
- Does the MVP actually work when you run it?
- Is core functionality fully implemented (not stubbed)?
- Do the examples run successfully?
- Does it prove the concept convincingly?
- Are there any critical bugs?

### API Design (Phase 2)
- Is the API intuitive and easy to understand?
- Does it feel pythonic and natural?
- Would developers enjoy using this?
- Are patterns consistent?
- Are type hints used effectively?
- Is error handling helpful?

### Code Quality (Phase 2)
- Is the code well-structured and modular?
- Is it readable and maintainable?
- Are concerns properly separated?
- Are there appropriate comments and docstrings?
- Does it follow Python best practices?

### Documentation (Phase 2)
- Does the README make you want to try the library?
- Are installation instructions clear and complete?
- Do examples showcase the library's value?
- Is the "wow factor" communicated effectively?
- Can someone actually use this by reading the docs?

### Testing (Phase 2)
- Are there meaningful tests (not just coverage theater)?
- Do tests verify core functionality?
- Are edge cases considered?
- Do all tests pass?

### Packaging (Phase 2)
- Can it be installed with `pip install -e .`?
- Are dependencies clearly specified?
- Is the package structure proper?
- Is the Python version requirement specified?

## Technical Constraints

- **Python 3.10+** required for the library implementation
- **Web research required** - must research real libraries, not just speculate
- **Two-phase structure**: Research/ideation first, then implementation
- **Deliverables**: `RESEARCH.md` with findings and ideas, working MVP with tests and docs
- **Focus**: Creative/fun use cases preferred over business applications
- **5-7 library concepts** required with detailed descriptions
- **100% functional MVP** - no placeholders or TODOs in core functionality
- **Minimal dependencies** - only what's truly needed

## Starting Point

The `_base` folder contains:
- Complete task specification in `prompt.md`
- Basic `pyproject.toml` template
- `.gitignore` for Python artifacts
- No implementation code (agent builds from scratch)
- No predetermined library concept (agent researches and decides)

This minimal scaffolding ensures the agent starts with research and creative thinking rather than following a predetermined path.

Copy `_base` to your test folder and let your agent work from the `prompt.md` specification.
