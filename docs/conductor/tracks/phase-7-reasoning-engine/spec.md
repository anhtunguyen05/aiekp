# Phase 7: Reasoning Engine Specification

## 1. Executive Summary
The Reasoning Engine is the brain of the AI Engineering Knowledge Platform. It orchestrates the process of answering complex developer queries by actively retrieving context, analyzing it, and synthesizing accurate answers or code. By strictly relying on the `Context Intelligence Engine` (and adhering to ADR-0001), it ensures all reasoning is grounded in the "Digital Twin" of the codebase rather than raw file parsing.

## 2. Architecture Overview
We will implement the Reasoning Engine using **LangGraph**, enabling an Agentic Workflow capable of cyclic reasoning, introspection, and multi-step execution.

### Hexagonal Layers
Following our standard architecture:
1. **Domain (Core)**: 
   - `ReasoningState`: Represents the state of the LangGraph execution (query, accumulated context, intermediate reasoning steps, final answer).
   - `ReasoningResult`: The final output provided to the user.
2. **Ports (Interfaces)**:
   - *Inbound (Driving)*: `IReasoningService` (The entry point for triggering reasoning).
   - *Outbound (Driven)*: `IContextFetcher` (Interface to fetch context), `ILLMGenerator` (Interface to trigger LLM completions).
3. **Adapters (Implementations)**:
   - *Driving Adapters*: FastAPI router exposing `POST /reason`.
   - *Driven Adapters*: `ContextEngineHttpAdapter` (Calls Phase 6 Context Engine), `LangChainLLMAdapter` (Wraps LangChain/LangGraph LLM calls).

## 3. LangGraph Workflow (Agentic Reasoning)

The core orchestration happens in a state graph with the following nodes:

1. **Analyze Query Node**: Understands the user's question and decides the initial retrieval strategy.
2. **Fetch Context Node**: Calls the Context Engine (`POST /context/retrieve`) to get the `EvidencePayload`.
3. **Evaluate Context Node**: The LLM reviews the fetched context. If it is insufficient (e.g., "I see the function call, but I need its implementation"), it loops back to `Fetch Context Node` with refined parameters.
4. **Synthesize Node**: Once sufficient context is gathered, generates the final explanation, code snippet, or architectural summary.

## 4. Data Models

```python
from pydantic import BaseModel
from typing import List, Optional, Any

class ReasoningRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class ReasoningResult(BaseModel):
    answer: str
    sources_used: List[str] # List of Node IDs or File Paths from Evidence
    confidence_score: float

class ReasoningState(BaseModel):
    query: str
    context_accumulated: List[Any]
    is_context_sufficient: bool = False
    iterations: int = 0
    final_answer: Optional[str] = None
```

## 5. Integration Points
- **Inbound API**: Exposes `POST /reason` in the main FastAPI application.
- **Outbound API**: Calls `POST /context/retrieve` to interact with the Context Engine.
- **LLM Provider**: Connects to OpenAI/Anthropic/Local LLM via LangChain.

## 6. Design Decisions & ADRs
- **ADR-0001**: The engine never reads the file system directly.
- **ADR-0004**: LangGraph is chosen over linear chains to support cyclic reasoning and conditional branching.

## 7. Future Enhancements
- **Multi-Agent Orchestration**: Separate agents for "Code Generation", "Security Auditing", and "Architecture Review", orchestrated by a supervisor node in LangGraph.
- **Human-in-the-Loop**: Pause the graph to ask the developer for clarification before continuing execution.
