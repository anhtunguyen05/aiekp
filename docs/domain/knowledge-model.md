# Knowledge Model

This document outlines the schema and structure of the Engineering Knowledge Graph stored in Neo4j, which forms the "Digital Twin" of the software repository.

## 1. Graph Nodes (Entities)

The Knowledge Graph represents code and architectural artifacts as distinct nodes.

| Node Label | Description | Example Properties |
|------------|-------------|--------------------|
| `Repository` | The root project being analyzed. | `name`, `url`, `branch`, `last_scanned` |
| `File` | A physical source file. | `path`, `extension`, `loc` (lines of code) |
| `Class` | A class/struct definition. | `name`, `namespace`, `is_abstract` |
| `Function` / `Method` | A block of executable code. | `name`, `signature`, `return_type` |
| `Dependency` | A third-party library or package. | `name`, `version`, `ecosystem` |
| `Concept` | An abstract domain or architectural concept. | `name`, `description` |

## 2. Graph Edges (Relationships)

Edges define how the entities interact, which is critical for Impact Analysis and Context Retrieval.

| Relationship Type | Source -> Target | Description |
|-------------------|------------------|-------------|
| `CONTAINS` | `Repository` -> `File` | Structural hierarchy. |
| `DEFINES` | `File` -> `Class`/`Function` | Where the AST node physically lives. |
| `CALLS` | `Function` -> `Function` | Execution flow. |
| `IMPLEMENTS` | `Class` -> `Class` | Inheritance or interface realization. |
| `IMPORTS` | `File` -> `Dependency` | Package usage. |
| `RELATED_TO` | `Function`/`Class` -> `Concept` | Semantic linking (e.g., this function handles "Authentication"). |

## 3. Metadata & Embeddings

While the Graph handles relationships, dense data is stored alongside it:

*   **Vector Embeddings**: Each `Function` and `Class` node will have its raw code (and docstrings) embedded via an LLM embedding model and stored in **Qdrant**. This allows for semantic search (e.g., "Find the function that validates user email") which then maps back to the Graph node to fetch dependencies.
*   **AST Pointers**: Nodes contain a pointer (offset/line numbers) back to the raw Abstract Syntax Tree to allow the Context Engine to reconstruct precise code snippets as evidence.
