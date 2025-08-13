# analyzers/api_extractor.py
"""API endpoint extractor for PHP web applications."""

import re
import os
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class APIEndpoint:
    """Represents an API endpoint."""
    method: str  # GET, POST, PUT, DELETE, PATCH
    route: str   # URL pattern
    handler: str  # Function/method name that handles the request
    file_path: str
    line_number: int = 0
    parameters: List[str] = field(default_factory=list)
    middleware: List[str] = field(default_factory=list)
    authentication: Optional[str] = None
    description: Optional[str] = None
    request_body: Optional[Dict[str, Any]] = None
    response_format: Optional[str] = None
    
    
@dataclass
class APIGroup:
    """Represents a group of related API endpoints."""
    name: str
    prefix: str
    endpoints: List[APIEndpoint] = field(default_factory=list)
    middleware: List[str] = field(default_factory=list)
    description: Optional[str] = None


class APIExtractor:
    """Extracts API endpoints and routes from PHP applications."""
    
    def __init__(self):
        # Laravel route patterns
        self.laravel_patterns = [
            re.compile(r'Route::(get|post|put|delete|patch|any)\s*\(\s*["\']([^"\']+)["\']\s*,\s*["\']?([^"\')\s]+)["\']?\s*\)', re.IGNORECASE),
            re.compile(r'Route::(get|post|put|delete|patch|any)\s*\(\s*["\']([^"\']+)["\']\s*,\s*\[([^\]]+)\]\s*\)', re.IGNORECASE),
            re.compile(r'\$router->(get|post|put|delete|patch|any)\s*\(\s*["\']([^"\']+)["\']\s*,\s*["\']?([^"\')\s]+)["\']?\s*\)', re.IGNORECASE)
        ]
        
        # Slim framework patterns
        self.slim_patterns = [
            re.compile(r'\$app->(get|post|put|delete|patch|any)\s*\(\s*["\']([^"\']+)["\']\s*,\s*["\']?([^"\')\s]+)["\']?\s*\)', re.IGNORECASE),
            re.compile(r'\$app->(get|post|put|delete|patch|any)\s*\(\s*["\']([^"\']+)["\']\s*,\s*function\s*\(', re.IGNORECASE)
        ]
        
        # CodeIgniter patterns
        self.codeigniter_patterns = [
            re.compile(r'\$route\[["\']([^"\']+)["\']\]\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
        ]
        
        # Generic PHP patterns
        self.generic_patterns = [
            re.compile(r'\$_(?:GET|POST|PUT|DELETE|REQUEST)\s*\[["\']([^"\']+)["\']\]', re.IGNORECASE),
            re.compile(r'if\s*\(\s*\$_SERVER\[["\']REQUEST_METHOD["\']\]\s*==\s*["\'](\w+)["\']\s*\)', re.IGNORECASE)
        ]
        
        # Authentication patterns
        self.auth_patterns = [
            re.compile(r'(jwt|token|bearer|auth|session)', re.IGNORECASE),
            re.compile(r'middleware\s*\(\s*["\']([^"\']*auth[^"\']*)["\']', re.IGNORECASE),
            re.compile(r'@authenticated|@auth|@guest', re.IGNORECASE)
        ]
        
        # Response format patterns
        self.response_patterns = [
            re.compile(r'header\s*\(\s*["\']Content-Type:\s*application/json["\']', re.IGNORECASE),
            re.compile(r'json_encode\s*\(', re.IGNORECASE),
            re.compile(r'response\(\)->json\(', re.IGNORECASE),
            re.compile(r'return\s+response\(\)', re.IGNORECASE)
        ]
    
    def extract_from_file(self, file_path: str) -> List[APIEndpoint]:
        """Extract API endpoints from a single PHP file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            return self._extract_endpoints_from_content(content, file_path)
            
        except Exception as e:
            print(f"Error extracting from file {file_path}: {str(e)}")
            return []
    
    def extract_from_directory(self, directory_path: str) -> List[APIEndpoint]:
        """Extract API endpoints from all PHP files in a directory."""
        endpoints = []
        
        for root, dirs, files in os.walk(directory_path):
            # Skip common directories to ignore
            dirs[:] = [d for d in dirs if d not in ['vendor', 'node_modules', '.git', 'cache', 'logs', 'storage']]
            
            for file in files:
                if file.endswith(('.php', '.phtml')):
                    file_path = os.path.join(root, file)
                    file_endpoints = self.extract_from_file(file_path)
                    endpoints.extend(file_endpoints)
        
        return endpoints
    
    def _extract_endpoints_from_content(self, content: str, file_path: str) -> List[APIEndpoint]:
        """Extract endpoints from PHP content."""
        endpoints = []
        
        # Try different framework patterns
        endpoints.extend(self._extract_laravel_routes(content, file_path))
        endpoints.extend(self._extract_slim_routes(content, file_path))
        endpoints.extend(self._extract_codeigniter_routes(content, file_path))
        endpoints.extend(self._extract_generic_routes(content, file_path))
        
        # Add authentication and response format info
        for endpoint in endpoints:
            self._analyze_endpoint_details(endpoint, content)
        
        return endpoints
    
    def _extract_laravel_routes(self, content: str, file_path: str) -> List[APIEndpoint]:
        """Extract Laravel/Lumen route definitions."""
        endpoints = []
        lines = content.split('\n')
        
        for pattern in self.laravel_patterns:
            for match in pattern.finditer(content):
                method = match.group(1).upper()
                route = match.group(2)
                handler = match.group(3) if len(match.groups()) >= 3 else "anonymous"
                
                # Find line number
                line_number = content[:match.start()].count('\n') + 1
                
                endpoint = APIEndpoint(
                    method=method,
                    route=route,
                    handler=handler,
                    file_path=file_path,
                    line_number=line_number
                )
                
                # Extract route parameters
                endpoint.parameters = self._extract_route_parameters(route)
                
                # Look for middleware in the same line or nearby
                endpoint.middleware = self._extract_middleware_from_context(content, match.start(), match.end())
                
                endpoints.append(endpoint)
        
        # Look for route groups
        self._process_route_groups(content, endpoints, file_path)
        
        return endpoints
    
    def _extract_slim_routes(self, content: str, file_path: str) -> List[APIEndpoint]:
        """Extract Slim framework route definitions."""
        endpoints = []
        
        for pattern in self.slim_patterns:
            for match in pattern.finditer(content):
                method = match.group(1).upper()
                route = match.group(2)
                handler = match.group(3) if len(match.groups()) >= 3 else "closure"
                
                line_number = content[:match.start()].count('\n') + 1
                
                endpoint = APIEndpoint(
                    method=method,
                    route=route,
                    handler=handler,
                    file_path=file_path,
                    line_number=line_number
                )
                
                endpoint.parameters = self._extract_route_parameters(route)
                endpoints.append(endpoint)
        
        return endpoints
    
    def _extract_codeigniter_routes(self, content: str, file_path: str) -> List[APIEndpoint]:
        """Extract CodeIgniter route definitions."""
        endpoints = []
        
        for pattern in self.codeigniter_patterns:
            for match in pattern.finditer(content):
                route = match.group(1)
                controller_method = match.group(2)
                
                line_number = content[:match.start()].count('\n') + 1
                
                # CodeIgniter routes don't specify HTTP method directly
                # We'll infer from the route pattern or default to GET
                method = self._infer_http_method(route, controller_method)
                
                endpoint = APIEndpoint(
                    method=method,
                    route=route,
                    handler=controller_method,
                    file_path=file_path,
                    line_number=line_number
                )
                
                endpoint.parameters = self._extract_route_parameters(route)
                endpoints.append(endpoint)
        
        return endpoints
    
    def _extract_generic_routes(self, content: str, file_path: str) -> List[APIEndpoint]:
        """Extract routes from generic PHP code."""
        endpoints = []
        
        # Look for $_GET, $_POST patterns
        param_pattern = re.compile(r'\$_(GET|POST|PUT|DELETE|REQUEST)\s*\[["\']([^"\']+)["\']\]')
        for match in param_pattern.finditer(content):
            method = match.group(1)
            if method == 'REQUEST':
                method = 'GET'  # Default assumption
            
            param_name = match.group(2)
            
            # Try to infer route from context
            route = f"/{param_name}"  # Simple assumption
            
            line_number = content[:match.start()].count('\n') + 1
            
            endpoint = APIEndpoint(
                method=method,
                route=route,
                handler="unknown",
                file_path=file_path,
                line_number=line_number
            )
            
            endpoints.append(endpoint)
        
        # Look for REQUEST_METHOD checks
        method_pattern = re.compile(r'if\s*\(\s*\$_SERVER\[["\']REQUEST_METHOD["\']\]\s*==\s*["\'](\w+)["\']\s*\)')
        for match in method_pattern.finditer(content):
            method = match.group(1).upper()
            line_number = content[:match.start()].count('\n') + 1
            
            # Try to determine route from file name or context
            route = self._infer_route_from_file(file_path)
            
            endpoint = APIEndpoint(
                method=method,
                route=route,
                handler=os.path.basename(file_path),
                file_path=file_path,
                line_number=line_number
            )
            
            endpoints.append(endpoint)
        
        return endpoints
    
    def _extract_route_parameters(self, route: str) -> List[str]:
        """Extract parameters from route pattern."""
        parameters = []
        
        # Laravel/Slim style: {id}, {name}
        laravel_params = re.findall(r'\{(\w+)\??}', route)
        parameters.extend(laravel_params)
        
        # CodeIgniter style: (:num), (:any), (:segment)
        ci_params = re.findall(r'\(:(num|any|segment)\)', route)
        parameters.extend([f"param_{i}" for i, param in enumerate(ci_params)])
        
        # Express style: :id, :name
        express_params = re.findall(r':(\w+)', route)
        parameters.extend(express_params)
        
        return parameters
    
    def _extract_middleware_from_context(self, content: str, start: int, end: int) -> List[str]:
        """Extract middleware from route context."""
        middleware = []
        
        # Look for middleware in the same line or nearby lines
        context_start = max(0, start - 200)
        context_end = min(len(content), end + 200)
        context = content[context_start:context_end]
        
        # Laravel middleware patterns
        middleware_patterns = [
            re.compile(r'middleware\s*\(\s*["\']([^"\']+)["\']', re.IGNORECASE),
            re.compile(r'->middleware\s*\(\s*["\']([^"\']+)["\']', re.IGNORECASE)
        ]
        
        for pattern in middleware_patterns:
            for match in pattern.finditer(context):
                middleware.append(match.group(1))
        
        return middleware
    
    def _process_route_groups(self, content: str, endpoints: List[APIEndpoint], file_path: str) -> None:
        """Process route groups and apply group settings to endpoints."""
        group_pattern = re.compile(
            r'Route::group\s*\(\s*\[([^\]]+)\]\s*,\s*function\s*\(\s*\)\s*\{',
            re.IGNORECASE | re.DOTALL
        )
        
        for match in group_pattern.finditer(content):
            group_config = match.group(1)
            group_start = match.end()
            
            # Find the end of the group
            group_end = self._find_closure_end(content, group_start)
            if group_end == -1:
                continue
            
            # Parse group configuration
            prefix = self._extract_group_prefix(group_config)
            middleware = self._extract_group_middleware(group_config)
            
            # Apply to endpoints within this group
            for endpoint in endpoints:
                if group_start <= content.find(f"line {endpoint.line_number}") <= group_end:
                    if prefix:
                        endpoint.route = f"{prefix}{endpoint.route}"
                    endpoint.middleware.extend(middleware)
    
    def _find_closure_end(self, content: str, start: int) -> int:
        """Find the end of a closure starting at given position."""
        brace_count = 0
        pos = start
        
        while pos < len(content):
            if content[pos] == '{':
                brace_count += 1
            elif content[pos] == '}':
                brace_count -= 1
                if brace_count == 0:
                    return pos
            pos += 1
        
        return -1
    
    def _extract_group_prefix(self, group_config: str) -> Optional[str]:
        """Extract prefix from route group configuration."""
        prefix_match = re.search(r'["\']prefix["\']\s*=>\s*["\']([^"\']+)["\']', group_config)
        return prefix_match.group(1) if prefix_match else None
    
    def _extract_group_middleware(self, group_config: str) -> List[str]:
        """Extract middleware from route group configuration."""
        middleware = []
        
        # Single middleware
        single_match = re.search(r'["\']middleware["\']\s*=>\s*["\']([^"\']+)["\']', group_config)
        if single_match:
            middleware.append(single_match.group(1))
        
        # Array of middleware
        array_match = re.search(r'["\']middleware["\']\s*=>\s*\[([^\]]+)\]', group_config)
        if array_match:
            middleware_str = array_match.group(1)
            middleware_items = re.findall(r'["\']([^"\']+)["\']', middleware_str)
            middleware.extend(middleware_items)
        
        return middleware
    
    def _infer_http_method(self, route: str, handler: str) -> str:
        """Infer HTTP method from route and handler."""
        route_lower = route.lower()
        handler_lower = handler.lower()
        
        # Common patterns
        if any(word in route_lower for word in ['create', 'store', 'add']):
            return 'POST'
        elif any(word in route_lower for word in ['update', 'edit']):
            return 'PUT'
        elif any(word in route_lower for word in ['delete', 'remove']):
            return 'DELETE'
        elif any(word in handler_lower for word in ['post', 'create', 'store']):
            return 'POST'
        elif any(word in handler_lower for word in ['put', 'update', 'edit']):
            return 'PUT'
        elif any(word in handler_lower for word in ['delete', 'remove']):
            return 'DELETE'
        else:
            return 'GET'  # Default
    
    def _infer_route_from_file(self, file_path: str) -> str:
        """Infer route from file path."""
        # Get filename without extension
        filename = Path(file_path).stem
        
        # Convert to route format
        if filename == 'index':
            return '/'
        else:
            return f'/{filename}'
    
    def _analyze_endpoint_details(self, endpoint: APIEndpoint, content: str) -> None:
        """Analyze endpoint for additional details like authentication and response format."""
        # Check for authentication
        for pattern in self.auth_patterns:
            if pattern.search(content):
                endpoint.authentication = "required"
                break
        
        # Check response format
        for pattern in self.response_patterns:
            if pattern.search(content):
                endpoint.response_format = "json"
                break
        
        # If no specific format found, assume HTML
        if not endpoint.response_format:
            endpoint.response_format = "html"
    
    def group_endpoints(self, endpoints: List[APIEndpoint]) -> List[APIGroup]:
        """Group endpoints by common prefixes or patterns."""
        groups = {}
        
        for endpoint in endpoints:
            # Determine group based on route prefix
            route_parts = endpoint.route.strip('/').split('/')
            if len(route_parts) > 0 and route_parts[0]:
                group_name = route_parts[0]
                prefix = f"/{route_parts[0]}"
            else:
                group_name = "root"
                prefix = ""
            
            if group_name not in groups:
                groups[group_name] = APIGroup(
                    name=group_name,
                    prefix=prefix,
                    endpoints=[],
                    description=f"Endpoints for {group_name}"
                )
            
            groups[group_name].endpoints.append(endpoint)
        
        return list(groups.values())
    
    def analyze_endpoints(self, endpoints: List[APIEndpoint]) -> Dict[str, Any]:
        """Analyze extracted endpoints and provide summary."""
        analysis = {
            'total_endpoints': len(endpoints),
            'http_methods': {},
            'authentication_required': 0,
            'response_formats': {},
            'parameters': {
                'total_parameterized': 0,
                'common_parameter_names': {}
            },
            'middleware_usage': {},
            'file_distribution': {},
            'complexity_score': 0
        }
        
        for endpoint in endpoints:
            # Count HTTP methods
            method = endpoint.method
            analysis['http_methods'][method] = analysis['http_methods'].get(method, 0) + 1
            
            # Count authentication
            if endpoint.authentication:
                analysis['authentication_required'] += 1
            
            # Count response formats
            format_type = endpoint.response_format or 'unknown'
            analysis['response_formats'][format_type] = analysis['response_formats'].get(format_type, 0) + 1
            
            # Analyze parameters
            if endpoint.parameters:
                analysis['parameters']['total_parameterized'] += 1
                for param in endpoint.parameters:
                    analysis['parameters']['common_parameter_names'][param] = \
                        analysis['parameters']['common_parameter_names'].get(param, 0) + 1
            
            # Analyze middleware
            for middleware in endpoint.middleware:
                analysis['middleware_usage'][middleware] = analysis['middleware_usage'].get(middleware, 0) + 1
            
            # File distribution
            file_name = os.path.basename(endpoint.file_path)
            analysis['file_distribution'][file_name] = analysis['file_distribution'].get(file_name, 0) + 1
        
        # Calculate complexity score
        # Based on number of endpoints, parameters, middleware, etc.
        complexity_factors = [
            len(endpoints),
            len(analysis['http_methods']),
            analysis['parameters']['total_parameterized'],
            len(analysis['middleware_usage']),
            analysis['authentication_required']
        ]
        
        analysis['complexity_score'] = sum(complexity_factors) / 5  # Normalized score
        
        # Determine complexity level
        if analysis['complexity_score'] < 5:
            analysis['complexity_level'] = 'low'
        elif analysis['complexity_score'] < 15:
            analysis['complexity_level'] = 'medium'
        else:
            analysis['complexity_level'] = 'high'
        
        return analysis
    
    def generate_openapi_spec(self, endpoints: List[APIEndpoint], title: str = "API") -> Dict[str, Any]:
        """Generate OpenAPI specification from endpoints."""
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": title,
                "version": "1.0.0",
                "description": "API converted from PHP"
            },
            "paths": {}
        }
        
        for endpoint in endpoints:
            route = endpoint.route
            method = endpoint.method.lower()
            
            if route not in spec["paths"]:
                spec["paths"][route] = {}
            
            operation = {
                "summary": f"{endpoint.handler} handler",
                "description": endpoint.description or f"Endpoint handled by {endpoint.handler}",
                "responses": {
                    "200": {
                        "description": "Successful response"
                    }
                }
            }
            
            # Add parameters
            if endpoint.parameters:
                operation["parameters"] = []
                for param in endpoint.parameters:
                    operation["parameters"].append({
                        "name": param,
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"}
                    })
            
            # Add authentication
            if endpoint.authentication:
                operation["security"] = [{"bearerAuth": []}]
            
            spec["paths"][route][method] = operation
        
        # Add security schemes if authentication is used
        if any(ep.authentication for ep in endpoints):
            spec["components"] = {
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
            }
        
        return spec