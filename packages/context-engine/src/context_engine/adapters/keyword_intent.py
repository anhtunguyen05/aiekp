import re
from context_engine.domain.models import RetrievalIntent
from context_engine.ports.outbound import IIntentAnalyzer

class KeywordIntentAdapter(IIntentAnalyzer):
    """
    A basic MVP intent analyzer that uses heuristics to extract keywords and target types.
    """
    async def analyze(self, query: str) -> RetrievalIntent:
        query_lower = query.lower()
        
        # Simple heuristic to determine target types
        target_types = []
        if any(word in query_lower for word in ["class", "struct", "model"]):
            target_types.append("class")
        if any(word in query_lower for word in ["function", "method", "def"]):
            target_types.append("method")
        if any(word in query_lower for word in ["module", "file", "script"]):
            target_types.append("module")
            
        if not target_types:
            target_types = ["class", "method", "function"]  # Default
            
        # Very simple keyword extraction (remove common stop words)
        stop_words = {"what", "where", "how", "is", "the", "in", "does", "do", "a", "an", "of", "to", "for", "code", "logic", "handled", "implemented"}
        words = re.findall(r'\b\w+\b', query_lower)
        keywords = [w for w in words if w not in stop_words]
        
        return RetrievalIntent(
            query=query,
            target_types=target_types,
            semantic_keywords=keywords,
            graph_expansion_depth=1
        )
