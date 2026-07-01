# Track: Phase 10 VSCode Extension

## 1. Goal
Deliver the ultimate user experience by integrating the AIEKP API directly into the developer's IDE (Visual Studio Code). Provide a chat interface and context-aware capabilities allowing developers to query the Knowledge Graph and receive real-time streaming AI responses without leaving their editor.

## 2. Context & Rationale
Developers spend most of their time in the IDE. A command-line tool or a web dashboard forces context switching. By bringing the AIEKP Reasoning Engine into VSCode as an extension, we minimize friction. The extension will read the currently active file/selection as "context" and leverage the streaming endpoint (`/reason/stream`) to provide fast, intelligent, and context-aware answers.

## 3. Scope & Requirements

### 3.1 Extension Core
- Setup a new package `apps/vscode-extension` using standard VSCode extension scaffolding (TypeScript).
- Establish configuration settings in `package.json` for:
  - `aiekp.apiUrl`: The URL of the AIEKP backend (default: `http://localhost:8000`).
  - `aiekp.apiKey`: The API key for authentication.

### 3.2 Chat Interface (Webview)
- Implement a custom Webview panel `AIEKP Chat` using HTML/CSS/JS.
- The chat interface should support Markdown rendering (for code blocks, lists).
- It must handle incoming streamed chunks to display Server-Sent Events (SSE) token-by-token from the backend seamlessly.

### 3.3 Context Injection
- Read the currently active text editor's content, file path, and language.
- Provide a command (e.g., "AIEKP: Ask about current file") to automatically bundle this context and send it as part of the query payload.
- Allow users to select a block of code and ask questions about that specific block.

### 3.4 Integration Points
- Communicate with `POST /reason/stream` endpoint with headers: `Content-Type: application/json` and `X-API-Key`.
- Support gracefully handling connectivity errors or invalid API keys.

## 4. Definition of Done
- Extension compiles and can be launched via F5 in VSCode (Extension Development Host).
- Settings can be configured in VSCode preferences.
- User can open the AIEKP Webview panel.
- User can send a message, and the extension successfully streams the AI's response from the backend.
- The extension automatically includes the active file context in queries.
