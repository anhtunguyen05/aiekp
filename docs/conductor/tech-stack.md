# Tech Stack & Architecture

## High Level Architecture

1. **Client** (CLI / API / VSCode)
2. **Application Layer**
3. **Context Intelligence Engine**
4. **Reasoning Engine** (LangGraph)
5. **Knowledge Engine**
6. **Storage Layer**
7. **Repository**

## Architecture Style
The project uses multiple architecture styles tailored to specific engine requirements:

* **Knowledge Engine**: Clean Architecture, DDD Lite
* **Context Engine**: Hexagonal Architecture
* **Reasoning Engine**: LangGraph Workflow, State Machine
* **Parser**: Plugin Architecture, Strategy Pattern
* **Storage**: Repository Pattern
* **LLM**: Adapter Pattern

## Technology Stack

* **Language**: Python
* **Package Manager**: uv
* **Backend**: FastAPI
* **Workflow**: LangGraph
* **Knowledge Graph**: Neo4j
* **Metadata Database**: PostgreSQL
* **Vector Database**: Qdrant
* **Cache**: Redis
* **Storage**: MinIO
* **Parser**: Tree-sitter + language specific parsers
* **Deployment**: Docker Compose (Future: Kubernetes)

## Monorepo Structure

```
apps/
  api/
  cli/
  dashboard/
  vscode/

packages/
  knowledge-engine/
  context-engine/
  reasoning-engine/
  graph-engine/
  parser-core/
  scanner/
  llm-adapter/
  storage/
  shared/

plugins/
  java/
  python/
  typescript/
  flutter/

infrastructure/
  docker/

scripts/
docs/
tests/
```
