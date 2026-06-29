# Phase 0: Project Foundation Specification

## 1. Goal
Establish the monorepo structure, initialize the workspace, configure the database infrastructure (Docker Compose), and define the core interfaces so that independent engines can be developed in subsequent phases without stepping on each other.

## 2. Prerequisites
*   Context-Driven Documentation must be complete (You are reading it).
*   Python environment tools (like `uv`) must be decided.

## 3. Technical Requirements

### 3.1 Workspace Setup
*   Initialize a Python monorepo using `uv`.
*   Create the standard directory structure (`apps/`, `packages/`, `infrastructure/`).

### 3.2 Infrastructure Configuration
*   Create a `docker-compose.yml` that provisions:
    *   **PostgreSQL**: For metadata storage.
    *   **Neo4j**: For the Knowledge Graph.
    *   **Qdrant**: For Vector embeddings.
    *   **Redis**: For caching.
    *   **MinIO**: For file storage.
*   *Constraint*: Set reasonable memory limits so local development does not crash.

### 3.3 Core Definitions
*   Define the base interfaces (abstract classes) for `KnowledgeEngine`, `ContextEngine`, and `ReasoningEngine`.
*   Define the Domain Models (`Repository`, `ASTNode`, `KnowledgeNode`) in Python.

## 4. Definition of Done (DoD)
- [x] Running `docker compose up` starts all 5 databases without errors.
- [x] The `uv` workspace is valid and packages can be imported across the monorepo.
- [x] Core interface files are committed to the `packages/shared/` directory.
- [x] A FastAPI application (`apps/api`) is set up with a `/health` endpoint that successfully connects to all 5 databases.
