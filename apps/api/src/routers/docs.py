import json
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from knowledge_graph import Neo4jGraphManager
from src.dependencies import get_neo4j_manager, get_reasoning_service
from reasoning_engine.ports.inbound import IReasoningService
from reasoning_engine.domain.models import ReasoningRequest

router = APIRouter(prefix="/docs", tags=["Docs"])

# -------------------------------------------------------------------------
# Schemas
# -------------------------------------------------------------------------


class DocGenerateRequest(BaseModel):
    doc_type: Literal[
        "architecture_overview",
        "onboarding_guide",
        "key_entry_points",
        "module_dependencies",
    ]
    session_id: str = "doc-gen"


# -------------------------------------------------------------------------
# Prompts
# -------------------------------------------------------------------------

PROMPT_TEMPLATES = {
    "architecture_overview": """
You are a senior software architect. Based on the actual codebase analysis below,
write a concise Architecture Overview document in Markdown.

## Codebase Statistics & Structure:
{context}

Instructions:
- Describe the main layers/modules you can infer from the node types and relationships.
- Identify 3-5 key architectural patterns visible in the data.
- DO NOT invent information not present in the statistics above.
- Output ONLY valid Markdown, starting with # Architecture Overview.
""",
    "onboarding_guide": """
You are a senior developer writing a Getting Started guide for a new team member.
Based on the actual codebase data below, write a practical Onboarding Guide in Markdown.

## Codebase Analysis & Entry Points:
{context}

Instructions:
- Identify the most important entry points and explain what they do.
- Suggest a reading order for understanding the codebase.
- Highlight any critical files with high connectivity (hotspots).
- Output ONLY valid Markdown, starting with # Developer Onboarding Guide.
""",
    "key_entry_points": """
You are documenting the entry points of a software project.
Based on the codebase metrics below, list and explain the key entry points.

## Entry Point Analysis:
{context}

Instructions:
- List each entry point with its purpose inferred from its name and connectivity.
- Explain why each is important (high fan-in = many dependents).
- Output ONLY valid Markdown, starting with # Key Entry Points.
""",
    "module_dependencies": """
You are creating a Module Dependencies document.
Based on the relationship data below, write a dependencies overview with a Mermaid diagram.

## Dependency Data:
{context}

Instructions:
- Generate a Mermaid `graph TD` diagram showing the top module dependencies. DO NOT use parentheses `()` inside node labels or IDs in Mermaid to avoid syntax errors.
- Add a brief explanation of the dependency structure below the diagram.
- Output ONLY valid Markdown with a valid ```mermaid code block.
""",
}

# -------------------------------------------------------------------------
# Context Assembler Helpers
# -------------------------------------------------------------------------


async def _assemble_context(doc_type: str, graph_manager: Neo4jGraphManager) -> str:
    """Collects relevant graph metrics and structures them into text context."""
    driver = graph_manager.driver

    # Common stats: labels and hotspots
    labels_records, _, _ = driver.execute_query(
        "MATCH (n) RETURN labels(n)[0] as label, count(*) as count"
    )
    nodes_by_label = {r["label"]: r["count"] for r in labels_records if r["label"]}

    hotspots_records, _, _ = driver.execute_query(
        "MATCH (n)-[r]-() WITH n, count(r) as rel_count ORDER BY rel_count DESC LIMIT 10 "
        "RETURN coalesce(n.id, n.path) as id, labels(n)[0] as type, rel_count"
    )
    hotspots = [
        {"id": r["id"], "type": r["type"], "connections": r["rel_count"]}
        for r in hotspots_records
    ]

    context_parts = [
        "### Nodes by Type",
        json.dumps(nodes_by_label, indent=2),
        "### Hotspots (Most connected nodes)",
        json.dumps(hotspots, indent=2),
    ]

    if doc_type == "architecture_overview":
        edges_records, _, _ = driver.execute_query(
            "MATCH (a)-[r:CONTAINS|DEFINES]->(b) "
            "WITH a, type(r) as rel, b, count(*) as count "
            "ORDER BY count DESC LIMIT 50 "
            "RETURN coalesce(a.id, a.path) as source, rel, coalesce(b.id, b.path) as target"
        )
        edges = [
            {"source": r["source"], "rel": r["rel"], "target": r["target"]}
            for r in edges_records
        ]
        context_parts.extend(
            [
                "### Top Structural Relationships (CONTAINS/DEFINES)",
                json.dumps(edges, indent=2),
            ]
        )

    elif doc_type == "onboarding_guide" or doc_type == "key_entry_points":
        fanin_records, _, _ = driver.execute_query(
            "MATCH ()-[r]->(n) "
            "WITH n, count(r) as in_degree "
            "ORDER BY in_degree DESC LIMIT 10 "
            "RETURN coalesce(n.id, n.path) as id, labels(n)[0] as type, in_degree"
        )
        entry_points = [
            {"id": r["id"], "type": r["type"], "incoming_connections": r["in_degree"]}
            for r in fanin_records
        ]
        context_parts.extend(
            [
                "### Key Entry Points (Highest Fan-In)",
                json.dumps(entry_points, indent=2),
            ]
        )

    elif doc_type == "module_dependencies":
        file_edges_records, _, _ = driver.execute_query(
            "MATCH (a:File)-[r:IMPORTS|CALLS|USES]->(b:File) "
            "WITH a, type(r) as rel, b, count(*) as count "
            "ORDER BY count DESC LIMIT 100 "
            "RETURN a.path as source, rel, b.path as target"
        )
        file_edges = [
            {"source": r["source"], "rel": r["rel"], "target": r["target"]}
            for r in file_edges_records
        ]
        context_parts.extend(
            ["### File-to-File Dependencies", json.dumps(file_edges, indent=2)]
        )

    return "\n\n".join(context_parts)


# -------------------------------------------------------------------------
# Endpoints
# -------------------------------------------------------------------------


@router.post("/generate")
async def generate_doc(
    request: DocGenerateRequest,
    graph_manager: Neo4jGraphManager = Depends(get_neo4j_manager),
    reasoning_service: IReasoningService = Depends(get_reasoning_service),
):
    """
    Generate an automated onboarding document using the reasoning engine and graph context.
    Streams back Server-Sent Events (SSE).
    """
    if request.doc_type not in PROMPT_TEMPLATES:
        raise HTTPException(status_code=400, detail="Invalid doc_type")

    async def sse_generator():
        # 1. Assemble context
        yield f"data: {json.dumps({'type': 'status', 'content': 'Assembling context from Knowledge Graph...'})}\n\n"

        try:
            context = await _assemble_context(request.doc_type, graph_manager)
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': f'Error reading graph context: {str(e)}'})}\n\n"
            yield "data: [DONE]\n\n"
            return

        yield f"data: {json.dumps({'type': 'status', 'content': 'Generating document with AI...'})}\n\n"

        # 2. Build prompt
        prompt = PROMPT_TEMPLATES[request.doc_type].format(context=context)

        # 3. Stream from reasoning engine
        reasoning_request = ReasoningRequest(
            query=prompt, session_id=request.session_id
        )

        try:
            async for chunk in reasoning_service.stream_process_query(
                reasoning_request
            ):
                # The stream_process_query yields dicts or strings. Format them into SSE.
                if isinstance(chunk, dict):
                    payload = json.dumps(chunk)
                else:
                    payload = json.dumps({"type": "message", "content": str(chunk)})
                yield f"data: {payload}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': f'Error generating document: {str(e)}'})}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(sse_generator(), media_type="text/event-stream")
