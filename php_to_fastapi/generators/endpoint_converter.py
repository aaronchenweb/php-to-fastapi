# generators/endpoint_converter.py
"""Converts PHP API endpoints to FastAPI routes with LLM assistance."""

import os
import re
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

from ..config.settings import Settings
from ..core.user_interface import UserInterface
from ..generators.llm_assisted_generator import LLMAssistedGenerator, ConversionRequest, ConversionContext


class EndpointConverter:
    """Converts PHP API endpoints to FastAPI routes."""
    
    def __init__(self, settings: Settings, ui: UserInterface):
        self.settings = settings
        self.ui = ui
        self.llm_generator = LLMAssistedGenerator(settings, ui)
        
        # HTTP method mappings
        self.http_methods = {
            'GET': 'get',
            'POST': 'post', 
            'PUT': 'put',
            'DELETE': 'delete',
            'PATCH': 'patch',
            'OPTIONS': 'options',
            'HEAD': 'head'
        }
        
        # Common PHP to FastAPI pattern mappings
        self.route_patterns = {
            r'\{(\w+)\}': r'{{\1}}',  # Laravel style {id} -> {id}
            r':(\w+)': r'{{\1}}',     # Express style :id -> {id}
            r'\((\w+)\)': r'{{\1}}',  # Some custom styles
        }
    
    def convert_endpoint_group(self, endpoint_group: Dict[str, Any],
                              analysis_result: Dict[str, Any],
                              planning_result: Dict[str, Any],
                              output_path: str) -> List[str]:
        """Convert a group of related endpoints to FastAPI."""
        try:
            endpoints = endpoint_group.get('endpoints', [])
            group_name = endpoint_group.get('name', 'endpoints')
            
            self.ui.debug(f"Converting endpoint group: {group_name} ({len(endpoints)} endpoints)")
            
            # Create conversion context
            context = self._create_conversion_context(analysis_result, planning_result)
            
            # Group endpoints by file/module for better organization
            endpoint_modules = self._organize_endpoints_by_module(endpoints, group_name)
            
            generated_files = []
            
            for module_name, module_endpoints in endpoint_modules.items():
                self.ui.debug(f"Converting module: {module_name}")
                
                # Convert endpoints in this module
                module_files = self._convert_endpoint_module(
                    module_name, module_endpoints, context, 
                    analysis_result, planning_result, output_path
                )
                generated_files.extend(module_files)
            
            return generated_files
            
        except Exception as e:
            self.ui.error(f"Failed to convert endpoint group: {str(e)}")
            return []
    
    def _convert_endpoint_module(self, module_name: str, endpoints: List[Dict[str, Any]],
                                context: ConversionContext, analysis_result: Dict[str, Any],
                                planning_result: Dict[str, Any], output_path: str) -> List[str]:
        """Convert endpoints for a single module."""
        try:
            # Generate PHP code representation of endpoints
            php_code = self._generate_php_code_for_endpoints(endpoints)
            
            # Create conversion request
            request = ConversionRequest(
                php_code=php_code,
                conversion_type='endpoint',
                context=context,
                file_path=f"{module_name}.php",
                additional_instructions=self._create_endpoint_instructions(endpoints, module_name)
            )
            
            # Convert using LLM
            result = self.llm_generator.convert_php_batch(request)
            
            if not result.success:
                self.ui.error(f"Failed to convert endpoints in {module_name}: {result.error_message}")
                return []
            
            # Write FastAPI file
            fastapi_file_path = self._write_fastapi_endpoints(
                module_name, result.python_code, output_path
            )
            
            if fastapi_file_path:
                return [fastapi_file_path]
            else:
                return []
                
        except Exception as e:
            self.ui.error(f"Failed to convert endpoint module {module_name}: {str(e)}")
            return []
    
    def _create_conversion_context(self, analysis_result: Dict[str, Any],
                                  planning_result: Dict[str, Any]) -> ConversionContext:
        """Create conversion context from analysis and planning results."""
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
        
        # Convert to list of package names
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
            endpoint_style='fastapi_router',
            project_structure='standard'
        )
    
    def _organize_endpoints_by_module(self, endpoints: List[Dict[str, Any]], 
                                     group_name: str) -> Dict[str, List[Dict[str, Any]]]:
        """Organize endpoints into logical modules."""
        modules = {}
        
        for endpoint in endpoints:
            module_name = self._determine_endpoint_module(endpoint, group_name)
            
            if module_name not in modules:
                modules[module_name] = []
            
            modules[module_name].append(endpoint)
        
        return modules
    
    def _determine_endpoint_module(self, endpoint: Dict[str, Any], group_name: str) -> str:
        """Determine which module an endpoint belongs to."""
        route = endpoint.get('route', '/')
        method = endpoint.get('method', 'GET')
        
        # Clean up route for analysis
        route_clean = route.strip('/').lower()
        
        if not route_clean:
            return f"{group_name}_root"
        
        # Get first path segment
        parts = route_clean.split('/')
        first_part = parts[0]
        
        # Remove version prefixes
        if first_part in ['api', 'v1', 'v2', 'v3']:
            if len(parts) > 1:
                first_part = parts[1]
            else:
                return f"{group_name}_api"
        
        # Create module name
        module_name = first_part.replace('-', '_').replace('.', '_')
        
        # Ensure valid Python module name
        if not module_name[0].isalpha():
            module_name = f"endpoint_{module_name}"
        
        return module_name
    
    def _generate_php_code_for_endpoints(self, endpoints: List[Dict[str, Any]]) -> str:
        """Generate PHP code representation for endpoints."""
        php_parts = []
        
        for i, endpoint in enumerate(endpoints):
            method = endpoint.get('method', 'GET').upper()
            route = endpoint.get('route', '/')
            handler = endpoint.get('handler', f'handler_{i}')
            
            # Create PHP function representation
            php_code = self._create_php_endpoint_code(endpoint)
            php_parts.append(php_code)
        
        return '\n\n'.join(php_parts)
    
    def _create_php_endpoint_code(self, endpoint: Dict[str, Any]) -> str:
        """Create PHP code representation for a single endpoint."""
        method = endpoint.get('method', 'GET').upper()
        route = endpoint.get('route', '/')
        handler = endpoint.get('handler', 'handle_request')
        parameters = endpoint.get('parameters', [])
        middleware = endpoint.get('middleware', [])
        auth = endpoint.get('authentication', None)
        response_format = endpoint.get('response_format', 'json')
        
        # Start building PHP code
        lines = []
        
        # Add route comment
        lines.append(f"// {method} {route}")
        
        # Add middleware comments
        if middleware:
            lines.append(f"// Middleware: {', '.join(middleware)}")
        
        # Add auth comment
        if auth:
            lines.append(f"// Authentication: {auth}")
        
        # Function signature
        param_string = ', '.join([f"${param}" for param in parameters])
        lines.append(f"function {handler}({param_string}) {{")
        
        # Set content type for JSON
        if response_format == 'json':
            lines.append("    header('Content-Type: application/json');")
        
        # Add authentication check if needed
        if auth:
            lines.append("    // Authentication check")
            lines.append("    if (!authenticate()) {")
            lines.append("        http_response_code(401);")
            lines.append("        echo json_encode(['error' => 'Unauthorized']);")
            lines.append("        return;")
            lines.append("    }")
        
        # Add method-specific logic
        if method == 'GET':
            lines.extend(self._get_method_logic(parameters))
        elif method == 'POST':
            lines.extend(self._post_method_logic())
        elif method == 'PUT':
            lines.extend(self._put_method_logic(parameters))
        elif method == 'DELETE':
            lines.extend(self._delete_method_logic(parameters))
        else:
            lines.extend(self._generic_method_logic(method))
        
        lines.append("}")
        
        return '\n'.join(lines)
    
    def _get_method_logic(self, parameters: List[str]) -> List[str]:
        """Generate GET method logic."""
        lines = []
        lines.append("    // Handle GET request")
        
        if parameters:
            lines.append("    // Extract parameters")
            for param in parameters:
                lines.append(f"    ${param} = $_GET['{param}'] ?? null;")
        
        lines.append("    ")
        lines.append("    // Business logic here")
        lines.append("    $data = [];")
        lines.append("    ")
        lines.append("    echo json_encode($data);")
        
        return lines
    
    def _post_method_logic(self) -> List[str]:
        """Generate POST method logic."""
        return [
            "    // Handle POST request",
            "    $input = json_decode(file_get_contents('php://input'), true);",
            "    ",
            "    // Validate input",
            "    if (!$input) {",
            "        http_response_code(400);",
            "        echo json_encode(['error' => 'Invalid JSON']);",
            "        return;",
            "    }",
            "    ",
            "    // Business logic here",
            "    $result = process_post_data($input);",
            "    ",
            "    http_response_code(201);",
            "    echo json_encode($result);"
        ]
    
    def _put_method_logic(self, parameters: List[str]) -> List[str]:
        """Generate PUT method logic."""
        lines = []
        lines.append("    // Handle PUT request")
        lines.append("    $input = json_decode(file_get_contents('php://input'), true);")
        
        if parameters:
            lines.append("    // Extract parameters")
            for param in parameters:
                lines.append(f"    ${param} = $_GET['{param}'] ?? null;")
        
        lines.extend([
            "    ",
            "    // Validate input",
            "    if (!$input) {",
            "        http_response_code(400);",
            "        echo json_encode(['error' => 'Invalid JSON']);",
            "        return;",
            "    }",
            "    ",
            "    // Business logic here",
            "    $result = update_data($input);",
            "    ",
            "    echo json_encode($result);"
        ])
        
        return lines
    
    def _delete_method_logic(self, parameters: List[str]) -> List[str]:
        """Generate DELETE method logic."""
        lines = []
        lines.append("    // Handle DELETE request")
        
        if parameters:
            lines.append("    // Extract parameters")
            for param in parameters:
                lines.append(f"    ${param} = $_GET['{param}'] ?? null;")
        
        lines.extend([
            "    ",
            "    // Business logic here",
            "    $success = delete_data();",
            "    ",
            "    if ($success) {",
            "        http_response_code(204);",
            "    } else {",
            "        http_response_code(404);",
            "        echo json_encode(['error' => 'Not found']);",
            "    }"
        ])
        
        return lines
    
    def _generic_method_logic(self, method: str) -> List[str]:
        """Generate generic method logic."""
        return [
            f"    // Handle {method} request",
            "    ",
            "    // Business logic here",
            "    $data = ['method' => '{method}'];",
            "    ",
            "    echo json_encode($data);"
        ]
    
    def _create_endpoint_instructions(self, endpoints: List[Dict[str, Any]], 
                                    module_name: str) -> str:
        """Create specific instructions for endpoint conversion."""
        endpoint_count = len(endpoints)
        methods = list(set(ep.get('method', 'GET') for ep in endpoints))
        
        instructions = f"""
Convert these {endpoint_count} PHP endpoints to a FastAPI router module named '{module_name}':

HTTP Methods used: {', '.join(methods)}

Requirements:
1. Create a FastAPI APIRouter instance
2. Convert each PHP function to a FastAPI route handler
3. Maintain exact same route paths and HTTP methods
4. Use proper Pydantic models for request/response validation
5. Include proper error handling with HTTPException
6. Add type hints for all parameters
7. Use async/await where appropriate
8. Include proper status codes
9. Add docstrings for each endpoint
10. Handle authentication using FastAPI dependencies

File structure:
- Create router instance at top
- Add all route handlers
- Include any helper functions
- Export router at bottom
"""
        
        return instructions
    
    def _write_fastapi_endpoints(self, module_name: str, python_code: str, 
                                output_path: str) -> Optional[str]:
        """Write FastAPI endpoints to file."""
        try:
            # Determine file path
            endpoints_dir = os.path.join(output_path, 'app', 'api', 'v1', 'endpoints')
            os.makedirs(endpoints_dir, exist_ok=True)
            
            file_path = os.path.join(endpoints_dir, f"{module_name}.py")
            
            # Add imports and router setup if not present
            if 'from fastapi import' not in python_code:
                python_code = self._add_fastapi_imports() + '\n\n' + python_code
            
            if 'router = APIRouter()' not in python_code:
                # Find a good place to insert router
                lines = python_code.split('\n')
                import_end = 0
                for i, line in enumerate(lines):
                    if line.strip() and not (line.startswith('from ') or line.startswith('import ')):
                        import_end = i
                        break
                
                router_line = 'router = APIRouter()'
                lines.insert(import_end, '')
                lines.insert(import_end + 1, router_line)
                lines.insert(import_end + 2, '')
                python_code = '\n'.join(lines)
            
            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(python_code)
            
            self.ui.debug(f"Generated FastAPI endpoints: {file_path}")
            return file_path
            
        except Exception as e:
            self.ui.error(f"Failed to write FastAPI endpoints for {module_name}: {str(e)}")
            return None
    
    def _add_fastapi_imports(self) -> str:
        """Add standard FastAPI imports."""
        return """from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.deps import get_db
from app.models import *
from app.schemas import *"""