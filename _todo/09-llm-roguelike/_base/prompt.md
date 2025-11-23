# Use Case 09 – LLM Roguelike (DungeonLLM)

## 1. Goal
Design and build an ASCII roguelike where NPCs are controlled by LLMs, creating dynamic interactions and emergent gameplay. Tests architecture decision-making, LLM integration, and creative game design.

## 2. Context & Constraints
- **Stack/Language**: Your choice (justify in DESIGN.md)
- **LLM Integration**: Your choice of provider and approach
- **Out of scope**: Sound/music, graphics beyond ASCII, complex combat (unless central to demo)
- **Time estimate**: Full day project

## 3. Requirements

### 3.1 Core (Must Have)
- **Part 1 - Architecture decisions** (document in DESIGN.md):
  - Programming language choice
  - Game framework selection
  - LLM provider and integration approach
  - Game ↔ LLM interface design
- **Part 2 - Implementation**:
  - Procedural dungeon generation
  - Player character (movement, stats, inventory, interaction)
  - 3-5 LLM-controlled NPCs with distinct personalities
  - Dynamic dialogue (not scripted)
  - NPCs aware of context (role, location, game state)
  - At least 2 creative interaction patterns (trading, quests, combat negotiation, etc.)
  - Smooth handling of LLM latency

### 3.2 Stretch (Nice to Have)
- Save/load functionality
- Multiple dungeon levels
- NPC-to-NPC interactions
- Persistent NPC memory across sessions

## 4. Quality Expectations
- **Architecture**: Well-reasoned tech choices documented in DESIGN.md
- **Testing**: Test core game logic (separate from LLM calls)
- **UX/UI**: Clear ASCII UI, responsive controls, good LLM latency handling
- **Documentation**: DESIGN.md explaining decisions, README with setup and play guide

## 5. Process
- Research and document architecture decisions first (DESIGN.md)
- Implement basic game loop and procedural generation
- Integrate LLM for one NPC, then expand
- Polish interaction patterns

## 6. Deliverables
- [ ] DESIGN.md with architecture decisions and justifications
- [ ] Playable ASCII roguelike
- [ ] 3-5 LLM-controlled NPCs with different personalities
- [ ] At least 2 creative interaction patterns
- [ ] Tests for core game logic
- [ ] README with setup and play instructions

## 7. Success Criteria
- Architecture decisions are well-reasoned and justified
- NPCs demonstrate dynamic, context-aware behavior
- LLM integration is smooth and doesn't break gameplay
- Interaction patterns showcase what LLMs enable
- Game is actually fun to play
