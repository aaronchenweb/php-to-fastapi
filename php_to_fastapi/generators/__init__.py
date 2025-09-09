# generators/__init__.py
"""Code generators for PHP to FastAPI conversion."""

# Import shared data classes first
from .shared import GeneratedFile, GenerationResult
from .auth_converter import AuthConverter
from .business_logic_translator import BusinessLogicTranslator
from .code_batch_processor import CodeBatchProcessor, CodeBatch, BatchGroup
from .config_generator import ConfigGenerator
from .endpoint_converter import EndpointConverter
from .fastapi_generator import FastAPIGenerator
from .llm_assisted_generator import LLMAssistedGenerator
from .model_generator import ModelGenerator
from .project_assembler import ProjectAssembler
from .route_generator import RouteGenerator
from .schema_generator import SchemaGenerator

__all__ = [
    'GeneratedFile',
    'GenerationResult',
    'AuthConverter',
    'BusinessLogicTranslator',
    'CodeBatchProcessor',
    'CodeBatch',
    'BatchGroup',
    'ConfigGenerator',
    'EndpointConverter',
    'FastAPIGenerator',
    'LLMAssistedGenerator',
    'ModelGenerator',
    'ProjectAssembler',
    'RouteGenerator',
    'SchemaGenerator'
]