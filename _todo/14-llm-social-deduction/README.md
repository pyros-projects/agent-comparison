# Use Case 14: LLM Social Deduction (AmongWeb)

**Port the terminal-based Among LLMs game into a stylish, modern web application where one human must survive among AI agents hunting for the hidden player.**

## The Challenge

Take [Among LLMs](https://github.com/0xd3ba/among-llms), a terminal-based social deception game built with Python's Textual library, and transform it into a polished web-based experience. The original game is available in `_base/external/among-llms/` for reference. The game drops a single human player into a chatroom full of AI agents, all trying to identify and vote out the human through conversation and deduction. Your task: preserve the core gameplay while creating an intuitive, visually compelling browser interface that makes this unique LLM-powered game accessible to anyone with a web browser.

This tests full-stack development skills, UI/UX design thinking, LLM integration, real-time interaction patterns, and the ability to understand and adapt existing game mechanics for a new platform.

See [`_base/prompt.md`](_base/prompt.md) for the complete specification.

## What This Tests

### Understanding Existing Systems
The challenge begins with comprehension:
- **Code archaeology**: Reading and understanding unfamiliar codebase (available in `_base/external/among-llms/`)
- **Gameplay analysis**: Playing the original to grasp mechanics and feel
- **Architecture extraction**: Identifying core systems (state management, voting, DMs, LLM integration)
- **Feature mapping**: Determining what to port, what to adapt, what to enhance
- **Dependency analysis**: Understanding Textual UI patterns and how to translate them

This tests the ability to learn from existing code and gameplay, not build from scratch.

### Full-Stack Web Development
Building a complete web application tests:
- **Backend design**: Game state management, LLM API integration, real-time updates
- **Frontend development**: Modern UI framework (React/Vue/Svelte), component architecture
- **Client-server communication**: REST APIs or WebSockets for real-time chat
- **State synchronization**: Keeping client and server in sync
- **Data modeling**: Messages, participants, votes, personas, game state

This tests end-to-end web development, not just frontend or backend in isolation.

### UI/UX Translation
Adapting a terminal UI to web requires design thinking:
- **Interface design**: Translating text-based interactions to graphical elements
- **Information hierarchy**: Organizing chat, DMs, participants, votes, controls
- **Interaction patterns**: Making complex features (impersonation, message editing) intuitive
- **Visual feedback**: Showing game state, AI thinking, vote progress, eliminations
- **Accessibility**: Clear affordances for all player actions

This tests UI/UX design skills and understanding of web-native interaction patterns.

### Real-Time Interaction Design
Creating a live chatroom experience tests:
- **Message streaming**: Displaying AI messages as they're generated
- **Concurrent actions**: Handling multiple agents "thinking" and posting simultaneously
- **State updates**: Reflecting vote changes, DMs, message edits in real-time
- **User agency**: Allowing player actions (send, edit, delete, vote) without blocking
- **Performance**: Smooth updates even with many agents and long conversation history

This tests real-time system design and async programming.

### LLM Integration Patterns
Connecting AI agents to the web interface tests:
- **API abstraction**: Supporting multiple LLM providers (OpenAI, Anthropic, local Ollama)
- **Prompt engineering**: Maintaining agent personas, scenario context, conversation history
- **Context management**: Handling chat history with token limits (original uses 30-message window)
- **Response streaming**: Showing AI responses as they generate, not waiting for completion
- **Error handling**: Gracefully handling API failures, rate limits, timeout

This tests practical LLM integration beyond simple API calls.

### Game State Management
Managing complex game state tests:
- **Persistence**: Save/load complete game state as JSON
- **Consistency**: Ensuring all game elements (messages, votes, DMs, personas) remain coherent
- **History tracking**: Recording all events for replay or debugging
- **Reset capability**: Clearing messages while preserving scenario/personas
- **Serialization**: Converting in-memory game state to portable format

This tests state management architecture and data integrity.

### Message Manipulation Mechanics
Implementing the player's "chaos powers" tests:
- **Edit functionality**: Retroactively changing any participant's message
- **Deletion**: Removing messages from history (with tracking for player)
- **Impersonation**: Sending messages as any participant
- **Visual indicators**: Showing player which messages they've manipulated
- **Undo/history**: Allowing player to revert manipulation actions
- **Agent perception**: Ensuring AI agents see manipulated chat as truth

This tests complex interaction design and state mutation logic.

### Voting System Implementation
Building the elimination mechanic tests:
- **Vote initiation**: Starting votes as any participant
- **Vote tracking**: Recording who voted for whom
- **Vote UI**: Displaying current vote state, progress, countdown
- **Vote resolution**: Determining majority, handling ties, triggering elimination
- **Vote impersonation**: Allowing player to vote as other participants
- **Win/loss detection**: Recognizing game-ending conditions

This tests event-driven system design and game rule implementation.

### Scenario & Persona System
Implementing dynamic game setup tests:
- **Scenario generation**: Creating coherent scenario contexts (Fantasy, Sci-Fi, Thriller, etc.)
- **Persona creation**: Generating fitting backstories and personalities for each agent
- **Randomization**: Creating varied setups for replayability
- **Customization**: Allowing manual scenario/persona definition
- **Integration**: Weaving personas and scenario into agent prompts and behavior

This tests procedural generation and prompt engineering for context-rich gameplay.

## Why This Use Case?

This task was chosen because it tests **porting and enhancement skills** combined with **full-stack web + LLM integration**:

1. **Code comprehension** - Must understand existing implementation before porting
2. **Platform translation** - Terminal → Web requires rethinking interaction paradigms
3. **Full-stack scope** - Tests both frontend and backend, not just one layer
4. **Real-time systems** - Chatroom mechanics require proper async/event handling
5. **LLM integration** - Agent behavior is core mechanic, not peripheral feature
6. **UX design** - Success requires making complex mechanics intuitive and visually appealing
7. **State management** - Complex game state with persistence and manipulation

An agent that handles this well demonstrates:

- **Reverse engineering**: Understanding existing systems from code and gameplay
- **Architectural thinking**: Designing clean separation between game logic, LLM, UI
- **Full-stack capability**: Building complete, working web applications
- **UX sensibility**: Creating interfaces that are intuitive and polished, not just functional
- **Real-time systems**: Handling async LLM calls, concurrent agent actions, state updates
- **Feature parity + enhancement**: Matching original capabilities while improving experience

This is fundamentally different from other use cases:
- **vs. Puzzle Game**: Porting existing game vs. designing new game
- **vs. Collaborative Editor**: Chatroom with AI agents vs. multi-user document editing
- **vs. LLM Roguelike**: Social deception with voting vs. turn-based adventure
- **vs. Video Curator**: Web UI for game vs. web UI for media management

## Evaluation Focus

When reviewing implementations, pay attention to:

### Gameplay Parity
- Are all core mechanics from the original working? (Chat, DMs, voting, manipulation)
- Do AI agents behave convincingly in conversations?
- Does the voting system work correctly (initiation, tracking, elimination)?
- Can player impersonate, edit, and delete messages effectively?
- Is the persona/scenario system generating interesting setups?

### UI/UX Quality
- Is the interface intuitive for new players?
- Are complex interactions (DMs, impersonation, voting) easy to understand and use?
- Is the visual design polished and modern, not basic/ugly?
- Do animations and transitions enhance the experience, not distract?
- Is information hierarchy clear? (What's important is prominent)

### Real-Time Feel
- Do AI messages appear smoothly as they're generated?
- Does the UI feel responsive to player actions?
- Are vote updates and elimination events handled dramatically/clearly?
- Is there appropriate feedback for all player actions?

### Technical Implementation
- Clean architecture separating game logic, LLM integration, UI?
- Proper state management (no lost/corrupted game state)?
- Efficient LLM integration (streaming, context management)?
- Real-time updates implemented well (WebSockets or polling)?
- Save/load functionality working reliably?

### Code Quality
- Component-based frontend architecture?
- Type safety (TypeScript types or Python type hints)?
- Clear separation of concerns?
- Tests for critical game logic (voting, state management)?
- Good documentation explaining architecture and setup?
- Optionally: Playwright MCP testing demonstrating key user flows?

### Enhancement Beyond Original
- Does the web version improve on the terminal experience?
- Are there thoughtful UX additions not in the original?
- Is the game more accessible/easier to learn than terminal version?
- Any clever features that leverage web platform strengths?

## Original Game Context

[Among LLMs](https://github.com/0xd3ba/among-llms) is a terminal-based social deception game where:

- **Setting**: One human player vs. multiple AI agents in a chatroom
- **Objective (Human)**: Survive until only you and one agent remain
- **Objective (AI Agents)**: Identify and vote out the human
- **Mechanics**: Public chat, private DMs, voting, message manipulation
- **Features**: Random scenarios/personas, save/load state, customizable agent count
- **Tech**: Python, Textual (terminal UI), Ollama (local LLMs)
- **Unique Twist**: Player can read all DMs, edit any message, impersonate anyone

The game was created for the OpenAI Open Model Hackathon 2025 and has gained traction in the terminal gaming community.

## Example Game Flow

```
1. [Setup]
   → Choose scenario: "Sci-Fi Space Station Mystery"
   → 8 AI agents with generated personas (engineer, security, scientist, etc.)
   → Player assigned persona: "Maintenance Technician"

2. [Chat Phase]
   → AI agents start conversing about recent "incidents"
   → Player joins conversation, trying to blend in
   → Some agents start getting suspicious, scrutinizing messages

3. [DM Phase]
   → Player DMs individual agents to manipulate them
   → Reads AI agents' private DMs to each other (they don't know player can see)
   → Uses information from DMs to gaslight agents in public chat

4. [Manipulation Phase]
   → Player edits another agent's message to make them seem suspicious
   → Deletes a message that revealed player's mistake
   → Impersonates an agent to start false accusations

5. [Voting Phase]
   → An agent initiates vote to eliminate suspected human
   → Player votes as other agents to frame someone else
   → Elimination occurs (not the player this time)

6. [Endgame]
   → After several rounds, only player and one agent remain
   → Victory screen, option to save game state or start new game
```

## Success Signals

**Minimal Success:**
- Web app runs with chatroom interface
- AI agents post messages (even if slowly/sequentially)
- Basic voting works (initiate vote, eliminate participant)
- DM system exists (send private messages)
- Player can send messages and see AI responses

**Good Success:**
- All core mechanics working (chat, DMs, voting, manipulation)
- AI agents behave convincingly in scenario contexts
- UI is polished and intuitive, not just functional
- Real-time feel with smooth message updates
- Save/load state works reliably
- Persona/scenario system creates varied games

**Excellent Success:**
- Feature parity with original + web-specific enhancements
- Exceptional UI/UX that makes game more accessible than terminal version
- Smooth real-time updates with proper WebSocket implementation
- Advanced features (spectator mode, replay, statistics)
- Support for multiple LLM providers with easy configuration
- Comprehensive documentation and tutorial/onboarding

## Useful Resources

- **Local Among LLMs Copy**: `_base/external/among-llms/` (complete repository for reference)
- [Original Among LLMs Repo](https://github.com/0xd3ba/among-llms) (upstream repository)
- [Among LLMs Quick Start Guide](https://github.com/0xd3ba/among-llms/blob/main/docs/guide.md)
- [Textual Documentation](https://textual.textualize.io/) (to understand original UI patterns)
- [r/AmongLLMs Subreddit](https://www.reddit.com/r/AmongLLMs/) (community examples and strategies)
