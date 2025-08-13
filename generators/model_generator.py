# generators/model_generator.py
"""Generates SQLAlchemy models from PHP database analysis."""

import re
from typing import Dict, List, Any, Optional, Tuple

from .shared import GeneratedFile, ModelField, ModelRelationship, ModelInfo


class ModelGenerator:
    """Generates SQLAlchemy models from database analysis."""
    
    def __init__(self):
        # PHP to SQLAlchemy type mappings
        self.type_mappings = {
            'int': 'Integer',
            'integer': 'Integer',
            'bigint': 'BigInteger',
            'smallint': 'SmallInteger',
            'tinyint': 'SmallInteger',
            'varchar': 'String',
            'char': 'String',
            'text': 'Text',
            'longtext': 'Text',
            'mediumtext': 'Text',
            'datetime': 'DateTime',
            'timestamp': 'DateTime',
            'date': 'Date',
            'time': 'Time',
            'boolean': 'Boolean',
            'bool': 'Boolean',
            'decimal': 'Numeric',
            'float': 'Float',
            'double': 'Float',
            'json': 'JSON',
            'blob': 'LargeBinary',
            'enum': 'Enum'
        }
    
    def generate_model_files(self, 
                           analysis_result: Dict[str, Any], 
                           planning_result: Dict[str, Any]) -> List[GeneratedFile]:
        """Generate all model files."""
        files = []
        
        # Generate base model
        base_model_content = self._generate_base_model()
        files.append(GeneratedFile(
            path="app/db/base.py",
            content=base_model_content,
            file_type="python",
            description="Base model class with common fields"
        ))
        
        # Generate database configuration
        database_content = self._generate_database_config(analysis_result, planning_result)
        files.append(GeneratedFile(
            path="app/db/database.py",
            content=database_content,
            file_type="python",
            description="Database configuration and session management"
        ))
        
        # Generate db __init__.py
        db_init_content = '''"""Database package."""\n\nfrom .base import Base\nfrom .database import SessionLocal, engine, get_db\n\n__all__ = ["Base", "SessionLocal", "engine", "get_db"]'''
        files.append(GeneratedFile(
            path="app/db/__init__.py",
            content=db_init_content,
            file_type="python",
            description="Database package initialization"
        ))
        
        # Generate models from database analysis
        database_analysis = analysis_result.get('database_analysis', {})
        tables = database_analysis.get('tables', [])
        
        if tables:
            # Group tables by domain for better organization
            table_groups = self._group_tables_by_domain(tables)
            
            for domain, domain_tables in table_groups.items():
                models_content = self._generate_domain_models(domain, domain_tables, analysis_result)
                
                files.append(GeneratedFile(
                    path=f"app/models/{domain}.py",
                    content=models_content,
                    file_type="python",
                    description=f"Models for {domain} domain",
                    php_source_files=[table.get('name', '') for table in domain_tables]
                ))
        else:
            # Generate example models if no tables found
            example_models_content = self._generate_example_models()
            files.append(GeneratedFile(
                path="app/models/example.py",
                content=example_models_content,
                file_type="python",
                description="Example models for reference"
            ))
        
        # Generate models __init__.py
        models_init_content = self._generate_models_init(files)
        files.append(GeneratedFile(
            path="app/models/__init__.py",
            content=models_init_content,
            file_type="python",
            description="Models package initialization"
        ))
        
        return files
    
    def _generate_base_model(self) -> str:
        """Generate base model class."""
        template = '''"""
Base model class with common fields and functionality.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import as_declarative

Base = declarative_base()


@as_declarative()
class BaseModel:
    """Base model with common fields."""
    
    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name."""
        # Convert CamelCase to snake_case
        import re
        name = re.sub('(.)([A-Z][a-z]+)', r'\\1_\\2', cls.__name__)
        return re.sub('([a-z0-9])([A-Z])', r'\\1_\\2', name).lower()
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<{self.__class__.__name__}(id={self.id})>"
    
    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create model instance from dictionary."""
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})


# For backward compatibility
Base = BaseModel
'''
        
        return template.strip()
    
    def _generate_database_config(self, 
                                analysis_result: Dict[str, Any], 
                                planning_result: Dict[str, Any]) -> str:
        """Generate database configuration."""
        template = '''"""
Database configuration and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings

# Database engine configuration
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite configuration
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.DEBUG
    )
else:
    # PostgreSQL/MySQL configuration
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        echo=settings.DEBUG
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables."""
    from app.db.base import Base
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all tables."""
    from app.db.base import Base
    Base.metadata.drop_all(bind=engine)
'''
        
        return template.strip()
    
    def _group_tables_by_domain(self, tables: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group tables by domain/functionality."""
        domains = {
            'user': [],
            'auth': [],
            'content': [],
            'system': [],
            'business': []
        }
        
        for table in tables:
            table_name = table.get('name', '').lower()
            
            # Categorize based on table name patterns
            if any(keyword in table_name for keyword in ['user', 'profile', 'account', 'person']):
                domains['user'].append(table)
            elif any(keyword in table_name for keyword in ['auth', 'token', 'session', 'login', 'permission', 'role']):
                domains['auth'].append(table)
            elif any(keyword in table_name for keyword in ['post', 'article', 'content', 'page', 'blog', 'news']):
                domains['content'].append(table)
            elif any(keyword in table_name for keyword in ['config', 'setting', 'system', 'log', 'audit']):
                domains['system'].append(table)
            else:
                domains['business'].append(table)
        
        # Remove empty domains
        return {k: v for k, v in domains.items() if v}
    
    def _generate_domain_models(self, 
                              domain: str, 
                              tables: List[Dict[str, Any]], 
                              analysis_result: Dict[str, Any]) -> str:
        """Generate models for a specific domain."""
        models = []
        
        for table in tables:
            model_info = self._analyze_table_for_model(table, analysis_result)
            model_code = self._generate_single_model(model_info)
            models.append(model_code)
        
        # Generate imports
        imports = self._generate_model_imports(tables)
        
        # Generate docstring
        docstring = f'"""\nModels for {domain} domain.\nGenerated from PHP database analysis.\n"""\n\n'
        
        return docstring + imports + '\n\n' + '\n\n\n'.join(models)
    
    def _analyze_table_for_model(self, 
                                table: Dict[str, Any], 
                                analysis_result: Dict[str, Any]) -> ModelInfo:
        """Analyze table and create model info."""
        table_name = table.get('name', '')
        model_name = self._table_to_model_name(table_name)
        
        # Extract fields
        fields = self._extract_model_fields(table)
        
        # Extract relationships (simplified)
        relationships = []
        
        return ModelInfo(
            name=model_name,
            table_name=table_name,
            fields=fields,
            relationships=relationships,
            php_source_table=table_name,
            description=f"Model for {table_name} table"
        )
    
    def _table_to_model_name(self, table_name: str) -> str:
        """Convert table name to model class name."""
        # Remove plural suffix
        name = table_name
        if name.endswith('ies'):
            name = name[:-3] + 'y'
        elif name.endswith('es'):
            name = name[:-2]
        elif name.endswith('s') and not name.endswith('ss'):
            name = name[:-1]
        
        # Convert snake_case to PascalCase
        return ''.join(word.capitalize() for word in name.split('_'))
    
    def _extract_model_fields(self, table: Dict[str, Any]) -> List[ModelField]:
        """Extract fields from table information."""
        fields = []
        estimated_columns = table.get('estimated_columns', [])
        
        # Process each column
        for column_def in estimated_columns:
            field = self._parse_column_definition(column_def)
            if field:
                fields.append(field)
        
        return fields
    
    def _parse_column_definition(self, column_def: str) -> Optional[ModelField]:
        """Parse column definition string."""
        if not column_def:
            return None
        
        # Simple parsing - could be improved
        parts = column_def.split()
        if not parts:
            return None
        
        column_name = parts[0].strip('()')
        column_type = parts[1] if len(parts) > 1 else 'string'
        
        # Remove type parameters like varchar(255)
        base_type = re.sub(r'\(\d+\)', '', column_type.lower())
        
        # Map to SQLAlchemy type
        sqlalchemy_type = self._map_column_type(base_type, column_type)
        
        # Determine field properties
        nullable = 'not null' not in column_def.lower()
        unique = 'unique' in column_def.lower()
        primary_key = column_name.lower() == 'id' or 'primary key' in column_def.lower()
        
        # Check for foreign key pattern
        foreign_key = None
        if column_name.endswith('_id') and column_name != 'id':
            # Infer foreign key relationship
            referenced_table = column_name[:-3] + 's'  # Simple pluralization
            foreign_key = f"{referenced_table}.id"
        
        return ModelField(
            name=column_name,
            python_type=sqlalchemy_type,
            nullable=nullable,
            primary_key=primary_key,
            foreign_key=foreign_key,
            unique=unique,
            index=unique or primary_key,
            description=f"Column from {column_def}"
        )
    
    def _map_column_type(self, base_type: str, full_type: str) -> str:
        """Map column type to SQLAlchemy type."""
        # Extract size if present
        size_match = re.search(r'\((\d+)\)', full_type)
        size = size_match.group(1) if size_match else None
        
        # Map base type
        mapped_type = self.type_mappings.get(base_type, 'String')
        
        # Add size for string types
        if mapped_type == 'String' and size:
            return f"String({size})"
        elif mapped_type == 'String' and not size:
            return "String(255)"
        
        return mapped_type
    
    def _generate_single_model(self, model_info: ModelInfo) -> str:
        """Generate code for a single model."""
        class_definition = f'class {model_info.name}(Base):'
        docstring = f'    """{model_info.description}."""\n'
        
        # Table name
        table_name_line = f'    __tablename__ = "{model_info.table_name}"\n'
        
        # Fields
        field_lines = []
        for field in model_info.fields:
            field_line = self._generate_field_definition(field)
            field_lines.append(f'    {field_line}')
        
        # Combine all parts
        parts = [class_definition, docstring, '', table_name_line]
        
        if field_lines:
            parts.append('    # Fields')
            parts.extend(field_lines)
        
        return '\n'.join(parts)
    
    def _generate_field_definition(self, field: ModelField) -> str:
        """Generate SQLAlchemy field definition."""
        column_args = []
        
        # Add type
        column_args.append(field.python_type)
        
        # Add constraints
        if field.primary_key:
            column_args.append('primary_key=True')
        
        if not field.nullable:
            column_args.append('nullable=False')
        
        if field.unique:
            column_args.append('unique=True')
        
        if field.index and not field.primary_key and not field.unique:
            column_args.append('index=True')
        
        if field.foreign_key:
            column_args.append(f'ForeignKey("{field.foreign_key}")')
        
        if field.default_value:
            if field.default_value.startswith('func.'):
                column_args.append(f'server_default={field.default_value}')
            else:
                column_args.append(f'default={field.default_value}')
        
        column_def = f"Column({', '.join(column_args)})"
        
        return f"{field.name} = {column_def}"
    
    def _generate_model_imports(self, tables: List[Dict[str, Any]]) -> str:
        """Generate imports for model file."""
        imports = [
            'from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float, Numeric',
            'from sqlalchemy.orm import relationship',
            'from sqlalchemy.sql import func',
            '',
            'from app.db.base import Base'
        ]
        
        return '\n'.join(imports)
    
    def _generate_example_models(self) -> str:
        """Generate example models when no tables are found."""
        template = '''"""
Example models for reference.
Replace with your actual models based on database analysis.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class User(Base):
    """Example user model."""
    
    __tablename__ = "users"
    
    # Fields
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    items = relationship("Item", back_populates="owner")


class Item(Base):
    """Example item model."""
    
    __tablename__ = "items"
    
    # Fields
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    owner = relationship("User", back_populates="items")
'''
        
        return template.strip()
    
    def _generate_models_init(self, model_files: List[GeneratedFile]) -> str:
        """Generate models package __init__.py."""
        imports = []
        
        for file in model_files:
            if file.path.startswith('app/models/') and file.path.endswith('.py') and file.path != 'app/models/__init__.py':
                module_name = file.path.replace('app/models/', '').replace('.py', '')
                if module_name not in ['base', 'database']:
                    imports.append(f"from .{module_name} import *")
        
        template = f'''"""
Models package for the FastAPI application.
"""

# Import all models for Alembic auto-generation
from app.db.base import Base

{chr(10).join(imports)}

# Make sure all models are imported for Alembic
__all__ = ["Base"]
'''
        
        return template.strip()