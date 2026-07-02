# Phase 11: Multi-Agent Swarm & Polyglot Expansion

## 1. Overview
Currently, the AIEKP Reasoning Engine operates as a single LLM agent that processes the retrieved context and generates an answer. Phase 11 aims to evolve this architecture into a **Multi-Agent Swarm** using LangGraph, where specialized agents (Architect, QA, Security) collaborate under a Supervisor to solve complex coding tasks. 
Additionally, this phase expands the platform's multi-language parsing capabilities by introducing native support for **TypeScript and JavaScript**.

## 2. Goals
1. **Multi-Agent Orchestration**: Replace the single `synthesize` node in the reasoning graph with a routing network of specialized AI agents.
2. **TypeScript/JavaScript Support**: Develop `tree-sitter` based parser and extractor plugins to ingest `.ts`, `.tsx`, `.js`, and `.jsx` files into the Knowledge Graph.
3. **Streaming Compatibility**: Ensure that the multi-agent collaboration process can be streamed back to the CLI/VSCode extension in real-time (e.g., showing which agent is currently thinking).

## 3. Scope of Work

### 3.1 Context Engine Plugins
- Create `plugins/typescript_parser` using `tree-sitter-typescript` and `tree-sitter-javascript`.
- Create `plugins/typescript_extractor` to extract AST nodes into the domain model (Classes, Methods, Interfaces, Functions).
- Update the workspace configuration (`pyproject.toml`) and integrate the new plugins into the dependency tree of `apps/cli` and `apps/api`.

### 3.2 LangGraph Multi-Agent Architecture
- Re-architect `packages/reasoning-engine/src/reasoning_engine/services/orchestrator.py`.
- Define a new `GraphState` capable of holding conversational memory (e.g., an array of `BaseMessage`).
- Implement the following Agent Nodes:
  - **SupervisorNode**: Analyzes the initial query, routes to the appropriate specialized agents, and synthesizes the final output.
  - **ArchitectNode**: Specialized prompt focused on system design, SOLID principles, and dependency flow.
  - **QANode**: Specialized prompt focused on edge cases, testability, and logic bugs.
  - **SecurityNode**: Specialized prompt focused on identifying vulnerabilities (SQL injection, XSS, insecure data exposure).

### 3.3 Streaming Enhancements
- Update `ReasoningService.stream_process_query()` to listen to `astream_events` from the new LangGraph setup, allowing frontend clients to render intermediate thoughts before the final answer.

## 4. Open Architectural Decisions (Pending User Input)
1. **Plugin Unification**: Do we unify TypeScript and JavaScript into a single `typescript_parser` plugin, or separate them?
2. **Context Fetching Strategy**: Should the Supervisor fetch the context from the Knowledge Graph once and pass it to all sub-agents, or should each sub-agent have the autonomy to query the graph themselves using tools?

## 5. Acceptance Criteria
- [ ] Running `aiekp ingest` on a TypeScript/JavaScript codebase successfully creates nodes and relationships in Neo4j.
- [ ] The reasoning engine routes queries to at least two different specialized agents depending on the prompt (e.g., asking about security routes to the Security Agent).
- [ ] The VSCode extension and CLI successfully stream the output from the multi-agent swarm without crashing.
