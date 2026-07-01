from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from reasoning_engine.ports.outbound import IContextFetcher, ILLMGenerator
import json


class GraphState(TypedDict):
    query: str
    session_id: str
    context_accumulated: List[Dict[str, Any]]
    is_context_sufficient: bool
    iterations: int
    final_answer: Optional[str]
    sources_used: List[str]
    error: Optional[str]


class ReasoningOrchestrator:
    def __init__(self, context_fetcher: IContextFetcher, llm_generator: ILLMGenerator):
        self.context_fetcher = context_fetcher
        self.llm_generator = llm_generator
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(GraphState)

        workflow.add_node("fetch_context", self.fetch_context_node)
        workflow.add_node("evaluate_context", self.evaluate_context_node)
        workflow.add_node("synthesize", self.synthesize_node)

        # Set entry point
        workflow.set_entry_point("fetch_context")

        workflow.add_edge("fetch_context", "evaluate_context")

        # Conditional edge from evaluate_context
        workflow.add_conditional_edges(
            "evaluate_context",
            self.route_evaluation,
            {"synthesize": "synthesize", "fetch_context": "fetch_context", "end": END},
        )

        workflow.add_edge("synthesize", END)

        # For MVP we don't compile with a checkpointer, but we will add Postgres checkpointer soon
        # if the user requested it. Let's start with in-memory or no checkpointer to test the flow first.
        return workflow.compile()

    async def fetch_context_node(self, state: GraphState):
        """Fetches context from Context Intelligence Engine."""
        # Simple backoff/expansion logic for iterations
        target_types = ["class", "method", "function", "interface"]
        if state["iterations"] > 0:
            target_types = []  # broader search

        try:
            payload = await self.context_fetcher.fetch_context(
                state["query"], target_types
            )

            # Append fetched nodes
            new_context = state["context_accumulated"].copy()
            new_context.append(payload)

            # Extract sources
            sources = state.get("sources_used", [])
            for node in payload.get("nodes", []):
                if node["id"] not in sources:
                    sources.append(node["id"])

            return {
                "context_accumulated": new_context,
                "sources_used": sources,
                "iterations": state["iterations"] + 1,
            }
        except Exception as e:
            return {
                "error": str(e),
                "is_context_sufficient": True,
            }  # Force end on error

    async def evaluate_context_node(self, state: GraphState):
        """Evaluates if the fetched context is sufficient to answer the query."""
        if state.get("error"):
            return {"is_context_sufficient": True}

        if state["iterations"] >= 3:
            # Max iterations reached, force synthesis
            return {"is_context_sufficient": True}

        # Format the context for the LLM
        context_str = json.dumps(
            [p.get("summary", "No summary") for p in state["context_accumulated"]]
        )

        prompt = f"""
        User Query: {state["query"]}
        
        Current Context:
        {context_str}
        
        Is the provided context sufficient to answer the query accurately? 
        Answer with ONLY 'YES' or 'NO'.
        """
        response = await self.llm_generator.generate(
            prompt, "You are a context evaluator."
        )

        is_sufficient = "yes" in response.lower()
        return {"is_context_sufficient": is_sufficient}

    def route_evaluation(self, state: GraphState):
        if state.get("error"):
            return "end"
        if state["is_context_sufficient"]:
            return "synthesize"
        return "fetch_context"

    async def synthesize_node(self, state: GraphState):
        """Generates the final answer."""
        if state.get("error"):
            return {
                "final_answer": f"Error occurred during reasoning: {state['error']}"
            }

        context_str = json.dumps(state["context_accumulated"], indent=2)
        prompt = f"""
        User Query: {state["query"]}
        
        Context Evidence:
        {context_str}
        
        Please provide a comprehensive answer based ONLY on the provided context.
        """
        answer = await self.llm_generator.generate(
            prompt,
            "You are a senior software architect AI. Answer questions using only the provided context.",
        )
        return {"final_answer": answer}
