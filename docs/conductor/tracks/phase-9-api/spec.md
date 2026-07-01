# Phase 9: REST/GraphQL API Specification

## 1. Executive Summary
While the AIEKP currently possesses a functional internal API, Phase 9 focuses on hardening this API for external consumption (e.g., VSCode Extension, Web Dashboard). This involves integrating GraphQL for complex graph queries, implementing streaming for LLM responses, and enforcing security to make the API robust, scalable, and production-ready.

## 2. Architecture Overview
- **Framework**: FastAPI (existing)
- **GraphQL Engine**: `Strawberry` (integrated into FastAPI) for flexible entity and relationship queries.
- **Streaming**: Server-Sent Events (SSE) or WebSockets for real-time reasoning feedback.
- **Security**: Basic API Key authentication middleware and CORS configuration.

## 3. Core Capabilities to Implement

### 3.1 GraphQL Integration
- Endpoint: `/graphql`
- **Schema Requirements**:
  - `Node`: Represents files, classes, functions, etc.
  - `Edge`: Represents relationships (imports, calls, contains).
- **Queries**:
  - Fetch a node and its direct dependencies.
  - Traverse relationships (e.g., all functions called by function X).

### 3.2 Real-time Streaming (Reasoning Engine)
- Endpoint: `/reason/stream`
- Stream LangGraph node executions (e.g., `retrieving_context`, `generating_answer`) and the final LLM response chunk by chunk to drastically improve perceived performance on the client side.

### 3.3 Security & Middleware
- **CORS**: Configured to allow local Web Dashboard (e.g., localhost:3000) and VSCode Extension.
- **Authentication**: `X-API-Key` header validation for protected endpoints.
- **Error Handling**: Standardized Problem Details for HTTP APIs (RFC 7807).

## 4. Integration Points
- Extends the `apps/api` package.
- Consumes Neo4j (via GraphQL resolvers) and LangGraph (via async streaming).

## 5. Definition of Done
- GraphQL endpoint is live and can traverse Neo4j relationships.
- Endpoint can stream reasoning responses in real-time.
- API requires a valid API key (configurable via `.env`).
