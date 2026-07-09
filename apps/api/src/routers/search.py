from fastapi import APIRouter, Depends
from knowledge_graph import QdrantVectorManager, LocalSentenceTransformerEmbedder
from src.dependencies import get_qdrant_manager, get_embedder, get_current_user, CurrentUser
from src.schemas import SearchRequest, SearchResponse, SearchResultItem

router = APIRouter(prefix="/search", tags=["search"])


@router.post("/", response_model=SearchResponse)
async def semantic_search(
    request: SearchRequest,
    current_user: CurrentUser = Depends(get_current_user),
    vector_manager: QdrantVectorManager = Depends(get_qdrant_manager),
    embedder: LocalSentenceTransformerEmbedder = Depends(get_embedder),
):
    # 1. Embed the query
    query_vector = embedder.embed([request.query])[0]

    # 2. Search in Qdrant
    results = vector_manager.search(
        collection_name="code_nodes", query_vector=query_vector, tenant_id=current_user.tenant_id, limit=request.top_k
    )

    # 3. Format results
    items = []
    for res in results:
        # Note: res is likely a ScoredPoint from qdrant_client
        payload = res.payload or {}
        items.append(
            SearchResultItem(
                node_id=payload.get("id", ""),
                content=payload.get("content", ""),
                score=res.score,
                metadata={
                    "type": payload.get("type", ""),
                    "name": payload.get("name", ""),
                    "file_path": payload.get("file_path", ""),
                },
            )
        )

    return SearchResponse(query=request.query, results=items)
