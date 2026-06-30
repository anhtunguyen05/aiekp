# Phase 5: Knowledge Engine API

## Objective
Wrap Phases 1-4 into a cohesive, decoupled service with a clean interface for querying and updating the Knowledge Graph. This phase transforms the underlying workspace libraries (`scanner`, `parser`, `metadata_extractor`, `knowledge_graph`) into a usable RESTful API (FastAPI).

## Scope
- Expand `apps/api` to orchestrate the entire ingestion pipeline.
- Implement an ingestion endpoint (`POST /api/v1/ingest/repository`) that triggers the `ScannerEngine`, parses files, extracts metadata, and ingests them into Neo4j and Qdrant.
- Implement structural querying endpoints (`GET /api/v1/graph/nodes/{node_id}`, `GET /api/v1/graph/dependencies/{node_id}`).
- Implement a semantic search endpoint (`GET /api/v1/search`) to query Qdrant and return matching nodes.
- Implement dependency injection in FastAPI to manage singletons for Neo4j, Qdrant, and the Embedder.
- Establish robust error handling and API validation (Pydantic models for requests and responses).

## Technical Requirements
- **Framework**: FastAPI
- **Dependencies**: `scanner`, `parser_core`, `python_parser`, `metadata_extractor`, `python_extractor`, `knowledge_graph` (all local workspace packages).
- **Configuration**: Setup environment variables for DB credentials, hostnames, and paths.
- **Testing**: Add API endpoint testing using `FastAPI TestClient`.

## Out of Scope
- Authentication and Authorization (to be added in a future security phase).
- Long-running asynchronous tasks with Celery/RabbitMQ (ingestion will remain synchronous for the MVP, though structured to allow future async task offloading).
- Context Intelligence Engine (Phase 6).

## Definition of Done
- FastAPI application exposes endpoints for ingestion, graph queries, and semantic search.
- Swagger UI (`/docs`) accurately reflects the API schema with Pydantic models.
- Calling the `/ingest` endpoint on a target repository successfully populates Neo4j and Qdrant.
- Calling the semantic search endpoint returns correct nodes from the vector database.
- Integration tests for the new API endpoints pass successfully.
