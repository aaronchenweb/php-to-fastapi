# generators/llm_assisted_generator.py
"""LLM-assisted code generation for PHP to FastAPI conversion."""

import json
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

from ..config.settings import Settings
from ..core.user_interface import UserInterface
from ..core.llm_client import LLMClient, LLMResponse


@dataclass
class ConversionContext:
    """Context information for LLM conversion."""
    framework: str
    database_type: str
    auth_method: str
    python_dependencies: List[str]
    endpoint_style: str
    project_structure: str


@dataclass
class ConversionRequest:
    """Request for LLM code conversion."""
    php_code: str
    conversion_type: str  # 'endpoint', 'model', 'logic', 'auth', etc.
    context: ConversionContext
    file_path: str
    additional_instructions: Optional[str] = None


@dataclass
class ConversionResult:
    """Result from LLM code conversion."""
    success: bool
    python_code: str
    error_message: Optional[str] = None
    warnings: List[str] = None
    suggestions: List[str] = None
    file_path: Optional[str] = None
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.suggestions is None:
            self.suggestions = []
        if self.dependencies is None:
            self.dependencies = []


class LLMAssistedGenerator:
    """Handles LLM-assisted code generation for complex conversions."""
    
    def __init__(self, settings: Settings, ui: UserInterface):
        self.settings = settings
        self.ui = ui
        self.llm_client = LLMClient(settings)
        
        # Template for different conversion types
        self.conversion_templates = {
            'endpoint': self._get_endpoint_conversion_template(),
            'model': self._get_model_conversion_template(),
            'auth': self._get_auth_conversion_template(),
            'logic': self._get_logic_conversion_template(),
            'config': self._get_config_conversion_template()
        }
    
    def convert_php_batch(self, request: ConversionRequest) -> ConversionResult:
        """
        Convert a batch of PHP code to Python using LLM assistance.
        
        Args:
            request: Conversion request with PHP code and context
            
        Returns:
            ConversionResult with Python code or error
        """
        try:
            self.ui.debug(f"Converting {request.conversion_type} with LLM: {request.file_path}")
            
            # Get appropriate conversion template
            template = self.conversion_templates.get(
                request.conversion_type, 
                self.conversion_templates['logic']
            )
            
            # Build conversion prompt
            system_prompt = self._build_system_prompt(request.context)
            user_prompt = self._build_user_prompt(request, template)
            
            # Send to LLM
            response = self.llm_client.generate_response(
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )
            
            if not response.success:
                return ConversionResult(
                    success=False,
                    python_code="",
                    error_message=f"LLM request failed: {response.error_message}",
                    file_path=request.file_path
                )
            
            # Parse LLM response
            return self._parse_llm_response(response, request)
            
        except Exception as e:
            return ConversionResult(
                success=False,
                python_code="",
                error_message=f"Conversion failed: {str(e)}",
                file_path=request.file_path
            )
    
    def convert_endpoint_group(self, endpoints: List[Dict[str, Any]], 
                              context: ConversionContext) -> ConversionResult:
        """Convert a group of related endpoints together for better consistency."""
        try:
            # Combine endpoints into a single conversion request
            php_code_parts = []
            endpoint_descriptions = []
            
            for endpoint in endpoints:
                endpoint_desc = f"// {endpoint.get('method', 'GET')} {endpoint.get('route', '/')}"
                endpoint_descriptions.append(endpoint_desc)
                
                # Extract PHP code if available (would come from file analysis)
                if 'php_code' in endpoint:
                    php_code_parts.append(f"{endpoint_desc}\n{endpoint['php_code']}")
                else:
                    # Create stub based on endpoint info
                    stub = self._create_endpoint_stub(endpoint)
                    php_code_parts.append(f"{endpoint_desc}\n{stub}")
            
            combined_php = "\n\n".join(php_code_parts)
            
            request = ConversionRequest(
                php_code=combined_php,
                conversion_type='endpoint',
                context=context,
                file_path="endpoints_group.php",
                additional_instructions=f"Convert these {len(endpoints)} related endpoints to FastAPI"
            )
            
            return self.convert_php_batch(request)
            
        except Exception as e:
            return ConversionResult(
                success=False,
                python_code="",
                error_message=f"Endpoint group conversion failed: {str(e)}"
            )
    
    def validate_conversion(self, original_php: str, converted_python: str, 
                           conversion_type: str) -> Dict[str, Any]:
        """Validate converted code for correctness and completeness."""
        try:
            validation_prompt = f"""
# Code Validation Task

Original PHP Code:
```php
{original_php}
```

Converted Python Code:
```python
{converted_python}
```

Please validate this {conversion_type} conversion and provide a JSON response:

{{
    "validation_status": "passed|failed|warnings",
    "completeness_score": 0.0-1.0,
    "issues": [
        {{
            "severity": "error|warning|info",
            "description": "string",
            "line_number": number,
            "suggestion": "string"
        }}
    ],
    "missing_features": ["feature1", "feature2"],
    "improvements": ["improvement1", "improvement2"]
}}
"""
            
            response = self.llm_client.generate_response(
                system_prompt="You are a code validation expert.",
                user_prompt=validation_prompt
            )
            
            if response.success:
                return self.llm_client.parse_json_response(response)
            else:
                return {"validation_status": "failed", "error": response.error_message}
                
        except Exception as e:
            return {"validation_status": "failed", "error": str(e)}
    
    def _build_system_prompt(self, context: ConversionContext) -> str:
        """Build system prompt with context information."""
        return f"""You are an expert PHP to Python/FastAPI converter with deep knowledge of both ecosystems.

Current conversion context:
- Framework: {context.framework}
- Database: {context.database_type}
- Authentication: {context.auth_method}
- Project Structure: {context.project_structure}
- Available Dependencies: {', '.join(context.python_dependencies)}

Key requirements:
1. Maintain exact API compatibility (same endpoints, methods, parameters)
2. Preserve business logic exactly
3. Use FastAPI best practices
4. Generate clean, production-ready code
5. Include proper error handling
6. Add type hints and documentation
7. Handle async/await properly when needed

Convert PHP patterns to Python equivalents:
- Classes → Python classes with proper inheritance
- Functions → Python functions with type hints
- Arrays → Lists/Dicts as appropriate
- Database queries → SQLAlchemy ORM
- Request handling → FastAPI request/response patterns
- Validation → Pydantic models
- Authentication → FastAPI dependencies"""
    
    def _build_user_prompt(self, request: ConversionRequest, template: str) -> str:
        """Build user prompt for specific conversion request."""
        additional_instructions = request.additional_instructions or ""
        
        return f"""
{template}

## PHP Code to Convert:
```php
{request.php_code}
```

## File Context:
- Original file: {request.file_path}
- Conversion type: {request.conversion_type}

{additional_instructions}

## Required Output:
Provide a JSON response with the following structure:

```json
{{
    "converted_code": "string (Python/FastAPI code)",
    "file_path": "string (suggested Python file path)",
    "dependencies": ["package1", "package2"],
    "imports": ["import statement1", "import statement2"],
    "notes": ["note1", "note2"],
    "warnings": ["warning1", "warning2"]
}}
```

Make sure the converted code:
1. Is syntactically correct Python
2. Follows FastAPI patterns
3. Maintains the same functionality as the PHP code
4. Includes proper error handling
5. Has type hints where appropriate
"""
    
    def _parse_llm_response(self, response: LLMResponse, 
                           request: ConversionRequest) -> ConversionResult:
        """Parse LLM response into ConversionResult."""
        try:
            # Parse JSON response
            parsed = self.llm_client.parse_json_response(response)
            
            return ConversionResult(
                success=True,
                python_code=parsed.get('converted_code', ''),
                file_path=parsed.get('file_path', request.file_path.replace('.php', '.py')),
                dependencies=parsed.get('dependencies', []),
                suggestions=parsed.get('notes', []),
                warnings=parsed.get('warnings', [])
            )
            
        except Exception as e:
            # If JSON parsing fails, try to extract code from response
            python_code = self._extract_code_from_response(response.content)
            
            if python_code:
                return ConversionResult(
                    success=True,
                    python_code=python_code,
                    file_path=request.file_path.replace('.php', '.py'),
                    warnings=[f"Response parsing failed, extracted code manually: {str(e)}"]
                )
            else:
                return ConversionResult(
                    success=False,
                    python_code="",
                    error_message=f"Failed to parse LLM response: {str(e)}"
                )
    
    def _extract_code_from_response(self, response_content: str) -> Optional[str]:
        """Extract Python code from LLM response if JSON parsing fails."""
        # Look for Python code blocks
        patterns = [
            r'```python\n(.*?)\n```',
            r'```\n(.*?)\n```',
            r'```py\n(.*?)\n```'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response_content, re.DOTALL)
            if matches:
                return matches[0].strip()
        
        # If no code blocks found, look for code after certain keywords
        lines = response_content.split('\n')
        code_lines = []
        in_code = False
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['from fastapi', 'import fastapi', 'def ', 'class ', 'app = FastAPI']):
                in_code = True
            
            if in_code:
                code_lines.append(line)
        
        if code_lines:
            return '\n'.join(code_lines).strip()
        
        return None
    
    def _create_endpoint_stub(self, endpoint: Dict[str, Any]) -> str:
        """Create a PHP stub for an endpoint based on metadata."""
        method = endpoint.get('method', 'GET').upper()
        route = endpoint.get('route', '/')
        handler = endpoint.get('handler', 'handle_request')
        
        stub = f"""
// {method} {route}
function {handler}() {{
    header('Content-Type: application/json');
    
"""
        
        if method == 'GET':
            stub += "    // Handle GET request\n"
            stub += "    $data = ['message' => 'GET response'];\n"
        elif method == 'POST':
            stub += "    // Handle POST request\n"
            stub += "    $input = json_decode(file_get_contents('php://input'), true);\n"
            stub += "    $data = ['message' => 'POST response', 'received' => $input];\n"
        elif method == 'PUT':
            stub += "    // Handle PUT request\n"
            stub += "    $input = json_decode(file_get_contents('php://input'), true);\n"
            stub += "    $data = ['message' => 'PUT response', 'updated' => $input];\n"
        elif method == 'DELETE':
            stub += "    // Handle DELETE request\n"
            stub += "    $data = ['message' => 'DELETE response'];\n"
        
        stub += """    
    echo json_encode($data);
}
"""
        return stub
    
    def _get_endpoint_conversion_template(self) -> str:
        """Template for endpoint conversion."""
        return """
# FastAPI Endpoint Conversion

Convert the PHP endpoint(s) to FastAPI following these patterns:

## Example Conversion:
PHP:
```php
function getUser($id) {
    header('Content-Type: application/json');
    // Get user logic
    echo json_encode($user);
}
```

FastAPI:
```python
@app.get("/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

Focus on:
- Converting routes to FastAPI decorators
- Proper parameter handling
- Request/response models
- Error handling with HTTPException
- Database operations with SQLAlchemy
- Authentication with dependencies
"""
    
    def _get_model_conversion_template(self) -> str:
        """Template for model conversion."""
        return """
# Database Model Conversion

Convert PHP model/entity classes to SQLAlchemy models.

## Example Conversion:
PHP (Eloquent):
```php
class User extends Model {
    protected $table = 'users';
    protected $fillable = ['name', 'email'];
    
    public function posts() {
        return $this->hasMany(Post::class);
    }
}
```

SQLAlchemy:
```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime, default=func.now())
    
    posts = relationship("Post", back_populates="user")
```

Focus on:
- Table definitions
- Column types and constraints
- Relationships
- Indexes and unique constraints
"""
    
    def _get_auth_conversion_template(self) -> str:
        """Template for authentication conversion."""
        return """
# Authentication System Conversion

Convert PHP authentication to FastAPI with proper security.

## Example Conversion:
PHP:
```php
function authenticate() {
    $token = $_SERVER['HTTP_AUTHORIZATION'] ?? '';
    if (!validateJWT($token)) {
        http_response_code(401);
        exit('Unauthorized');
    }
}
```

FastAPI:
```python
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username
```

Focus on:
- JWT token handling
- FastAPI security schemes
- Dependency injection for auth
- Proper exception handling
"""
    
    def _get_logic_conversion_template(self) -> str:
        """Template for business logic conversion."""
        return """
# Business Logic Conversion

Convert PHP business logic classes and functions to Python.

## Example Conversion:
PHP:
```php
class OrderService {
    public function processOrder($orderData) {
        $order = new Order($orderData);
        $order->validate();
        $order->save();
        $this->sendConfirmation($order);
        return $order;
    }
}
```

Python:
```python
class OrderService:
    def __init__(self, db: Session):
        self.db = db
    
    async def process_order(self, order_data: OrderCreate) -> Order:
        order = Order(**order_data.dict())
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        await self.send_confirmation(order)
        return order
```

Focus on:
- Class structure and methods
- Type hints and validation
- Async/await where appropriate
- Error handling
- Database session management
"""
    
    def _get_config_conversion_template(self) -> str:
        """Template for configuration conversion."""
        return """
# Configuration Conversion

Convert PHP configuration to Python settings.

## Example Conversion:
PHP:
```php
return [
    'database' => [
        'host' => env('DB_HOST', 'localhost'),
        'port' => env('DB_PORT', 3306),
        'name' => env('DB_NAME', 'app_db')
    ]
];
```

Python (Pydantic Settings):
```python
class Settings(BaseSettings):
    database_host: str = "localhost"
    database_port: int = 3306
    database_name: str = "app_db"
    
    class Config:
        env_prefix = "DB_"
```

Focus on:
- Environment variable handling
- Type validation
- Default values
- Configuration organization
"""