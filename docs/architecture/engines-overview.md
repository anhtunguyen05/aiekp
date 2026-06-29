# Core Engines Architecture

The AIEKP platform is divided into three distinct, decoupled engines. This separation of concerns ensures that the platform can scale, swap underlying technologies (like LLMs or parsers), and be tested independently.

## 1. Knowledge Engine

**Role**: Converting repositories into engineering knowledge.
**Architecture Style**: Clean Architecture, DDD Lite.

This is the heart of the project. It handles raw code and turns it into structured, queryable data.

### Responsibilities
* **Repository Scanner**: Finds and filters source code files.
* **Parser**: Uses Tree-sitter and language-specific plugins to parse code into Abstract Syntax Trees (AST).
* **Metadata Builder**: Extracts structural and semantic metadata (classes, methods, dependencies).
* **Knowledge Builder**: Aggregates metadata into cohesive knowledge artifacts.
* **Knowledge Graph**: Stores relationships in Neo4j.
* **Engineering Memory**: Maintains historical evolution and decisions over time.

---

## 2. Context Intelligence Engine

**Role**: Generating the optimal context for a specific reasoning task.
**Architecture Style**: Hexagonal Architecture.

This is the main innovation of the project. Instead of dumping raw files to an LLM, this engine fetches the exact slice of the Knowledge Graph needed.

### Responsibilities
* **Intent Detection**: Analyzes the user's or system's query to determine what knowledge is needed.
* **Knowledge Planning**: Plans the retrieval steps.
* **Knowledge Retrieval**: Interacts with the Knowledge Engine to fetch data (via interfaces, never directly hitting DBs).
* **Evidence Collection**: Gathers hard evidence (AST fragments, ADRs, Commit history).
* **Context Ranking**: Scores and filters retrieved knowledge to fit within LLM context windows.
* **Context Composition**: Packages the context cleanly for the Reasoning Engine.

---

## 3. Reasoning Engine

**Role**: Orchestrating AI reasoning.
**Architecture Style**: LangGraph Workflow, State Machine.

This engine utilizes LLMs to answer questions, analyze architecture, or review code, strictly based on the context provided.

### Responsibilities
* **Planner**: Deconstructs the overarching task into smaller AI tasks.
* **Agent Orchestration**: Manages LangGraph nodes (e.g., Code Analyst Agent, Architect Agent).
* **Reviewer**: Verifies that the AI's output aligns with the provided evidence.
* **Final Answer**: Formulates the user-facing response.

### Strict Boundary
**The Reasoning Engine should never directly read repositories.** It must request context from the Context Intelligence Engine.
