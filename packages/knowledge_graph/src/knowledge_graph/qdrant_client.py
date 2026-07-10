from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
import uuid


class QdrantVectorManager:
    """
    Manages vector collections and points in Qdrant.
    """

    def __init__(self, host: str = "localhost", port: int = 6333):
        self.client = QdrantClient(host=host, port=port)

    def ensure_collection(self, collection_name: str, vector_size: int):
        """
        Creates the collection if it doesn't already exist.
        """
        if not self.client.collection_exists(collection_name=collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )

    def upsert_vectors(
        self,
        collection_name: str,
        vectors: List[List[float]],
        payloads: List[Dict[str, Any]],
        tenant_id: str,
    ):
        """
        Upserts vectors and their associated metadata payloads into Qdrant with tenant_id.
        """
        if not vectors or not payloads or len(vectors) != len(payloads):
            return

        points = []
        for vector, payload in zip(vectors, payloads):
            # Inject tenant_id into payload
            payload["tenant_id"] = tenant_id

            point_id = str(
                uuid.uuid5(uuid.NAMESPACE_DNS, payload.get("id", str(uuid.uuid4())))
            )

            points.append(PointStruct(id=point_id, vector=vector, payload=payload))

        self.client.upsert(collection_name=collection_name, points=points)

    def search(
        self,
        collection_name: str,
        query_vector: List[float],
        tenant_id: str,
        limit: int = 10,
    ):
        """
        Search for nearest vectors in Qdrant for a specific tenant.
        """
        tenant_filter = Filter(
            must=[FieldCondition(key="tenant_id", match=MatchValue(value=tenant_id))]
        )
        return self.client.query_points(
            collection_name=collection_name,
            query=query_vector,
            query_filter=tenant_filter,
            limit=limit,
        ).points
