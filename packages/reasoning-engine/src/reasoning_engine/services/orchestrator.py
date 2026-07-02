import json
from typing import TypedDict, List, Dict, Any, Optional, Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from reasoning_engine.ports.outbound import IContextFetcher, ILLMGenerator


class GraphState(TypedDict):
    query: str
    session_id: str
    context_accumulated: List[Dict[str, Any]]
    sources_used: List[str]
    messages: List[BaseMessage]
    error: Optional[str]
    next_agent: str


class ReasoningOrchestrator:
    def __init__(self, context_fetcher: IContextFetcher, llm_generator: ILLMGenerator):
        self.context_fetcher = context_fetcher
        self.llm_generator = llm_generator
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(GraphState)

        workflow.add_node("fetch_context", self.fetch_context_node)
        workflow.add_node("supervisor", self.supervisor_node)
        workflow.add_node("architect", self.architect_node)
        workflow.add_node("qa", self.qa_node)
        workflow.add_node("security", self.security_node)

        # Entry point is always fetching context first
        workflow.set_entry_point("fetch_context")

        workflow.add_edge("fetch_context", "supervisor")

        # Supervisor routes to agents or END
        workflow.add_conditional_edges(
            "supervisor",
            lambda state: state["next_agent"],
            {
                "architect": "architect",
                "qa": "qa",
                "security": "security",
                "FINISH": END,
            },
        )

        # Specialized agents always report back to the supervisor
        workflow.add_edge("architect", "supervisor")
        workflow.add_edge("qa", "supervisor")
        workflow.add_edge("security", "supervisor")

        return workflow.compile()

    async def fetch_context_node(self, state: GraphState):
        """Fetches context from Context Intelligence Engine."""
        try:
            # For simplicity, we just do one broad fetch at the start
            payload = await self.context_fetcher.fetch_context(
                state["query"], ["class", "method", "function", "interface"]
            )
            
            new_context = state.get("context_accumulated", [])
            new_context.append(payload)

            sources = state.get("sources_used", [])
            for node in payload.get("nodes", []):
                if node["id"] not in sources:
                    sources.append(node["id"])

            return {
                "context_accumulated": new_context,
                "sources_used": sources,
                "error": None
            }
        except Exception as e:
            return {
                "error": str(e),
                "next_agent": "FINISH"
            }

    async def supervisor_node(self, state: GraphState):
        """
        The supervisor decides which agent to call next based on the query and conversation history,
        or synthesize the final answer and call FINISH.
        """
        if state.get("error"):
            return {"next_agent": "FINISH"}

        # If no messages yet, this is the first supervisor pass. We should route to at least one expert.
        # Alternatively, if there's enough history, it routes to FINISH.
        history_str = "\\n".join([f"{type(m).__name__}: {m.content}" for m in state.get("messages", [])])
        
        prompt = f"""
        User Query: {state['query']}
        
        Conversation History:
        {history_str}
        
        You are the Supervisor. Your job is to route this query to a specialized agent (architect, qa, security) to gather insights based on the retrieved code context.
        If you have enough information to answer the query fully, output 'FINISH' and your final synthesized answer.
        
        Respond ONLY with a JSON object in this format:
        {{"next_agent": "architect|qa|security|FINISH", "final_answer": "your answer if FINISH, else null"}}
        """
        response_str = await self.llm_generator.generate(prompt, "You are a JSON-only supervisor agent.")
        
        try:
            import re
            
            # Remove markdown code blocks if they exist
            cleaned_response = re.sub(r'```json\s*', '', response_str)
            cleaned_response = re.sub(r'```\s*', '', cleaned_response)
            
            json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
            if json_match:
                response = json.loads(json_match.group(0))
            else:
                response = json.loads(cleaned_response)
            
            next_agent = response.get("next_agent", "FINISH")
            final_answer = response.get("final_answer", "")
            
            if next_agent == "FINISH":
                # Add the final answer to messages
                new_msg = AIMessage(content=final_answer, name="Supervisor")
                return {"next_agent": "FINISH", "messages": state.get("messages", []) + [new_msg]}
            else:
                return {"next_agent": next_agent}
        except Exception as e:
            # Fallback
            new_msg = AIMessage(content=f"Error parsing supervisor output: {str(e)}\nRaw LLM output was:\n{response_str}", name="Supervisor")
            return {"next_agent": "FINISH", "messages": state.get("messages", []) + [new_msg]}

    async def _specialized_agent_node(self, state: GraphState, role_name: str, system_prompt: str):
        context_str = json.dumps(state["context_accumulated"], indent=2)
        history_str = "\\n".join([f"{type(m).__name__}: {m.content}" for m in state.get("messages", [])])
        
        prompt = f"""
        User Query: {state['query']}
        
        Context Evidence:
        {context_str}
        
        Previous Analysis:
        {history_str}
        
        Please provide your analysis based ONLY on the provided context.
        """
        answer = await self.llm_generator.generate(prompt, system_prompt)
        
        new_msg = AIMessage(content=answer, name=role_name)
        return {"messages": state.get("messages", []) + [new_msg]}

    async def architect_node(self, state: GraphState):
        return await self._specialized_agent_node(
            state, "Architect", "You are a Software Architect AI. Focus on system design, SOLID principles, dependencies, and structural integrity."
        )

    async def qa_node(self, state: GraphState):
        return await self._specialized_agent_node(
            state, "QA", "You are a QA Engineer AI. Focus on edge cases, testability, logic bugs, and potential failures."
        )

    async def security_node(self, state: GraphState):
        return await self._specialized_agent_node(
            state, "Security", "You are a Security Expert AI. Focus on identifying vulnerabilities (XSS, SQLi, insecure data, etc.)"
        )
