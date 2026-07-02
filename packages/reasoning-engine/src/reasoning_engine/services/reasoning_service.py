from reasoning_engine.ports.inbound import IReasoningService
from reasoning_engine.ports.outbound import IContextFetcher, ILLMGenerator
from reasoning_engine.domain.models import ReasoningRequest, ReasoningResult
from reasoning_engine.services.orchestrator import ReasoningOrchestrator, GraphState


class ReasoningService(IReasoningService):
    def __init__(
        self,
        context_fetcher: IContextFetcher,
        llm_generator: ILLMGenerator,
        db_uri: str = None,
    ):
        self.orchestrator = ReasoningOrchestrator(context_fetcher, llm_generator)
        self.db_uri = db_uri  # For checkpointing if needed

    async def process_query(self, request: ReasoningRequest) -> ReasoningResult:
        initial_state: GraphState = {
            "query": request.query,
            "session_id": request.session_id,
            "context_accumulated": [],
            "is_context_sufficient": False,
            "iterations": 0,
            "final_answer": None,
            "sources_used": [],
            "error": None,
        }

        # For MVP, running without checkpointing explicitly connected,
        # but configured ready for async streaming.
        config = {"configurable": {"thread_id": request.session_id}}

        # We invoke the graph
        final_state = await self.orchestrator.graph.ainvoke(
            initial_state, config=config
        )

        return ReasoningResult(
            answer=final_state.get("final_answer", "No answer generated."),
            sources_used=final_state.get("sources_used", []),
            confidence_score=1.0 if not final_state.get("error") else 0.0,
        )

    async def stream_process_query(self, request: ReasoningRequest):
        import json

        # Simple streaming orchestration (bypassing full graph for direct streaming MVP)
        target_types = ["class", "method", "function", "interface"]
        try:
            payload = await self.orchestrator.context_fetcher.fetch_context(
                request.query, target_types
            )
        except Exception as e:
            yield f"Error fetching context: {str(e)}"
            return

        context_str = json.dumps([payload], indent=2)
        system_message = """You are AIEKP (AI Engineering Knowledge Platform), an elite Senior Software Architect AI.
Your purpose is to answer the user's questions strictly based on the provided Knowledge Graph context.
Rules:
1. DO NOT hallucinate or guess. If the provided context does not contain enough information to answer the question, explicitly state: "Based on the available context, I cannot fully answer this question."
2. Use GitHub Flavored Markdown for formatting. Format code blocks with appropriate syntax highlighting.
3. Keep your answers concise, direct, and focused on architectural or code-level insights.
4. When referencing a file or a class, try to use its exact name from the context.
"""

        prompt = f"""
User Query: {request.query}

--- START OF KNOWLEDGE GRAPH CONTEXT ---
{context_str}
--- END OF KNOWLEDGE GRAPH CONTEXT ---

Please provide your answer based ONLY on the context above.
"""

        async for chunk in self.orchestrator.llm_generator.astream(
            prompt,
            system_message,
        ):
            yield chunk
