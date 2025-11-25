# Use Case 14 – LLM Social Deduction (AmongWeb)

## 1. Goal

Port the terminal-based game [Among LLMs](https://github.com/0xd3ba/among-llms) into a modern, stylish web-based multiplayer game. Transform the command-line social deception experience into an engaging browser-based interface where one human player must survive among AI agents that are hunting for the hidden human. Maintain the core mechanics (voting, DMs, message manipulation, impersonation) while creating an intuitive, visually compelling web UI that makes the game accessible and immersive.

## 2. Context & Constraints

- **Stack/Language**: Full-stack JavaScript/TypeScript (Node.js backend + React/Vue/Svelte frontend) or Python (FastAPI/Flask + modern frontend)
- **Original Game**: Terminal UI built with Textual library, Ollama local LLM backend, chatroom-based gameplay
- **Core Mechanics to Port**: Chatroom with AI agents, voting system, direct messages, message editing/deletion/impersonation, persona/scenario system, save/load state
- **LLM Integration**: Any provider (OpenAI, Anthropic, local models via Ollama) - not restricted to original's Ollama-only
- **Time estimate**: 8-10 hours (2-3h understanding original, 5-7h web implementation)
- **Out of scope**: Voice chat, mobile app, advanced anti-cheat, complex animations beyond CSS/simple libraries

## 3. Requirements

### 3.1 Core (Must Have)

**Game Setup & Configuration**
- Create or load chatroom with customizable settings
- Choose scenario (Fantasy, Sci-Fi, Thriller, Crime, Custom) or randomize
- Set number of AI agents (scalable: 3-15+ agents)
- Auto-generate or manually define agent personas and backstories
- Configure LLM provider and model selection

**Chatroom Interface**
- Main chat feed showing all participant messages with timestamps
- Participant list with personas, avatars/colors, and status indicators
- Message composition area with send functionality
- Visual distinction between player, AI agents, and system messages
- Real-time message updates as AI agents converse

**Direct Messaging System**
- Private DM interface for player to send messages to individual agents
- View all DM conversations (player sees AI DMs too, but AIs don't know this)
- Clear visual separation between public chat and DMs
- Notification system for new DMs

**Message Manipulation Powers**
- **Edit**: Modify any participant's message retroactively
- **Delete**: Remove any message from the chat
- **Impersonate**: Send messages as any participant
- Visual indicators for manipulated messages (only visible to player)
- Undo/history for player's manipulation actions

**Voting Mechanism**
- Initiate vote to eliminate suspected human (as any participant)
- Vote UI showing current votes, who voted for whom
- Vote countdown/timer
- Elimination screen when player is voted out
- Ability to vote as other participants (impersonation)

**Game State Management**
- Track conversation history, agent states, vote records
- Export chatroom state as JSON (save mid-game)
- Load saved chatroom states to resume games
- Reset chatroom (keep setup, clear messages)

**Win/Loss Conditions**
- Detect when player is eliminated (loss)
- Detect when only player and one agent remain (win)
- Victory/defeat screens with game summary

### 3.2 Stretch (Nice to Have)

- Multiple concurrent chatrooms (tabs or sessions)
- Spectator mode (observe game without participating)
- Replay mode (step through saved game states)
- Customizable UI themes (dark/light mode, color schemes)
- Sound effects and ambient audio
- Advanced agent behavior settings (aggression, suspicion levels)
- Statistics dashboard (games played, win rate, favorite strategies)
- Share game states with others (link or file sharing)
- Agent personality visualization (suspicion meters, relationship graphs)
- Tutorial/guided first game
- Message filters (search, highlight keywords)
- Keyboard shortcuts for power users
- Manual testing with Playwright MCP to validate UI interactions and game flow

## 4. Quality Expectations

- **UI/UX Excellence**: Polished, intuitive interface that makes complex interactions (DMs, voting, impersonation) easy to understand and use. Not just functional—stylish.
- **Responsive Design**: Works smoothly on desktop browsers (1920x1080 to 1366x768 minimum). Mobile support is stretch but interface should degrade gracefully.
- **Performance**: Real-time feel with smooth message updates. LLM delays are expected, but UI should never feel sluggish.
- **Code Quality**: Clean separation between game logic, LLM integration, and UI. TypeScript types or Python type hints throughout. Component-based architecture.
- **Testing**: Tests for game state management, voting logic, message manipulation. UI component tests for critical interactions. Optionally use Playwright MCP for manual browser testing.
- **Documentation**: README with setup instructions, game rules explanation, architecture overview. Comments for complex game logic.

## 5. Process

**Phase 1: Research & Planning (2-3 hours)**

1. **Study Original Game**
   - Review the Among LLMs codebase in `external/among-llms/`
   - Read code to understand state management, voting, DM system
   - Document core features and interaction patterns

2. **Design Web Adaptation**
   - Sketch UI layout (chat area, participant list, DM panel, controls)
   - Plan tech stack (React vs Vue? REST vs WebSockets?)
   - Design data models (message, participant, vote, game state)
   - Plan LLM integration strategy

**Phase 2: Core Implementation (4-5 hours)**

- Set up project structure (frontend + backend)
- Implement chatroom with basic messaging
- Add AI agent integration (LLM calls, persona-based responses)
- Build voting system
- Implement DM functionality
- Create message manipulation features

**Phase 3: Polish & Enhancement (2-3 hours)**

- Style UI with modern CSS/component library
- Add animations and transitions
- Implement save/load state
- Test game flow end-to-end
- Refine agent behavior and prompting
- use Playwright MCP for interactive browser testing and validation

## 6. Deliverables

- [ ] **Working web application** - Browser-based game with frontend and backend
- [ ] **Chatroom interface** - Public chat with AI agents conversing in real-time
- [ ] **DM system** - Private messaging with visibility into AI DM conversations
- [ ] **Message manipulation** - Edit, delete, impersonate functionality working smoothly
- [ ] **Voting mechanism** - Initiate votes, vote as other participants, elimination logic
- [ ] **Game state persistence** - Save/load chatroom states as JSON
- [ ] **Scenario/persona system** - Multiple scenarios, randomized or custom personas
- [ ] **Polished UI** - Modern, styled interface that's intuitive and visually appealing
- [ ] **README** - Setup, gameplay, architecture documentation
- [ ] **Test suite** - Tests for game logic, state management, voting

## 7. Success Criteria

- **Gameplay Parity**: All core mechanics from original terminal game work in web version (chat, DMs, voting, manipulation, personas).
- **UI Quality**: Interface is intuitive, visually polished, and makes the game more accessible than terminal version. New players can understand how to play within 2-3 minutes.
- **Real-time Feel**: AI agents respond and converse naturally. Message updates feel live, not clunky. Voting and DMs work smoothly.
- **State Management**: Save/load works reliably. Game state is consistent across sessions. No lost progress or corrupted saves.
- **Agent Behavior**: AI agents behave convincingly (accuse, defend, whisper, vote). Conversations feel dynamic, not repetitive.
- **Code Quality**: Clean architecture, well-documented, easy to extend with new features (new scenarios, agent behaviors, UI themes).

---

## Notes

This is a **porting and enhancement challenge** testing:
- Understanding existing game mechanics from code and gameplay
- Translating terminal UI concepts to modern web interfaces
- Full-stack web development (frontend + backend + LLM integration)
- Real-time interaction design
- Balancing feature parity with UX improvements

The goal is not just to replicate the terminal game, but to **make it better** through thoughtful web-native design while preserving what makes the original compelling.
