"""
Main API router for version 1.
"""

from fastapi import APIRouter
from app.api.v1.endpoints.example import router as example_router

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(example_router, prefix="/example", tags=["Example"])


@api_router.get("/")
async def api_root():
    """API root endpoint."""
    return {
        "message": "FastAPI v1 API",
        "version": "1.0.0",
        "endpoints": "See /docs for available endpoints"
    }