# PROJECT_CONTEXT.md

# AI Engineering Knowledge Platform (AIEKP)

> Master Context Document
>
> This document contains the complete high-level context of the project.
> Every AI Agent working on this project must read this document before implementing any feature.

---

# 1. Project Vision

## Mission

Build an AI Engineering Knowledge Platform that transforms software repositories into persistent engineering knowledge, allowing AI agents to reason over software systems instead of repeatedly reading source code.

The project is NOT another AI coding assistant.

The project focuses on creating a Digital Twin of software projects.

---

# 2. Problem Statement

Current coding agents (Claude Code, Cursor, Codex, Gemini CLI...) work by:

Repository
→ Search
→ Read files
→ Build temporary context
→ LLM reasoning

Problems

* Knowledge disappears after every request
* No engineering memory
* No architecture memory
* No decision memory
* No evolution tracking
* Same reasoning repeated multiple times

This project solves those problems by converting source code into persistent engineering knowledge.

---

# 3. Core Idea

Repository

↓

Knowledge Extraction

↓

Knowledge Graph

↓

Engineering Memory

↓

Context Intelligence Engine

↓

Reasoning Engine

↓

LLM

The LLM should reason over knowledge instead of raw source code whenever possible.

---

# 4. Core Principles

## Knowledge over Prompt

Do not rely on prompting the LLM to read the repository every time.

Build reusable knowledge.

---

## Evidence First

Every answer must contain evidence.

Possible evidence:

* AST
* Knowledge Graph
* Metadata
* ADR
* Commit
* Source Code
* Dependency

Never answer without evidence.

---

## Interface First

Every engine communicates through interfaces.

Never couple implementations directly.

---

## Plugin Everything

Support plugins for:

* Parser
* LLM
* Storage
* Rule Engine
* Programming Languages

---

## LLM Agnostic

Support

* OpenAI
* Gemini
* Claude
* Ollama
* Azure OpenAI
* Future models

Never depend on one provider.

---

## Incremental Update

Never rebuild the entire knowledge graph unless necessary.

Update only changed files.

---

## Separation of Responsibility

Three independent engines

Knowledge Engine

Context Engine

Reasoning Engine

No engine should know internal implementation details of another.

---

# 5. Product Goals

The platform should support

Repository Scan

Knowledge Extraction

Architecture Review

Impact Analysis

Technical Debt Analysis

Decision Analysis

Requirement Traceability

Onboarding

Dependency Analysis

Business Flow Explanation

Future

Security Review

Compliance

Enterprise Governance

---

# 6. High Level Architecture

Client

↓

CLI / API / VSCode

↓

Application Layer

↓

Context Intelligence Engine

↓

Reasoning Engine (LangGraph)

↓

Knowledge Engine

↓

Storage Layer

↓

Repository

---

# 7. Main Engines

## Knowledge Engine

Responsible for converting repositories into engineering knowledge.

Responsibilities

* Repository Scanner
* Parser
* Metadata Builder
* Knowledge Builder
* Knowledge Graph
* Engineering Memory

This is the heart of the project.

---

## Context Intelligence Engine

Responsible for generating the optimal context for a specific task.

Responsibilities

* Intent Detection
* Knowledge Planning
* Knowledge Retrieval
* Evidence Collection
* Context Ranking
* Context Composition

This is the main innovation of the project.

---

## Reasoning Engine

Responsible for orchestrating AI reasoning.

Implemented using LangGraph.

Responsibilities

* Planner
* Agent Orchestration
* Reviewer
* Final Answer

The Reasoning Engine should never directly read repositories.

---

# 8. Knowledge Pipeline

Repository

↓

Scanner

↓

Parser

↓

Metadata

↓

Knowledge Graph

↓

Knowledge Base

↓

Context Engine

↓

Reasoning

↓

Answer

---

# 9. Architecture Style

The project uses multiple architecture styles.

Knowledge Engine

* Clean Architecture
* DDD Lite

Context Engine

* Hexagonal Architecture

Reasoning Engine

* LangGraph Workflow
* State Machine

Parser

* Plugin Architecture
* Strategy Pattern

Storage

* Repository Pattern

LLM

* Adapter Pattern

---

# 10. Technology Stack

Language

Python

Package Manager

uv

Backend

FastAPI

Workflow

LangGraph

Knowledge Graph

Neo4j

Metadata Database

PostgreSQL

Vector Database

Qdrant

Cache

Redis

Storage

MinIO

Parser

Tree-sitter + language specific parsers

Deployment

Docker Compose

Future

Kubernetes

---

# 11. Monorepo Structure

apps/

api/

cli/

dashboard/

vscode/

packages/

knowledge-engine/

context-engine/

reasoning-engine/

graph-engine/

parser-core/

scanner/

llm-adapter/

storage/

shared/

plugins/

java/

python/

typescript/

flutter/

infrastructure/

docker/

scripts/

docs/

tests/

---

# 12. Development Philosophy

Implementation order

Phase 0

Project Foundation

↓

Phase 1

Repository Scanner

↓

Phase 2

Parser

↓

Phase 3

Metadata

↓

Phase 4

Knowledge Graph

↓

Phase 5

Knowledge Engine

↓

Phase 6

Context Intelligence Engine

↓

Phase 7

Reasoning Engine

↓

Phase 8

CLI

↓

Phase 9

API

↓

Phase 10

VSCode

LangGraph is intentionally implemented after the Knowledge Engine.

---

# 13. Implementation Rules

Never call LLM directly from the parser.

Never mix business logic with API.

Never access Neo4j directly outside Graph Engine.

Never access LLM directly outside LLM Adapter.

Always communicate through interfaces.

Every module must be independently testable.

Every recommendation should contain evidence.

---

# 14. Future Direction

The project should evolve into an Engineering Intelligence Platform.

Future capabilities

Enterprise Knowledge

Architecture Governance

Engineering Memory

Decision Intelligence

Software Digital Twin

Continuous Repository Learning

Organization Knowledge

Eventually the platform should become an AI operating system for software engineering rather than a repository analysis tool.

---

# 15. Immediate Next Step

Current milestone

Project Foundation

Tasks

* Initialize monorepo
* Setup uv workspace
* Setup Docker Compose
* Configure PostgreSQL
* Configure Neo4j
* Configure Redis
* Configure Qdrant
* Setup FastAPI
* Define project interfaces
* Define domain models

No AI implementation should begin before the foundation is complete.

---

# 16. Definition of Success

The MVP is successful if it can

* Scan a repository
* Parse source code
* Build metadata
* Build a Knowledge Graph
* Answer architecture questions using the Knowledge Graph
* Perform reasoning using LangGraph
* Produce evidence-based answers

The project is NOT successful if it only wraps an LLM around source code.

The long-term goal is to create a reusable engineering knowledge platform that continuously accumulates knowledge and enables high-quality reasoning across software projects.
