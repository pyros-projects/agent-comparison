# Use Case 11 – Video Dataset Curator (FrameCraft)

## 1. Goal

Build a local web application for curating video datasets for training video generation AI models. The app provides a sleek masonry gallery for browsing uploaded videos, supports video upload with FPS conversion, and enables splitting videos into clips via scene detection or fixed frame intervals. This tests full-stack web development, video processing, modern UI design, and handling large media assets efficiently.

## 2. Context & Constraints

- **Stack/Language**: Your choice - JavaScript/TypeScript (Node.js + React/Vue) or Python (FastAPI/Flask + modern frontend). Justify your stack choice in README.
- **Video Processing**: Use FFmpeg (via subprocess or library wrapper) for conversion and scene detection
- **Storage**: Local filesystem for videos and metadata (SQLite or JSON for metadata)
- **Time estimate**: 4-6 hours for a capable full-stack developer
- **Out of scope**: Cloud deployment, user authentication, multi-user support, advanced editing features

## 3. Requirements

### 3.1 Core (Must Have)

- **Video Gallery View**
  - Masonry layout displaying all uploaded videos
  - Infinite scroll pagination (load more as user scrolls)
  - Preview size slider (small/medium/large thumbnails)
  - Auto-play toggle (all videos play preview loops simultaneously)
  - Video metadata displayed (filename, duration, resolution, FPS)

- **Video Upload System**
  - Drag-and-drop or file picker upload interface
  - FPS target selection (e.g., 24, 30, 60 fps)
  - Automatic video conversion to target FPS using FFmpeg
  - Progress indicator during upload and processing
  - Metadata extraction and persistence (duration, resolution, original FPS)

- **Video Splitting**
  - Click on video to enter split mode
  - Split via scene detection (using FFmpeg scene filter)
  - Split via fixed frame intervals (user specifies frame count per clip)
  - Preview split points before confirming
  - Generate and save individual clip files
  - Update gallery with new clips

- **Technical Requirements**
  - Responsive, modern UI design (clean, professional aesthetic)
  - Efficient video thumbnail generation
  - Handle videos up to several GB in size
  - Non-blocking video processing (background jobs or async)

### 3.2 Stretch (Nice to Have)

- Batch upload multiple videos at once
- Search/filter videos by metadata (duration, resolution, FPS)
- Tag system for organizing videos
- Export video list with metadata to CSV/JSON
- Clip trimming (select exact in/out points)
- Video playback controls in gallery (play/pause individual videos)
- Delete videos from dataset
- Dark mode toggle

## 4. Quality Expectations

- **Architecture**: Clean separation between frontend, backend API, and video processing logic. Modular design for easy extension.
- **Testing**: Integration tests for upload and processing workflows. Frontend tests for key interactions.
- **Code Quality**: Type hints/TypeScript for type safety. Error handling for file operations and FFmpeg failures. Proper async handling.
- **UX/UI**: Sleek, modern design using a UI framework (Tailwind, Material-UI, or similar). Smooth animations. Responsive layout. Clear feedback during processing.
- **Documentation**: README with setup instructions, architecture overview, dependencies (FFmpeg installation), usage guide. Code comments for complex video processing logic.

## 5. Process

- **Stack Decision**: Choose and justify your tech stack based on video processing needs, frontend capabilities, and development speed.
- **FFmpeg Integration**: Research FFmpeg scene detection parameters and FPS conversion commands before implementing.
- **UI Design**: Sketch out or reference masonry gallery patterns and modern video gallery UIs.
- **Performance**: Consider thumbnail generation strategy, lazy loading, and background processing early.

## 6. Deliverables

- [ ] Working web application with all core features functional
- [ ] Video upload with FPS conversion pipeline
- [ ] Masonry gallery with infinite scroll and auto-play
- [ ] Video splitting (scene detection + fixed frame modes)
- [ ] Test suite covering upload and splitting workflows
- [ ] README with setup, FFmpeg installation, and usage instructions
- [ ] Clean, modular source code with clear structure

## 7. Success Criteria

- **Functionality**: All core features work reliably - upload, convert, display, split, and gallery browsing all function correctly
- **UX Quality**: UI is modern, responsive, and polished. Video processing provides clear feedback. Gallery is smooth and performant.
- **Video Processing**: FFmpeg integration is robust. Scene detection produces meaningful splits. FPS conversion maintains quality.
- **Code Quality**: Well-structured, maintainable code with proper error handling and async patterns
- **Documentation**: Another developer can install dependencies, set up FFmpeg, and run the app successfully by following the README
