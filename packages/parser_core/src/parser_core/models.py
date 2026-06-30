from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class AiekpAstNode(BaseModel):
    """
    Normalized AST Node that wraps a language-specific node (like tree-sitter).
    This ensures that downstream consumers don't rely on raw parser implementations.
    """
    type: str = Field(..., description="The type of the node (e.g., 'class_definition', 'function_definition')")
    text: str = Field(..., description="The raw source code corresponding to this node")
    start_byte: int = Field(..., description="Start byte position in the source code")
    end_byte: int = Field(..., description="End byte position in the source code")
    start_point: tuple[int, int] = Field(..., description="Start point as (row, column)")
    end_point: tuple[int, int] = Field(..., description="End point as (row, column)")
    children: List['AiekpAstNode'] = Field(default_factory=list, description="Child nodes")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Additional language-specific properties")

AiekpAstNode.model_rebuild()
