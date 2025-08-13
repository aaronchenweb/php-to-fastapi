# core/__init__.py
"""Core components for PHP to FastAPI converter."""

from .detector import PHPProjectDetector, ProjectValidationResult
from .orchestrator import ConversionOrchestrator
from .llm_client import LLMClient, LLMResponse
from .user_interface import UserInterface

__all__ = [
    'PHPProjectDetector',
    'ProjectValidationResult',
    'ConversionOrchestrator', 
    'LLMClient',
    'LLMResponse',
    'UserInterface'
]