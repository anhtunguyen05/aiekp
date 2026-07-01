# Implementation Plan: Phase 7 - Reasoning Engine

## Phase 7.1: Workspace Setup & Domain Modeling
- [ ] Create `packages/reasoning-engine` directory and initialize `pyproject.toml`.
- [ ] Define the Domain Models (`ReasoningState`, `ReasoningRequest`, `ReasoningResult`).
- [ ] Define the Inbound/Outbound Ports (`IReasoningService`, `IContextFetcher`, `ILLMGenerator`).

## Phase 7.2: Implement Adapters
- [ ] Implement `ContextEngineHttpAdapter`: HTTP client that talks to `POST /context/retrieve`.
- [ ] Implement `LangChainLLMAdapter`: Wrapper around `ChatOpenAI` or `ChatAnthropic` to provide text generation.

## Phase 7.3: LangGraph Orchestration
- [ ] Create the LangGraph State definition using `TypedDict` or `Pydantic`.
- [ ] Implement Graph Nodes:
  - `analyze_node`: Parses query.
  - `fetch_context_node`: Uses `IContextFetcher`.
  - `evaluate_context_node`: Conditional edge logic (Sufficient vs Insufficient context).
  - `synthesize_node`: Uses `ILLMGenerator` to write the final response.
- [ ] Compile the graph into `ReasoningOrchestrator` inside `ReasoningService`.

## Phase 7.4: API Integration
- [ ] Add `reasoning-engine` to the `apps/api/pyproject.toml` workspace dependencies.
- [ ] Create `apps/api/src/routers/reason.py` with `POST /reason` endpoint.
- [ ] Setup Dependency Injection in `apps/api/src/dependencies.py` to instantiate `ReasoningService`.

## Phase 7.5: Testing & Verification
- [ ] Write unit tests for the adapters.
- [ ] Write a mock test for the LangGraph flow to ensure conditional routing works without hitting a real LLM.
- [ ] End-to-end integration test (Ingest -> Context -> Reasoning).
