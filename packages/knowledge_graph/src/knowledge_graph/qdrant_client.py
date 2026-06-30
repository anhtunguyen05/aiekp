from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
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
    ):
        """
        Upserts vectors and their associated metadata payloads into Qdrant.
        """
        if not vectors or not payloads or len(vectors) != len(payloads):
            return

        points = []
        for vector, payload in zip(vectors, payloads):
            # We use a UUID string derived from the payload id or a random one to avoid collision.
            # Using MD5 of the unique ID can give a deterministic UUID, but for simplicity we generate uuid4
            # if we don't do deterministic, upserts with same metadata will duplicate.
            # So let's make it deterministic if `id` is in payload.
            point_id = str(
                uuid.uuid5(uuid.NAMESPACE_DNS, payload.get("id", str(uuid.uuid4())))
            )

            points.append(PointStruct(id=point_id, vector=vector, payload=payload))

        self.client.upsert(collection_name=collection_name, points=points)
