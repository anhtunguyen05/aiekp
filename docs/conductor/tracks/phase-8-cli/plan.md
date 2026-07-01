# Phase 8: CLI Implementation Plan

## Prerequisites
- [x] Phase 7 (Reasoning Engine) is complete.
- [x] REST API endpoints (`/ingest`, `/context/retrieve`, `/reason`) are fully functional.

## Step 1: Package Scaffolding
- [ ] Create `apps/cli` directory.
- [ ] Initialize `pyproject.toml` using `uv init`.
- [ ] Add dependencies: `typer`, `rich`, `httpx`, `python-dotenv`.
- [ ] Add `apps/cli` to the workspace `pyproject.toml` members.

## Step 2: Base CLI Setup
- [ ] Create `src/aiekp_cli/main.py`.
- [ ] Initialize Typer app.
- [ ] Implement configuration loading (API URL).
- [ ] Add basic `status` command and verify connection to the REST API.

## Step 3: Command Implementation
- [ ] Implement `ingest` command with Rich spinner and error handling.
- [ ] Implement `context` command to render `EvidencePayload`.
- [ ] Implement `reason` command with Markdown rendering for the answer.

## Step 4: Polish & Integration
- [ ] Ensure proper error handling for unreachable API.
- [ ] Add entrypoint script in `pyproject.toml` so `uv run aiekp` works.
- [ ] Update root README with CLI usage instructions.
