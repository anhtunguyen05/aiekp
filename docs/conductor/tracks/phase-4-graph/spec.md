# Phase 4: Knowledge Graph Construction

## Objective
Take the parsed `FileMetadata` (containing Classes, Functions, and their Docstrings) from Phase 3 and ingest them into the Engineering Memory. This involves constructing a relational graph in Neo4j and a semantic vector space in Qdrant.

## Scope
- Create `packages/knowledge_graph`.
- Implement `Neo4jGraphManager` for defining node labels (`File`, `Class`, `Function`) and relationships (`CONTAINS`, `DEFINES`).
- Implement `Embedder` using `sentence-transformers` (model: `all-MiniLM-L6-v2`) to generate embeddings for source code and docstrings.
- Implement `QdrantVectorManager` to store and query the generated embeddings.
- Implement `GraphIngestor` to orchestrate the synchronous extraction and insertion of data into both databases.
- Test the integration end-to-end locally using Docker instances of Neo4j and Qdrant.

## Out of Scope
- Creating the public Knowledge Engine API (deferred to Phase 5).
- Implementing asynchronous ingestion via message queues (deferred to future scalability phase).
- Implementing incremental updates (only "upsert-all" is required initially).

## Definition of Done
- `aiekp-knowledge-graph` package is created and dependencies are configured.
- Running `scratch_test_graph.py` on a sample Python file successfully populates Neo4j and Qdrant without errors.
- Neo4j browser shows the created nodes and edges correctly.
- Qdrant dashboard shows the created vectors and payloads.
