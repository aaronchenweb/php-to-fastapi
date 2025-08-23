# generators/schema_generator.py
"""Generates Pydantic schemas for FastAPI request/response validation."""

import os
import re
from typing import Dict, Any, List, Optional, Tuple, Set
from pathlib import Path

from config.settings import Settings
from core.user_interface import UserInterface
from generators.llm_assisted_generator import LLMAssistedGenerator, ConversionRequest, ConversionContext


class SchemaGenerator:
    """Generates Pydantic schemas from API analysis and model information."""
    
    def __init__(self, settings: Settings, ui: UserInterface):
        self.settings = settings
        self.ui = ui
        self.llm_generator = LLMAssistedGenerator(settings, ui)
        
        # PHP to Python type mappings for Pydantic
        self.pydantic_type_mappings = {
            'int': 'int',
            'integer': 'int',
            'bigint': 'int',
            'tinyint': 'int',
            'smallint': 'int',
            'varchar': 'str',
            'char': 'str',
            'string': 'str',
            'text': 'str',
            'longtext': 'str',
            'mediumtext': 'str',
            'json': 'Dict[str, Any]',
            'decimal': 'Decimal',
            'float': 'float',
            'double': 'float',
            'boolean': 'bool',
            'bool': 'bool',
            'datetime': 'datetime',
            'timestamp': 'datetime',
            'date': 'date',
            'time': 'time',
            'email': 'EmailStr',
            'url': 'HttpUrl',
            'uuid': 'UUID4'
        }
        
        # Common validation patterns
        self.validation_patterns = {
            'email': r'.*email.*',
            'password': r'.*password.*',
            'phone': r'.*phone.*',
            'url': r'.*url.*',
            'uuid': r'.*uuid.*|.*id$',
            'slug': r'.*slug.*',
            'token': r'.*token.*'
        }
        
        # HTTP method to schema type mapping
        self.method_schema_mapping = {
            'GET': ['response'],
            'POST': ['create', 'response'],
            'PUT': ['update', 'response'],
            'PATCH': ['update', 'response'],
            'DELETE': ['response']
        }
    
    def generate_schemas(self, api_info: Dict[str, Any], planning_result: Dict[str, Any], 
                        output_path: str) -> List[str]:
        """Generate Pydantic schemas from API analysis."""
        try:
            endpoints_detail = api_info.get('endpoints_detail', [])
            
            if not endpoints_detail:
                self.ui.debug("No API endpoints found, generating basic schemas")
                return self._generate_basic_schemas(output_path)
            
            self.ui.debug(f"Generating schemas for {len(endpoints_detail)} endpoints")
            
            # Create conversion context
            context = self._create_schema_context(api_info, planning_result)
            
            generated_files = []
            
            # Analyze endpoints to extract schema requirements
            schema_requirements = self._analyze_schema_requirements(endpoints_detail)
            
            # Generate base schemas
            base_schemas_file = self._generate_base_schemas(output_path)
            if base_schemas_file:
                generated_files.append(base_schemas_file)
            
            # Generate entity-specific schemas
            for entity, entity_info in schema_requirements.items():
                schema_file = self._generate_entity_schemas(
                    entity, entity_info, context, output_path
                )
                if schema_file:
                    generated_files.append(schema_file)
            
            # Generate auth schemas if authentication is used
            if api_info.get('authentication_methods'):
                auth_schemas_file = self._generate_auth_schemas(output_path)
                if auth_schemas_file:
                    generated_files.append(auth_schemas_file)
            
            # Generate schemas __init__.py
            init_file = self._generate_schemas_init(schema_requirements, output_path)
            if init_file:
                generated_files.append(init_file)
            
            return generated_files
            
        except Exception as e:
            self.ui.error(f"Failed to generate schemas: {str(e)}")
            return []
    
    def _create_schema_context(self, api_info: Dict[str, Any], 
                              planning_result: Dict[str, Any]) -> ConversionContext:
        """Create conversion context for schema generation."""
        return ConversionContext(
            framework='pydantic',
            database_type='postgresql',
            auth_method='jwt',
            python_dependencies=['pydantic', 'email-validator'],
            endpoint_style='pydantic_models',
            project_structure='schemas'
        )
    
    def _analyze_schema_requirements(self, endpoints: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Analyze endpoints to determine schema requirements."""
        schema_requirements = {}
        
        for endpoint in endpoints:
            route = endpoint.get('route', '/')
            method = endpoint.get('method', 'GET').upper()
            parameters = endpoint.get('parameters', [])
            
            # Extract entity name from route
            entity = self._extract_entity_from_route(route)
            
            if entity not in schema_requirements:
                schema_requirements[entity] = {
                    'entity_name': entity,
                    'fields': set(),
                    'endpoints': [],
                    'requires_create': False,
                    'requires_update': False,
                    'requires_response': False,
                    'has_list_endpoint': False,
                    'validation_rules': {}
                }
            
            entity_info = schema_requirements[entity]
            entity_info['endpoints'].append(endpoint)
            
            # Determine schema types needed
            if method == 'POST':
                entity_info['requires_create'] = True
            elif method in ['PUT', 'PATCH']:
                entity_info['requires_update'] = True
            
            entity_info['requires_response'] = True
            
            if 'list' in route.lower() or route.endswith('s'):
                entity_info['has_list_endpoint'] = True
            
            # Extract field information from parameters
            for param in parameters:
                field_name = param if isinstance(param, str) else param.get('name', param)
                entity_info['fields'].add(field_name)
                
                # Infer validation rules
                validation_rule = self._infer_validation_rule(field_name)
                if validation_rule:
                    entity_info['validation_rules'][field_name] = validation_rule
        
        # Convert sets to lists for JSON serialization
        for entity_info in schema_requirements.values():
            entity_info['fields'] = list(entity_info['fields'])
        
        return schema_requirements
    
    def _generate_entity_schemas(self, entity: str, entity_info: Dict[str, Any],
                                context: ConversionContext, output_path: str) -> Optional[str]:
        """Generate schemas for a specific entity."""
        try:
            # Create PHP representation for LLM conversion
            php_code = self._create_php_schema_representation(entity, entity_info)
            
            # Create conversion request
            request = ConversionRequest(
                php_code=php_code,
                conversion_type='schema',
                context=context,
                file_path=f"{entity}_schemas.php",
                additional_instructions=self._create_schema_instructions(entity, entity_info)
            )
            
            # Convert using LLM
            result = self.llm_generator.convert_php_batch(request)
            
            if not result.success:
                # Fallback to template-based generation
                self.ui.debug(f"LLM conversion failed for {entity} schemas, using template")
                pydantic_code = self._generate_entity_schema_template(entity, entity_info)
            else:
                pydantic_code = result.python_code
            
            # Write schema file
            schema_file = self._write_schema_file(entity, pydantic_code, output_path)
            return schema_file
            
        except Exception as e:
            self.ui.error(f"Failed to generate {entity} schemas: {str(e)}")
            return None
    
    def _create_php_schema_representation(self, entity: str, entity_info: Dict[str, Any]) -> str:
        """Create PHP representation for schema generation."""
        fields = entity_info['fields']
        validation_rules = entity_info.get('validation_rules', {})
        
        class_name = entity.capitalize()
        
        php_code = f"""<?php

// {class_name} entity for API request/response

class {class_name}Request
{{
"""
        
        # Add properties
        for field in fields:
            validation = validation_rules.get(field, {})
            field_type = validation.get('type', 'string')
            required = validation.get('required', True)
            
            if required:
                php_code += f"    public ${field}; // {field_type}, required\n"
            else:
                php_code += f"    public ${field}; // {field_type}, optional\n"
        
        php_code += """
    public function validate()
    {
        // Validation logic here
"""
        
        # Add validation for each field
        for field, validation in validation_rules.items():
            if validation.get('required'):
                php_code += f"        if (empty($this->{field})) {{\n"
                php_code += f"            throw new ValidationException('{field} is required');\n"
                php_code += f"        }}\n"
            
            if validation.get('type') == 'email':
                php_code += f"        if (!filter_var($this->{field}, FILTER_VALIDATE_EMAIL)) {{\n"
                php_code += f"            throw new ValidationException('Invalid email format');\n"
                php_code += f"        }}\n"
        
        php_code += """    }
}

class {class_name}Response
{
"""
        
        # Add response properties (usually includes ID and timestamps)
        response_fields = ['id'] + fields + ['created_at', 'updated_at']
        for field in response_fields:
            php_code += f"    public ${field};\n"
        
        php_code += f"""
    public function toArray()
    {{
        return [
"""
        
        for field in response_fields:
            php_code += f"            '{field}' => $this->{field},\n"
        
        php_code += """        ];
    }
}
"""
        
        return php_code
    
    def _create_schema_instructions(self, entity: str, entity_info: Dict[str, Any]) -> str:
        """Create specific instructions for schema conversion."""
        entity_name = entity.capitalize()
        
        instructions = f"""
Convert these PHP request/response classes to Pydantic schemas for {entity_name}:

Requirements:
1. Create separate schemas for different use cases:
   - {entity_name}Base: Common fields shared across schemas
   - {entity_name}Create: For POST requests (no ID, no timestamps)
   - {entity_name}Update: For PUT/PATCH requests (optional fields)
   - {entity_name}Response: For API responses (includes ID and timestamps)
   - {entity_name}InDB: For database operations (includes all fields)

2. Use proper Pydantic field types and validators:
   - str for text fields
   - int for integer fields  
   - EmailStr for email fields
   - HttpUrl for URL fields
   - datetime for timestamp fields
   - Optional[T] for optional fields

3. Add field validation:
   - Use Field() for length constraints, regex patterns
   - Use validator decorators for custom validation
   - Add proper error messages

4. Follow naming conventions:
   - Use snake_case for field names
   - Use descriptive field descriptions
   - Add examples where helpful

5. Handle relationships:
   - Use Pydantic models for nested objects
   - Use List[Model] for collections
   - Use proper forward references if needed

Schema inheritance structure:
```python
class {entity_name}Base(BaseModel):
    # Common fields
    pass

class {entity_name}Create({entity_name}Base):
    # Fields for creation (no ID)
    pass

class {entity_name}Update(BaseModel):
    # Optional fields for updates
    pass

class {entity_name}Response({entity_name}Base):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class {entity_name}InDB({entity_name}Response):
    # Additional internal fields
    pass
```
"""
        
        return instructions
    
    def _generate_entity_schema_template(self, entity: str, entity_info: Dict[str, Any]) -> str:
        """Generate entity schema template when LLM conversion fails."""
        entity_name = entity.capitalize()
        fields = entity_info['fields']
        validation_rules = entity_info.get('validation_rules', {})
        
        template = f'''"""Pydantic schemas for {entity_name}."""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, validator

class {entity_name}Base(BaseModel):
    """Base {entity_name} schema with common fields."""
'''
        
        # Add base fields (exclude id, timestamps)
        for field in fields:
            if field in ['id', 'created_at', 'updated_at']:
                continue
                
            field_type = self._get_pydantic_field_type(field, validation_rules.get(field, {}))
            description = f'"{field.replace("_", " ").title()}"'
            
            template += f'    {field}: {field_type} = Field(..., description={description})\n'
        
        # Create schema
        template += f'''
class {entity_name}Create({entity_name}Base):
    """Schema for creating {entity_name}."""
    pass

class {entity_name}Update(BaseModel):
    """Schema for updating {entity_name}."""
'''
        
        # Add optional fields for update
        for field in fields:
            if field in ['id', 'created_at', 'updated_at']:
                continue
                
            field_type = self._get_pydantic_field_type(field, validation_rules.get(field, {}))
            template += f'    {field}: Optional[{field_type}] = None\n'
        
        template += f'''
class {entity_name}Response({entity_name}Base):
    """Schema for {entity_name} response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class {entity_name}InDB({entity_name}Response):
    """Schema for {entity_name} in database."""
    pass
'''
        
        # Add list response schema if needed
        if entity_info.get('has_list_endpoint'):
            template += f'''
class {entity_name}ListResponse(BaseModel):
    """Schema for {entity_name} list response."""
    items: List[{entity_name}Response]
    total: int
    page: int = 1
    size: int = 50
    pages: int
'''
        
        return template
    
    def _generate_basic_schemas(self, output_path: str) -> List[str]:
        """Generate basic schemas when no endpoints are found."""
        try:
            generated_files = []
            
            # Generate base schemas
            base_file = self._generate_base_schemas(output_path)
            if base_file:
                generated_files.append(base_file)
            
            # Generate user schemas as example
            user_schemas = '''"""User schemas for authentication."""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    """Base user schema."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    is_active: bool = True

class UserCreate(UserBase):
    """Schema for user creation."""
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    """Schema for user updates."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserInDB(UserResponse):
    """Schema for user in database."""
    hashed_password: str
'''
            
            user_file = self._write_schema_file('user', user_schemas, output_path)
            if user_file:
                generated_files.append(user_file)
            
            return generated_files
            
        except Exception as e:
            self.ui.error(f"Failed to generate basic schemas: {str(e)}")
            return []
    
    def _generate_base_schemas(self, output_path: str) -> Optional[str]:
        """Generate base schemas with common functionality."""
        try:
            schemas_dir = os.path.join(output_path, 'app', 'schemas')
            os.makedirs(schemas_dir, exist_ok=True)
            
            file_path = os.path.join(schemas_dir, 'base.py')
            
            base_code = '''"""Base schemas with common functionality."""

from typing import Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field

class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    class Config:
        from_attributes = True
        validate_assignment = True
        use_enum_values = True

class TimestampMixin(BaseModel):
    """Mixin for timestamp fields."""
    created_at: datetime
    updated_at: datetime

class ResponseMixin(BaseModel):
    """Mixin for response schemas."""
    id: int = Field(..., description="Unique identifier")

class PaginationParams(BaseModel):
    """Schema for pagination parameters."""
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(50, ge=1, le=100, description="Page size")

class PaginatedResponse(BaseModel):
    """Schema for paginated responses."""
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")

class HealthCheck(BaseModel):
    """Schema for health check response."""
    status: str = "ok"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"

class ErrorResponse(BaseModel):
    """Schema for error responses."""
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    errors: Optional[Dict[str, Any]] = Field(None, description="Validation errors")
'''
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(base_code)
            
            return file_path
            
        except Exception as e:
            self.ui.error(f"Failed to generate base schemas: {str(e)}")
            return None
    
    def _generate_auth_schemas(self, output_path: str) -> Optional[str]:
        """Generate authentication schemas."""
        try:
            auth_schemas = '''"""Authentication schemas."""

from typing import Optional
from pydantic import BaseModel, Field

class Token(BaseModel):
    """Schema for token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None

class TokenData(BaseModel):
    """Schema for token data."""
    username: Optional[str] = None

class Login(BaseModel):
    """Schema for login request."""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")

class RefreshToken(BaseModel):
    """Schema for refresh token request."""
    refresh_token: str = Field(..., description="Refresh token")

class PasswordReset(BaseModel):
    """Schema for password reset request."""
    email: str = Field(..., description="Email address")

class PasswordChange(BaseModel):
    """Schema for password change request."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
'''
            
            auth_file = self._write_schema_file('auth', auth_schemas, output_path)
            return auth_file
            
        except Exception as e:
            self.ui.error(f"Failed to generate auth schemas: {str(e)}")
            return None
    
    def _generate_schemas_init(self, schema_requirements: Dict[str, Dict[str, Any]], 
                              output_path: str) -> Optional[str]:
        """Generate schemas __init__.py file."""
        try:
            schemas_dir = os.path.join(output_path, 'app', 'schemas')
            file_path = os.path.join(schemas_dir, '__init__.py')
            
            init_code = '''"""Schemas package."""

from .base import (
    BaseSchema,
    TimestampMixin,
    ResponseMixin,
    PaginationParams,
    PaginatedResponse,
    HealthCheck,
    ErrorResponse
)
'''
            
            # Import entity schemas
            for entity in schema_requirements.keys():
                entity_name = entity.capitalize()
                init_code += f'''from .{entity} import (
    {entity_name}Base,
    {entity_name}Create,
    {entity_name}Update,
    {entity_name}Response,
    {entity_name}InDB,
)
'''
            
            # Import auth schemas if they exist
            init_code += '''
# Import auth schemas if available
try:
    from .auth import Token, TokenData, Login, RefreshToken, PasswordReset, PasswordChange
except ImportError:
    pass

# Import user schemas if available
try:
    from .user import UserBase, UserCreate, UserUpdate, UserResponse, UserInDB
except ImportError:
    pass
'''
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(init_code)
            
            return file_path
            
        except Exception as e:
            self.ui.error(f"Failed to generate schemas __init__.py: {str(e)}")
            return None
    
    def _write_schema_file(self, entity: str, schema_code: str, output_path: str) -> Optional[str]:
        """Write schema to file."""
        try:
            schemas_dir = os.path.join(output_path, 'app', 'schemas')
            os.makedirs(schemas_dir, exist_ok=True)
            
            file_name = f"{entity}.py"
            file_path = os.path.join(schemas_dir, file_name)
            
            # Enhance schema code with imports
            enhanced_code = self._enhance_schema_code(schema_code)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(enhanced_code)
            
            self.ui.debug(f"Generated schema file: {file_path}")
            return file_path
            
        except Exception as e:
            self.ui.error(f"Failed to write schema file {entity}: {str(e)}")
            return None
    
    def _extract_entity_from_route(self, route: str) -> str:
        """Extract entity name from route."""
        # Remove version prefixes and clean route
        clean_route = route.strip('/').lower()
        parts = clean_route.split('/')
        
        # Remove common prefixes
        if parts and parts[0] in ['api', 'v1', 'v2', 'v3']:
            parts = parts[1:]
        
        if not parts:
            return 'item'
        
        # Get first meaningful part
        entity = parts[0]
        
        # Remove common suffixes and make singular
        if entity.endswith('s'):
            entity = entity[:-1]
        
        # Handle special cases
        entity_mappings = {
            'user': 'user',
            'auth': 'auth',
            'login': 'auth',
            'register': 'auth',
            'post': 'post',
            'article': 'post',
            'product': 'product',
            'order': 'order',
            'category': 'category',
            'tag': 'tag'
        }
        
        return entity_mappings.get(entity, entity)
    
    def _infer_validation_rule(self, field_name: str) -> Optional[Dict[str, Any]]:
        """Infer validation rules from field name."""
        field_lower = field_name.lower()
        
        for pattern_name, pattern in self.validation_patterns.items():
            if re.search(pattern, field_lower):
                if pattern_name == 'email':
                    return {'type': 'email', 'required': True}
                elif pattern_name == 'password':
                    return {'type': 'string', 'required': True, 'min_length': 8}
                elif pattern_name == 'phone':
                    return {'type': 'string', 'pattern': r'^\+?1?\d{9,15}$'}
                elif pattern_name == 'url':
                    return {'type': 'url', 'required': False}
                elif pattern_name == 'uuid':
                    return {'type': 'uuid', 'required': True}
                elif pattern_name == 'slug':
                    return {'type': 'string', 'pattern': r'^[a-z0-9-]+$'}
        
        return None
    
    def _get_pydantic_field_type(self, field_name: str, validation_rule: Dict[str, Any]) -> str:
        """Get Pydantic field type for a field."""
        rule_type = validation_rule.get('type', 'string')
        
        if rule_type == 'email':
            return 'EmailStr'
        elif rule_type == 'url':
            return 'HttpUrl'
        elif rule_type == 'uuid':
            return 'UUID4'
        elif rule_type in self.pydantic_type_mappings:
            return self.pydantic_type_mappings[rule_type]
        else:
            return 'str'
    
    def _enhance_schema_code(self, schema_code: str) -> str:
        """Enhance schema code with proper imports."""
        base_imports = '''from typing import Optional, List, Dict, Any
from datetime import datetime, date, time
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr, HttpUrl, validator
'''
        
        # Check if imports are already present
        if 'from pydantic import' not in schema_code:
            return base_imports + '\n\n' + schema_code
        
        return schema_code