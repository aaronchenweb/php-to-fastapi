"""
Models package for the FastAPI application.
"""

# Import all models for Alembic auto-generation
from app.db.base import Base

from .example import *

# Make sure all models are imported for Alembic
__all__ = ["Base"]