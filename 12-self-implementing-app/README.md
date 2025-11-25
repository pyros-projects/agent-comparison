# Use Case 12: Self-Implementing App (MetaMorph)

**A meta-application that transforms itself on-the-fly based on user descriptions, demonstrating code generation, runtime transformation, and creative meta-programming.**

## The Challenge

Build an application that starts as a simple text box where users describe any software idea (e.g., "project management software", "recipe organizer", "habit tracker"). The app then uses LLM interaction to generate and execute code that transforms itself into the described application—complete with UI, business logic, and data persistence.

This is a **two-phase challenge**: first, research the viability and approach (producing `REPORT.md`), then implement the meta-app based on findings. The task requires understanding code generation techniques, safe code execution, dynamic persistence, security sandboxing, and the fundamental limits of self-modifying applications.

See [`_base/prompt.md`](_base/prompt.md) for the complete specification.

## What This Tests

### Meta-Programming & Code Generation
Building a self-transforming app tests:
- **Code generation strategies**: Template-based, AST manipulation, string concatenation, LLM-structured output
- **Dynamic UI generation**: Creating components, forms, layouts from descriptions
- **Business logic synthesis**: Translating requirements into executable code
- **Runtime code execution**: Safely running generated code in the browser or server
- **Component composition**: Assembling complex UIs from primitives

This tests deep understanding of code as data and meta-programming concepts.

### Security & Sandboxing
Executing user-generated code requires:
- **Sandbox design**: Isolating generated code from the host application
- **Attack prevention**: Blocking arbitrary code execution, XSS, code injection
- **Permission models**: Restricting what generated code can access
- **Execution environments**: iframes, WebAssembly, containers, restricted interpreters
- **Validation**: Ensuring generated code is safe before execution

This tests security awareness and understanding of runtime isolation techniques.

### Dynamic Persistence & Schema Management
Supporting unknown data models tests:
- **Schema-less storage**: Persisting data when structure is unknown until runtime
- **Dynamic schemas**: Creating tables/collections on-the-fly
- **Migration handling**: Adapting storage when app is refined or changed
- **Persistence strategies**: Document databases, JSON blobs, schemaless SQLite
- **Data retrieval**: Querying dynamically structured data

This tests database design flexibility and storage architecture.

### Research & Feasibility Analysis
The mandatory research phase tests:
- **Technology investigation**: Exploring multiple approaches and understanding tradeoffs
- **Constraint identification**: Recognizing what's possible vs. impossible
- **Security analysis**: Understanding threat models and mitigation strategies
- **Architecture design**: Planning system structure before implementation
- **Documentation**: Communicating findings clearly in REPORT.md

This tests research capability and analytical thinking before coding.

### LLM Integration for Code Generation
Using LLMs to generate executable code tests:
- **Prompt engineering**: Crafting prompts that produce structured, valid code
- **Output parsing**: Extracting code from LLM responses reliably
- **Error handling**: Dealing with invalid or unsafe generated code
- **Iterative refinement**: Supporting follow-up requests ("add tags", "make it dark mode")
- **Context management**: Providing LLM with current app state for modifications

This tests practical LLM engineering for structured output.

### Creative System Design
The open-ended nature tests:
- **Novel architecture**: There's no standard pattern for self-modifying apps
- **Constraint navigation**: Balancing flexibility with safety and simplicity
- **Scope management**: Defining what types of apps are feasible
- **User experience**: Making transformation feel magical but controllable
- **Failure handling**: Gracefully handling vague or impossible requests

This tests creative problem-solving and architectural vision.

### Full-Stack Complexity
Bringing it all together tests:
- **Frontend & backend integration**: If using server-side generation
- **State management**: Tracking current app state, transformation history
- **UI/UX design**: Clear feedback during transformation, error states
- **Testing**: Validating code generation, sandboxing, persistence
- **Documentation**: Explaining complex architecture clearly

## Why This Use Case?

This task was chosen because it tests **meta-programming and runtime transformation** unlike any other use case:

1. **Self-modifying code** - The ultimate meta-programming challenge
2. **Security critical** - Must sandbox generated code safely
3. **Research required** - Can't skip to implementation without feasibility analysis
4. **Creative architecture** - No established patterns to follow
5. **LLM code generation** - Testing structured code output, not just text

An agent that handles this well demonstrates:

- **Research capability**: Investigating approaches and understanding constraints before coding
- **Security mindset**: Recognizing and mitigating code execution risks
- **Meta-programming mastery**: Code generation, runtime execution, dynamic systems
- **Architectural creativity**: Designing novel systems without established patterns
- **LLM engineering**: Prompt design for reliable code generation
- **Full-stack proficiency**: Frontend, backend, persistence, and integration

This is fundamentally different from other use cases:
- **vs. Code Migration**: Generating new code vs. transforming existing code
- **vs. LLM Roguelike**: Code generation vs. content generation
- **vs. Novel AI Library**: Building meta-tools vs. building libraries
- **vs. Video Curator**: Dynamic code vs. static media processing

## Evaluation Focus

When reviewing implementations, pay attention to:

### Research Quality (Phase 1)
- Is the viability analysis thorough and realistic?
- Are multiple code generation approaches explored?
- Is the security model clearly understood and documented?
- Are persistence strategies evaluated with pros/cons?
- Does REPORT.md clearly define scope and limitations?
- Are risks identified with mitigation strategies?

### Transformation Capability (Phase 2)
- Can the app successfully transform based on user descriptions?
- Do generated apps have functional UI and logic?
- Can it handle at least 3 different app types (todo, notes, expenses)?
- Are transformations reliable or fragile?
- How well does it handle vague or complex requests?

### Security Implementation
- Is generated code properly sandboxed?
- Are arbitrary code execution attacks prevented?
- Is the security model documented and sound?
- Are permission boundaries clear and enforced?
- Can you break out of the sandbox? (Test this!)

### Persistence & Data Management
- Does data survive page refresh or restart?
- Can different app types persist different data structures?
- Is the storage approach flexible enough for unknown schemas?
- Are there migration issues when apps are refined?

### Code Quality
- Is the transformation engine modular and well-structured?
- Is code generation logic testable and tested?
- Is the architecture clearly documented?
- Are error cases handled gracefully?
- Is LLM integration robust (handles failures, invalid output)?

### User Experience
- Is the transformation process clear and engaging?
- Are loading/progress states communicated well?
- Do errors provide helpful feedback?
- Can users understand what happened when transformation fails?
- Does it feel "magical" or clunky?

### Scope & Feasibility
- Are the claimed capabilities actually achievable?
- Does the implementation match the REPORT's scope?
- Are limitations clearly communicated to users?
- Is the "reset" functionality working?

## Technical Constraints

- **Research Phase**: Mandatory - must produce REPORT.md before implementation
- **Stack**: Open choice - justify based on code generation and sandboxing capabilities
- **LLM Integration**: Required for generating app code
- **Security**: Generated code must execute in a sandbox
- **Persistence**: Generated apps must store data persistently
- **Multiple Apps**: Must successfully generate at least 3 different app types
- **Deliverables**: REPORT.md with research findings + working meta-app implementation

## Starting Point

The `_base` folder contains:
- Complete task specification in `prompt.md`
- Basic `package.json` for Node.js projects (if choosing JS/TS)
- Basic `pyproject.toml` for Python projects (if choosing Python)
- `.gitignore` for artifacts and generated code
- No implementation code (agent builds from scratch)
- No prescribed approach (agent researches and decides)

This minimal scaffolding ensures the agent starts with research and architectural thinking rather than jumping to implementation.

Copy `_base` to your test folder and let your agent work from the `prompt.md` specification.

## Key Challenges

### Code Generation
How do you reliably generate valid, functional code from natural language descriptions? Template-based generation is safer but less flexible. LLM-direct generation is flexible but harder to validate.

### Safe Execution
How do you run user-generated code without security risks? Browser iframes provide isolation but have limitations. Server-side containers are secure but complex. Interpreted approaches (JSON UI definitions) are safest but least powerful.

### Dynamic Schemas
How do you store data when you don't know the schema until runtime? Document databases handle this naturally. Relational databases require creative solutions. File-based storage (JSON) is simple but doesn't scale.

### Scope Definition
What types of apps are actually possible? Simple CRUD apps work well. Real-time collaborative apps are harder. Games might be feasible. ML training pipelines are impossible. Where's the line?

### User Expectations
How do you manage what users expect vs. what's achievable? Clear communication about limitations is critical. Good error messages when requests are too complex.

## Success Signals

**Minimal Success:**
- REPORT.md exists and covers key research areas
- App transforms from text box to at least one generated app type
- Basic persistence works
- Security approach is documented

**Good Success:**
- Comprehensive REPORT.md with multiple approaches evaluated
- Successfully generates 3+ different app types
- Persistence works across different schemas
- Generated code is sandboxed with documented security model
- Code quality is high with tests

**Excellent Success:**
- Thorough research with deep analysis of tradeoffs
- Reliable transformation for wide variety of app descriptions
- Iterative refinement works (user can modify generated apps)
- Security model is robust and well-tested
- Architecture is elegant and extensible
- Documentation makes complex system understandable
- Demonstrates truly novel meta-programming approach
