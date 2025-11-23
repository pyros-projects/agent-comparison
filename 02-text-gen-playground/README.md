# Use Case 02: Text Generation Playground

**An educational web application with interactive visualizations for teaching early text generation concepts to laypeople.**

## The Challenge

Build a polished, interactive web playground that teaches non-technical users about the early history and mechanics of text-based generative AI. The application must include:

- **N-gram Lab** - Interactive experimentation with n-gram language models
- **Genetic Text Lab** - Visualized genetic algorithm for text generation/optimization
- **Mystery Lab** - A third important concept (agent's choice) with interactive controls

The app should feel like a "state of the art" modern UI with clear explanations, live visualizations, and hands-on parameter tweaking that helps users intuitively understand how these foundational methods work.

See [`_base/prompt.md`](_base/prompt.md) for the complete specification.

## What This Tests

### Educational UX Design
Creating an app for laypeople tests whether the agent can:
- Translate complex technical concepts into plain language
- Design intuitive, exploratory interfaces
- Balance depth with accessibility
- Use visual feedback to reinforce learning
- Create "aha moment" experiences through interaction

### Algorithm Visualization
Each lab requires meaningful visualizations:
- N-gram frequency charts and context highlighting
- Real-time genetic algorithm fitness graphs
- Step-by-step execution views
- Parameter-to-output cause-and-effect demonstrations

This tests the agent's ability to choose appropriate visual representations and implement them effectively.

### Client-Side Computation
The specification encourages client-side implementations where feasible. This evaluates:
- Algorithm implementation from scratch (not just API calls)
- Performance optimization for browser execution
- Efficient state management for interactive controls
- Progressive rendering for long-running computations

### Modern SPA Architecture
Building a polished single-page app tests:
- Component structure and organization
- Routing/navigation between labs
- State management patterns
- Responsive design and layout
- CSS framework usage (e.g., Tailwind)

### Pedagogical Clarity
The agent must explain concepts effectively:
- What is an n-gram? How does it predict text?
- How do genetic algorithms work? (Population, fitness, selection, crossover, mutation)
- Why are these historically important?
- How do they compare to modern neural LMs?

This tests the agent's own understanding and ability to teach.

### Creative Problem Solving (Mystery Lab)
The third lab is agent's choice. This tests:
- Independent research and decision-making
- Justification of choices (conceptual importance + implementability + educational clarity)
- Creative thinking about what would be valuable to include
- Ability to compare and contrast different approaches

Common choices might include: temperature/sampling strategies, beam search, Markov chains, or tiny RNNs.

### Code Quality & Maintainability
With three distinct labs, the codebase structure matters:
- Are components reusable across labs?
- Is the code clean and well-organized?
- Can new labs be added easily?
- Is the architecture extensible?

## Why This Use Case?

This task was chosen because it requires a **very different skill set** from the other use cases:

1. **No backend complexity** - Focus is on frontend and algorithms
2. **Education over features** - UX clarity is paramount
3. **Visual thinking** - Charts, graphs, and interactive demos
4. **Algorithm implementation** - Actually coding n-grams, GAs from scratch
5. **User empathy** - Must consider non-technical audience needs

An agent that excels here demonstrates:

- Strong frontend development skills
- Ability to implement algorithms, not just integrate APIs
- UX/UI design sensibility
- Communication and teaching ability
- Creative problem-solving (Mystery Lab choice)
- Understanding of CS fundamentals (text generation history)

This is quite different from backend-heavy tasks like the Research Scraper, revealing different strengths and weaknesses in agent capabilities.

## Evaluation Focus

When reviewing implementations, pay attention to:

### User Experience
- Can a non-technical person understand what's happening?
- Are explanations clear and accurate without being condescending?
- Do interactive controls respond smoothly?
- Is the visual design polished and modern?
- Is the learning progression logical?

### Educational Effectiveness
- Do the labs actually teach the concepts?
- Are visualizations helpful or just decorative?
- Do parameter changes create "aha moments"?
- Are comparisons between methods clear?
- Would a user walk away with real understanding?

### Technical Implementation
- Are algorithms implemented correctly?
- Is performance acceptable for browser execution?
- Is the code clean and well-structured?
- Are there appropriate tests for core logic?
- Is the SPA architecture sound?

### Mystery Lab Quality
- Is the chosen third concept genuinely important?
- Is the choice well-justified in code comments or docs?
- Is it implemented as interactively as the other labs?
- Does it complement the n-gram and GA labs well?

### Polish & Completeness
- Does the app feel finished?
- Is there a landing page that orients users?
- Are all three labs complete and functional?
- Is the UI consistent across labs?
- Are there any rough edges or placeholder content?

## Technical Constraints

- **Modern SPA stack** - React + TypeScript recommended, or similar
- **Utility-first CSS** - Tailwind or comparable framework
- **Optional backend** - Keep it simple (FastAPI) if needed for heavy computation
- **Accessibility** - Keyboard navigation, good contrast
- **Performance** - Should run smoothly in modern browsers
- **Testing** - At least basic tests for core algorithm logic

## Starting Point

The `_base` folder contains:
- Complete task specification in `prompt.md`
- No boilerplate code (agent chooses stack)

This is intentionally minimal to give the agent maximum flexibility in choosing the right tools and structure for an educational web app.

Copy `_base` to your test folder and let your agent work from the `prompt.md` specification.
