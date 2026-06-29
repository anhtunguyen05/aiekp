from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class Repository(BaseModel):
    """Represents a target software repository."""
    uri: str = Field(..., description="URI of the repository (e.g., local path or git URL)")
    branch: Optional[str] = Field(None, description="Branch name if applicable")
    commit_hash: Optional[str] = Field(None, description="Commit hash for the specific state")
    language_stack: List[str] = Field(default_factory=list, description="List of primary programming languages")

class ASTNode(BaseModel):
    """A structured representation of a specific piece of source code."""
    id: str = Field(..., description="Unique identifier for the node")
    type: str = Field(..., description="Type of the node (e.g., Function, Class, Import)")
    start_line: int = Field(..., description="Start line of the node in the source file")
    end_line: int = Field(..., description="End line of the node in the source file")
    raw_content: str = Field(..., description="Raw string content of the code block")
    file_path: str = Field(..., description="Path to the file containing this node")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Extracted structural info above AST")

class KnowledgeNode(BaseModel):
    """The fundamental building block of the Engineering Memory Graph."""
    id: str = Field(..., description="Unique node identifier")
    label: str = Field(..., description="Graph node label (e.g., File, Class, Method, ADR)")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Node attributes")
    embedding: Optional[List[float]] = Field(None, description="Vector embedding for semantic search")

class Evidence(BaseModel):
    """A packaged wrapper around Knowledge Nodes or AST fragments to prove an AI assertion."""
    source_id: str = Field(..., description="ID of the Knowledge Node or AST Node")
    content: str = Field(..., description="The relevant content snippet")
    type: str = Field(..., description="Type of evidence (e.g., source_code, graph_path, adr)")
