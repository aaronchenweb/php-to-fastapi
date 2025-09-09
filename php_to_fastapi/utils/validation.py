"""
Validation utilities for PHP to FastAPI converter.
Validates generated Python/FastAPI code for syntax errors, imports, and best practices.
"""

import ast
import os
import sys
import re
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, NamedTuple, Tuple
from dataclasses import dataclass
import importlib.util

try:
    from ..core.detector import PHPProjectDetector
except ImportError:
    # Fallback for development
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from ..core.detector import PHPProjectDetector

@dataclass
class ValidationResult:
    """Result of a validation operation."""
    is_valid: bool
    message: str
    suggestions: Optional[List[str]] = None
    warnings: Optional[List[str]] = None


def validate_project_path(project_path: str) -> bool:
    """
    Validate that the PHP project path is valid and contains a PHP project.
    
    Args:
        project_path: Path to the PHP project directory
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Check if path exists
    if not os.path.exists(project_path):
        print(f"❌ Error: Path '{project_path}' does not exist")
        return False
    
    # Check if it's a directory
    if not os.path.isdir(project_path):
        print(f"❌ Error: Path '{project_path}' is not a directory")
        return False
    
    # Check if it's a valid PHP project
    detector = PHPProjectDetector()
    validation_result = detector.validate_project(project_path)
    
    if not validation_result.is_valid:
        print(f"❌ Error: '{project_path}' does not appear to be a valid PHP web API project")
        print(f"   Reason: {validation_result.reason}")
        if validation_result.suggestions:
            print("   Suggestions:")
            for suggestion in validation_result.suggestions:
                print(f"   • {suggestion}")
        return False
    
    return True


def validate_output_path(output_path: str, create_if_missing: bool = True) -> ValidationResult:
    """
    Validate output directory path.
    
    Args:
        output_path: Path to the output directory
        create_if_missing: Whether to create directory if it doesn't exist
        
    Returns:
        ValidationResult: Validation result with details
    """
    path = Path(output_path)
    
    # Check if path exists
    if path.exists():
        if not path.is_dir():
            return ValidationResult(
                is_valid=False,
                message=f"Output path '{output_path}' exists but is not a directory"
            )
        
        # Check if directory is empty
        if any(path.iterdir()):
            return ValidationResult(
                is_valid=True,
                message=f"Output directory '{output_path}' exists and is not empty",
                warnings=[
                    "Directory is not empty - existing files may be overwritten",
                    "Consider using a different output directory or backing up existing files"
                ]
            )
    else:
        # Try to create directory if requested
        if create_if_missing:
            try:
                path.mkdir(parents=True, exist_ok=True)
                return ValidationResult(
                    is_valid=True,
                    message=f"Created output directory: {output_path}"
                )
            except PermissionError:
                return ValidationResult(
                    is_valid=False,
                    message=f"Permission denied: Cannot create directory '{output_path}'",
                    suggestions=[
                        "Check directory permissions",
                        "Try a different output directory",
                        "Run with appropriate permissions"
                    ]
                )
            except Exception as e:
                return ValidationResult(
                    is_valid=False,
                    message=f"Failed to create directory '{output_path}': {e}"
                )
        else:
            return ValidationResult(
                is_valid=False,
                message=f"Output directory '{output_path}' does not exist"
            )
    
    return ValidationResult(
        is_valid=True,
        message=f"Output directory '{output_path}' is valid"
    )


def validate_file_path(file_path: str, must_exist: bool = True) -> ValidationResult:
    """
    Validate file path.
    
    Args:
        file_path: Path to the file
        must_exist: Whether file must exist
        
    Returns:
        ValidationResult: Validation result with details
    """
    path = Path(file_path)
    
    if must_exist:
        if not path.exists():
            return ValidationResult(
                is_valid=False,
                message=f"File '{file_path}' does not exist"
            )
        
        if not path.is_file():
            return ValidationResult(
                is_valid=False,
                message=f"Path '{file_path}' is not a file"
            )
    else:
        # Check if parent directory exists and is writable
        parent = path.parent
        if not parent.exists():
            try:
                parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                return ValidationResult(
                    is_valid=False,
                    message=f"Cannot create parent directory for '{file_path}': {e}"
                )
        
        # Check write permissions
        if not os.access(parent, os.W_OK):
            return ValidationResult(
                is_valid=False,
                message=f"No write permission for directory '{parent}'"
            )
    
    return ValidationResult(
        is_valid=True,
        message=f"File path '{file_path}' is valid"
    )


def validate_llm_config() -> ValidationResult:
    """
    Validate LLM configuration from environment variables.
    
    Returns:
        ValidationResult: Validation result with details
    """
    api_key = os.getenv('LLM_API_KEY')
    provider = os.getenv('LLM_PROVIDER', 'openai')
    model = os.getenv('LLM_MODEL')
    
    if not api_key:
        return ValidationResult(
            is_valid=False,
            message="LLM_API_KEY environment variable is required",
            suggestions=[
                "Set LLM_API_KEY environment variable",
                "Example: export LLM_API_KEY='your-api-key-here'"
            ]
        )
    
    # Validate provider
    valid_providers = ['openai', 'anthropic', 'gemini']
    if provider not in valid_providers:
        return ValidationResult(
            is_valid=False,
            message=f"Invalid LLM provider '{provider}'",
            suggestions=[
                f"Valid providers: {', '.join(valid_providers)}",
                f"Set LLM_PROVIDER to one of: {', '.join(valid_providers)}"
            ]
        )
    
    # Check API key format (basic validation)
    warnings = []
    if provider == 'openai' and not api_key.startswith('sk-'):
        warnings.append("OpenAI API keys typically start with 'sk-'")
    elif provider == 'anthropic' and not api_key.startswith('sk-ant-'):
        warnings.append("Anthropic API keys typically start with 'sk-ant-'")
    
    return ValidationResult(
        is_valid=True,
        message="LLM configuration is valid",
        warnings=warnings
    )


def validate_python_environment() -> ValidationResult:
    """
    Validate Python environment requirements.
    
    Returns:
        ValidationResult: Validation result with details
    """
    import sys
    
    # Check Python version
    if sys.version_info < (3, 8):
        return ValidationResult(
            is_valid=False,
            message=f"Python 3.8 or higher required (current: {sys.version})",
            suggestions=[
                "Upgrade to Python 3.8 or higher",
                "Use pyenv or conda to manage Python versions"
            ]
        )
    
    # Check required modules (basic check)
    required_modules = [
        'argparse', 'pathlib', 'json', 'os', 'sys',
        'typing', 'dataclasses', 'logging'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        return ValidationResult(
            is_valid=False,
            message=f"Missing required modules: {', '.join(missing_modules)}",
            suggestions=[
                "Install missing modules",
                "Consider using a virtual environment"
            ]
        )
    
    return ValidationResult(
        is_valid=True,
        message="Python environment is valid"
    )


def validate_all_requirements(
    php_project_path: str,
    output_path: Optional[str] = None
) -> Tuple[bool, List[ValidationResult]]:
    """
    Validate all requirements for conversion.
    
    Args:
        php_project_path: Path to PHP project
        output_path: Optional output path
        
    Returns:
        Tuple of (all_valid, list_of_results)
    """
    results = []
    
    # Validate Python environment
    results.append(validate_python_environment())
    
    # Validate LLM configuration
    results.append(validate_llm_config())
    
    # Validate PHP project path
    if validate_project_path(php_project_path):
        results.append(ValidationResult(
            is_valid=True,
            message=f"PHP project path '{php_project_path}' is valid"
        ))
    else:
        results.append(ValidationResult(
            is_valid=False,
            message=f"PHP project path '{php_project_path}' is invalid"
        ))
    
    # Validate output path if provided
    if output_path:
        results.append(validate_output_path(output_path))
    
    # Check if all validations passed
    all_valid = all(result.is_valid for result in results)
    
    return all_valid, results


class ValidationError(Exception):
    """Exception raised for validation errors."""
    pass


@dataclass
class ValidationResult:
    """Result of a validation operation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]
    
    def __bool__(self) -> bool:
        """Return True if validation passed."""
        return self.is_valid
    
    def add_error(self, error: str) -> None:
        """Add an error to the result."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str) -> None:
        """Add a warning to the result."""
        self.warnings.append(warning)
    
    def add_suggestion(self, suggestion: str) -> None:
        """Add a suggestion to the result."""
        self.suggestions.append(suggestion)


class PythonValidator:
    """Validates Python code syntax and structure."""
    
    def __init__(self):
        self.required_imports = {
            'fastapi': ['FastAPI', 'APIRouter', 'HTTPException', 'Depends'],
            'pydantic': ['BaseModel', 'Field'],
            'typing': ['Optional', 'List', 'Dict']
        }
    
    def validate_syntax(self, code: str, filename: str = "<string>") -> ValidationResult:
        """
        Validate Python syntax using AST parsing.
        
        Args:
            code: Python code to validate
            filename: Name for error reporting
            
        Returns:
            ValidationResult with syntax validation results
        """
        result = ValidationResult(True, [], [], [])
        
        try:
            # Parse the code into an AST
            ast.parse(code, filename=filename)
            
        except SyntaxError as e:
            result.add_error(f"Syntax error in {filename} at line {e.lineno}: {e.msg}")
            
        except Exception as e:
            result.add_error(f"Failed to parse {filename}: {str(e)}")
        
        return result
    
    def validate_imports(self, code: str) -> ValidationResult:
        """
        Validate that required imports are present and correctly formatted.
        
        Args:
            code: Python code to validate
            
        Returns:
            ValidationResult with import validation results
        """
        result = ValidationResult(True, [], [], [])
        
        try:
            tree = ast.parse(code)
            
            # Extract all imports
            imports = {}
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports[name.name] = name.asname or name.name
                        
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        for name in node.names:
                            key = f"{node.module}.{name.name}"
                            imports[key] = name.asname or name.name
            
            # Check for unused imports (basic check)
            code_text = code.replace('\n', ' ')
            for import_path, alias in imports.items():
                if alias not in code_text:
                    result.add_warning(f"Potentially unused import: {import_path}")
            
            # Check for missing common imports
            if 'fastapi' in code.lower():
                if not any('fastapi' in imp for imp in imports):
                    result.add_suggestion("Consider importing FastAPI components")
            
            if 'basemodel' in code.lower():
                if not any('pydantic' in imp for imp in imports):
                    result.add_suggestion("Consider importing from pydantic for BaseModel")
                    
        except Exception as e:
            result.add_error(f"Failed to validate imports: {str(e)}")
        
        return result
    
    def validate_function_definitions(self, code: str) -> ValidationResult:
        """
        Validate function definitions for common issues.
        
        Args:
            code: Python code to validate
            
        Returns:
            ValidationResult with function validation results
        """
        result = ValidationResult(True, [], [], [])
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check for missing docstrings
                    if not ast.get_docstring(node):
                        result.add_warning(f"Function '{node.name}' missing docstring")
                    
                    # Check for async functions without await
                    if isinstance(node, ast.AsyncFunctionDef):
                        has_await = any(
                            isinstance(n, ast.Await) 
                            for n in ast.walk(node)
                        )
                        if not has_await:
                            result.add_warning(f"Async function '{node.name}' has no await statements")
                    
                    # Check for functions with too many parameters
                    if len(node.args.args) > 5:
                        result.add_suggestion(f"Function '{node.name}' has many parameters, consider using a model")
                        
        except Exception as e:
            result.add_error(f"Failed to validate functions: {str(e)}")
        
        return result
    
    def validate_code_quality(self, code: str) -> ValidationResult:
        """
        Validate code quality and style.
        
        Args:
            code: Python code to validate
            
        Returns:
            ValidationResult with quality validation results
        """
        result = ValidationResult(True, [], [], [])
        
        # Check line length
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            if len(line) > 100:
                result.add_warning(f"Line {i} exceeds 100 characters")
        
        # Check for hardcoded values
        hardcoded_patterns = [
            r'"localhost"',
            r"'localhost'",
            r'127\.0\.0\.1',
            r'password.*=.*["\'][^"\']*["\']',
            r'secret.*=.*["\'][^"\']*["\']'
        ]
        
        for pattern in hardcoded_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                result.add_suggestion("Consider using environment variables for configuration")
                break
        
        # Check for TODO/FIXME comments
        todo_pattern = r'#.*(?:TODO|FIXME|XXX)'
        if re.search(todo_pattern, code, re.IGNORECASE):
            result.add_warning("Code contains TODO/FIXME comments")
        
        return result


class FastAPIValidator:
    """Validates FastAPI-specific code patterns."""
    
    def validate_route_definitions(self, code: str) -> ValidationResult:
        """
        Validate FastAPI route definitions.
        
        Args:
            code: Python code to validate
            
        Returns:
            ValidationResult with route validation results
        """
        result = ValidationResult(True, [], [], [])
        
        try:
            tree = ast.parse(code)
            
            # Find route decorators
            route_decorators = ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check if function has route decorator
                    has_route_decorator = False
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Attribute):
                            if decorator.attr in route_decorators:
                                has_route_decorator = True
                                break
                        elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
                            if decorator.func.attr in route_decorators:
                                has_route_decorator = True
                                break
                    
                    if has_route_decorator:
                        # Validate route function
                        if not node.args.args:
                            result.add_error(f"Route function '{node.name}' has no parameters")
                        
                        # Check for proper return type annotation
                        if not node.returns:
                            result.add_suggestion(f"Route function '{node.name}' missing return type annotation")
                        
                        # Check for proper error handling
                        has_http_exception = any(
                            isinstance(n, ast.Name) and n.id == 'HTTPException'
                            for n in ast.walk(node)
                        )
                        if not has_http_exception:
                            result.add_suggestion(f"Route function '{node.name}' should handle errors with HTTPException")
                            
        except Exception as e:
            result.add_error(f"Failed to validate routes: {str(e)}")
        
        return result
    
    def validate_pydantic_models(self, code: str) -> ValidationResult:
        """
        Validate Pydantic model definitions.
        
        Args:
            code: Python code to validate
            
        Returns:
            ValidationResult with model validation results
        """
        result = ValidationResult(True, [], [], [])
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if class inherits from BaseModel
                    inherits_basemodel = any(
                        (isinstance(base, ast.Name) and base.id == 'BaseModel') or
                        (isinstance(base, ast.Attribute) and base.attr == 'BaseModel')
                        for base in node.bases
                    )
                    
                    if inherits_basemodel:
                        # Validate model fields
                        has_fields = False
                        for item in node.body:
                            if isinstance(item, ast.AnnAssign):
                                has_fields = True
                                # Check field annotation
                                if not item.annotation:
                                    result.add_error(f"Model field in '{node.name}' missing type annotation")
                        
                        if not has_fields:
                            result.add_warning(f"Pydantic model '{node.name}' has no fields")
                        
                        # Check for docstring
                        if not ast.get_docstring(node):
                            result.add_suggestion(f"Pydantic model '{node.name}' missing docstring")
                            
        except Exception as e:
            result.add_error(f"Failed to validate Pydantic models: {str(e)}")
        
        return result
    
    def validate_dependency_injection(self, code: str) -> ValidationResult:
        """
        Validate FastAPI dependency injection patterns.
        
        Args:
            code: Python code to validate
            
        Returns:
            ValidationResult with dependency validation results
        """
        result = ValidationResult(True, [], [], [])
        
        # Check for proper Depends usage
        if 'Depends(' in code:
            if 'from fastapi import' not in code and 'import fastapi' not in code:
                result.add_error("Using Depends() but FastAPI not imported")
        
        # Check for database dependency patterns
        if 'get_db' in code:
            if 'yield' not in code:
                result.add_suggestion("Database dependencies should use yield for proper cleanup")
        
        return result


class ProjectValidator:
    """Validates entire FastAPI project structure."""
    
    def __init__(self, project_path: Union[str, Path]):
        """
        Initialize project validator.
        
        Args:
            project_path: Path to the FastAPI project
        """
        self.project_path = Path(project_path)
    
    def validate_project_structure(self) -> ValidationResult:
        """
        Validate overall project structure.
        
        Returns:
            ValidationResult with project validation results
        """
        result = ValidationResult(True, [], [], [])
        
        if not self.project_path.exists():
            result.add_error(f"Project path {self.project_path} does not exist")
            return result
        
        # Check for essential files
        essential_files = [
            'main.py',
            'requirements.txt',
            '.env'
        ]
        
        for file_name in essential_files:
            file_path = self.project_path / file_name
            if not file_path.exists():
                result.add_error(f"Missing essential file: {file_name}")
        
        # Check for recommended directories
        recommended_dirs = [
            'app',
            'app/routers',
            'app/models',
            'app/core'
        ]
        
        for dir_name in recommended_dirs:
            dir_path = self.project_path / dir_name
            if not dir_path.exists():
                result.add_suggestion(f"Consider creating directory: {dir_name}")
        
        return result
    
    def validate_all_python_files(self) -> ValidationResult:
        """
        Validate all Python files in the project.
        
        Returns:
            ValidationResult with all file validation results
        """
        result = ValidationResult(True, [], [], [])
        
        python_validator = PythonValidator()
        fastapi_validator = FastAPIValidator()
        
        # Find all Python files
        python_files = list(self.project_path.rglob("*.py"))
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    code = f.read()
                
                # Validate syntax
                syntax_result = python_validator.validate_syntax(code, str(py_file))
                result.errors.extend(syntax_result.errors)
                result.warnings.extend(syntax_result.warnings)
                result.suggestions.extend(syntax_result.suggestions)
                
                if not syntax_result.is_valid:
                    result.is_valid = False
                    continue  # Skip further validation if syntax is invalid
                
                # Validate imports
                import_result = python_validator.validate_imports(code)
                result.warnings.extend(import_result.warnings)
                result.suggestions.extend(import_result.suggestions)
                
                # Validate FastAPI specific patterns
                if 'fastapi' in code.lower():
                    route_result = fastapi_validator.validate_route_definitions(code)
                    result.errors.extend(route_result.errors)
                    result.warnings.extend(route_result.warnings)
                    result.suggestions.extend(route_result.suggestions)
                    
                    if not route_result.is_valid:
                        result.is_valid = False
                
                if 'basemodel' in code.lower():
                    model_result = fastapi_validator.validate_pydantic_models(code)
                    result.errors.extend(model_result.errors)
                    result.warnings.extend(model_result.warnings)
                    result.suggestions.extend(model_result.suggestions)
                    
                    if not model_result.is_valid:
                        result.is_valid = False
                
            except Exception as e:
                result.add_error(f"Failed to validate {py_file}: {str(e)}")
        
        return result
    
    def validate_requirements(self) -> ValidationResult:
        """
        Validate requirements.txt file.
        
        Returns:
            ValidationResult with requirements validation results
        """
        result = ValidationResult(True, [], [], [])
        
        req_file = self.project_path / 'requirements.txt'
        if not req_file.exists():
            result.add_error("requirements.txt file not found")
            return result
        
        try:
            with open(req_file, 'r', encoding='utf-8') as f:
                requirements = f.read()
            
            # Check for essential dependencies
            essential_deps = ['fastapi', 'uvicorn', 'pydantic']
            
            for dep in essential_deps:
                if dep not in requirements.lower():
                    result.add_error(f"Missing essential dependency: {dep}")
            
            # Check for version pinning
            lines = [line.strip() for line in requirements.split('\n') if line.strip()]
            unpinned = [line for line in lines if not re.search(r'[=<>]', line)]
            
            if unpinned:
                result.add_suggestion("Consider pinning versions for: " + ", ".join(unpinned))
                
        except Exception as e:
            result.add_error(f"Failed to validate requirements.txt: {str(e)}")
        
        return result
    
    def run_linting(self) -> ValidationResult:
        """
        Run external linting tools if available.
        
        Returns:
            ValidationResult with linting results
        """
        result = ValidationResult(True, [], [], [])
        
        # Try to run flake8 if available
        try:
            cmd = ['flake8', str(self.project_path), '--max-line-length=100']
            output = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if output.returncode != 0:
                result.add_warning("Linting issues found (flake8)")
                for line in output.stdout.split('\n'):
                    if line.strip():
                        result.add_warning(line.strip())
                        
        except (subprocess.TimeoutExpired, FileNotFoundError):
            result.add_suggestion("Install flake8 for additional code quality checks")
        except Exception as e:
            result.add_warning(f"Linting check failed: {str(e)}")
        
        return result


def validate_generated_project(project_path: Union[str, Path]) -> ValidationResult:
    """
    Validate a complete generated FastAPI project.
    
    Args:
        project_path: Path to the generated project
        
    Returns:
        ValidationResult with comprehensive validation results
    """
    validator = ProjectValidator(project_path)
    
    # Combine all validation results
    results = [
        validator.validate_project_structure(),
        validator.validate_all_python_files(),
        validator.validate_requirements(),
        validator.run_linting()
    ]
    
    # Merge results
    final_result = ValidationResult(True, [], [], [])
    
    for result in results:
        final_result.errors.extend(result.errors)
        final_result.warnings.extend(result.warnings)
        final_result.suggestions.extend(result.suggestions)
        
        if not result.is_valid:
            final_result.is_valid = False
    
    return final_result