# Product Definition

This document establishes the Vision (Why) and the Requirements (What) of the AIEKP platform.

---

## 1. Project Vision

### Mission
Build an **AI Engineering Knowledge Platform (AIEKP)** that transforms software repositories into persistent engineering knowledge, allowing AI agents to reason over software systems instead of repeatedly reading source code.

**Note:** The project is NOT another AI coding assistant. The project focuses on creating a **Digital Twin** of software projects.

### Problem Statement
Current coding agents (Claude Code, Cursor, Codex, Gemini CLI...) work by:
1. Searching the repository
2. Reading files
3. Building temporary context
4. Using LLM reasoning

**Core Problems:**
* Knowledge disappears after every request.
* No engineering memory (why was this built?).
* No architecture memory (how is this connected?).
* No decision memory.
* No evolution tracking.
* The same reasoning is repeated multiple times (wasting tokens and time).

This project solves those problems by converting source code into persistent engineering knowledge.

### The Core Idea
The LLM should reason over knowledge instead of raw source code whenever possible.

`Repository -> Knowledge Extraction -> Knowledge Graph -> Engineering Memory -> Context Intelligence Engine -> Reasoning Engine -> LLM`

---

## 2. Product Requirements

### Definition of Success
The MVP is successful if it can:
1. Scan a repository.
2. Parse source code into ASTs.
3. Build metadata from ASTs.
4. Build a interconnected Knowledge Graph.
5. Answer complex architecture questions using the Knowledge Graph.
6. Perform multi-step reasoning using LangGraph.
7. Produce **evidence-based** answers (linking back to the graph/AST).

**Constraint:** The project is NOT successful if it only wraps an LLM around raw source code.

### MVP Capabilities
The platform MUST support:
* **Repository Scan**: Detect and parse changes incrementally.
* **Knowledge Extraction**: Extract classes, methods, dependencies.
* **Architecture Review**: Analyze structural integrity.
* **Impact Analysis**: E.g., "If I change interface X, what services break?"

### Future Capabilities
* **Technical Debt Analysis**
* **Decision Analysis**
* **Requirement Traceability**
* **Onboarding Assistant**
* **Business Flow Explanation**
* **Security & Compliance Review**
* **Enterprise Architecture Governance**

*Eventually, the platform should become an AI operating system for software engineering rather than just a repository analysis tool.*
