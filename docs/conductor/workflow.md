# Implementation Phases & Workflow

This document defines HOW we work and WHEN things are built.

---

## 1. Core Principles

*   **Knowledge over Prompt**: Build reusable knowledge; don't just prompt the LLM to read raw files.
*   **Evidence First**: Every AI answer MUST contain evidence (AST, Graph, etc.). Never answer blindly.
*   **Interface First**: Engines communicate strictly through decoupled interfaces.
*   **Plugin Everything**: Parsers, LLMs, Storage must be extensible via plugins.
*   **LLM Agnostic**: We must support OpenAI, Gemini, Claude, Local models.
*   **Incremental Update**: Update only changed files in the graph.
*   **Separation of Responsibility**: No engine knows the internal implementation details of another.

---

## 2. Implementation Phases

We follow a strict, sequential implementation strategy. **Do not jump phases.**
For the full roadmap and summary of all phases (Phase 0 to Phase 10), please refer to the **[Implementation Roadmap](roadmap.md)**.

---

## 3. Implementation Rules (Hard Constraints)

1.  **Never call LLM directly from the parser.**
2.  **Never mix business logic with API routes.**
3.  **Never access Neo4j directly outside the Graph Engine.**
4.  **Never access LLM directly outside the LLM Adapter.**
5.  **Always communicate through interfaces.**
6.  **Every module must be independently testable.**
