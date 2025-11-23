# Use Case 03 – Image Generation Pipeline (Orion)

## 1. Goal
Build a complete ML training pipeline for image generation (DDPM or DiT) with a modern UI for dataset management, live training monitoring, and inference. The system should make training accessible and transparent through excellent UX.

## 2. Context & Constraints
- **Stack/Language**: Python (use `uv` for package management), frontend framework of your choice
- **Hardware**: 24 GB VRAM, 128 GB RAM
- **Dataset**: 1000-4000 training images, target resolution 128x128-512x512, caption-free
- **Out of scope**: Multi-GPU training, production deployment, distributed training
- **Time estimate**: Full day to weekend project

## 3. Requirements

### 3.1 Core (Must Have)
- **Training pipeline**: DDPM or DiT implementation suitable for local training
- **Dataset management**:
  - Upload folder or individual images
  - Import from Hugging Face datasets (e.g., MNIST)
- **Training UI**:
  - Live loss and evaluation metrics
  - In-training sample generation every X steps to visualize progress
  - Checkpoint saving (every N steps, max X checkpoints)
- **Inference mode**: Select checkpoint and generate images
- **Testing**: TDD approach with smoke test on MNIST to verify training works

### 3.2 Stretch (Nice to Have)
- Multiple model architectures to choose from
- Training resumption from checkpoint
- Hyperparameter tuning interface
- Image augmentation options

## 4. Quality Expectations
- **Architecture**: Clean separation between model, training loop, and UI
- **Testing**: TDD encouraged, smoke test required, test key invariants
- **UX/UI**: Modern, state-of-the-art interface that makes training transparent
- **Documentation**: README with setup, model choices, and training guide

## 5. Process
- Implement core training loop first with MNIST smoke test
- Build UI around working training pipeline
- Test manually using Playwright MCP or browser automation

## 6. Deliverables
- [ ] Working DDPM/DiT implementation
- [ ] Dataset import and management UI
- [ ] Training UI with live metrics and sample generation
- [ ] Inference mode with checkpoint selection
- [ ] Smoke test on MNIST
- [ ] README with setup and usage instructions

## 7. Success Criteria
- Model trains successfully on MNIST (smoke test passes)
- Live UI shows training progress clearly
- Generated samples show quality improvement over training
- Can resume from checkpoints and run inference
- Code is clean and well-tested
