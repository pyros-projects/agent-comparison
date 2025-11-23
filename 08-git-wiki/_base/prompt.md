# Use Case 08 – Git-Based Wiki (WikiGit)

## 1. Goal
Build a wiki where every page is a markdown file stored in Git, accessible through a web interface. Leverages Git's version control for page history, diffs, and collaborative editing.

## 2. Context & Constraints
- **Stack/Language**: Your choice (Python/Node.js/etc.)
- **Storage**: Git repository (local, all pages as .md files)
- **Out of scope**: User authentication, rich media uploads, real-time collaboration
- **Time estimate**: Half to full day

## 3. Requirements

### 3.1 Core (Must Have)
- **Git storage**: All pages as markdown files in Git repo
- **Web interface**: Create, edit, view pages through browser
- **Version history**: View page history, show diffs between versions
- **Search**: Full-text search across all pages
- **Markdown rendering**: Display pages as formatted HTML
- **Git operations**: Each change commits to Git with author and message

### 3.2 Stretch (Nice to Have)
- Branch-based drafts
- Conflict resolution UI
- Recent changes feed
- Page linking and backlinks
- Visual timeline

## 4. Quality Expectations
- **Architecture**: Clean Git integration, proper commit messages
- **Testing**: Test core CRUD operations and Git interactions
- **UX/UI**: Intuitive interface for non-technical wiki users
- **Documentation**: README with setup and usage

## 6. Deliverables
- [ ] Web application with Git backend
- [ ] Page CRUD operations
- [ ] Version history with visual diffs
- [ ] Search functionality
- [ ] Tests for core features
- [ ] README with setup instructions

## 7. Success Criteria
- Can create, edit, and view wiki pages
- Every edit creates a proper Git commit
- Version history and diffs work correctly
- Search finds relevant pages
- Git repository structure is clean and logical
