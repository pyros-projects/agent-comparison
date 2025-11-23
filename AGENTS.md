# Repository Guidelines

Guide for contributing agent runs. Keep changes scoped to your run and avoid touching others.

## Project Structure
- Each challenge lives in `01-…` through `10-…`, containing `_base/` (prompt + starter), `coding_agents/`, `orchestration/`, and a use-case `README.md`.
- Create a new run by copying only `_base`, e.g., `cp -r 01-research-scraper/_base 01-research-scraper/coding_agents/my-agent`.
- Treat `_base/` as read-only. Place all code, assets, and notes inside your run folder. Shared docs and evaluation templates live in `docs/`.

## Build, Test & Development
- Fast path: `python setup-run.py` scaffolds a run and branch name.
- Python (uv backend): `uv sync` for deps, `uv run pytest` for tests, `uv run <entrypoint>` for apps/CLIs. Follow any scripts in `pyproject.toml`.
- Node/JS (package.json present): `npm install`, `npm test`, `npm run dev` or `npm run build` as indicated in the local README.
- Run commands from the specific agent/orchestration folder instead of the repo root to avoid polluting other runs.

## Coding Style & Naming
- Align with language norms: Python 4-space indents + type hints; JS/TS 2-space indents + ES modules.
- Use configured tooling when present (`ruff`, `black`, `eslint`, `prettier`, etc.) and format before committing.
- Naming: Python modules `snake_case.py`; React/Vue components `PascalCase`; utilities in `utils/` or `lib/`. Functions should be verb-first and intention-revealing.

## Testing Guidelines
- Common stacks: `pytest` for Python, `*.test.ts|js` for JS/TS. Mirror existing test layout (often `tests/` under your run).
- Add focused tests that map to acceptance criteria in `prompt.md`; prefer deterministic unit/integration tests over brittle snapshots.
- When fixing bugs, add a regression test alongside the fix.

## Commit & PR Practices
- Follow Conventional Commits seen in history (`feat`, `fix`, `chore`, `docs`, `test`, `refactor`) and scope to the use case, e.g., `feat(research-scraper): add graph view`.
- PRs should include a short summary, affected path, commands/tests run, and screenshots or GIFs for UI changes.
- Call out known gaps or follow-ups; link issues when applicable.

## Security & Config
- Never commit secrets or tokens. Use environment variables and, if needed, add a redacted `.env.example` inside your run folder.
- Prefer mocks/fakes for external calls in tests; ensure endpoints/keys are injected via config, not hardcoded.

## Agent-Specific Notes
- Keep dependencies local to your run; avoid repo-wide tooling changes unless the use-case README requires it.
- Do not modify sibling agent outputs when adding or reviewing your own implementation.
