# generators/__init__.py
"""Code generators for PHP to FastAPI conversion."""

# Import shared data classes first
from .shared import GeneratedFile, GenerationResult

# Import generator classes (avoid circular imports by being explicit)
from .fastapi_generator import FastAPIGenerator
from .route_generator import RouteGenerator
from .model_generator import ModelGenerator
from .config_generator import ConfigGenerator

__all__ = [
    'GeneratedFile',
    'GenerationResult',
    'FastAPIGenerator',
    'RouteGenerator',
    'ModelGenerator',
    'ConfigGenerator'
]