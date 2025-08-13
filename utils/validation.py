"""
Validation utilities for PHP to FastAPI converter.
Validates generated Python/FastAPI code for syntax errors, imports, and best practices.
"""

import ast
import sys
import re
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, NamedTuple
from dataclasses import dataclass
import importlib.util


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