# Use Case 03: Image Generation (Orion)

**A complete ML training pipeline combining web research, architecture decisions, and a polished real-time training UI.**

## The Challenge

Build a toy image generation model training pipeline designed for local experimentation on consumer hardware. This task has two major phases:

1. **Research Phase** - Investigate and choose an appropriate model architecture (DDPM or DiT) suitable for:
   - 24 GB GPU VRAM
   - 128 GB system RAM
   - 1000–4000 training images
   - 128×128 to 512×512 resolution
   - Caption-free training

2. **Implementation Phase** - Build a state-of-the-art modern UI around the training workflow with:
   - Dataset import (upload folders, single images, or HuggingFace datasets)
   - Live training monitoring (loss curves, evaluation metrics)
   - In-training sample generation to visualize progress
   - Checkpoint management and inference mode

See [`_base/prompt.md`](_base/prompt.md) for the complete specification.

## What This Tests

### Research & Decision-Making Capabilities
The agent must perform genuine web research to:
- Survey current model architectures for image generation
- Understand hardware constraints and their implications
- Evaluate trade-offs between different approaches
- Estimate training time and resource usage
- Document reasoning in `architecture.md`

This tests whether the agent can go beyond code generation to do real research and make informed technical decisions.

### ML/AI Domain Knowledge
Implementing a diffusion model or DiT from scratch tests:
- Understanding of image generation architectures
- Knowledge of training loops, loss functions, and optimization
- Familiarity with modern ML frameworks (PyTorch/JAX)
- Awareness of hardware constraints (VRAM, batch sizes, precision)
- Ability to implement realistic, not toy, models

### Training Infrastructure
Building a complete training pipeline requires:
- Dataset loading and preprocessing
- Training loop with proper logging
- Checkpoint saving and loading
- Evaluation set handling
- In-training inference for progress monitoring

This tests the agent's ability to create production-ready ML infrastructure.

### Real-Time Monitoring UI
The UI must provide live feedback during training:
- Real-time loss visualization (charts updated during training)
- Evaluation metrics displayed as they're computed
- Generated sample images every X steps
- Progress tracking and ETA estimation

This tests both frontend skills and the ability to architect real-time data flow between training process and UI.

### Test-Driven Development
The specification requires:
- TDD approach to development
- A smoke test training on MNIST to validate behavior
- Manual UI testing with browser tools/Playwright MCP
- Verification that in-training samples show convergence

This tests the agent's ability to follow best practices and implement meaningful tests.

### Hardware-Aware Optimization
With strict constraints (24GB VRAM, local training), the agent must:
- Choose appropriate model sizes
- Implement efficient batching
- Consider mixed precision training
- Estimate realistic training times
- Avoid over-ambitious architectures

This tests practical ML engineering skills beyond just algorithm knowledge.

## Why This Use Case?

This task was chosen because it **combines research with implementation** in a way that tests very different capabilities:

1. **Research first, code second** - Agent must think before coding
2. **ML domain expertise** - Can't fake understanding of diffusion models
3. **Hardware constraints** - Must work within realistic limits
4. **Real-time systems** - Live training monitoring is non-trivial
5. **End-to-end ML pipeline** - From data loading to inference
6. **Documentation** - Must explain choices in `architecture.md`

An agent that handles this well demonstrates:

- Ability to perform independent research
- Strong ML/AI fundamentals
- Practical engineering judgment (not just theoretical knowledge)
- Full-stack ML skills (data, training, UI, inference)
- Awareness of real-world constraints
- Clear technical communication

This is fundamentally different from web apps (Use Cases 01 and 02), revealing whether an agent has genuine ML expertise or just pattern-matches web development.

## Evaluation Focus

When reviewing implementations, pay attention to:

### Research Quality
- Is `architecture.md` thoughtful and well-reasoned?
- Does the chosen architecture fit the constraints?
- Are alternatives discussed meaningfully?
- Are training time estimates realistic?
- Does the agent understand the trade-offs?

### Model Implementation
- Is the model architecture correctly implemented?
- Are training dynamics sound (loss decreases, samples improve)?
- Is the code idiomatic for the ML framework used?
- Are there obvious bugs or conceptual errors?
- Would this actually train successfully?

### Training Pipeline
- Is dataset loading efficient?
- Is the training loop robust and well-structured?
- Are checkpoints saved properly?
- Can training be resumed?
- Is logging comprehensive?

### UI & Monitoring
- Does the UI update in real-time during training?
- Are visualizations helpful and clear?
- Can users understand training progress at a glance?
- Is the interface polished and professional?
- Does it feel like a "real" research tool?

### Testing
- Is there a MNIST smoke test that validates training?
- Does the test verify convergence (improving samples)?
- Are there UI tests using Playwright or similar?
- Can the tests catch obvious regressions?

### Code Quality
- Is the code clean and maintainable?
- Is the project structure logical?
- Are dependencies managed with `uv` correctly?
- Is the codebase ready for extension (new models, datasets)?
- Are there comments explaining complex ML logic?

## Technical Constraints

- **Python with `uv`** for package and run management
- **PyTorch or JAX** for ML framework (agent's choice)
- **Any frontend framework** for the UI
- **DDPM or DiT** architecture (or well-justified alternative)
- **Local training constraints**: 24GB VRAM, 128GB RAM
- **Dataset size**: 1000–4000 images at 128×128 to 512×512
- **Caption-free** training approach

## Starting Point

The `_base` folder contains:
- Complete task specification in `prompt.md`
- Initialized Python project with `uv` configuration
- Minimal boilerplate code

The agent must first research architectures, then implement the chosen approach with a complete training UI.

Copy `_base` to your test folder and let your agent work from the `prompt.md` specification.
