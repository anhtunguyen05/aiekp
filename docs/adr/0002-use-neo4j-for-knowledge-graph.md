# ADR-0002: Use Neo4j for Knowledge Graph

## Status

Accepted

## Context

The AIEKP platform aims to build a "Digital Twin" of software projects by extracting knowledge from repositories (AST, dependencies, metadata, architectural patterns) and storing it as Engineering Memory. We need a database capable of modeling, storing, and querying these complex, highly interconnected relationships.

## Decision Drivers

* **Complex Relationships**: Codebases have deep hierarchies (files -> classes -> methods -> variables) and cross-cutting dependencies (method calls, imports, inheritance).
* **Query Capabilities**: We need to easily query paths, clusters, and impacts (e.g., "Find all services affected if this DB interface changes").
* **Integration**: Needs to integrate well with Python and modern LLM frameworks (LangChain/LangGraph support for graph traversal).

## Considered Options

### Option 1: Relational Database (PostgreSQL)
- **Pros**: Mature, ACID compliant, team familiarity.
- **Cons**: Modeling recursive hierarchies and deep relationship traversals (e.g., multi-hop dependencies) requires complex, slow `JOIN` or `WITH RECURSIVE` queries.

### Option 2: Graph Database (Neo4j)
- **Pros**: Native graph storage, Cypher query language is highly optimized for relationship traversals, excellent visualization tools (Neo4j Bloom/Browser), good integrations.
- **Cons**: Steep learning curve for Cypher, resource-intensive for local development.

### Option 3: Multi-model (ArangoDB)
- **Pros**: Supports documents and graphs in one engine.
- **Cons**: Smaller ecosystem and community support compared to Neo4j, especially in AI/LLM tooling.

## Decision

We will use **Neo4j** as the core database for the Knowledge Graph within the Knowledge Engine.

## Rationale

The primary value of AIEKP lies in understanding the *relationships* within code, not just the isolated elements. Neo4j is the industry standard for graph databases, offering the best performance for deep traversal queries. Its query language, Cypher, is perfectly suited for tracing requirement traceability, impact analysis, and dependency chains. Furthermore, its integration with AI ecosystems makes it the best choice for passing graph contexts to the Reasoning Engine.

## Consequences

### Positive
* Easy modeling of AST and architectural relationships.
* Fast execution of complex impact analysis queries.
* Visual debugging of the extracted knowledge via Neo4j Browser.

### Negative
* Adds significant footprint to the `docker-compose` stack (requires JVM).
* Developers need to learn Cypher.

### Risks
* **Risk**: High resource usage during local Phase 0 development.
* **Mitigation**: Provide a lightweight mock or an in-memory test configuration for unit tests, ensuring developers don't always need a running Neo4j instance unless working on the Graph Engine.

## Implementation Notes

* The Graph Engine is the ONLY component allowed to access Neo4j directly.
* Other engines must use interfaces provided by the Graph Engine.
