from context_engine.domain.models import EvidencePayload
from context_engine.ports.inbound import IContextService
from context_engine.ports.outbound import IIntentAnalyzer, IKnowledgeEngineClient

class ContextService(IContextService):
    """
    Core orchestrator for Context Intelligence.
    Wires intent analysis with knowledge retrieval.
    """
    def __init__(self, intent_analyzer: IIntentAnalyzer, knowledge_client: IKnowledgeEngineClient):
        self.intent_analyzer = intent_analyzer
        self.knowledge_client = knowledge_client

    async def retrieve_context(self, query: str) -> EvidencePayload:
        # 1. Analyze Intent
        intent = await self.intent_analyzer.analyze(query)
        
        # 2. Perform Semantic Search to find entry points
        # Use the extracted semantic keywords joined by space for better vector match
        search_query = " ".join(intent.semantic_keywords) if intent.semantic_keywords else intent.query
        search_results = await self.knowledge_client.search_nodes(query=search_query, top_k=3)
        
        # 3. Expand Context via Graph (fetch details for top nodes)
        nodes = []
        for result in search_results:
            node_id = result.get("node_id")
            if node_id:
                node_detail = await self.knowledge_client.get_node_details(node_id)
                
                # In a more advanced implementation, we would also loop through node_detail.relationships 
                # to fetch N hops of connected nodes. For MVP, we just include the node itself 
                # (which already contains its relationships list).
                nodes.append(node_detail)
                
        # 4. Assemble Payload
        summary = f"Retrieved {len(nodes)} relevant context nodes for intent: {intent.target_types}"
        
        return EvidencePayload(
            original_query=query,
            intent=intent,
            nodes=nodes,
            summary=summary
        )
