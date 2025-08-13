# generators/fastapi_generator.py
"""Main FastAPI project generator that coordinates all code generation."""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional

from .shared import GeneratedFile, GenerationResult


class FastAPIGenerator:
    """Main generator for FastAPI projects."""
    
    def __init__(self):
        # Import generators here to avoid circular imports
        from .route_generator import RouteGenerator
        from .model_generator import ModelGenerator
        from .config_generator import ConfigGenerator
        
        self.route_generator = RouteGenerator()
        self.model_generator = ModelGenerator()
        self.config_generator = ConfigGenerator()
        
        # Template cache
        self._templates = {}
        
        # Generation statistics
        self.stats = {
            'files_generated': 0,
            'lines_generated': 0,
            'errors': 0,
            'warnings': 0
        }
    
    def generate_project(self, 
                        analysis_result: Dict[str, Any],
                        planning_result: Dict[str, Any],
                        output_path: str) -> GenerationResult:
        """Generate complete FastAPI project."""
        
        result = GenerationResult(success=False)
        
        try:
            # Create output directory structure
            self._create_directory_structure(output_path, planning_result)
            
            # Generate core application files
            core_files = self._generate_core_files(output_path, analysis_result, planning_result)
            result.generated_files.extend(core_files)
            
            # Generate configuration files
            config_files = self.config_generator.generate_config_files(analysis_result, planning_result)
            result.generated_files.extend(config_files)
            
            # Generate database models
            model_files = self.model_generator.generate_model_files(analysis_result, planning_result)
            result.generated_files.extend(model_files)
            
            # Generate API routes
            route_files = self.route_generator.generate_route_files(analysis_result, planning_result)
            result.generated_files.extend(route_files)
            
            # Generate schemas
            schema_files = self._generate_schema_files(output_path, analysis_result, planning_result)
            result.generated_files.extend(schema_files)
            
            # Generate services
            service_files = self._generate_service_files(output_path, analysis_result, planning_result)
            result.generated_files.extend(service_files)
            
            # Generate utility files
            utility_files = self._generate_utility_files(output_path, analysis_result, planning_result)
            result.generated_files.extend(utility_files)
            
            # Generate test files
            test_files = self._generate_test_files(output_path, analysis_result, planning_result)
            result.generated_files.extend(test_files)
            
            # Generate documentation files
            doc_files = self._generate_documentation_files(output_path, analysis_result, planning_result)
            result.generated_files.extend(doc_files)
            
            # Write all files to disk
            self._write_files_to_disk(output_path, result.generated_files)
            
            # Calculate statistics
            result.total_files = len(result.generated_files)
            result.total_lines = sum(f.content.count('\n') + 1 for f in result.generated_files)
            
            result.success = True
            
        except Exception as e:
            result.errors.append(f"Generation failed: {str(e)}")
            result.success = False
        
        return result
    
    def _create_directory_structure(self, output_path: str, planning_result: Dict[str, Any]) -> None:
        """Create the directory structure for the FastAPI project."""
        # Create standard FastAPI project structure
        directories = [
            "app",
            "app/api",
            "app/api/v1", 
            "app/api/v1/endpoints",
            "app/core",
            "app/db",
            "app/models",
            "app/schemas",
            "app/services",
            "app/utils",
            "app/middleware", 
            "app/exceptions",
            "tests",
            "alembic",
            "alembic/versions",
            "logs",
            "uploads"
        ]
        
        for directory in directories:
            Path(output_path, directory).mkdir(parents=True, exist_ok=True)
    
    def _generate_core_files(self, output_path: str, 
                           analysis_result: Dict[str, Any], 
                           planning_result: Dict[str, Any]) -> List[GeneratedFile]:
        """Generate core FastAPI application files."""
        files = []
        
        # Generate main.py
        main_content = self._generate_main_file(analysis_result, planning_result)
        files.append(GeneratedFile(
            path="main.py",
            content=main_content,
            file_type="python",
            description="FastAPI application entry point"
        ))
        
        # Generate app/__init__.py
        app_init_content = self._generate_app_init(analysis_result, planning_result)
        files.append(GeneratedFile(
            path="app/__init__.py",
            content=app_init_content,
            file_type="python",
            description="Application package initialization"
        ))
        
        # Generate dependencies.py
        deps_content = self._generate_dependencies_file(analysis_result, planning_result)
        files.append(GeneratedFile(
            path="app/api/dependencies.py",
            content=deps_content,
            file_type="python",
            description="FastAPI dependencies and injections"
        ))
        
        return files
    
    def _generate_main_file(self, analysis_result: Dict[str, Any], planning_result: Dict[str, Any]) -> str:
        """Generate the main FastAPI application file."""
        project_info = analysis_result.get('project_info', {})
        
        template = '''"""
FastAPI application entry point.
Generated from PHP project conversion.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.api import api_router

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.DEBUG else None,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Configure CORS
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "FastAPI application is running",
        "version": settings.VERSION,
        "docs_url": "/docs" if settings.DEBUG else None
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.PROJECT_NAME}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
    )
'''
        
        return template.strip()
    
    def _generate_app_init(self, analysis_result: Dict[str, Any], planning_result: Dict[str, Any]) -> str:
        """Generate app package initialization."""
        template = '''"""
FastAPI application package.
Converted from PHP project.
"""

__version__ = "1.0.0"
__description__ = "FastAPI application converted from PHP"
'''
        
        return template.strip()
    
    def _generate_dependencies_file(self, analysis_result: Dict[str, Any], planning_result: Dict[str, Any]) -> str:
        """Generate FastAPI dependencies file."""
        template = '''"""
FastAPI dependencies and dependency injection.
"""

from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import verify_token
from app.db.database import SessionLocal

# Security schemes
security = HTTPBearer()


def get_db() -> Generator:
    """Get database session."""
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> dict:
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = verify_token(token)
        if payload is None:
            raise credentials_exception
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
    except Exception:
        raise credentials_exception
    
    # TODO: Get user from database
    # user = get_user_by_id(db, user_id=user_id)
    # if user is None:
    #     raise credentials_exception
    
    return {"id": user_id}


async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Get current active user."""
    # TODO: Check if user is active
    # if not current_user.is_active:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[dict]:
    """Get user from token if provided, otherwise return None."""
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None
'''
        
        return template.strip()
    
    # Include all other methods from the original file with GeneratedFile usage...
    # (Truncated for brevity - the methods would remain the same but use shared.GeneratedFile)
    
    def _generate_schema_files(self, output_path: str, 
                             analysis_result: Dict[str, Any], 
                             planning_result: Dict[str, Any]) -> List[GeneratedFile]:
        """Generate Pydantic schema files."""
        files = []
        
        # Generate base schemas
        base_schema_content = '''"""
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
'''
        
        files.append(GeneratedFile(
            path="app/schemas/__init__.py",
            content=base_schema_content,
            file_type="python",
            description="Base Pydantic schemas"
        ))
        
        return files
    
    def _generate_service_files(self, output_path: str, 
                              analysis_result: Dict[str, Any], 
                              planning_result: Dict[str, Any]) -> List[GeneratedFile]:
        """Generate service layer files."""
        files = []
        
        base_service_content = '''"""
Base service classes for business logic.
"""

from typing import Generic, TypeVar, Type, Optional, List, Any
from sqlalchemy.orm import Session

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base service class with common CRUD operations."""
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """Get a single record by ID."""
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get multiple records with pagination."""
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record."""
        obj_in_data = obj_in.dict() if hasattr(obj_in, 'dict') else obj_in
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, *, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        """Update an existing record."""
        obj_data = obj_in.dict(exclude_unset=True) if hasattr(obj_in, 'dict') else obj_in
        
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def remove(self, db: Session, *, id: int) -> ModelType:
        """Delete a record."""
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj
'''
        
        files.append(GeneratedFile(
            path="app/services/__init__.py",
            content=base_service_content,
            file_type="python",
            description="Base service classes"
        ))
        
        return files
    
    def _generate_utility_files(self, output_path: str, 
                              analysis_result: Dict[str, Any], 
                              planning_result: Dict[str, Any]) -> List[GeneratedFile]:
        """Generate utility files."""
        return []  # Simplified for now
    
    def _generate_test_files(self, output_path: str, 
                           analysis_result: Dict[str, Any], 
                           planning_result: Dict[str, Any]) -> List[GeneratedFile]:
        """Generate test files."""
        return []  # Simplified for now
    
    def _generate_documentation_files(self, output_path: str, 
                                    analysis_result: Dict[str, Any], 
                                    planning_result: Dict[str, Any]) -> List[GeneratedFile]:
        """Generate documentation files."""
        return []  # Simplified for now
    
    def _write_files_to_disk(self, output_path: str, files: List[GeneratedFile]) -> None:
        """Write all generated files to disk."""
        for file in files:
            file_path = Path(output_path) / file.path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file.content)