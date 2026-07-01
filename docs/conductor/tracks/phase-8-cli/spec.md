# Phase 8: Command Line Interface (CLI) Specification

## 1. Executive Summary
The Command Line Interface (CLI) serves as the primary developer-facing tool for interacting with the AIEKP locally. It abstracts the complexity of the underlying `uv` workspace and REST API, providing a seamless way to scan repositories, query architectural contexts, and execute reasoning tasks directly from the terminal.

## 2. Architecture Overview
The CLI will be a standalone Python application under the monorepo workspace (`apps/cli`). It will act as a thin client that communicates with the `apps/api` REST endpoints. 

### Key Technologies:
- **Typer**: For building the command-line interface with strong typing and subcommands.
- **Rich**: For beautiful terminal output, including formatting LLM markdown responses, spinners for long-running API calls, and tables for data presentation.
- **HTTPX**: For async communication with the REST API.
- **Python Dotenv**: To load environment configurations (API URL, keys).

## 3. Core Commands

1. **`aiekp ingest <path>`**
   - **Purpose**: Triggers the ingestion pipeline for a specific local directory.
   - **Flow**: Sends a `POST /ingest` request to the API with the absolute path of the target directory.
   - **Output**: A spinner while ingesting, followed by a summary table of files scanned, AST nodes parsed, and metadata extracted.

2. **`aiekp context <query>`**
   - **Purpose**: Fetches relevant context from the Knowledge Graph.
   - **Flow**: Sends a `POST /context/retrieve` request.
   - **Output**: Renders the returned `EvidencePayload` in a structured format (showing relationships, summaries, and file paths).

3. **`aiekp reason <query>`**
   - **Purpose**: End-to-end question answering and code reasoning.
   - **Flow**: Sends a `POST /reason` request.
   - **Output**: Streams or renders the final markdown answer in the terminal using `Rich`'s Markdown component, along with confidence scores and source citations.

4. **`aiekp status`**
   - **Purpose**: Health check.
   - **Flow**: Hits the API health check endpoint.
   - **Output**: Displays the status of the API, Neo4j, and Qdrant connections.

## 4. Integration Points
- **REST API**: Connects to `http://localhost:8000` (default) or the URL defined in the `.env` file.
- **Local File System**: `ingest` command resolves relative paths to absolute paths before sending them to the API.

## 5. Error Handling & DX
- **Connection Errors**: Display friendly messages if the API server is not running (e.g., "API server not reachable. Did you run `uv run uvicorn src.main:app`?").
- **Timeouts**: Generous timeouts for `reason` and `ingest` commands, accompanied by informative loading spinners.
- **Help Menus**: Typer automatically generates `--help` documentation for all commands.

## 6. Future Enhancements
- Support for streaming LLM responses directly to the terminal for faster perceived performance.
- Interactive mode (`aiekp chat`) for continuous, session-based reasoning.
