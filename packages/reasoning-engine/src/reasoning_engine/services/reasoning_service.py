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
            "sources_used": [],
            "messages": [],
            "error": None,
            "next_agent": "",
        }

        config = {"configurable": {"thread_id": request.session_id}}

        final_state = await self.orchestrator.graph.ainvoke(
            initial_state, config=config
        )

        messages = final_state.get("messages", [])
        answer = messages[-1].content if messages else "No answer generated."

        return ReasoningResult(
            answer=answer,
            sources_used=final_state.get("sources_used", []),
            confidence_score=1.0 if not final_state.get("error") else 0.0,
        )

    async def stream_process_query(self, request: ReasoningRequest):
        initial_state: GraphState = {
            "query": request.query,
            "session_id": request.session_id,
            "context_accumulated": [],
            "sources_used": [],
            "messages": [],
            "error": None,
            "next_agent": "",
        }

        config = {"configurable": {"thread_id": request.session_id}}

        try:
            yield {"type": "status", "content": "Initializing Multi-Agent Swarm..."}
            async for output in self.orchestrator.graph.astream(
                initial_state, config=config
            ):
                for node_name, state_update in output.items():
                    if node_name == "fetch_context":
                        yield {
                            "type": "status",
                            "content": "[System] Context fetched from Knowledge Graph.",
                        }
                    elif node_name == "supervisor":
                        next_agent = state_update.get("next_agent")
                        if next_agent == "FINISH":
                            sources = state_update.get("sources_used", [])
                            if sources:
                                yield {"type": "evidence", "data": sources}
                            messages = state_update.get("messages", [])
                            if messages:
                                yield {
                                    "type": "message",
                                    "content": messages[-1].content,
                                }
                        else:
                            yield {
                                "type": "status",
                                "content": f"[Supervisor] Routing query to {next_agent.upper()} Agent for specialized analysis...",
                            }
                    elif node_name in ["architect", "qa", "security"]:
                        yield {
                            "type": "status",
                            "content": f"[{node_name.capitalize()} Agent] Analysis complete.",
                        }
        except Exception as e:
            yield {
                "type": "error",
                "content": f"Error during multi-agent reasoning: {str(e)}",
            }
