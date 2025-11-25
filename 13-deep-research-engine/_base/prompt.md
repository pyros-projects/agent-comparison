# Use Case 13 – Deep Research Engine (ResearchFlow)

## 1. Goal

Build a deep research application similar to OpenAI's ChatGPT Deep Research that generates comprehensive, multi-page research reports on any topic. The system must use one or more specialized but lesser-known orchestration libraries to create self-recursive workflows that generate sub-research tasks, collect information, synthesize findings, and produce polished reports matching a target page count. This tests the ability to learn unfamiliar libraries, design intricate recursive flows, and orchestrate complex multi-agent research processes.

## 2. Context & Constraints

- **Stack/Language**: Python 3.11+ (required for library compatibility)
- **Required Libraries**: Must use at least ONE of:
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
- **LLM Integration**: Any provider (OpenAI, Anthropic, local models)
- **Web Search**: Required for gathering research material (Tavily, Bing, SerpAPI, or similar)
- **Time estimate**: 6-8 hours (2-3h learning libraries, 4-5h implementation)
- **Out of scope**: Real-time collaboration, GUI editor, multi-user support, citation management systems

## 3. Requirements

### 3.1 Core (Must Have)

**Research Input Interface**
- Accept research topic as user input (e.g., "The impact of AI on healthcare")
- Accept target page count (DIN A4 pages, assume ~500 words per page)
- Optional: Specify depth/detail level or research focus areas

**Library Learning & Selection**
- **Research phase**: Evaluate at least 2-3 of the available libraries
- Understand their orchestration paradigms, strengths, and limitations
- **Document choice**: Explain in README why you chose specific library/libraries
- Demonstrate understanding through implemented workflows

**Recursive Research Workflow**
- **Topic decomposition**: Break main topic into research sub-tasks
- **Self-recursion**: Sub-tasks can generate their own sub-tasks if needed
- **Depth management**: Control recursion depth to prevent infinite expansion
- **Parallel execution**: Execute independent research tasks concurrently
- **Progress tracking**: Monitor workflow state and completion

**Research Task Types** (implement at least 3)
- **Web search tasks**: Query search engines, extract relevant information
- **Synthesis tasks**: Combine multiple sources into coherent summaries
- **Outline generation**: Create structured report outlines
- **Section writing**: Generate polished prose for report sections
- **Fact verification**: Cross-check claims across sources (stretch)

**Content Assembly**
- Collect research findings from all tasks
- Generate structured outline (sections, subsections)
- Write sections to meet target length
- Ensure coherent narrative flow
- Format as readable document (Markdown, PDF, or HTML)

**Output & Artifacts**
- Final research report matching target page count (±10%)
- Workflow visualization showing research task tree
- Metadata: Sources consulted, sub-tasks generated, execution time

### 3.2 Stretch (Nice to Have)

- Use multiple libraries in combination (e.g., LMQL for queries + Burr for orchestration)
- Citation tracking and bibliography generation
- Iterative refinement: User can request deeper exploration of specific sections
- Quality scoring: Assess research depth and identify weak areas
- Export to multiple formats (Markdown, LaTeX, DOCX)
- Interactive workflow: Ask user for guidance at decision points
- Caching: Store search results and synthesis to avoid redundant work
- Resume capability: Continue interrupted research sessions

## 4. Quality Expectations

- **Library Mastery**: Demonstrate understanding of chosen library's patterns and idioms. Don't just wrap it—use it properly.
- **Workflow Design**: Research flow should be elegant, not hacky. Leverage library strengths, not fight them.
- **Code Quality**: Clean separation between orchestration logic, LLM calls, and research tasks. Type hints, docstrings.
- **Testing**: Tests for individual research tasks, workflow state management, recursion depth limiting.
- **Documentation**: README explaining library choice, workflow architecture, usage instructions. Comments in complex workflow code.
- **Output Quality**: Generated reports should be coherent, comprehensive, well-structured, and accurate (factually grounded).

## 5. Process

**Phase 1: Library Research (Mandatory - 2-3 hours)**

1. **Explore Each Library**
   - Read documentation and examples for at least 2-3 libraries
   - Understand orchestration paradigm (state machines, agents, query language, etc.)
   - Run example code to verify understanding
   - Note strengths, weaknesses, and use cases

2. **Evaluate for This Task**
   - Which library best supports recursive workflows?
   - Which handles parallel task execution well?
   - Which has clearest state management?
   - Which integrates easily with LLM APIs?
   - Can multiple libraries be combined effectively?

3. **Document Decision**
   - In README, explain which library/libraries you chose
   - Justify based on research workflow requirements
   - Acknowledge limitations and workarounds

**Phase 2: Workflow Design (1-2 hours)**

1. **Design Research Flow**
   - Sketch out main workflow states/stages
   - Define recursive sub-task generation logic
   - Plan depth limiting and termination conditions
   - Design task types (search, synthesize, write, etc.)

2. **Plan Content Assembly**
   - How to aggregate findings from multiple tasks?
   - How to structure outline generation?
   - How to ensure target page count is met?

**Phase 3: Implementation (3-4 hours)**

- Implement workflow using chosen library
- Integrate LLM API for task generation and synthesis
- Add web search integration
- Build content assembly and formatting
- Test with multiple topics and page counts

## 6. Deliverables

- [ ] **Working research application** - CLI or simple UI for topic input and report generation
- [ ] **Recursive workflow** - Demonstrates self-decomposing research tasks
- [ ] **Library integration** - Proper use of at least one specialized orchestration library
- [ ] **Generated reports** - 2-3 example reports on different topics showing quality
- [ ] **Workflow visualization** - Diagram or log showing task decomposition tree
- [ ] **README** - Library evaluation, choice justification, architecture explanation, usage guide
- [ ] **Test suite** - Tests for workflow logic, task types, recursion limiting

## 7. Success Criteria

- **Library Learning**: Agent demonstrates genuine understanding of chosen library's paradigm and uses it idiomatically (not just as a thin wrapper).
- **Recursive Workflow**: Research tasks successfully decompose into sub-tasks. Recursion is controlled and terminates appropriately.
- **Report Quality**: Generated reports are comprehensive, coherent, well-structured, and approximately match target page count.
- **Research Depth**: System explores topics thoroughly with multiple angles and sources, not just superficial summaries.
- **Parallel Execution**: Independent research tasks run concurrently, not sequentially (if library supports).
- **Code Quality**: Workflow code is clean, modular, well-documented, and demonstrates library mastery.

---

## Notes

This is an **advanced challenge** testing:
- Learning unfamiliar libraries quickly
- Designing recursive, self-expanding workflows
- Multi-agent orchestration patterns
- Complex LLM integration
- Research methodology automation

The focus is on **library mastery** and **intricate flow design**, not just getting something working.
