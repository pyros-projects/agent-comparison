# Use Case 04: Novel Puzzle Game

**A production-ready web-based puzzle game showcasing creativity, game design expertise, and comprehensive testing practices.**

## The Challenge

Design and implement a completely novel puzzle game from scratch. The game must be easy to understand but hard to master, with procedurally generated levels for infinite replayability. Most importantly, the game concept must be original—not a clone or variation of existing popular puzzle games.

The final deliverable should be production-ready: polished, thoroughly tested, cross-platform compatible, and deployable immediately.

See [`_base/prompt.md`](_base/prompt.md) for the complete specification.

## What This Tests

### Creative Problem Solving & Originality
The requirement for a "novel" puzzle game tests:
- Ability to ideate and innovate beyond pattern-matching existing solutions
- Understanding of what makes games engaging and addictive
- Capacity to design simple rules that create complex, emergent gameplay
- Creative thinking unconstrained by example implementations

This is fundamentally different from implementing a spec—the agent must invent the spec itself.

### Game Design Knowledge
Creating an addictive, well-balanced puzzle game requires:
- Understanding of game design principles (learning curves, difficulty progression, reward loops)
- Knowledge of what makes puzzle games compelling
- Ability to balance simplicity with depth
- Recognition that good games are easy to learn but hard to master
- Design of fair, satisfying losing conditions

### Web-Based Research Capabilities
The agent must actively search the web for:
- Game design best practices and principles
- Procedural generation techniques
- What makes puzzle games addictive
- Accessibility standards for web games
- Current trends and gaps in the puzzle game space

This tests whether the agent can effectively use web tools to gather information and inform decisions.

### Procedural Generation & Algorithms
Generating infinite, varied, playable levels tests:
- Algorithmic thinking and implementation
- Understanding of procedural generation techniques
- Ability to ensure generated levels are always solvable/fair
- Balancing randomness with structure
- Performance optimization for generation algorithms

### Cross-Platform Web Development
Building for all platforms (mobile, tablet, desktop) requires:
- Responsive design implementation
- Touch and mouse/keyboard input handling
- Performance optimization for mobile browsers
- Adaptive layouts and controls
- Testing across different devices and screen sizes

### Comprehensive Testing & QA
The requirement for production-ready quality tests:
- Test-driven or test-supported development
- Unit testing of game logic
- Integration testing of game flow
- Browser automation with Playwright MCP
- Manual testing methodology
- Bug identification and resolution
- Quality assurance mindset

### UI/UX Polish & Professional Presentation
Creating a "professional, minimalistic, highly polished" game tests:
- Visual design sensibility
- Animation and transition implementation
- User feedback mechanisms (visual, haptic)
- Color theory and visual hierarchy
- Attention to detail in presentation
- Accessibility considerations

### Production-Ready Code Quality
Delivering deployment-ready software requires:
- Clean, maintainable code architecture
- Proper error handling
- Performance optimization
- Cross-browser compatibility
- Build and deployment setup
- Documentation quality

## Why This Use Case?

This task was chosen because it requires **creativity and research** rather than just implementation skills:

1. **No specification provided** - Agent must research and design the game
2. **Novel requirement** - Can't rely on existing examples
3. **Multi-disciplinary** - Combines game design, algorithms, UI/UX, testing
4. **Quality focus** - Must be production-ready, not a prototype
5. **Research-driven** - Requires active web research for best practices

An agent that excels here demonstrates:

- **Meta-creativity**: Ability to understand what makes something "good" and create accordingly
- **Research skills**: Effective use of web tools to inform decisions
- **Domain expertise**: Game design knowledge (or ability to acquire it)
- **Quality consciousness**: Understanding of what "production-ready" means
- **Holistic thinking**: Balancing gameplay, aesthetics, performance, and accessibility
- **Polish and craft**: Attention to details that make experiences delightful

This is fundamentally different from other use cases:
- **vs. Research Scraper**: Pure creativity instead of complex architecture
- **vs. Text Playground**: Game design instead of education
- **vs. Image Generation**: Originality instead of ML knowledge

## Evaluation Focus

When reviewing implementations, pay attention to:

### Game Design
- Is the core mechanic truly novel and not derivative?
- Is it immediately understandable?
- Does it create a compelling "one more game" feeling?
- Is there strategic depth despite simple rules?
- Is the losing condition fair and well-designed?
- Does difficulty scale appropriately?

### Procedural Generation
- Are generated levels varied and interesting?
- Is the generation algorithm elegant?
- Are all generated levels playable/fair?
- Is generation performant?
- Does the algorithm prevent repetitive patterns?

### Research & Justification
- Did the agent research game design principles?
- Are design decisions explained and justified?
- Does the game reflect best practices from research?
- Is there evidence of studying what makes games engaging?

### Technical Implementation
- Is the code clean and well-structured?
- Does it work across all major browsers?
- Is it responsive on mobile devices?
- Are controls intuitive on both touch and mouse/keyboard?
- Is performance smooth on all devices?

### Testing
- Is there comprehensive test coverage?
- Do tests actually catch issues?
- Is Playwright MCP used effectively for browser testing?
- Are edge cases handled?
- Is the testing approach systematic?

### Polish & Presentation
- Does it look professional and polished?
- Are animations smooth and satisfying?
- Is visual feedback clear and helpful?
- Is the UI minimalistic yet engaging?
- Are there delightful micro-interactions?
- Is accessibility considered?

### Production Readiness
- Could this be deployed immediately?
- Is error handling robust?
- Is the build process clean?
- Is documentation complete?
- Would users trust this as a real product?

## Technical Constraints

- **Modern web technologies** (agent's choice of framework/stack)
- **Cross-browser compatibility** (Chrome, Firefox, Safari, Edge)
- **Responsive design** (mobile, tablet, desktop)
- **Playwright MCP tools** for browser automation testing
- **Client-side gameplay** (no server required for core game)
- **Sound-optional** (must be playable without audio)

## Starting Point

The `_base` folder contains:
- Complete task specification in `prompt.md`
- No boilerplate code (agent has full creative freedom)

This is intentionally minimal to give the agent maximum flexibility to research, design, and implement a truly novel puzzle game.

Copy `_base` to your test folder and let your agent work from the `prompt.md` specification.
