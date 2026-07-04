# AIEKP (AI Engineering Knowledge Platform)

AIEKP is an AI-powered engineering knowledge platform that transforms your codebase into a navigable, reasoning-capable Knowledge Graph. With AIEKP, you can ask architectural questions, perform code queries, and seamlessly trace evidence through your code repository—right from your terminal or VSCode editor.

## Features

- **AST Code Parsing:** Parses Python projects into a structural Knowledge Graph.
- **Neo4j Backend:** Uses Neo4j to store evidence, classes, methods, and their relationships.
- **Reasoning Engine:** Context-aware LLM answers driven by precise graph queries to eliminate hallucination.
- **Command Line Interface:** Manage Docker, API server, and ingestion tasks from the CLI.
- **VSCode Extension:** Integrated AI chat and codebase reasoning directly inside your editor.

## Quick Start (Alpha Release)

### 1. Installation

AIEKP CLI is published on PyPI and can be installed via `pip`:

```bash
pip install aiekp-cli
```

### 2. Configuration (Cloud DB & LLM Keys)

AIEKP can connect to Cloud Databases (e.g., Neo4j Aura, Qdrant Cloud) and requires an LLM API key (OpenAI or Gemini). Set them globally using the CLI:

```bash
# Set LLM API Key
aiekp config set GEMINI_API_KEY "your-api-key"

# (Optional) Set Cloud Database URI if you don't want to run Docker locally
aiekp config set NEO4J_URI "neo4j+s://xxxxxx.databases.neo4j.io"
aiekp config set NEO4J_PASSWORD "your-neo4j-password"
```

To view your current configuration:
```bash
aiekp config list
```

### 3. Local Infrastructure (Optional)

If you prefer to run the databases locally instead of using a Cloud DB, ensure you have [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and run:

```bash
aiekp init
```
*This will start a local Neo4j container on port 7687.*

### 4. Start the API Server

The Reasoning Engine and Context Engine are exposed via a FastAPI server. Start the backend with:

```bash
uv run --directory apps/cli aiekp server start
```

*The server will be available at `http://127.0.0.1:8000`.*

### 5. Install the VSCode Extension

For the best experience, install the VSCode extension. 

1. Locate the packaged VSIX file at `apps/vscode-extension/aiekp-1.0.0.vsix`.
2. Open VSCode and go to the **Extensions** view (`Ctrl+Shift+X`).
3. Click the `...` menu in the top right and select **Install from VSIX...**.
4. Choose `aiekp-1.0.0.vsix`.
5. Open the AIEKP Chat panel from the activity bar!

## Architecture

This monorepo contains:
- `apps/cli/`: The AIEKP management CLI.
- `apps/api/`: The FastAPI backend serving the Reasoning and Context engines.
- `apps/vscode-extension/`: The official VSCode extension.
- `packages/context-engine/`: Retrieves relevant subgraph data based on query intents.
- `packages/reasoning-engine/`: Coordinates LLM generation using the extracted context.
- `plugins/python_parser/`: Extracts AST nodes and relationships from Python code.

---
*Built for the Phase 10.5 Release.*
