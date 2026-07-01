# Phase 10 VSCode Extension - Implementation Plan

## Phase 10.1: Project Setup
- [ ] Initialize `apps/vscode-extension` using standard VSCode extension scaffolding (TypeScript).
- [ ] Update Monorepo config (`uv.lock` or standard workspace configuration if applicable) to ignore or accommodate the npm/node package.
- [ ] Configure `esbuild` or `webpack` for fast compilation.
- [ ] Add basic configuration contributions in `package.json` (`aiekp.apiUrl`, `aiekp.apiKey`).

## Phase 10.2: Webview Panel Infrastructure
- [ ] Create a `ChatPanel` class to manage the Webview lifecycle.
- [ ] Register a command `aiekp.startChat` to open the panel.
- [ ] Design the basic HTML/CSS structure for the chat interface.
- [ ] Implement two-way message passing between the Extension Host and the Webview (using `postMessage`).

## Phase 10.3: Context Extraction
- [ ] Create a `ContextManager` utility to get the active editor's document text, language ID, and selection.
- [ ] Register a command `aiekp.askAboutSelection` to trigger the chat with pre-filled context.

## Phase 10.4: API Integration & Streaming
- [ ] Implement the API client in the Extension Host to communicate with `http://localhost:8000/reason/stream`.
- [ ] Handle Server-Sent Events (SSE) stream.
- [ ] Stream tokens back to the Webview via `postMessage` chunks.
- [ ] Add markdown rendering library (like `marked`) inside the Webview to parse and display the streamed response cleanly.

## Phase 10.5: Testing and Polish
- [ ] Verify error handling (API down, invalid API key).
- [ ] Test the user experience for responsiveness.
- [ ] Document how to build and install the `.vsix` file locally.
