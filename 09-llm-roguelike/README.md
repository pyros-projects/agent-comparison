# Use Case 09: ASCII Roguelike with LLM NPCs (Dungeon Dreams)

**An ASCII roguelike game with LLM-powered NPCs demonstrating architecture decision-making, creative LLM integration, and emergent gameplay.**

## The Challenge

Design and implement an ASCII roguelike game where NPCs are powered by LLMs, creating dynamic narratives and emergent interactions. Unlike other use cases with prescribed stacks, this begins with research and architectural decisions—agents must evaluate options, justify choices, and build a proof-of-concept showcasing LLM-driven characters.

The task requires procedural generation, turn-based gameplay, natural language NPC dialogue, creative demonstration of what makes LLM-powered game characters special, and a design document justifying all major architectural decisions.

See [`_base/prompt.md`](_base/prompt.md) for the complete specification.

## What This Tests

### Architecture & Technology Decision-Making
This use case uniquely requires agents to make foundational choices before coding:
- **Language selection**: Python, Rust, Go, JavaScript/TypeScript? Justify based on LLM integration, performance, libraries
- **Game framework**: libtcod, BearLibTerminal, Textual, custom engine? Evaluate tradeoffs
- **LLM provider**: OpenAI, Anthropic, local models? Consider cost, latency, quality
- **Agent framework**: LangChain, AutoGen, CrewAI, custom? Analyze overhead vs. benefits
- **Interface design**: How does game state communicate with LLMs? How do responses translate to actions?

This tests research capability, systems thinking, and architectural justification—not just coding.

### LLM Integration Patterns
Integrating LLMs into real-time gameplay requires:
- **Context management**: Efficiently providing NPCs with relevant game state without hitting token limits
- **Latency handling**: Graceful UX during 1-5 second response times
- **Guardrails**: Preventing hallucinations from breaking gameplay (NPCs claiming impossible actions)
- **Memory systems**: NPCs remembering previous interactions within sessions
- **Async patterns**: Non-blocking LLM calls in game loops
- **Error handling**: API failures, rate limits, timeout recovery

This tests practical LLM engineering beyond simple prompt-response patterns.

### Game Design & Procedural Generation
Building a playable roguelike tests:
- **Procedural generation**: Random dungeons with rooms, corridors, interesting layouts
- **Game loop architecture**: Turn-based or real-time input handling
- **Player mechanics**: Movement, stats, inventory, interaction systems
- **Visual presentation**: Clear ASCII/terminal rendering despite text constraints
- **Save/load systems**: Persistence across sessions (optional but valuable)

### Creative System Integration
The "demonstrate potential" requirement tests:
- **Novel gameplay patterns**: What can LLM NPCs do that scripted NPCs can't?
- **Emergent narratives**: Can player actions create unexpected but coherent stories?
- **Interaction design**: Bargaining, party formation, quest generation, dynamic storytelling?
- **Polish**: Loading indicators, helpful UI, tutorial hints, coherent experience

This tests creativity and vision, not just technical execution.

### Documentation & Communication
The design document requirement tests:
- **Decision justification**: Clear pros/cons analysis for architectural choices
- **Technical writing**: Can another developer understand the design?
- **Setup documentation**: Complete, accurate installation and usage instructions
- **Design clarity**: Is the game ↔ LLM interface well-explained?

## Why This Use Case?

This task was chosen because it tests **creative LLM integration** and **architecture thinking** rather than following prescribed patterns:

1. **Open-ended architecture** - No prescribed stack; agent must research and justify choices
2. **Creative AI application** - LLMs for gameplay, not just chatbots or assistants
3. **Real-time constraints** - Must handle latency gracefully in interactive experience
4. **Emergent complexity** - NPCs should enable unexpected but valid gameplay moments
5. **Vision demonstration** - Not just "does it work" but "is this exciting?"

An agent that handles this well demonstrates:

- **Research capability**: Investigating multiple options and understanding tradeoffs
- **Creative thinking**: Imagining novel applications of LLM capabilities
- **Systems integration**: Combining game engines, LLMs, and user interaction smoothly
- **UX sensitivity**: Making latency-heavy interactions feel responsive
- **Vision execution**: Building something that makes you excited about possibilities

This is fundamentally different from other use cases:
- **vs. Research Scraper**: Creative gameplay vs. data processing
- **vs. Collaborative Editor**: Emergent narratives vs. deterministic algorithms
- **vs. Job Orchestrator**: Real-time interaction vs. background processing
- **vs. Code Migration**: Building new experiences vs. transforming existing code

## Evaluation Focus

When reviewing implementations, pay attention to:

### Architecture & Decision-Making
- Did the agent research multiple options for language, framework, LLM integration?
- Are architectural choices justified with clear pros/cons analysis?
- Is the `DESIGN.md` comprehensive and well-reasoned?
- Does the chosen stack make sense for the constraints (latency, cost, complexity)?
- Is the game ↔ LLM interface thoughtfully designed?
- Are potential scaling, performance, and reliability issues addressed?

### LLM Integration Quality
- Do NPCs have relevant context without wasteful token usage?
- Are responses natural and contextually appropriate?
- Is latency handled gracefully (loading indicators, async patterns)?
- Do guardrails prevent game-breaking outputs (NPCs claiming impossible actions)?
- Can NPCs remember previous interactions within a session?
- How well are API failures, timeouts, and rate limits handled?

### Game Implementation
- Is procedural generation interesting and functional?
- Are player controls responsive and intuitive?
- Does the game loop work smoothly (turn-based or real-time)?
- Is the ASCII/terminal UI clear and helpful?
- Are there multiple distinct NPC personalities?
- Do the demonstrated interaction patterns (2-3 required) work reliably?

### Code Quality
- Clean separation between game logic, rendering, and LLM integration?
- Modular architecture that's maintainable and extensible?
- Proper error handling, especially for LLM failures?
- Async/concurrency handled correctly if applicable?
- Well-commented, particularly around LLM integration logic?

### Creative Demonstration
- Does this showcase something unique that only LLM NPCs enable?
- Are the interaction patterns creative and engaging?
- Can players create emergent, unexpected but valid gameplay moments?
- Does it make you excited about LLM-driven game possibilities?
- Is there replay value through dynamic content?

### Documentation
- Is `DESIGN.md` clear and comprehensive?
- Can another developer understand and reproduce the setup?
- Are architectural decisions well-documented?
- Is the README helpful for getting started?
- Are interesting design choices explained?

### Polish & User Experience
- Despite ASCII constraints, is the UI/UX clear?
- Are there helpful tutorials or hints?
- Does it feel like a coherent game experience?
- Are loading states well-communicated?
- Does the game feel playable and fun?

## Technical Constraints

- **Language**: Open choice (Python, Rust, Go, JavaScript/TypeScript, etc.) - must justify selection
- **Framework**: Open choice (libtcod, BearLibTerminal, Textual, custom, etc.) - must justify selection
- **LLM Integration**: Any provider/framework allowed - must justify approach
- **Design Documentation**: `DESIGN.md` required with architecture justification
- **Procedural Generation**: Dungeons must be randomly generated each run
- **NPC Diversity**: Multiple NPCs with distinct personalities
- **Interaction Patterns**: Demonstrate 2-3 interesting LLM-enabled interactions
- **Persistence**: Save/load optional but recommended

## Starting Point

The `_base` folder contains:
- Complete task specification in `prompt.md`
- Basic `pyproject.toml` as reference (if choosing Python)
- `.gitignore` for common artifacts
- No implementation code (agent builds from scratch)
- No prescribed stack (agent researches and decides)

This minimal scaffolding ensures agents start with research and decision-making rather than following a predefined path.

Copy `_base` to your test folder and let your agent work from the `prompt.md` specification.
