# Phase 11: Multi-Agent Swarm & Polyglot Expansion - Implementation Plan

## Phase 1: Context Engine Plugins (TS/JS)

### 1.1 Typescript Parser Plugin
- Create `plugins/typescript_parser/pyproject.toml` with dependencies: `tree-sitter-typescript`, `tree-sitter-javascript`, `parser-core`.
- Implement `TypescriptParser` extending `LanguageParser`.
- Add `register(factory)` function mapping `.ts`, `.tsx`, `.js`, `.jsx` to this parser.

### 1.2 Typescript Extractor Plugin
- Create `plugins/typescript_extractor/pyproject.toml` with dependencies: `metadata-extractor`, `tree-sitter-typescript`.
- Implement `TypescriptExtractor` extending `LanguageExtractor`.
- Map Tree-sitter AST nodes (classes, interfaces, methods, functions) to AIEKP Domain Nodes.
- Add `register(factory)` function.

### 1.3 Workspace Integration
- Add both plugins to root `pyproject.toml` workspace members.
- Ensure `apps/api` and `apps/cli` dependencies include these plugins so they are loaded during `aiekp ingest`.

## Phase 2: LangGraph Multi-Agent Architecture

### 2.1 Graph State & Nodes Definition
- Modify `ReasoningOrchestrator` in `packages/reasoning-engine/src/reasoning_engine/services/orchestrator.py`.
- Define `GraphState` containing `messages` (list of Langchain BaseMessage), `context_str`, `next` (for routing).
- Define Prompts for Sub-agents:
  - `ArchitectNode`: Focuses on architecture, patterns, dependencies.
  - `QANode`: Focuses on bugs, tests, edge cases.
  - `SecurityNode`: Focuses on vulnerabilities.
- Define `SupervisorNode`: Uses LLM with function calling to decide which sub-agent should act next, or if it should synthesize the `FINISH` output.

### 2.2 Streaming Implementation
- Modify `ReasoningService.stream_process_query()` to call `astream_events` on the new LangGraph.
- Stream intermediate logs (e.g., "Supervisor decided to call QA Agent") and the final answer to the client UI.

## Phase 3: Testing & Polish
- Run unit tests on the new TS plugins.
- Test E2E with CLI `aiekp ingest` on a JS/TS project.
- Test E2E multi-agent reasoning flow via VS Code extension.
