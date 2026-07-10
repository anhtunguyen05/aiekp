from typing import Dict, Any
from neo4j import GraphDatabase

from metadata_extractor.models import FileMetadata


class Neo4jGraphManager:
    """
    Manages the creation of nodes and relationships in Neo4j.
    """

    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def _execute_query(self, query: str, parameters: Dict[str, Any] = None):
        with self.driver.session() as session:
            return session.run(query, parameters).data()

    def clear_database(self, tenant_id: str = None):
        """
        Deletes nodes and relationships for a specific tenant, or all if tenant_id is None.
        """
        if tenant_id:
            self._execute_query(
                "MATCH (n {tenant_id: $tenant_id}) DETACH DELETE n",
                {"tenant_id": tenant_id},
            )
        else:
            self._execute_query("MATCH (n) DETACH DELETE n")

    def ingest_file_metadata(self, metadata: FileMetadata, tenant_id: str):
        """
        Upserts the file metadata, including its classes and functions, into Neo4j with tenant_id.
        """
        # 1. Merge File Node
        file_query = """
        MERGE (f:File {path: $file_path, tenant_id: $tenant_id})
        SET f.language = $language
        RETURN f
        """
        self._execute_query(
            file_query,
            {
                "file_path": metadata.file_path,
                "language": metadata.language,
                "tenant_id": tenant_id,
            },
        )

        # 2. Merge Standalone Functions and link to File
        for func in metadata.standalone_functions:
            func_id = f"{metadata.file_path}::{func.name}"
            func_query = """
            MATCH (f:File {path: $file_path, tenant_id: $tenant_id})
            MERGE (func:Function {id: $func_id, tenant_id: $tenant_id})
            SET func.name = $name,
                func.docstring = $docstring,
                func.parameters = $parameters,
                func.return_type = $return_type
            MERGE (f)-[:DEFINES]->(func)
            """
            self._execute_query(
                func_query,
                {
                    "file_path": metadata.file_path,
                    "func_id": func_id,
                    "name": func.name,
                    "docstring": func.docstring,
                    "parameters": func.parameters,
                    "return_type": func.return_type,
                    "tenant_id": tenant_id,
                },
            )

        # 3. Merge Classes and link to File
        for cls in metadata.classes:
            cls_id = f"{metadata.file_path}::{cls.name}"
            cls_query = """
            MATCH (f:File {path: $file_path, tenant_id: $tenant_id})
            MERGE (c:Class {id: $cls_id, tenant_id: $tenant_id})
            SET c.name = $name,
                c.docstring = $docstring
            MERGE (f)-[:DEFINES]->(c)
            """
            self._execute_query(
                cls_query,
                {
                    "file_path": metadata.file_path,
                    "cls_id": cls_id,
                    "name": cls.name,
                    "docstring": cls.docstring,
                    "tenant_id": tenant_id,
                },
            )

            # 4. Merge Methods and link to Class
            for method in cls.methods:
                method_id = f"{cls_id}::{method.name}"
                method_query = """
                MATCH (c:Class {id: $cls_id, tenant_id: $tenant_id})
                MERGE (m:Function {id: $method_id, tenant_id: $tenant_id})
                SET m.name = $name,
                    m.docstring = $docstring,
                    m.parameters = $parameters,
                    m.return_type = $return_type,
                    m.is_method = true
                MERGE (c)-[:CONTAINS]->(m)
                """
                self._execute_query(
                    method_query,
                    {
                        "cls_id": cls_id,
                        "method_id": method_id,
                        "name": method.name,
                        "docstring": method.docstring,
                        "parameters": method.parameters,
                        "return_type": method.return_type,
                        "tenant_id": tenant_id,
                    },
                )
