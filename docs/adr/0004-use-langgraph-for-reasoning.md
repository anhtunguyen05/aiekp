# ADR-0004: Use LangGraph for Reasoning Orchestration

## Status

Accepted

## Context

The Reasoning Engine (Phase 7) is responsible for answering complex codebase questions and generating code. This process is rarely linear. An LLM might determine that the initial context provided by the Context Intelligence Engine is insufficient and decide it needs to retrieve deeper dependencies or different files before formulating an answer. We need an orchestration framework that supports cyclic flows, state persistence, and complex branching logic.

## Decision Drivers

* **Cyclic Reasoning**: Support for Agentic loops (e.g., ReAct patterns where the model thinks, acts, observes, and thinks again).
* **State Management**: Ability to persist conversation and intermediate reasoning state.
* **Maintainability**: Clear visualizable flow of reasoning steps rather than tangled prompt chaining.

## Decision

We will use **LangGraph** (part of the LangChain ecosystem) to orchestrate the Reasoning Engine. The engine will be modeled as a state machine where nodes represent reasoning steps (e.g., `FetchContext`, `AnalyzeEvidence`, `GenerateAnswer`) and edges represent conditional routing logic driven by the LLM.

## Rationale

Traditional linear chains (like standard LangChain or LlamaIndex pipelines) are excellent for straight-through processing but fail gracefully when iterative refinement is needed. LangGraph treats the agent's workflow as a graph, allowing loops. This maps perfectly to our requirement: an agent can query the `Context Intelligence Engine`, inspect the `EvidencePayload`, realize it needs the callers of a specific method, and loop back to query the Context Engine again before delivering the final answer.

## Consequences

### Positive
* Highly flexible agent architecture.
* Built-in support for checkpoints and memory.
* Easy to visualize the reasoning flow, aiding in debugging complex agent behaviors.

### Negative
* LangGraph has a steeper learning curve compared to simple chains.
* It introduces tightly coupled dependencies to the LangChain ecosystem (though we will encapsulate this behind Hexagonal adapters).

### Implementation Notes
* The LangGraph workflow must only use the APIs exposed by the Context Engine (adhering to ADR-0001).
* The workflow state should include the original query, accumulated evidence, and current reasoning steps.
