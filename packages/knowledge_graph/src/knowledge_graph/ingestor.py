from metadata_extractor.models import FileMetadata
from .neo4j_client import Neo4jGraphManager
from .qdrant_client import QdrantVectorManager
from .embedder import Embedder


class GraphIngestor:
    """
    Orchestrates the ingestion of FileMetadata into Neo4j and Qdrant.
    """

    def __init__(
        self,
        neo4j_manager: Neo4jGraphManager,
        qdrant_manager: QdrantVectorManager,
        embedder: Embedder,
    ):
        self.neo4j = neo4j_manager
        self.qdrant = qdrant_manager
        self.embedder = embedder

        # Ensure collection exists
        self.qdrant.ensure_collection("code_nodes", self.embedder.vector_size)

    def ingest(self, metadata: FileMetadata, tenant_id: str):
        """
        Synchronously ingest the metadata into Graph and Vector DBs.
        """
        # 1. Ingest relational data into Neo4j
        self.neo4j.ingest_file_metadata(metadata, tenant_id)

        # 2. Extract texts to embed for Qdrant
        # We will embed functions and classes (especially their docstrings) for semantic search.
        texts_to_embed = []
        payloads = []

        # Standalone functions
        for func in metadata.standalone_functions:
            text = f"Function: {func.name}\n"
            if func.docstring:
                text += f"Docstring: {func.docstring}\n"
            text += f"Parameters: {', '.join(func.parameters)}"

            texts_to_embed.append(text)
            payloads.append(
                {
                    "id": f"{metadata.file_path}::{func.name}",
                    "type": "function",
                    "name": func.name,
                    "file_path": metadata.file_path,
                }
            )

        # Classes
        for cls in metadata.classes:
            cls_text = f"Class: {cls.name}\n"
            if cls.docstring:
                cls_text += f"Docstring: {cls.docstring}\n"

            texts_to_embed.append(cls_text)
            payloads.append(
                {
                    "id": f"{metadata.file_path}::{cls.name}",
                    "type": "class",
                    "name": cls.name,
                    "file_path": metadata.file_path,
                }
            )

            # Methods inside classes
            for method in cls.methods:
                method_text = f"Method: {method.name} of Class: {cls.name}\n"
                if method.docstring:
                    method_text += f"Docstring: {method.docstring}\n"
                method_text += f"Parameters: {', '.join(method.parameters)}"

                texts_to_embed.append(method_text)
                payloads.append(
                    {
                        "id": f"{metadata.file_path}::{cls.name}::{method.name}",
                        "type": "method",
                        "name": method.name,
                        "class_name": cls.name,
                        "file_path": metadata.file_path,
                    }
                )

        # 3. Generate embeddings
        if texts_to_embed:
            vectors = self.embedder.embed(texts_to_embed)

            # 4. Upsert to Qdrant
            self.qdrant.upsert_vectors(
                collection_name="code_nodes",
                vectors=vectors,
                payloads=payloads,
                tenant_id=tenant_id,
            )
