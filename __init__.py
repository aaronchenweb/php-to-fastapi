# php_to_fastapi/__init__.py
"""
PHP to FastAPI Converter
AI-powered tool for converting PHP web APIs to FastAPI applications.
"""

__version__ = "1.0.0-dev"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Main imports
from .cli import main

__all__ = ['main']


# php_to_fastapi/config/__init__.py
"""Configuration module for PHP to FastAPI converter."""

from .config.settings import Settings
from .config.prompts import Prompts

__all__ = ['Settings', 'Prompts']


# php_to_fastapi/core/__init__.py
"""Core modules for PHP to FastAPI converter."""

from .core.detector import PHPProjectDetector
from .core.orchestrator import ConversionOrchestrator
from .core.user_interface import UserInterface
from .core.llm_client import LLMClient

__all__ = [
    'PHPProjectDetector',
    'ConversionOrchestrator', 
    'UserInterface',
    'LLMClient'
]


# php_to_fastapi/utils/__init__.py
"""Utility modules for PHP to FastAPI converter."""

from .utils.validation import validate_project_path, validate_output_path

__all__ = ['validate_project_path', 'validate_output_path']
