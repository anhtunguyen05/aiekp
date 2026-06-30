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

    def ingest_file_metadata(self, metadata: FileMetadata):
        """
        Upserts the file metadata, including its classes and functions, into Neo4j.
        """
        # 1. Merge File Node
        file_query = """
        MERGE (f:File {path: $file_path})
        SET f.language = $language
        RETURN f
        """
        self._execute_query(
            file_query, {"file_path": metadata.file_path, "language": metadata.language}
        )

        # 2. Merge Standalone Functions and link to File
        for func in metadata.standalone_functions:
            func_id = f"{metadata.file_path}::{func.name}"
            func_query = """
            MATCH (f:File {path: $file_path})
            MERGE (func:Function {id: $func_id})
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
                },
            )

        # 3. Merge Classes and link to File
        for cls in metadata.classes:
            cls_id = f"{metadata.file_path}::{cls.name}"
            cls_query = """
            MATCH (f:File {path: $file_path})
            MERGE (c:Class {id: $cls_id})
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
                },
            )

            # 4. Merge Methods and link to Class
            for method in cls.methods:
                method_id = f"{cls_id}::{method.name}"
                method_query = """
                MATCH (c:Class {id: $cls_id})
                MERGE (m:Function {id: $method_id})
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
                    },
                )
