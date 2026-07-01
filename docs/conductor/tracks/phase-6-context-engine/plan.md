# Phase 6: Implementation Plan

## 1. Project Setup
- `[ ]` Create directory `packages/context-engine/src/context_engine`.
- `[ ]` Initialize `pyproject.toml` and configure dependencies (`pydantic`, `httpx`, `aiekp-shared`).
- `[ ]` Define the Hexagonal directory structure (`domain/`, `ports/`, `adapters/`, `services/`).

## 2. Domain & Ports
- `[ ]` Define domain models (`RetrievalIntent`, `EvidencePayload`) in `domain/models.py`.
- `[ ]` Define `IIntentAnalyzer` and `IKnowledgeEngineClient` interfaces in `ports/outbound.py`.
- `[ ]` Define `IContextService` interface in `ports/inbound.py`.

## 3. Adapters Implementation
- `[ ]` Implement `HttpKnowledgeEngineAdapter` to fetch data from Phase 5 API using `httpx`.
- `[ ]` Implement a mock or simple rule-based `KeywordIntentAdapter` first (before full LLM integration) to parse basic queries.

## 4. Core Service Orchestration
- `[ ]` Implement `ContextService` that wires the IntentAnalyzer and KnowledgeEngineClient together to build the `EvidencePayload`.

## 5. API Exposure (Optional / Testing)
- `[ ]` Add a FastAPI router in `apps/api/src/routers/context.py` or create a standalone microservice to test the Context Engine.
- `[ ]` Inject the dependencies (Adapters -> Service -> Router).

## 6. Verification
- `[ ]` Write unit tests for `ContextService` using mock adapters.
- `[ ]` Run end-to-end test querying "Where is the parser logic?" and verifying the payload contains the correct AST nodes from Neo4j.
