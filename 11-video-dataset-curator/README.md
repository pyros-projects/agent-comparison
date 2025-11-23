# Use Case 11: Video Dataset Curator (FrameCraft)

**A sleek web application for curating video datasets, demonstrating full-stack development, video processing, and modern UI design.**

## The Challenge

Build a local web application for managing video datasets used in training video generation AI models. The app features a masonry gallery for browsing videos, supports video upload with FPS conversion via FFmpeg, and enables splitting videos into clips through scene detection or fixed frame intervals.

The task requires modern UI design, efficient video processing, handling large media files, and providing smooth UX despite computationally expensive operations.

See [`_base/prompt.md`](_base/prompt.md) for the complete specification.

## What This Tests

### Full-Stack Web Development
Building a complete video management app tests:
- **Frontend architecture**: Modern JavaScript/TypeScript framework (React, Vue, Svelte)
- **Backend API design**: REST or GraphQL endpoints for uploads, metadata, processing
- **State management**: Handling video metadata, upload progress, processing status
- **Routing & navigation**: Gallery view, upload interface, split mode
- **Form handling**: File uploads, FPS selection, split parameters

### Modern UI/UX Design
The "sleek modern design" requirement tests:
- **Visual design**: Professional, polished interface using UI frameworks (Tailwind, Material-UI, etc.)
- **Layout systems**: Masonry grid that adapts to different video aspect ratios
- **Responsive design**: Works across desktop screen sizes
- **Interactive controls**: Preview size slider, auto-play toggle, infinite scroll
- **Feedback mechanisms**: Progress indicators, loading states, success/error messages

### Video Processing & FFmpeg Integration
The video manipulation requirements test:
- **FFmpeg command construction**: Correct flags for FPS conversion, scene detection, splitting
- **Subprocess management**: Running FFmpeg from backend code
- **Error handling**: Dealing with corrupted videos, unsupported formats, FFmpeg failures
- **Output parsing**: Extracting metadata (duration, resolution, FPS) from FFmpeg output
- **File management**: Organizing uploaded videos, processed clips, thumbnails

### Performance & Scalability Considerations
Handling large media files tests:
- **Async processing**: Non-blocking video conversion and splitting
- **Background jobs**: Queue system for long-running FFmpeg operations
- **Lazy loading**: Infinite scroll implementation for large video collections
- **Thumbnail generation**: Efficient preview extraction without loading full videos
- **Memory management**: Streaming uploads, avoiding memory leaks with large files

### Data Persistence & Management
The metadata requirement tests:
- **Schema design**: Storing video metadata (filename, duration, resolution, FPS, split relationships)
- **Database choice**: SQLite for simplicity or JSON files for minimal setup
- **CRUD operations**: Create (upload), Read (gallery), Update (metadata), Delete (optional stretch)
- **Relationships**: Parent videos to split clips

### Scene Detection & Video Analysis
The splitting features test:
- **Scene detection algorithms**: Using FFmpeg's scene filter with appropriate thresholds
- **Fixed interval math**: Calculating split points based on frame count and FPS
- **Preview generation**: Showing split points before confirming
- **Clip extraction**: Precise frame-accurate cutting

### Frontend State & Interactivity
The gallery and controls test:
- **Infinite scroll**: Fetching and rendering batches of videos as user scrolls
- **Masonry layout**: Grid library (Masonry.js, CSS Grid) handling variable aspect ratios
- **Auto-play management**: Coordinating playback of multiple videos simultaneously
- **Slider controls**: Dynamic thumbnail size adjustment
- **Modal/detail views**: Entering split mode for individual videos

## Why This Use Case?

This task was chosen because it tests **full-stack development with media processing** rather than pure business logic:

1. **Real-world video workflows** - Mirrors actual ML dataset curation tasks
2. **UI/UX focus** - Sleek design is explicitly required, not just functional
3. **Video processing complexity** - FFmpeg integration, scene detection, format conversion
4. **Performance challenges** - Large files, multiple simultaneous videos, background processing
5. **Modern web stack** - Tests current frontend and backend technologies

An agent that handles this well demonstrates:

- **Full-stack proficiency**: Frontend, backend, and video processing integration
- **Design sensibility**: Creating polished, modern UIs (not just functional forms)
- **Media handling expertise**: Working with video files, codecs, containers, FFmpeg
- **Performance awareness**: Async processing, lazy loading, background jobs
- **UX thinking**: Progress feedback, smooth interactions despite heavy operations

This is fundamentally different from other use cases:
- **vs. Text Playground**: Video processing vs. text generation
- **vs. Image Generation**: Full application vs. ML pipeline focus
- **vs. Collaborative Editor**: Media management vs. real-time text sync
- **vs. Puzzle Game**: Professional tool vs. creative game

## Evaluation Focus

When reviewing implementations, pay attention to:

### UI/UX Quality
- Is the design modern and professional (not just functional)?
- Does the masonry layout adapt well to different aspect ratios?
- Are controls (slider, auto-play, infinite scroll) smooth and intuitive?
- Is feedback clear during uploads and processing?
- Does the app feel polished or rough?

### Video Processing Correctness
- Does FPS conversion work correctly without quality loss?
- Does scene detection produce meaningful splits?
- Does fixed frame splitting calculate correctly?
- Are generated clips accurate (no dropped frames or misalignment)?
- Is FFmpeg error handling robust?

### Functionality Completeness
- Do all core features work (upload, gallery, conversion, splitting)?
- Can videos be uploaded and processed successfully?
- Does the gallery display all videos with correct metadata?
- Do both splitting modes work reliably?
- Are previews generated correctly?

### Performance & Responsiveness
- Is video processing non-blocking (async or background jobs)?
- Does infinite scroll load smoothly?
- Can the app handle large video files (>1GB)?
- Are thumbnails generated efficiently?
- Does auto-play work without performance degradation?

### Code Quality
- Clean separation between frontend, backend, and video processing?
- Modular architecture for video operations?
- Proper error handling for file operations and FFmpeg?
- Type safety (TypeScript or Python type hints)?
- Well-commented FFmpeg commands and complex logic?

### Architecture Decisions
- Was an appropriate tech stack chosen and justified?
- Is the backend API well-designed?
- Is state management handled cleanly on frontend?
- Are files organized logically (uploads/, processed/, thumbnails/)?
- Is the database schema appropriate?

### Testing
- Are upload and processing workflows tested?
- Are FFmpeg integrations tested (or at least error cases)?
- Are frontend interactions tested?
- Do tests cover edge cases (large files, invalid formats)?

### Documentation
- Can someone install dependencies (including FFmpeg) and run the app?
- Are FFmpeg installation instructions clear?
- Is the architecture explained?
- Are setup steps complete and accurate?

## Technical Constraints

- **Stack**: Open choice - JavaScript/TypeScript or Python - must justify in README
- **Video Processing**: FFmpeg required (via subprocess or wrapper library)
- **Storage**: Local filesystem + SQLite or JSON for metadata
- **UI Framework**: Modern frontend framework (React, Vue, Svelte, or similar)
- **Core Features**: All must work (upload, gallery, conversion, splitting)
- **Scene Detection**: FFmpeg scene filter (not custom algorithms)
- **No Authentication**: Single-user local application

## Starting Point

The `_base` folder contains:
- Complete task specification in `prompt.md`
- Basic `package.json` for Node.js projects (if choosing JS/TS)
- Basic `pyproject.toml` for Python projects (if choosing Python)
- `.gitignore` for common artifacts and video files
- No implementation code (agent builds from scratch)
- No prescribed frontend framework (agent chooses and justifies)

This minimal scaffolding allows the agent to design the full architecture while providing standard project structure.

Copy `_base` to your test folder and let your agent work from the `prompt.md` specification.
