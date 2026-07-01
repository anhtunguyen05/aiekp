from knowledge_graph import (
    Neo4jGraphManager,
    QdrantVectorManager,
    LocalSentenceTransformerEmbedder,
    GraphIngestor,
    Embedder,
)
from context_engine.ports.inbound import IContextService
from context_engine.adapters.keyword_intent import KeywordIntentAdapter
from context_engine.adapters.http_knowledge_client import HttpKnowledgeEngineAdapter
from context_engine.services.context_service import ContextService
from reasoning_engine.ports.inbound import IReasoningService
from reasoning_engine.adapters.context_fetcher import ContextEngineHttpAdapter
from reasoning_engine.adapters.llm_generator import LangChainLLMAdapter
from reasoning_engine.services.reasoning_service import ReasoningService
from src.config import settings

# Global instances that will be managed by lifespan
_neo4j_manager: Neo4jGraphManager | None = None
_qdrant_manager: QdrantVectorManager | None = None
_embedder: Embedder | None = None
_ingestor: GraphIngestor | None = None


async def init_dependencies() -> None:
    global _neo4j_manager, _qdrant_manager, _embedder, _ingestor
    _neo4j_manager = Neo4jGraphManager(
        uri=settings.neo4j_uri,
        user=settings.neo4j_user,
        password=settings.neo4j_password,
    )

    _qdrant_manager = QdrantVectorManager(
        host=settings.qdrant_host, port=settings.qdrant_port
    )

    from knowledge_graph import MockEmbedder

    # Use MockEmbedder for local development to avoid heavy PyTorch dependencies
    # unless specified otherwise in production config.
    try:
        if getattr(settings, "use_mock_embedder", True):
            _embedder = MockEmbedder()
        else:
            _embedder = LocalSentenceTransformerEmbedder()
    except ImportError:
        print("sentence-transformers not found. Falling back to MockEmbedder.")
        _embedder = MockEmbedder()
    _ingestor = GraphIngestor(
        neo4j_manager=_neo4j_manager, qdrant_manager=_qdrant_manager, embedder=_embedder
    )


async def close_dependencies() -> None:
    global _neo4j_manager
    if _neo4j_manager:
        _neo4j_manager.close()


def get_neo4j_manager() -> Neo4jGraphManager:
    if not _neo4j_manager:
        raise RuntimeError("Neo4j manager not initialized")
    return _neo4j_manager


def get_qdrant_manager() -> QdrantVectorManager:
    if not _qdrant_manager:
        raise RuntimeError("Qdrant manager not initialized")
    return _qdrant_manager


def get_embedder() -> Embedder:
    if not _embedder:
        raise RuntimeError("Embedder not initialized")
    return _embedder


def get_ingestor() -> GraphIngestor:
    if not _ingestor:
        raise RuntimeError("Ingestor not initialized")
    return _ingestor


# --- Context Engine Dependencies ---


def get_context_service() -> IContextService:
    intent_adapter = KeywordIntentAdapter()
    knowledge_client = HttpKnowledgeEngineAdapter(base_url="http://localhost:8000")
    return ContextService(
        intent_analyzer=intent_adapter, knowledge_client=knowledge_client
    )


# --- Reasoning Engine Dependencies ---


def get_reasoning_service() -> IReasoningService:
    context_fetcher = ContextEngineHttpAdapter(base_url="http://localhost:8000")
    llm_generator = LangChainLLMAdapter(model_name="gpt-4o-mini", temperature=0.0)
    return ReasoningService(
        context_fetcher=context_fetcher, llm_generator=llm_generator
    )
