# Phase 10.5 MVP Polish, QA & Packaging - Implementation Plan

## Phase 10.5.1: Real-World Testing & Bug Fixing
- [ ] Parse a sample medium-sized repository using the CLI.
- [ ] Identify and fix any AST parser crashes or missing edge cases.
- [ ] Validate GraphQL response times for large graph queries.
- [ ] Tune LLM prompts to reduce hallucinations.

## Phase 10.5.2: CLI Packaging & Automation
- [ ] Implement `aiekp init` to spin up Neo4j via Docker SDK or subprocess calls to `docker run`.
- [ ] Ensure `.env` management is user-friendly (prompts user for API Key on first run).
- [ ] Finalize `pyproject.toml` metadata (author, description, entry points).
- [ ] Test installation in a clean Python virtual environment.

## Phase 10.5.3: VSCode Extension Polish
- [ ] Add branding assets (icon, banner) to the extension.
- [ ] Write the extension's specific `README.md` with usage GIFs.
- [ ] Ensure settings (`aiekp.apiKey`, `aiekp.apiUrl`) are properly validated.
- [ ] Run `vsce package` and test the `.vsix` installation.

## Phase 10.5.4: Documentation & Launch
- [ ] Rewrite the root repository `README.md` to focus on the end-user.
- [ ] Create a "Quick Start" video or GIF demonstrating the CLI and VSCode Extension.
- [ ] Finalize the MVP milestone on GitHub and prepare for v1.0.0 release.
