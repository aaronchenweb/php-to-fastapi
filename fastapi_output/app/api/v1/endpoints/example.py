"""
example API endpoints.
Converted from PHP endpoints.
"""

from typing import List, Optionalfrom fastapi import APIRouter, Depends, HTTPException, statusfrom sqlalchemy.orm import Sessionfrom app.api.dependencies import get_db, get_current_userfrom app.schemas.example import exampleCreate, exampleUpdate, exampleResponsefrom app.services.example_service import example_servicerouter = APIRouter()

@router.get("/", response_model=List[exampleResponse])
async def get_example_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> List[exampleResponse]:
    """Get example list."""
    items = example_service.get_multi(db, skip=skip, limit=limit)
    return items

@router.get("/{item_id}", response_model=exampleResponse)
async def get_example(
    item_id: int,
    db: Session = Depends(get_db)
) -> exampleResponse:
    """Get example by ID."""
    item = example_service.get(db, id=item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="example not found")
    return item

@router.post("/", response_model=exampleResponse)
async def create_example(
    item: exampleCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> exampleResponse:
    """Create new example."""
    item = example_service.create(db, obj_in=item)
    return item

@router.put("/{item_id}", response_model=exampleResponse)
async def update_example(
    item_id: int,
    item: exampleUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> exampleResponse:
    """Update example."""
    db_item = example_service.get(db, id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="example not found")
    item = example_service.update(db, db_obj=db_item, obj_in=item)
    return item

@router.delete("/{item_id}", response_model=exampleResponse)
async def delete_example(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> exampleResponse:
    """Delete example."""
    item = example_service.remove(db, id=item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="example not found")
    return item