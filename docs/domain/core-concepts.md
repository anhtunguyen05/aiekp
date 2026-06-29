# Core Domain Concepts

This document defines the ubiquitous language and core entities used across the AIEKP platform, particularly within the Knowledge Engine (which employs DDD Lite).

## Core Entities

### 1. Repository
Represents the target software project.
* **Attributes**: URI, Branch, Commit Hash, Language Stack.
* **Behaviors**: Can be scanned, checked for diffs (incremental updates).

### 2. AST Node (Abstract Syntax Tree Node)
A structured representation of a specific piece of source code, parsed via Tree-sitter.
* **Attributes**: Type (Function, Class, Import), Start/End lines, Raw Content.

### 3. Metadata Object
Extracted structural information that lives above the AST.
* **Examples**: A `ClassMetadata` object might contain references to its methods, its parent class, and implemented interfaces.

### 4. Knowledge Node & Edge (The Graph)
The fundamental building blocks of the Engineering Memory.
* **Node**: Represents a tangible artifact (File, Class, Method, Developer, ADR).
* **Edge**: Represents relationships (`CALLS`, `IMPLEMENTS`, `DEPENDS_ON`, `AUTHORED_BY`).

### 5. Evidence
A packaged wrapper around Knowledge Nodes or AST fragments used to prove an AI's assertion.
* **Rule**: Every AI response must link back to one or more Evidence objects.

### 6. Context Payload
The composed set of Evidence and Instructions passed from the Context Intelligence Engine to the Reasoning Engine. It is specifically tailored to the current intent (e.g., "Impact Analysis" vs. "Security Review").
