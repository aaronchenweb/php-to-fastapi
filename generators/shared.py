# generators/shared.py
"""Shared data classes for code generation."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class GeneratedFile:
    """Represents a generated file."""
    path: str
    content: str
    file_type: str  # python, config, template, etc.
    description: str
    php_source_files: List[str] = field(default_factory=list)


@dataclass
class GenerationResult:
    """Result of the generation process."""
    success: bool
    generated_files: List[GeneratedFile] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    total_files: int = 0
    total_lines: int = 0


@dataclass
class ModelField:
    """Represents a model field."""
    name: str
    python_type: str
    nullable: bool = True
    primary_key: bool = False
    foreign_key: Optional[str] = None
    default_value: Optional[str] = None
    unique: bool = False
    index: bool = False
    description: str = ""


@dataclass
class ModelRelationship:
    """Represents a model relationship."""
    name: str
    target_model: str
    relationship_type: str  # one_to_one, one_to_many, many_to_one, many_to_many
    foreign_key: Optional[str] = None
    back_populates: Optional[str] = None
    cascade: Optional[str] = None


@dataclass
class ModelInfo:
    """Complete model information."""
    name: str
    table_name: str
    fields: List[ModelField]
    relationships: List[ModelRelationship]
    php_source_table: str
    description: str = ""


@dataclass
class RouteInfo:
    """Information about a route to be generated."""
    method: str
    path: str
    function_name: str
    description: str
    parameters: List[dict]
    requires_auth: bool
    request_body_schema: Optional[str]
    response_schema: Optional[str]
    php_source: str