# generators/business_logic_translator.py
"""Converts PHP business logic classes and functions to Python with LLM assistance."""

import os
import re
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

from config.settings import Settings
from core.user_interface import UserInterface
from generators.llm_assisted_generator import LLMAssistedGenerator, ConversionRequest, ConversionContext
from generators.code_batch_processor import CodeBatch


class BusinessLogicTranslator:
    """Converts PHP business logic to Python services and utilities."""
    
    def __init__(self, settings: Settings, ui: UserInterface):
        self.settings = settings
        self.ui = ui
        self.llm_generator = LLMAssistedGenerator(settings, ui)
        
        # Patterns for identifying different types of business logic
        self.service_patterns = [
            r'class\s+\w*Service\w*',
            r'class\s+\w*Manager\w*',
            r'class\s+\w*Handler\w*',
            r'class\s+\w*Processor\w*',
            r'class\s+\w*Business\w*'
        ]
        
        self.utility_patterns = [
            r'class\s+\w*Helper\w*',
            r'class\s+\w*Util\w*',
            r'class\s+\w*Tool\w*',
            r'function\s+\w*Helper\w*',
            r'function\s+format\w*',
            r'function\s+validate\w*'
        ]
        
        self.repository_patterns = [
            r'class\s+\w*Repository\w*',
            r'class\s+\w*DAO\w*',
            r'class\s+\w*DataAccess\w*'
        ]
    
    def convert_logic_batch(self, batch: CodeBatch, analysis_result: Dict[str, Any],
                           planning_result: Dict[str, Any], output_path: str) -> List[str]:
        """Convert a batch of business logic code to Python."""
        try:
            self.ui.debug(f"Converting business logic batch: {batch.name}")
            
            # Create conversion context
            context = self._create_conversion_context(analysis_result, planning_result)
            
            # Analyze the batch to determine conversion approach
            logic_type = self._analyze_logic_type(batch.php_code)
            
            # Create conversion request
            request = ConversionRequest(
                php_code=batch.php_code,
                conversion_type='logic',
                context=context,
                file_path=batch.file_path,
                additional_instructions=self._create_logic_instructions(logic_type, batch)
            )
            
            # Convert using LLM
            result = self.llm_generator.convert_php_batch(request)
            
            if not result.success:
                self.ui.error(f"Failed to convert logic batch {batch.name}: {result.error_message}")
                return []
            
            # Write Python files
            generated_files = self._write_python_logic_files(
                batch.name, result, logic_type, output_path
            )
            
            return generated_files
            
        except Exception as e:
            self.ui.error(f"Failed to convert logic batch {batch.name}: {str(e)}")
            return []
    
    def convert_service_class(self, php_class_code: str, class_name: str,
                             context: ConversionContext, output_path: str) -> Optional[str]:
        """Convert a specific PHP service class to Python."""
        try:
            request = ConversionRequest(
                php_code=php_class_code,
                conversion_type='logic',
                context=context,
                file_path=f"{class_name}.php",
                additional_instructions=f"Convert this PHP service class '{class_name}' to a Python service class with proper dependency injection and async support."
            )
            
            result = self.llm_generator.convert_php_batch(request)
            
            if not result.success:
                return None
            
            # Write service file
            service_file = self._write_service_file(class_name, result.python_code, output_path)
            return service_file
            
        except Exception as e:
            self.ui.error(f"Failed to convert service class {class_name}: {str(e)}")
            return None
    
    def _create_conversion_context(self, analysis_result: Dict[str, Any],
                                  planning_result: Dict[str, Any]) -> ConversionContext:
        """Create conversion context for business logic."""
        # Extract framework info
        project_summary = analysis_result.get('project_summary', {})
        framework = project_summary.get('framework_detected', 'vanilla_php')
        
        # Extract database info
        db_analysis = analysis_result.get('database_analysis', {})
        database_type = db_analysis.get('database_type', 'mysql')
        
        # Extract auth info
        endpoints_analysis = analysis_result.get('endpoints_analysis', {})
        auth_methods = endpoints_analysis.get('authentication_methods', [])
        auth_method = auth_methods[0] if auth_methods else 'none'
        
        # Extract dependencies
        dependency_conversion = planning_result.get('dependency_conversion', {})
        requirements = dependency_conversion.get('requirements_txt', [])
        
        python_dependencies = []
        for req in requirements:
            if isinstance(req, dict):
                python_dependencies.append(req.get('package', ''))
            elif isinstance(req, str):
                python_dependencies.append(req.split('>=')[0].split('==')[0])
        
        return ConversionContext(
            framework=framework,
            database_type=database_type,
            auth_method=auth_method,
            python_dependencies=python_dependencies,
            endpoint_style='fastapi_dependencies',
            project_structure='services'
        )
    
    def _analyze_logic_type(self, php_code: str) -> str:
        """Analyze PHP code to determine the type of business logic."""
        code_lower = php_code.lower()
        
        # Check for service patterns
        if any(re.search(pattern, php_code, re.IGNORECASE) for pattern in self.service_patterns):
            return 'service'
        
        # Check for repository patterns
        if any(re.search(pattern, php_code, re.IGNORECASE) for pattern in self.repository_patterns):
            return 'repository'
        
        # Check for utility patterns
        if any(re.search(pattern, php_code, re.IGNORECASE) for pattern in self.utility_patterns):
            return 'utility'
        
        # Check for validation logic
        if any(keyword in code_lower for keyword in ['validate', 'validation', 'validator']):
            return 'validator'
        
        # Check for configuration logic
        if any(keyword in code_lower for keyword in ['config', 'setting', 'environment']):
            return 'config'
        
        # Check for database-related logic
        if any(keyword in code_lower for keyword in ['query', 'database', 'sql', 'pdo', 'mysqli']):
            return 'database'
        
        # Check for API-related logic
        if any(keyword in code_lower for keyword in ['api', 'response', 'request', 'json', 'xml']):
            return 'api_logic'
        
        return 'general'
    
    def _create_logic_instructions(self, logic_type: str, batch: CodeBatch) -> str:
        """Create specific instructions for business logic conversion."""
        
        base_instructions = f"""
Convert this PHP {logic_type} code to Python following these guidelines:

1. Maintain the same business logic and functionality
2. Use proper Python class design patterns
3. Add type hints for all methods and parameters
4. Use dependency injection where appropriate
5. Convert to async/await if the logic involves I/O operations
6. Add proper error handling and logging
7. Follow Python naming conventions (snake_case)
8. Add docstrings for classes and methods
9. Use Pydantic models for data validation where appropriate
10. Implement proper separation of concerns

"""
        
        specific_instructions = {
            'service': """
Service Class Conversion:
- Convert to a Python service class with dependency injection
- Use constructor injection for dependencies (database, other services)
- Make I/O operations async
- Return appropriate data types or raise exceptions
- Use logging for important operations
- Structure: __init__, public methods, private helper methods
""",
            
            'repository': """
Repository Pattern Conversion:
- Convert to SQLAlchemy-based repository pattern
- Use Session dependency injection
- Convert all queries to SQLAlchemy ORM or Core
- Add proper error handling for database operations
- Return domain objects, not raw database records
- Implement CRUD operations as async methods
""",
            
            'utility': """
Utility Functions/Classes Conversion:
- Convert utility functions to static methods or standalone functions
- Group related utilities in utility classes
- Add comprehensive type hints
- Make pure functions whenever possible
- Add unit test examples in docstrings
- Handle edge cases properly
""",
            
            'validator': """
Validation Logic Conversion:
- Convert to Pydantic validators or custom validation functions
- Use Pydantic's validator decorators where appropriate
- Create custom validation exceptions
- Support both sync and async validation
- Add clear error messages
- Return ValidationError with details
""",
            
            'config': """
Configuration Logic Conversion:
- Convert to Pydantic Settings classes
- Use environment variable support
- Add validation for configuration values
- Support multiple environments (dev, prod, test)
- Use proper defaults
- Add configuration documentation
""",
            
            'database': """
Database Logic Conversion:
- Convert to SQLAlchemy operations
- Use Session management properly
- Convert raw SQL to ORM queries where possible
- Add proper transaction handling
- Use connection pooling
- Add query optimization hints
""",
            
            'api_logic': """
API Logic Conversion:
- Convert to FastAPI compatible functions
- Use proper request/response models
- Add HTTP status codes
- Use FastAPI dependencies for common logic
- Add proper API documentation
- Handle serialization/deserialization
""",
            
            'general': """
General Logic Conversion:
- Analyze the code and convert to appropriate Python patterns
- Maintain the same functionality and business rules
- Use appropriate Python libraries and frameworks
- Add proper error handling and logging
- Follow Python best practices
"""
        }
        
        return base_instructions + specific_instructions.get(logic_type, specific_instructions['general'])
    
    def _write_python_logic_files(self, batch_name: str, result, logic_type: str,
                                 output_path: str) -> List[str]:
        """Write converted Python logic to appropriate files."""
        try:
            generated_files = []
            
            # Determine target directory based on logic type
            target_dir = self._get_target_directory(logic_type, output_path)
            os.makedirs(target_dir, exist_ok=True)
            
            # Determine file name
            file_name = self._get_python_file_name(batch_name, logic_type)
            file_path = os.path.join(target_dir, file_name)
            
            # Add imports and structure if needed
            python_code = self._enhance_python_code(result.python_code, logic_type)
            
            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(python_code)
            
            generated_files.append(file_path)
            self.ui.debug(f"Generated {logic_type} file: {file_path}")
            
            # Create __init__.py if it doesn't exist
            init_file = os.path.join(target_dir, '__init__.py')
            if not os.path.exists(init_file):
                with open(init_file, 'w', encoding='utf-8') as f:
                    f.write('"""Business logic module."""\n')
                generated_files.append(init_file)
            
            return generated_files
            
        except Exception as e:
            self.ui.error(f"Failed to write Python logic files: {str(e)}")
            return []
    
    def _get_target_directory(self, logic_type: str, output_path: str) -> str:
        """Get target directory based on logic type."""
        app_path = os.path.join(output_path, 'app')
        
        directory_mapping = {
            'service': os.path.join(app_path, 'services'),
            'repository': os.path.join(app_path, 'repositories'),
            'utility': os.path.join(app_path, 'utils'),
            'validator': os.path.join(app_path, 'validators'),
            'config': os.path.join(app_path, 'core'),
            'database': os.path.join(app_path, 'db'),
            'api_logic': os.path.join(app_path, 'api', 'utils'),
            'general': os.path.join(app_path, 'services')
        }
        
        return directory_mapping.get(logic_type, os.path.join(app_path, 'services'))
    
    def _get_python_file_name(self, batch_name: str, logic_type: str) -> str:
        """Generate appropriate Python file name."""
        # Clean up batch name
        name = batch_name.replace('.php', '').replace('-', '_').lower()
        
        # Remove common prefixes/suffixes
        name = re.sub(r'^(php_|class_|function_)', '', name)
        name = re.sub(r'_(class|function|batch)$', '', name)
        
        # Add appropriate suffix based on type
        if logic_type == 'service' and not name.endswith('_service'):
            name += '_service'
        elif logic_type == 'repository' and not name.endswith('_repository'):
            name += '_repository'
        elif logic_type == 'utility' and not name.endswith('_utils'):
            name += '_utils'
        elif logic_type == 'validator' and not name.endswith('_validator'):
            name += '_validator'
        
        return f"{name}.py"
    
    def _enhance_python_code(self, python_code: str, logic_type: str) -> str:
        """Enhance Python code with appropriate imports and structure."""
        imports = self._get_imports_for_logic_type(logic_type)
        
        # Check if imports are already present
        if 'from ' not in python_code and 'import ' not in python_code:
            python_code = imports + '\n\n' + python_code
        
        return python_code
    
    def _get_imports_for_logic_type(self, logic_type: str) -> str:
        """Get appropriate imports for logic type."""
        common_imports = """from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)"""
        
        type_specific_imports = {
            'service': """from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.models import *
from app.schemas import *""",
            
            'repository': """from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from app.models import *""",
            
            'utility': """from datetime import datetime, timedelta
import json
import re""",
            
            'validator': """from pydantic import validator, ValidationError
from typing import Union""",
            
            'config': """from pydantic import BaseSettings, Field
import os""",
            
            'database': """from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings""",
            
            'api_logic': """from fastapi import HTTPException, status
from app.schemas import *"""
        }
        
        specific = type_specific_imports.get(logic_type, '')
        
        if specific:
            return common_imports + '\n' + specific
        else:
            return common_imports
    
    def _write_service_file(self, class_name: str, python_code: str, output_path: str) -> Optional[str]:
        """Write a service file specifically."""
        try:
            services_dir = os.path.join(output_path, 'app', 'services')
            os.makedirs(services_dir, exist_ok=True)
            
            # Convert class name to file name
            file_name = re.sub(r'([A-Z])', r'_\1', class_name).lower().lstrip('_')
            if not file_name.endswith('_service'):
                file_name += '_service'
            file_name += '.py'
            
            file_path = os.path.join(services_dir, file_name)
            
            # Add service-specific imports
            enhanced_code = self._enhance_python_code(python_code, 'service')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(enhanced_code)
            
            return file_path
            
        except Exception as e:
            self.ui.error(f"Failed to write service file {class_name}: {str(e)}")
            return None