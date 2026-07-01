# Phase 6: Context Intelligence Engine Specification

## 1. Executive Summary
The Context Intelligence Engine acts as the critical bridge between raw user prompts and the underlying Knowledge Graph. Its primary purpose is to **understand user intent**, formulate search strategies, and retrieve the precise architectural context (evidence) required to answer complex questions about the codebase. Without this engine, the LLM would lack the necessary grounded context to provide accurate answers.

## 2. Architecture Overview
Following the guidelines in `tech-stack.md`, this engine will be built using **Hexagonal Architecture (Ports and Adapters)**. This decoupled approach ensures that our core domain logic for context retrieval is entirely independent of external frameworks (FastAPI) or specific LLM implementations (OpenAI, Claude, etc.).

### Hexagonal Layers:
1. **Domain (Core)**: Entities representing Intent, QueryStrategy, and EvidencePayload.
2. **Ports (Interfaces)**:
   - *Inbound (Driving)*: `IContextService` (How external engines ask for context).
   - *Outbound (Driven)*: `IKnowledgeEngineClient` (How we fetch data from Phase 5 API), `IIntentAnalyzer` (How we parse raw strings into structured intents).
3. **Adapters (Implementations)**:
   - *Driving Adapters*: FastAPI router exposing the context service.
   - *Driven Adapters*: `HttpKnowledgeEngineAdapter` (calls the FastAPI backend), `LLMIntentAdapter` (calls the LLM to parse intent).

## 3. Core Components

### 3.1. Intent Analyzer (`IIntentAnalyzer`)
**Responsibility**: Converts natural language ("Where is the auth logic?") into a structured `RetrievalIntent`.
- Detects the *target entity type* (e.g., class, function, concept).
- Extracts *keywords* for Semantic Search.
- Determines the required *graph depth* (e.g., "Do we need the callers of this method?").

### 3.2. Knowledge Engine Client (`IKnowledgeEngineClient`)
**Responsibility**: Interacts with the API built in Phase 5.
- Executes `POST /search` to find entry points in Qdrant.
- Executes `GET /graph/nodes/{id}` to expand context via Neo4j relationships.

### 3.3. Context Orchestrator (`ContextService`)
**Responsibility**: The central Use Case interactor.
1. Receives raw query.
2. Asks `IntentAnalyzer` for the `RetrievalIntent`.
3. Loops through `KnowledgeEngineClient` to fetch nodes.
4. If a fetched node is highly relevant, fetches its dependencies (1-2 hops).
5. Assembles everything into an `EvidencePayload`.

## 4. Data Models

```python
from pydantic import BaseModel
from typing import List, Optional

class RetrievalIntent(BaseModel):
    query: str
    target_types: List[str]  # e.g., ["class", "method"]
    semantic_keywords: List[str]
    graph_expansion_depth: int = 1

class EvidenceNode(BaseModel):
    id: str
    name: str
    content: str
    type: str

class EvidencePayload(BaseModel):
    original_query: str
    intent: RetrievalIntent
    nodes: List[EvidenceNode]
    summary: str
```

## 5. Integration Points
- **Inbound**: Will expose a `POST /api/v1/context/retrieve` endpoint that the Reasoning Engine (Phase 7) will call.
- **Outbound**: 
  - Makes HTTP calls to `localhost:8000/api/v1/search` and `localhost:8000/api/v1/graph`.
  - Makes API calls to an LLM provider (via `llm-adapter` package) to perform lightweight intent classification.

## 6. Design Decisions
- **Why Hexagonal Architecture?** We may want to swap the `LLMIntentAdapter` from OpenAI to a local small model (e.g., Llama 3) for speed and cost. Hexagonal ensures the `ContextService` doesn't need to change.
- **Why separate from Phase 5 API?** Phase 5 is a pure data layer (CRUD over Graph/Vector). The Context Engine is an *application logic* layer. Keeping them separated prevents the Knowledge Engine from becoming bloated with prompt engineering and LLM specifics.

## 7. Future Enhancements & Scalability (Advanced RAG)
While the initial MVP implementation uses a basic `KeywordIntentAdapter`, the Hexagonal Architecture allows seamless integration of advanced Context/RAG techniques in the future without modifying core domain logic:
- **LLM Intent Adapter**: Replace static keyword extraction with a dedicated LLM call to classify intent dynamically based on chat history.
- **Query Transformation (Multi-Query)**: Rewrite the user's query into multiple sub-queries to maximize retrieval coverage across Qdrant.
- **Cross-Encoder Re-ranking**: Add a re-ranking adapter after semantic search to score and filter nodes more accurately before performing Graph Traversal.
- **Iterative Context Expansion (Agentic RAG)**: Allow the `ContextService` to fetch nodes, analyze if they are sufficient, and trigger secondary searches autonomously if context is missing.
- **Microservices Deployment**: The Context Engine can be fully decoupled into its own independent container or gRPC service for horizontal scaling.
