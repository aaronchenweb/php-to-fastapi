# generators/route_generator.py
"""Generates FastAPI routes from PHP API endpoints."""

import re
from typing import Dict, List, Any, Optional, Tuple

from .shared import GeneratedFile, RouteInfo


class RouteGenerator:
    """Generates FastAPI routes from PHP endpoints."""
    
    def __init__(self):
        # HTTP method mappings
        self.method_mappings = {
            'GET': 'get',
            'POST': 'post',
            'PUT': 'put',
            'DELETE': 'delete',
            'PATCH': 'patch'
        }
        
        # Common PHP to Python parameter type mappings
        self.param_type_mappings = {
            'int': 'int',
            'integer': 'int',
            'string': 'str',
            'bool': 'bool',
            'boolean': 'bool',
            'float': 'float',
            'array': 'list'
        }
    
    def generate_route_files(self, 
                           analysis_result: Dict[str, Any], 
                           planning_result: Dict[str, Any]) -> List[GeneratedFile]:
        """Generate all route files."""
        files = []
        
        # Generate main API router
        api_router_content = self._generate_api_router(analysis_result, planning_result)
        files.append(GeneratedFile(
            path="app/api/v1/api.py",
            content=api_router_content,
            file_type="python",
            description="Main API router"
        ))
        
        # Generate endpoint files by category
        endpoint_analysis = analysis_result.get('endpoint_analysis', {})
        endpoint_categories = endpoint_analysis.get('endpoint_categories', [])
        
        if not endpoint_categories:
            # Generate example endpoints if none found
            example_content = self._generate_example_endpoints()
            files.append(GeneratedFile(
                path="app/api/v1/endpoints/example.py",
                content=example_content,
                file_type="python",
                description="Example endpoints"
            ))
            endpoint_categories = [{'category': 'example'}]
        
        for category in endpoint_categories:
            category_name = category.get('category', 'general').lower().replace(' ', '_')
            endpoints_content = self._generate_category_endpoints(category, analysis_result)
            
            files.append(GeneratedFile(
                path=f"app/api/v1/endpoints/{category_name}.py",
                content=endpoints_content,
                file_type="python",
                description=f"Endpoints for {category.get('category', 'general')}",
                php_source_files=[endpoint.get('file_path', '') for endpoint in category.get('endpoints', [])]
            ))
        
        # Generate endpoints __init__.py
        endpoints_init_content = self._generate_endpoints_init(endpoint_categories)
        files.append(GeneratedFile(
            path="app/api/v1/endpoints/__init__.py",
            content=endpoints_init_content,
            file_type="python",
            description="Endpoints package initialization"
        ))
        
        # Generate API v1 __init__.py
        api_init_content = '''"""API v1 package."""\n\nfrom .api import api_router\n\n__all__ = ["api_router"]'''
        files.append(GeneratedFile(
            path="app/api/v1/__init__.py",
            content=api_init_content,
            file_type="python",
            description="API v1 package initialization"
        ))
        
        return files
    
    def _generate_api_router(self, 
                           analysis_result: Dict[str, Any], 
                           planning_result: Dict[str, Any]) -> str:
        """Generate the main API router."""
        endpoint_analysis = analysis_result.get('endpoint_analysis', {})
        endpoint_categories = endpoint_analysis.get('endpoint_categories', [])
        
        if not endpoint_categories:
            endpoint_categories = [{'category': 'example'}]
        
        # Generate imports
        imports = ['from fastapi import APIRouter']
        router_includes = []
        
        for category in endpoint_categories:
            category_name = category.get('category', 'general').lower().replace(' ', '_')
            module_name = f"app.api.v1.endpoints.{category_name}"
            imports.append(f"from {module_name} import router as {category_name}_router")
            
            tag_name = category.get('category', 'general').title()
            prefix = f"/{category_name}"
            router_includes.append(f'api_router.include_router({category_name}_router, prefix="{prefix}", tags=["{tag_name}"])')
        
        template = f'''"""
Main API router for version 1.
"""

{chr(10).join(imports)}

api_router = APIRouter()

# Include all endpoint routers
{chr(10).join(router_includes)}


@api_router.get("/")
async def api_root():
    """API root endpoint."""
    return {{
        "message": "FastAPI v1 API",
        "version": "1.0.0",
        "endpoints": "See /docs for available endpoints"
    }}
'''
        
        return template.strip()
    
    def _generate_category_endpoints(self, 
                                   category: Dict[str, Any], 
                                   analysis_result: Dict[str, Any]) -> str:
        """Generate endpoints for a specific category."""
        category_name = category.get('category', 'general')
        endpoints = category.get('endpoints', [])
        
        # Convert endpoints to route info
        routes = []
        for endpoint in endpoints:
            route_info = self._convert_endpoint_to_route(endpoint, category_name)
            if route_info:
                routes.append(route_info)
        
        # Generate the file content
        class_name = category_name.replace(' ', '')
        module_name = category_name.lower().replace(' ', '_')
        
        # Generate imports
        imports = [
            'from typing import List, Optional',
            'from fastapi import APIRouter, Depends, HTTPException, status',
            'from sqlalchemy.orm import Session',
            '',
            'from app.api.dependencies import get_db, get_current_user',
            f'from app.schemas.{module_name} import {class_name}Create, {class_name}Update, {class_name}Response',
            f'from app.services.{module_name}_service import {module_name}_service',
            ''
        ]
        
        # Generate router
        router_definition = f'router = APIRouter()\n\n'
        
        # Generate route functions
        route_functions = []
        for route in routes:
            function_code = self._generate_route_function(route, class_name, module_name)
            route_functions.append(function_code)
        
        # If no routes found, generate basic CRUD
        if not route_functions:
            route_functions = self._generate_basic_crud_routes(class_name, module_name)
        
        content = ''.join(imports) + router_definition + '\n\n'.join(route_functions)
        
        # Add docstring
        docstring = f'"""\n{category_name} API endpoints.\nConverted from PHP endpoints.\n"""\n\n'
        
        return docstring + content
    
    def _generate_example_endpoints(self) -> str:
        """Generate example endpoints when none found."""
        template = '''"""
Example API endpoints.
Replace with your actual endpoints based on PHP analysis.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user

router = APIRouter()


@router.get("/", response_model=Dict[str, Any])
async def get_example_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get example list."""
    return {
        "items": [],
        "total": 0,
        "skip": skip,
        "limit": limit,
        "message": "Replace with actual endpoint implementation"
    }


@router.get("/{item_id}", response_model=Dict[str, Any])
async def get_example(
    item_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get example by ID."""
    return {
        "id": item_id,
        "message": "Replace with actual endpoint implementation"
    }


@router.post("/", response_model=Dict[str, Any])
async def create_example(
    item: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Create new example."""
    return {
        "id": 1,
        "message": "Replace with actual endpoint implementation",
        "created_by": current_user.get("id")
    }
'''
        
        return template.strip()
    
    def _convert_endpoint_to_route(self, endpoint: Dict[str, Any], category_name: str) -> Optional[RouteInfo]:
        """Convert PHP endpoint to FastAPI route info."""
        route = endpoint.get('route', '')
        method = endpoint.get('method', 'GET').upper()
        handler = endpoint.get('handler', '')
        
        if not route or not method:
            return None
        
        # Clean and convert route
        fastapi_path = self._convert_php_route_to_fastapi(route)
        
        # Generate function name
        function_name = self._generate_function_name(method, route, handler)
        
        # Extract parameters
        parameters = self._extract_route_parameters(fastapi_path)
        
        # Determine if auth is required
        requires_auth = self._requires_authentication(endpoint)
        
        # Generate description
        description = self._generate_route_description(method, route, category_name)
        
        return RouteInfo(
            method=method,
            path=fastapi_path,
            function_name=function_name,
            description=description,
            parameters=parameters,
            requires_auth=requires_auth,
            request_body_schema=self._get_request_schema(method, category_name),
            response_schema=self._get_response_schema(category_name),
            php_source=f"{method} {route} -> {handler}"
        )
    
    def _convert_php_route_to_fastapi(self, php_route: str) -> str:
        """Convert PHP route pattern to FastAPI format."""
        # Remove leading/trailing slashes and whitespace
        route = php_route.strip().strip('/')
        
        # Convert PHP parameter patterns to FastAPI
        # {id} -> {id} (already compatible)
        # :id -> {id}
        route = re.sub(r':(\w+)', r'{\1}', route)
        
        # Handle Laravel optional parameters {id?} -> {id} (FastAPI doesn't support optional path params)
        route = re.sub(r'\{(\w+)\?\}', r'{\1}', route)
        
        # Ensure route starts with /
        if not route.startswith('/'):
            route = '/' + route
        
        return route
    
    def _generate_function_name(self, method: str, route: str, handler: str) -> str:
        """Generate FastAPI function name from PHP endpoint info."""
        # Extract meaningful parts from route
        route_parts = [part for part in route.split('/') if part and not part.startswith('{')]
        
        # Use handler name if available and meaningful
        if handler and handler != 'unknown' and handler != 'anonymous':
            base_name = handler.replace('Controller', '').replace('Action', '')
            # Convert camelCase to snake_case
            base_name = re.sub(r'(?<!^)(?=[A-Z])', '_', base_name).lower()
        else:
            # Generate from route and method
            if route_parts:
                base_name = '_'.join(route_parts)
            else:
                base_name = 'root'
        
        # Add method prefix for clarity
        method_prefixes = {
            'GET': 'get',
            'POST': 'create',
            'PUT': 'update',
            'DELETE': 'delete',
            'PATCH': 'patch'
        }
        
        prefix = method_prefixes.get(method, method.lower())
        
        # Combine and clean
        if base_name.startswith(prefix):
            function_name = base_name
        else:
            function_name = f"{prefix}_{base_name}"
        
        # Clean up
        function_name = re.sub(r'[^a-zA-Z0-9_]', '_', function_name)
        function_name = re.sub(r'_+', '_', function_name).strip('_')
        
        return function_name
    
    def _extract_route_parameters(self, route: str) -> List[Dict[str, Any]]:
        """Extract parameters from FastAPI route."""
        parameters = []
        
        # Find path parameters
        path_params = re.findall(r'\{(\w+)\}', route)
        for param in path_params:
            parameters.append({
                'name': param,
                'type': 'int' if param.endswith('_id') or param == 'id' else 'str',
                'location': 'path',
                'required': True
            })
        
        return parameters
    
    def _requires_authentication(self, endpoint: Dict[str, Any]) -> bool:
        """Determine if endpoint requires authentication."""
        route = endpoint.get('route', '').lower()
        middleware = endpoint.get('middleware', [])
        authentication = endpoint.get('authentication', '')
        
        # Check for auth indicators
        auth_indicators = [
            'auth' in route,
            'login' in route,
            'logout' in route,
            'protected' in route,
            'admin' in route,
            'user' in route,
            any('auth' in str(m).lower() for m in middleware),
            authentication == 'required'
        ]
        
        return any(auth_indicators)
    
    def _generate_route_description(self, method: str, route: str, category_name: str) -> str:
        """Generate description for the route."""
        route_clean = route.strip('/')
        
        if not route_clean:
            return f"{method} {category_name} root endpoint"
        
        # Generate based on method and route structure
        if method == 'GET':
            if '{' in route:
                return f"Get specific {category_name.lower()} by ID"
            else:
                return f"Get {category_name.lower()} list"
        elif method == 'POST':
            return f"Create new {category_name.lower()}"
        elif method == 'PUT':
            return f"Update {category_name.lower()}"
        elif method == 'DELETE':
            return f"Delete {category_name.lower()}"
        elif method == 'PATCH':
            return f"Partially update {category_name.lower()}"
        else:
            return f"{method} {category_name.lower()} endpoint"
    
    def _get_request_schema(self, method: str, category_name: str) -> Optional[str]:
        """Get request schema for the method."""
        class_name = category_name.replace(' ', '')
        
        if method in ['POST']:
            return f'{class_name}Create'
        elif method in ['PUT', 'PATCH']:
            return f'{class_name}Update'
        
        return None
    
    def _get_response_schema(self, category_name: str) -> str:
        """Get response schema for the category."""
        class_name = category_name.replace(' ', '')
        return f'{class_name}Response'
    
    def _generate_route_function(self, route: RouteInfo, class_name: str, module_name: str) -> str:
        """Generate FastAPI route function code."""
        # Build parameters
        params = []
        
        # Add path parameters
        for param in route.parameters:
            if param['location'] == 'path':
                param_type = param['type']
                params.append(f"{param['name']}: {param_type}")
        
        # Add database dependency
        params.append("db: Session = Depends(get_db)")
        
        # Add authentication if required
        if route.requires_auth:
            params.append("current_user: dict = Depends(get_current_user)")
        
        # Add request body for POST/PUT/PATCH
        if route.request_body_schema:
            params.append(f"item: {route.request_body_schema}")
        
        # Add query parameters for GET requests
        if route.method == 'GET' and not any(p['location'] == 'path' for p in route.parameters):
            params.append("skip: int = 0")
            params.append("limit: int = 100")
        
        params_str = ',\n    '.join(params)
        
        # Generate function body based on method
        body = self._generate_function_body(route, class_name, module_name)
        
        # Generate decorator
        method_lower = route.method.lower()
        response_model = f"List[{route.response_schema}]" if route.method == 'GET' and not any(p['location'] == 'path' for p in route.parameters) else route.response_schema
        
        decorator = f'@router.{method_lower}("{route.path}", response_model={response_model})'
        
        function_template = f'''{decorator}
async def {route.function_name}(
    {params_str}
) -> {response_model}:
    """{route.description}."""
{body}
'''
        
        return function_template
    
    def _generate_function_body(self, route: RouteInfo, class_name: str, module_name: str) -> str:
        """Generate function body based on route method."""
        service_name = f"{module_name}_service"
        
        if route.method == 'GET':
            if any(p['location'] == 'path' for p in route.parameters):
                # Get single item
                id_param = next(p['name'] for p in route.parameters if p['location'] == 'path')
                return f'''    item = {service_name}.get(db, id={id_param})
    if item is None:
        raise HTTPException(status_code=404, detail="{class_name} not found")
    return item'''
            else:
                # Get list
                return f'''    items = {service_name}.get_multi(db, skip=skip, limit=limit)
    return items'''
        
        elif route.method == 'POST':
            return f'''    item = {service_name}.create(db, obj_in=item)
    return item'''
        
        elif route.method in ['PUT', 'PATCH']:
            id_param = next((p['name'] for p in route.parameters if p['location'] == 'path'), 'id')
            return f'''    db_item = {service_name}.get(db, id={id_param})
    if db_item is None:
        raise HTTPException(status_code=404, detail="{class_name} not found")
    item = {service_name}.update(db, db_obj=db_item, obj_in=item)
    return item'''
        
        elif route.method == 'DELETE':
            id_param = next((p['name'] for p in route.parameters if p['location'] == 'path'), 'id')
            return f'''    item = {service_name}.remove(db, id={id_param})
    if item is None:
        raise HTTPException(status_code=404, detail="{class_name} not found")
    return item'''
        
        else:
            return f'''    # TODO: Implement {route.method} logic
    return {{"message": "{route.method} not implemented"}}'''
    
    def _generate_basic_crud_routes(self, class_name: str, module_name: str) -> List[str]:
        """Generate basic CRUD routes if no specific routes found."""
        service_name = f"{module_name}_service"
        
        routes = []
        
        # GET list
        routes.append(f'''@router.get("/", response_model=List[{class_name}Response])
async def get_{module_name}_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> List[{class_name}Response]:
    """Get {module_name} list."""
    items = {service_name}.get_multi(db, skip=skip, limit=limit)
    return items''')
        
        # GET single
        routes.append(f'''@router.get("/{{item_id}}", response_model={class_name}Response)
async def get_{module_name}(
    item_id: int,
    db: Session = Depends(get_db)
) -> {class_name}Response:
    """Get {module_name} by ID."""
    item = {service_name}.get(db, id=item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="{class_name} not found")
    return item''')
        
        # POST create
        routes.append(f'''@router.post("/", response_model={class_name}Response)
async def create_{module_name}(
    item: {class_name}Create,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> {class_name}Response:
    """Create new {module_name}."""
    item = {service_name}.create(db, obj_in=item)
    return item''')
        
        # PUT update
        routes.append(f'''@router.put("/{{item_id}}", response_model={class_name}Response)
async def update_{module_name}(
    item_id: int,
    item: {class_name}Update,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> {class_name}Response:
    """Update {module_name}."""
    db_item = {service_name}.get(db, id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="{class_name} not found")
    item = {service_name}.update(db, db_obj=db_item, obj_in=item)
    return item''')
        
        # DELETE
        routes.append(f'''@router.delete("/{{item_id}}", response_model={class_name}Response)
async def delete_{module_name}(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> {class_name}Response:
    """Delete {module_name}."""
    item = {service_name}.remove(db, id=item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="{class_name} not found")
    return item''')
        
        return routes
    
    def _generate_endpoints_init(self, endpoint_categories: List[Dict[str, Any]]) -> str:
        """Generate endpoints package __init__.py."""
        imports = []
        
        for category in endpoint_categories:
            category_name = category.get('category', 'general').lower().replace(' ', '_')
            imports.append(f"from .{category_name} import router as {category_name}_router")
        
        all_exports = [f"{cat.get('category', 'general').lower().replace(' ', '_')}_router" 
                      for cat in endpoint_categories]
        
        template = f'''"""
API endpoints package.
"""

{chr(10).join(imports)}

__all__ = [
    {", ".join(f'"{export}"' for export in all_exports)}
]
'''
        
        return template.strip()