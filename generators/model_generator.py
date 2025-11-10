# generators/model_generator.py
"""Generates SQLAlchemy models from PHP database models and schema analysis."""

import os
import re
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

from config.settings import Settings
from core.user_interface import UserInterface
from generators.llm_assisted_generator import LLMAssistedGenerator, ConversionRequest, ConversionContext


class ModelGenerator:
    """Generates SQLAlchemy models from PHP models and database analysis."""
    
    def __init__(self, settings: Settings, ui: UserInterface):
        self.settings = settings
        self.ui = ui
        self.llm_generator = LLMAssistedGenerator(settings, ui)
        
        # PHP to Python type mappings
        self.type_mappings = {
            'int': 'Integer',
            'integer': 'Integer',
            'bigint': 'BigInteger',
            'tinyint': 'SmallInteger',
            'smallint': 'SmallInteger',
            'varchar': 'String',
            'char': 'String',
            'text': 'Text',
            'longtext': 'Text',
            'mediumtext': 'Text',
            'json': 'JSON',
            'decimal': 'Numeric',
            'float': 'Float',
            'double': 'Float',
            'boolean': 'Boolean',
            'bool': 'Boolean',
            'datetime': 'DateTime',
            'timestamp': 'DateTime',
            'date': 'Date',
            'time': 'Time',
            'blob': 'LargeBinary',
            'binary': 'LargeBinary'
        }
        
        # Eloquent relationship patterns
        self.relationship_patterns = {
            'hasOne': 'one-to-one',
            'hasMany': 'one-to-many',
            'belongsTo': 'many-to-one',
            'belongsToMany': 'many-to-many',
            'morphTo': 'polymorphic',
            'morphMany': 'polymorphic'
        }
        
        # Common model patterns
        self.model_patterns = [
            r'class\s+(\w+)\s+extends\s+(?:Model|Eloquent|ActiveRecord)',
            r'protected\s+\$table\s*=\s*[\'"](\w+)[\'"]',
            r'protected\s+\$fillable\s*=\s*\[(.*?)\]',
            r'protected\s+\$hidden\s*=\s*\[(.*?)\]',
            r'protected\s+\$casts\s*=\s*\[(.*?)\]'
        ]
    
    def generate_models(self, db_info: Dict[str, Any], planning_result: Dict[str, Any], 
                       output_path: str) -> List[str]:
        """Generate SQLAlchemy models from database analysis."""
        try:
            if not db_info.get('table_references'):
                self.ui.debug("No database tables found, skipping model generation")
                return []
            
            self.ui.debug(f"Generating models for {len(db_info.get('table_references', []))} tables")
            
            # Create conversion context
            context = self._create_model_context(db_info, planning_result)
            
            generated_files = []
            
            # Generate base model if needed
            base_model_file = self._generate_base_model(output_path)
            if base_model_file:
                generated_files.append(base_model_file)
            
            # Process table references
            table_models = self._analyze_table_models(db_info)
            
            # Generate individual model files
            for table_name, model_info in table_models.items():
                model_file = self._generate_single_model(
                    table_name, model_info, context, output_path
                )
                if model_file:
                    generated_files.append(model_file)
            
            # Generate models __init__.py
            init_file = self._generate_models_init(table_models, output_path)
            if init_file:
                generated_files.append(init_file)
            
            return generated_files
            
        except Exception as e:
            self.ui.error(f"Failed to generate models: {str(e)}")
            return []
    
    def _create_model_context(self, db_info: Dict[str, Any], 
                             planning_result: Dict[str, Any]) -> ConversionContext:
        """Create conversion context for model generation."""
        database_type = db_info.get('database_type', 'mysql')
        orm_framework = db_info.get('orm_framework', 'none')
        
        return ConversionContext(
            framework='sqlalchemy',
            database_type=database_type,
            auth_method='none',
            python_dependencies=['sqlalchemy', 'pydantic'],
            endpoint_style='orm_models',
            project_structure='models'
        )
    
    def _analyze_table_models(self, db_info: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Analyze table references and create model information."""
        table_models = {}
        
        # Process table references
        table_refs = db_info.get('table_references', [])
        
        for table_name in table_refs:
            model_info = {
                'table_name': table_name,
                'class_name': self._table_name_to_class_name(table_name),
                'columns': self._infer_table_columns(table_name, db_info),
                'relationships': self._infer_table_relationships(table_name, db_info),
                'php_model_class': None,
                'has_timestamps': True,  # Default assumption
                'primary_key': 'id'  # Default assumption
            }
            
            table_models[table_name] = model_info
        
        # Process detected models if available
        models_detected = db_info.get('models_detected', [])
        for model in models_detected:
            table_name = model.get('table')
            model_class = model.get('model_class')
            
            if table_name in table_models:
                table_models[table_name]['php_model_class'] = model_class
        
        return table_models
    
    def _generate_single_model(self, table_name: str, model_info: Dict[str, Any],
                              context: ConversionContext, output_path: str) -> Optional[str]:
        """Generate a single SQLAlchemy model."""
        try:
            class_name = model_info['class_name']
            
            # Create PHP model representation for LLM
            php_model_code = self._create_php_model_representation(model_info)
            
            # Create conversion request
            request = ConversionRequest(
                php_code=php_model_code,
                conversion_type='model',
                context=context,
                file_path=f"{class_name}.php",
                additional_instructions=self._create_model_instructions(model_info)
            )
            
            # Convert using LLM
            result = self.llm_generator.convert_php_batch(request)
            
            if not result.success:
                # Fallback to template-based generation
                self.ui.debug(f"LLM conversion failed for {class_name}, using template")
                sqlalchemy_code = self._generate_model_template(model_info)
            else:
                sqlalchemy_code = result.python_code
            
            # Write model file
            model_file = self._write_model_file(class_name, sqlalchemy_code, output_path)
            return model_file
            
        except Exception as e:
            self.ui.error(f"Failed to generate model {table_name}: {str(e)}")
            return None
    
    def _create_php_model_representation(self, model_info: Dict[str, Any]) -> str:
        """Create PHP model representation for LLM conversion."""
        class_name = model_info['class_name']
        table_name = model_info['table_name']
        columns = model_info['columns']
        relationships = model_info['relationships']
        
        php_code = f"""<?php

class {class_name} extends Model
{{
    protected $table = '{table_name}';
    
    protected $fillable = [
"""
        
        # Add fillable columns
        fillable_columns = [col['name'] for col in columns if col['name'] not in ['id', 'created_at', 'updated_at']]
        for col in fillable_columns:
            php_code += f"        '{col}',\n"
        
        php_code += """    ];
    
    protected $casts = [
"""
        
        # Add casts for special types
        for col in columns:
            if col['type'] in ['json', 'boolean', 'datetime']:
                cast_type = col['type']
                if cast_type == 'boolean':
                    cast_type = 'bool'
                php_code += f"        '{col['name']}' => '{cast_type}',\n"
        
        php_code += """    ];
"""
        
        # Add relationships
        for rel in relationships:
            rel_type = rel['type']
            related_model = rel['related_model']
            
            if rel_type == 'hasMany':
                php_code += f"""
    public function {rel['name']}()
    {{
        return $this->hasMany({related_model}::class);
    }}
"""
            elif rel_type == 'belongsTo':
                php_code += f"""
    public function {rel['name']}()
    {{
        return $this->belongsTo({related_model}::class);
    }}
"""
            elif rel_type == 'hasOne':
                php_code += f"""
    public function {rel['name']}()
    {{
        return $this->hasOne({related_model}::class);
    }}
"""
        
        php_code += "\n}\n"
        
        return php_code
    
    def _create_model_instructions(self, model_info: Dict[str, Any]) -> str:
        """Create specific instructions for model conversion."""
        class_name = model_info['class_name']
        table_name = model_info['table_name']
        
        return f"""
Convert this PHP Eloquent model '{class_name}' to a SQLAlchemy model:

Requirements:
1. Create a SQLAlchemy model class inheriting from Base
2. Set __tablename__ = '{table_name}'
3. Define all columns with appropriate SQLAlchemy types
4. Add proper constraints (nullable, unique, index, etc.)
5. Define relationships using SQLAlchemy relationship()
6. Add timestamps (created_at, updated_at) if they exist
7. Use proper foreign key constraints
8. Add __repr__ method for debugging
9. Follow SQLAlchemy best practices

Column Mapping:
- Use proper SQLAlchemy column types
- Add indexes for foreign keys and commonly queried fields
- Set nullable=False for required fields
- Add unique=True for unique fields

Relationship Mapping:
- hasMany → one-to-many relationship
- belongsTo → many-to-one relationship  
- hasOne → one-to-one relationship
- belongsToMany → many-to-many relationship with association table

Example structure:
```python
class {class_name}(Base):
    __tablename__ = "{table_name}"
    
    id = Column(Integer, primary_key=True, index=True)
    # ... other columns
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    # related_items = relationship("RelatedModel", back_populates="parent")
```
"""
    
    def _generate_model_template(self, model_info: Dict[str, Any]) -> str:
        """Generate model template when LLM conversion fails."""
        class_name = model_info['class_name']
        table_name = model_info['table_name']
        columns = model_info['columns']
        relationships = model_info['relationships']
        
        template = f'''"""SQLAlchemy model for {table_name}."""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base

class {class_name}(Base):
    __tablename__ = "{table_name}"

    id = Column(Integer, primary_key=True, index=True)
'''
        
        # Add columns
        for col in columns:
            if col['name'] in ['id', 'created_at', 'updated_at']:
                continue
                
            col_type = self._get_sqlalchemy_type(col['type'], col.get('length'))
            nullable = col.get('nullable', True)
            unique = col.get('unique', False)
            index = col.get('index', False)
            
            template += f'    {col["name"]} = Column({col_type}'
            
            if not nullable:
                template += ', nullable=False'
            if unique:
                template += ', unique=True'
            if index:
                template += ', index=True'
                
            template += ')\n'
        
        # Add timestamps if model has them
        if model_info.get('has_timestamps', True):
            template += '''    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
'''
        
        # Add relationships
        for rel in relationships:
            rel_name = rel['name']
            related_model = rel['related_model']
            
            if rel['type'] == 'one-to-many':
                template += f'    {rel_name} = relationship("{related_model}", back_populates="{table_name}")\n'
            elif rel['type'] == 'many-to-one':
                template += f'    {rel_name}_id = Column(Integer, ForeignKey("{rel["foreign_table"]}.id"))\n'
                template += f'    {rel_name} = relationship("{related_model}", back_populates="{table_name}s")\n'
        
        template += f'''
    def __repr__(self):
        return f"<{class_name}(id={{self.id}})>"
'''
        
        return template
    
    def _write_model_file(self, class_name: str, model_code: str, output_path: str) -> Optional[str]:
        """Write model to file."""
        try:
            models_dir = os.path.join(output_path, 'app', 'models')
            os.makedirs(models_dir, exist_ok=True)
            
            # Convert class name to file name
            file_name = re.sub(r'([A-Z])', r'_\1', class_name).lower().lstrip('_') + '.py'
            file_path = os.path.join(models_dir, file_name)
            
            # Enhance model code with imports
            enhanced_code = self._enhance_model_code(model_code)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(enhanced_code)
            
            self.ui.debug(f"Generated model file: {file_path}")
            return file_path
            
        except Exception as e:
            self.ui.error(f"Failed to write model file {class_name}: {str(e)}")
            return None
    
    def _generate_base_model(self, output_path: str) -> Optional[str]:
        """Generate base model file."""
        try:
            models_dir = os.path.join(output_path, 'app', 'models')
            os.makedirs(models_dir, exist_ok=True)
            
            file_path = os.path.join(models_dir, 'base.py')
            
            base_code = '''"""Base model with common functionality."""

from typing import Any
from sqlalchemy.ext.declarative import as_declarative, declared_attr

@as_declarative()
class Base:
    id: Any
    __name__: str
    
    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
'''
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(base_code)
            
            return file_path
            
        except Exception as e:
            self.ui.error(f"Failed to generate base model: {str(e)}")
            return None
    
    def _generate_models_init(self, table_models: Dict[str, Dict[str, Any]], 
                             output_path: str) -> Optional[str]:
        """Generate models __init__.py file."""
        try:
            models_dir = os.path.join(output_path, 'app', 'models')
            file_path = os.path.join(models_dir, '__init__.py')
            
            init_code = '''"""Models package."""

from .base import Base
'''
            
            # Import all models
            for table_name, model_info in table_models.items():
                class_name = model_info['class_name']
                file_name = re.sub(r'([A-Z])', r'_\1', class_name).lower().lstrip('_')
                init_code += f'from .{file_name} import {class_name}\n'
            
            init_code += '\n__all__ = [\n    "Base",\n'
            
            for model_info in table_models.values():
                init_code += f'    "{model_info["class_name"]}",\n'
            
            init_code += ']\n'
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(init_code)
            
            return file_path
            
        except Exception as e:
            self.ui.error(f"Failed to generate models __init__.py: {str(e)}")
            return None
    
    def _table_name_to_class_name(self, table_name: str) -> str:
        """Convert table name to class name."""
        # Remove common prefixes
        clean_name = table_name
        if clean_name.startswith('tbl_'):
            clean_name = clean_name[4:]
        
        # Convert to PascalCase
        words = clean_name.split('_')
        class_name = ''.join(word.capitalize() for word in words)
        
        # Remove plural 's' from end (simple heuristic)
        if class_name.endswith('s') and len(class_name) > 3:
            class_name = class_name[:-1]
        
        return class_name
    
    def _infer_table_columns(self, table_name: str, db_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Infer table columns from available information."""
        # Default columns that most tables have
        columns = [
            {'name': 'id', 'type': 'int', 'nullable': False, 'primary_key': True},
        ]
        
        # Add common columns based on table name patterns
        if any(pattern in table_name for pattern in ['user', 'account', 'member']):
            columns.extend([
                {'name': 'username', 'type': 'varchar', 'length': 100, 'nullable': False, 'unique': True},
                {'name': 'email', 'type': 'varchar', 'length': 255, 'nullable': False, 'unique': True},
                {'name': 'password', 'type': 'varchar', 'length': 255, 'nullable': False},
                {'name': 'is_active', 'type': 'boolean', 'nullable': False, 'default': True},
            ])
        elif any(pattern in table_name for pattern in ['post', 'article', 'blog']):
            columns.extend([
                {'name': 'title', 'type': 'varchar', 'length': 255, 'nullable': False},
                {'name': 'content', 'type': 'text', 'nullable': True},
                {'name': 'status', 'type': 'varchar', 'length': 50, 'nullable': False},
                {'name': 'user_id', 'type': 'int', 'nullable': False, 'foreign_key': 'users.id'},
            ])
        elif any(pattern in table_name for pattern in ['category', 'tag']):
            columns.extend([
                {'name': 'name', 'type': 'varchar', 'length': 100, 'nullable': False},
                {'name': 'description', 'type': 'text', 'nullable': True},
                {'name': 'slug', 'type': 'varchar', 'length': 100, 'nullable': False, 'unique': True},
            ])
        else:
            # Generic columns
            columns.extend([
                {'name': 'name', 'type': 'varchar', 'length': 255, 'nullable': False},
                {'name': 'description', 'type': 'text', 'nullable': True},
            ])
        
        # Add timestamps (most tables have these)
        columns.extend([
            {'name': 'created_at', 'type': 'datetime', 'nullable': True},
            {'name': 'updated_at', 'type': 'datetime', 'nullable': True},
        ])
        
        return columns
    
    def _infer_table_relationships(self, table_name: str, db_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Infer table relationships from table name and patterns."""
        relationships = []
        
        # Common relationship patterns
        if table_name == 'users':
            relationships.extend([
                {'name': 'posts', 'type': 'one-to-many', 'related_model': 'Post', 'foreign_table': 'posts'},
                {'name': 'comments', 'type': 'one-to-many', 'related_model': 'Comment', 'foreign_table': 'comments'},
            ])
        elif table_name == 'posts':
            relationships.extend([
                {'name': 'user', 'type': 'many-to-one', 'related_model': 'User', 'foreign_table': 'users'},
                {'name': 'comments', 'type': 'one-to-many', 'related_model': 'Comment', 'foreign_table': 'comments'},
                {'name': 'category', 'type': 'many-to-one', 'related_model': 'Category', 'foreign_table': 'categories'},
            ])
        elif table_name == 'comments':
            relationships.extend([
                {'name': 'user', 'type': 'many-to-one', 'related_model': 'User', 'foreign_table': 'users'},
                {'name': 'post', 'type': 'many-to-one', 'related_model': 'Post', 'foreign_table': 'posts'},
            ])
        
        return relationships
    
    def _get_sqlalchemy_type(self, php_type: str, length: Optional[int] = None) -> str:
        """Get SQLAlchemy type from PHP type."""
        base_type = self.type_mappings.get(php_type.lower(), 'String')
        
        if base_type == 'String' and length:
            return f'String({length})'
        elif base_type == 'Numeric' and length:
            return f'Numeric(precision={length})'
        
        return base_type
    
    def _enhance_model_code(self, model_code: str) -> str:
        """Enhance model code with proper imports."""
        imports = '''from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base
'''
        
        # Check if imports are already present
        if 'from sqlalchemy import' not in model_code:
            return imports + '\n\n' + model_code
        
        return model_code