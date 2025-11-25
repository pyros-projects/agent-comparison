# Use Case 13: Deep Research Engine (ResearchFlow)

**A deep research application using specialized orchestration libraries to generate comprehensive multi-page research reports through recursive, self-expanding workflows.**

## The Challenge

Build a research system similar to OpenAI's ChatGPT Deep Research that generates comprehensive reports on any topic. The key constraint: you must use one or more lesser-known orchestration libraries (Burr, Towel, Flock, or LMQL) to design intricate, self-recursive workflows that decompose topics into sub-tasks, gather information, and synthesize polished reports matching a target page count.

This tests the ability to learn unfamiliar libraries quickly, master their orchestration paradigms, design complex recursive flows, and build production-quality research automation.

See [`_base/prompt.md`](_base/prompt.md) for the complete specification.

## What This Tests

### Learning Unfamiliar Libraries
The core challenge is mastering specialized tools without prior experience:
- **Documentation comprehension**: Understanding library paradigms from docs alone
- **Example analysis**: Learning from limited examples and code samples
- **Paradigm adoption**: Thinking in the library's mental model (state machines, agents, query language)
- **Idiomatic usage**: Using the library properly, not just wrapping it
- **Debugging**: Troubleshooting issues with unfamiliar APIs and error messages

This tests rapid learning capability—critical for real-world development with evolving tools.

### Recursive Workflow Design
Building self-expanding research flows tests:
- **Task decomposition**: Breaking complex topics into manageable sub-tasks
- **Recursive logic**: Tasks generating their own sub-tasks dynamically
- **Depth control**: Preventing infinite recursion with termination conditions
- **State management**: Tracking workflow progress across recursive levels
- **Dynamic planning**: Adapting research strategy based on findings

This tests advanced orchestration and algorithmic thinking.

### Multi-Agent Orchestration
Coordinating parallel research activities tests:
- **Concurrent execution**: Running independent tasks simultaneously
- **Task dependencies**: Managing sequential vs. parallel operations
- **Resource sharing**: LLM API calls, search quotas, shared state
- **Synchronization**: Collecting results from distributed tasks
- **Failure handling**: Graceful degradation when tasks fail

This tests distributed systems thinking and coordination patterns.

### LLM Integration Patterns
Using LLMs for research automation tests:
- **Structured prompting**: Generating tasks, outlines, sections with consistent format
- **Constraint application**: Using LMQL or similar to enforce output structure
- **Context management**: Providing relevant context without hitting token limits
- **Quality control**: Ensuring factual accuracy and coherence
- **Iterative refinement**: Improving outputs through multi-step processing

### Web Search Integration
Gathering research material tests:
- **Query formulation**: Generating effective search queries from research tasks
- **Result extraction**: Parsing and filtering search engine responses
- **Source diversity**: Querying multiple sources for comprehensive coverage
- **Information synthesis**: Combining findings from disparate sources
- **Relevance filtering**: Identifying high-quality, relevant information

### Content Assembly & Synthesis
Producing polished reports tests:
- **Outline generation**: Creating logical document structure
- **Section writing**: Generating coherent prose for each section
- **Length targeting**: Meeting page count requirements (±10%)
- **Narrative flow**: Ensuring sections connect logically
- **Formatting**: Producing readable Markdown/PDF/HTML output

### Library-Specific Challenges

**Burr (State Machine Orchestration)**
- Designing state transitions for research phases
- Managing workflow state across recursive tasks
- Leveraging graph-based flow visualization

**LMQL (Query Language for LLMs)**
- Writing queries with constraints for structured output
- Using control flow for multi-step generation
- Enforcing format requirements for tasks

**Flock (Multi-Agent Framework)**
- Coordinating multiple research agents
- Distributing tasks across agent pool
- Implementing agent communication patterns

**Towel (Clojure Functional)**
- Functional composition of research pipeline
- Immutable state management
- Clojure-Python interop (if chosen)

## Why This Use Case?

This task was chosen because it tests **learning unfamiliar tools** and **complex workflow orchestration**:

1. **Unknown libraries** - Forces learning from documentation, not prior knowledge
2. **Recursive complexity** - Self-expanding workflows are algorithmically challenging
3. **Real-world utility** - Research automation is genuinely useful
4. **Multiple paradigms** - Each library offers different orchestration approach
5. **Production quality** - Generated reports must be comprehensive and polished

An agent that handles this well demonstrates:

- **Rapid learning**: Mastering new libraries from documentation
- **Paradigm flexibility**: Adapting to different orchestration models
- **Complex orchestration**: Designing intricate, multi-stage workflows
- **LLM engineering**: Effective prompting and structured output
- **Systems thinking**: Coordinating parallel tasks, managing state, handling failures
- **Research methodology**: Understanding how to decompose and explore topics

This is fundamentally different from other use cases:
- **vs. Research Scraper**: Deep research with recursive decomposition vs. simple RAG
- **vs. LLM Roguelike**: Workflow orchestration vs. real-time interaction
- **vs. Code Migration**: Learning unfamiliar tools vs. AST manipulation
- **vs. Novel AI Library**: Using specialized libraries vs. creating libraries

## Evaluation Focus

When reviewing implementations, pay attention to:

### Library Learning & Mastery
- Did the agent genuinely learn the library or just wrap it superficially?
- Is the library used idiomatically (following its paradigm)?
- Is the choice of library justified based on requirements?
- If multiple libraries used, are they integrated thoughtfully?
- Does the code demonstrate understanding of library strengths?

### Workflow Design Quality
- Is the recursive decomposition logic sound?
- Are recursion depth limits properly implemented?
- Is the workflow elegant or convoluted?
- Does task decomposition make sense for research?
- Are parallel tasks identified and executed concurrently?

### Research Process Quality
- Does the system explore topics thoroughly?
- Are research sub-tasks meaningful and well-structured?
- Is information gathered from diverse sources?
- Are synthesis steps producing coherent summaries?
- Does the process adapt based on findings?

### Generated Report Quality
- Are reports comprehensive and well-structured?
- Does content match the target page count (±10%)?
- Is the writing coherent with good narrative flow?
- Are findings factually grounded (not hallucinated)?
- Is formatting clean and readable?

### Code Quality
- Clean separation between orchestration, LLM calls, search, synthesis?
- Type hints and docstrings throughout?
- Complex workflow logic well-commented?
- Proper error handling for API failures?
- Modular design for different task types?

### Testing
- Are individual research tasks tested?
- Is recursion depth limiting tested?
- Are workflow state transitions tested?
- Is content assembly tested?
- Are edge cases handled (API failures, no search results)?

### Documentation
- Is library choice explained and justified?
- Is workflow architecture clearly documented?
- Are usage instructions complete?
- Is complex orchestration logic explained?
- Are limitations acknowledged?

### Workflow Observability
- Can you see the research task tree?
- Is progress tracked and displayed?
- Are intermediate outputs logged?
- Can workflow state be inspected?
- Is debugging straightforward?

## Technical Constraints

- **Stack/Language**: Python 3.11+ (required for library compatibility)
- **Required Libraries**: Must use at least ONE of Burr, Towel, Flock, LMQL, Langroid, PocketFlow, or LiteSwarm
- **LLM Integration**: Any provider allowed (OpenAI, Anthropic, local)
- **Web Search**: Required for research material (Tavily, SerpAPI, Bing, etc.)
- **Recursive Workflow**: Must demonstrate self-decomposing task structure
- **Target Output**: Reports matching specified page count (DIN A4, ~500 words/page)
- **Format**: Markdown, PDF, or HTML output

## Starting Point

The `_base` folder contains:
- Complete task specification in `prompt.md`
- Basic `pyproject.toml` with Python 3.11 requirement and comments about library options
- `.gitignore` for artifacts and generated reports
- No implementation code (agent builds from scratch)
- No library pre-installed (agent must research and choose)

This minimal scaffolding ensures the agent starts with library research and workflow design rather than following a template.

Copy `_base` to your test folder and let your agent work from the `prompt.md` specification.

## Available Libraries

The agent must research and choose from these specialized orchestration libraries:

- [Burr](https://github.com/apache/burr/)
- [Towel](https://github.com/tolitius/towel)
- [Flock](https://github.com/whiteducksoftware/flock)
- [LMQL](https://github.com/eth-sri/lmql)
- [Langroid](https://github.com/langroid/langroid)
- [PocketFlow](https://github.com/The-Pocket/PocketFlow)
- [LiteSwarm](https://github.com/GlyphyAI/liteswarm)
- [KSI](https://github.com/durapensa/ksi)
- [Nexus](https://github.com/PrimisAI/nexus)
- [GraphAgent](https://github.com/Ji-Cather/GraphAgent)
- [Tool-Star](https://github.com/RUC-NLPIR/Tool-Star)
- [Python-Weaver](https://github.com/adv-11/python-weaver)
- [AgentNexus](https://github.com/MuhammadYossry/AgentNexus)
- [1LCB Agent](https://github.com/1LCB/agent)
- [Dynamiq](https://github.com/dynamiq-ai/dynamiq)
- [Orchestra](https://github.com/mainframecomputer/orchestra)
- [LLM-Use Agentic](https://github.com/llm-use/llm-use-agentic)
- [LLM-Use](https://github.com/llm-use/llm-use)
- [LLM Orchestrator](https://github.com/Azzarnuji/llm_orchestrator)
- [NextGen AI](https://github.com/gopeshkhandelwal/nextgen-ai)
- [Snowflake Orchestration Framework](https://github.com/Snowflake-Labs/orchestration-framework)
- [AgentScope Runtime](https://github.com/agentscope-ai/agentscope-runtime)

**Part of the challenge**: Understanding what each library does, how it works, and which is best suited for recursive research workflows. No descriptions or hints provided—agent must research documentation and examples independently.

## Example Research Flow

```
Topic: "The impact of AI on healthcare"
Target: 5 pages (~2500 words)

1. [Decomposition Task]
   → Sub-topics: Diagnostics, Treatment, Drug Discovery, Administration, Ethics

2. [Parallel Research Tasks]
   → Diagnostics: [Search] → [Synthesize]
   → Treatment: [Search] → [Synthesize]
   → Drug Discovery: [Search] → [Synthesize]
     → (Recursive): Specific drug discovery methods
   → Administration: [Search] → [Synthesize]
   → Ethics: [Search] → [Synthesize]

3. [Outline Generation]
   → Introduction, 5 main sections, conclusion

4. [Section Writing]
   → Write each section with synthesized findings

5. [Assembly & Formatting]
   → Combine sections, ensure flow, format output
```

## Success Signals

**Minimal Success:**
- Uses at least one required library
- Generates research reports on topics
- Basic recursive task decomposition works
- Output is readable

**Good Success:**
- Demonstrates genuine library understanding
- Recursive workflow with depth control works reliably
- Reports are comprehensive and well-structured
- Page count targets are met
- Code is clean with tests

**Excellent Success:**
- Library used idiomatically with clear mastery
- Elegant recursive workflow design
- Parallel task execution implemented
- Generated reports are high-quality and thorough
- Workflow is observable and debuggable
- Multiple libraries combined effectively
- Documentation clearly explains architecture
- Demonstrates advanced orchestration patterns
