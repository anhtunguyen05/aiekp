# Phase 9: REST/GraphQL API Implementation Plan

## Overview
This plan breaks down the delivery of the robust API layer into actionable steps, focusing on GraphQL integration, Streaming, and Security.

## Phase 1: Security & Foundation
- [ ] Add CORS middleware allowing configurable origins (`apps/api/src/main.py`).
- [ ] Implement API Key authentication middleware (`apps/api/src/dependencies.py`).
- [ ] Standardize error handling/responses globally across the API.

## Phase 2: GraphQL Setup & Resolvers
- [ ] Install `strawberry-graphql` as a dependency in `apps/api`.
- [ ] Define GraphQL types for `EntityNode` and `RelationshipEdge` (`apps/api/src/graphql/types.py`).
- [ ] Implement resolvers to fetch nodes and traverse relationships from Neo4j (`apps/api/src/graphql/resolvers.py`).
- [ ] Mount the Strawberry GraphQL app onto FastAPI (`/graphql`).

## Phase 3: Reasoning Engine Streaming
- [ ] Update `reasoning_engine` package to support async streaming of events/tokens.
- [ ] Create a streaming endpoint `/reason/stream` in `apps/api/src/routers/reason.py`.
- [ ] Test real-time streaming using a simple Python or JS client.

## Phase 4: Finalization & Documentation
- [ ] Generate/update OpenAPI documentation with authentication details.
- [ ] Document GraphQL schema examples.
- [ ] Run E2E tests for the new endpoints.
