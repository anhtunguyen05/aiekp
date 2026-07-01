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
            payload = await self.orchestrator.context_fetcher.fetch_context(request.query, target_types)
        except Exception as e:
            yield f"Error fetching context: {str(e)}"
            return
            
        context_str = json.dumps([payload], indent=2)
        prompt = f"""
        User Query: {request.query}
        
        Context Evidence:
        {context_str}
        
        Please provide a comprehensive answer based ONLY on the provided context.
        """
        
        async for chunk in self.orchestrator.llm_generator.astream(
            prompt,
            "You are a senior software architect AI. Answer questions using only the provided context."
        ):
            yield chunk
