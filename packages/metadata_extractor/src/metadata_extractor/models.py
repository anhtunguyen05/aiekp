from typing import List, Optional
from pydantic import BaseModel, Field


class FunctionMetadata(BaseModel):
    """Metadata extracted for a function or method."""

    name: str = Field(..., description="Name of the function")
    docstring: Optional[str] = Field(None, description="Docstring of the function")
    parameters: List[str] = Field(
        default_factory=list, description="List of parameter names/signatures"
    )
    return_type: Optional[str] = Field(
        None, description="Return type annotation if any"
    )
    start_line: int = Field(..., description="Starting line number (0-indexed)")
    end_line: int = Field(..., description="Ending line number (0-indexed)")


class ClassMetadata(BaseModel):
    """Metadata extracted for a class."""

    name: str = Field(..., description="Name of the class")
    docstring: Optional[str] = Field(None, description="Docstring of the class")
    methods: List[FunctionMetadata] = Field(
        default_factory=list, description="Methods defined in the class"
    )
    start_line: int = Field(..., description="Starting line number (0-indexed)")
    end_line: int = Field(..., description="Ending line number (0-indexed)")


class FileMetadata(BaseModel):
    """Metadata extracted for an entire source code file."""

    file_path: str = Field(..., description="Path to the source file")
    language: str = Field(..., description="Programming language of the file")
    classes: List[ClassMetadata] = Field(
        default_factory=list, description="Classes defined in the file"
    )
    standalone_functions: List[FunctionMetadata] = Field(
        default_factory=list, description="Functions defined outside any class"
    )
