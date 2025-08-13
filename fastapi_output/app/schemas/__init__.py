"""
Base Pydantic schemas for the application.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    model_config = ConfigDict(from_attributes=True)


class TimestampedSchema(BaseSchema):
    """Schema with timestamp fields."""
    created_at: datetime
    updated_at: Optional[datetime] = None


class IDSchema(BaseSchema):
    """Schema with ID field."""
    id: int


class BaseResponse(BaseSchema):
    """Base response schema."""
    success: bool = True
    message: Optional[str] = None


class ErrorResponse(BaseSchema):
    """Error response schema."""
    success: bool = False
    error: str
    detail: Optional[str] = None
