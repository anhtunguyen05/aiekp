# AIEKP Reasoning Assistant

AIEKP (AI Engineering Knowledge Platform) Reasoning Assistant integrates the AIEKP Reasoning Engine directly into Visual Studio Code. It allows you to chat with your local AI assistant, which has deep context of your entire codebase via a Knowledge Graph (Neo4j) and Vector Database (Qdrant).

## Features

- **Context-Aware Chat**: Ask questions about your architecture, find bugs, or get explanations. The assistant fetches relevant context automatically.
- **Selection/Active File Context**: Highlight code or open a file, then use the command palette (`AIEKP: Ask About Selection/Active File`) to send it as context.
- **Streaming Responses**: Real-time streaming of AI responses.
- **Multi-Tenant Secure**: Integrates securely with your AIEKP backend via JWT tokens.

## Setup Instructions

1. Ensure the AIEKP backend is running locally or remotely.
2. Open your terminal and log in using the AIEKP CLI:
   ```bash
   aiekp auth login
   ```
3. Locate your token (typically printed on successful login or stored in `~/.aiekp/auth.json`).
4. In VSCode, go to **Settings** (`Ctrl+,` or `Cmd+,`).
5. Search for `aiekp`.
6. Set the **AIEKP: Api Url** to your backend URL (e.g., `http://127.0.0.1:8000`).
7. Paste your JWT token into the **AIEKP: Token** setting.

## Usage

- Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac) and type `AIEKP: Open Chat`.
- Alternatively, highlight a block of code, right-click, and select `AIEKP: Ask About Selection/Active File`.

## Requirements

- VSCode `^1.90.0`
- A running instance of the AIEKP backend (Phase 16+).
