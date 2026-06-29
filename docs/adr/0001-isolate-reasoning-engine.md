# ADR-0001: Isolate Reasoning Engine from Repository

## Status

Accepted

## Context

Current AI coding assistants work by directly reading files from the repository to build temporary context, and then passing that to an LLM. This leads to missing context, repeated reasoning, and loss of engineering memory. In our architecture, the Reasoning Engine is responsible for orchestrating AI reasoning using LangGraph. We need to decide how this engine accesses information about the codebase.

## Decision Drivers

* **Knowledge over Prompt**: LLM should reason over knowledge instead of raw source code.
* **Separation of Responsibility**: Engines should be decoupled.
* **Evidence First**: All reasoning must be traceable to structured evidence (AST, graph, metadata) rather than raw text blobs.

## Decision

The Reasoning Engine **must never** directly read the repository. It must only interact with the Context Intelligence Engine and Knowledge Engine to retrieve pre-processed, structured engineering knowledge.

## Rationale

Allowing the Reasoning Engine to directly read source code would tightly couple the LLM's orchestration logic with the raw data format, reverting to the very problem we are trying to solve. By forcing the Reasoning Engine to consume structured knowledge, we ensure that:
1. The Knowledge Engine is robust enough to extract necessary information.
2. The LLM has high-quality, pre-digested context (AST, dependencies, architectural choices).
3. The reasoning process is reproducible and relies on our "Digital Twin" of the software.

## Consequences

### Positive
* Strongly enforces the "Digital Twin" philosophy.
* Prevents context window bloating with raw, irrelevant source code lines.
* Makes the Reasoning Engine highly testable (we can mock the Knowledge Engine).

### Negative
* High pressure on the Knowledge Engine and Parser; if they fail to extract a piece of information, the Reasoning Engine cannot see it.
* Requires designing comprehensive and expressive interfaces between engines early in Phase 0.

### Risks
* **Risk**: The parser might miss specific, nuanced code details (e.g., inline comments acting as logic markers).
* **Mitigation**: Implement robust, extensible parsers (Tree-sitter) and allow metadata extensions to capture such details.

## Implementation Notes

* The Reasoning Engine will use LangGraph.
* Any tool or node inside LangGraph designed to "read" must call an API or Interface exposed by the Context Engine, not `os.read()`.
