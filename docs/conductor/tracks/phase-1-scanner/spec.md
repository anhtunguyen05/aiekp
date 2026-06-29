# Phase 1: Repository Scanner Engine Specification

## 1. Goal
Implement the **Repository Scanner**, the foundational data ingestion component of the Knowledge Engine. This engine is responsible for crawling local source code directories, computing SHA-256 hashes of whitelisted files, and yielding a stream of delta events (ADDED, MODIFIED, DELETED) to power incremental AST parsing in future phases.

## 2. Prerequisites
* Phase 0 Infrastructure (PostgreSQL) is up and running.
* Prisma ORM and Pydantic are configured in the workspace.

## 3. Technical Requirements

### 3.1 Architectural Decisions
*   **Data Source:** Local file system paths only.
*   **Change Detection:** Content-based SHA-256 hashing.
*   **Target Scope:** Whitelisted text extensions (e.g., `.py`, `.js`, `.ts`, `.md`) to prevent binary/junk ingestion.
*   **Incremental State:** File hashes are stored in PostgreSQL using the Prisma `FileMetadata` model.

### 3.2 Prisma Schema Updates (`apps/api/prisma/schema.prisma`)
Create a new `FileMetadata` model:
*   `id`: String @id @default(uuid())
*   `repo_path`: String
*   `file_path`: String
*   `file_hash`: String
*   `last_scanned_at`: DateTime @default(now())
*   Constraints: `@@unique([repo_path, file_path])`

### 3.3 Knowledge Engine Package (`packages/knowledge_engine`)
*   Initialize as a new `uv` library.
*   Implement `RepositoryScanner` class.
*   **Core Method:** `scan_directory(repo_path: str) -> AsyncGenerator[FileScanEvent, None]`
    *   Recursively traverses the directory (ignoring `.git`, `node_modules`, `venv`, etc.).
    *   Yields `FileScanEvent` indicating the change status (ADDED, MODIFIED, UNCHANGED, DELETED).

### 3.4 API Integration (`apps/api/src/routers/scanner.py`)
*   Create a `POST /scanner/scan` endpoint.
*   Payload: `{"repo_path": "/absolute/path/to/repo"}`.
*   Logic:
    *   Iterate through the `RepositoryScanner` events.
    *   Update the `FileMetadata` database table accordingly (UPSERT for added/modified, DELETE for deleted).
    *   Return a summary payload (e.g., `{"added": 5, "modified": 2, "deleted": 0}`).

## 4. Definition of Done (DoD)
- [ ] `FileMetadata` schema is generated and pushed to PostgreSQL.
- [ ] `knowledge_engine` is importable as a local package.
- [ ] The `RepositoryScanner` successfully yields correct `FileScanEvent` instances on a test directory.
- [ ] The `/scanner/scan` endpoint updates PostgreSQL and returns an accurate summary of changes.
