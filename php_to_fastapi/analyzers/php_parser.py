# analyzers/php_parser.py
"""PHP code parser for extracting functions, classes, and code structure."""

import re
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PHPFunction:
    """Represents a PHP function."""
    name: str
    parameters: List[str] = field(default_factory=list)
    return_type: Optional[str] = None
    visibility: str = "public"  # public, private, protected
    is_static: bool = False
    docstring: Optional[str] = None
    body: str = ""
    line_number: int = 0
    file_path: str = ""


@dataclass
class PHPClass:
    """Represents a PHP class."""
    name: str
    namespace: Optional[str] = None
    extends: Optional[str] = None
    implements: List[str] = field(default_factory=list)
    properties: List[Dict[str, Any]] = field(default_factory=list)
    methods: List[PHPFunction] = field(default_factory=list)
    constants: List[Dict[str, Any]] = field(default_factory=list)
    is_abstract: bool = False
    is_interface: bool = False
    is_trait: bool = False
    docstring: Optional[str] = None
    line_number: int = 0
    file_path: str = ""


@dataclass
class PHPFile:
    """Represents a parsed PHP file."""
    file_path: str
    namespace: Optional[str] = None
    uses: List[str] = field(default_factory=list)  # use statements
    classes: List[PHPClass] = field(default_factory=list)
    functions: List[PHPFunction] = field(default_factory=list)
    constants: List[Dict[str, Any]] = field(default_factory=list)
    includes: List[str] = field(default_factory=list)  # require/include statements
    php_version_features: List[str] = field(default_factory=list)


class PHPParser:
    """Parser for PHP code files."""
    
    def __init__(self):
        self.function_pattern = re.compile(
            r'(?:(?P<visibility>public|private|protected)\s+)?'
            r'(?P<static>static\s+)?'
            r'function\s+(?P<name>\w+)\s*\((?P<params>[^)]*)\)'
            r'(?:\s*:\s*(?P<return_type>\w+))?',
            re.MULTILINE | re.DOTALL
        )
        
        self.class_pattern = re.compile(
            r'(?P<abstract>abstract\s+)?'
            r'(?P<type>class|interface|trait)\s+(?P<name>\w+)'
            r'(?:\s+extends\s+(?P<extends>\w+))?'
            r'(?:\s+implements\s+(?P<implements>[\w\s,]+))?',
            re.MULTILINE
        )
        
        self.property_pattern = re.compile(
            r'(?P<visibility>public|private|protected)\s+'
            r'(?P<static>static\s+)?'
            r'(?P<type>\$\w+)(?:\s*=\s*(?P<default>[^;]+))?;',
            re.MULTILINE
        )
        
        self.namespace_pattern = re.compile(r'namespace\s+([\w\\]+);')
        self.use_pattern = re.compile(r'use\s+([\w\\]+)(?:\s+as\s+(\w+))?;')
        self.include_pattern = re.compile(r'(?:require|include)(?:_once)?\s*\(?["\']([^"\']+)["\']')
    
    def parse_file(self, file_path: str) -> Optional[PHPFile]:
        """Parse a single PHP file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            return self._parse_content(content, file_path)
            
        except Exception as e:
            print(f"Error parsing file {file_path}: {str(e)}")
            return None
    
    def parse_directory(self, directory_path: str) -> List[PHPFile]:
        """Parse all PHP files in a directory."""
        parsed_files = []
        
        for root, dirs, files in os.walk(directory_path):
            # Skip common directories to ignore
            dirs[:] = [d for d in dirs if d not in ['vendor', 'node_modules', '.git', 'cache', 'logs']]
            
            for file in files:
                if file.endswith(('.php', '.phtml', '.inc')):
                    file_path = os.path.join(root, file)
                    parsed_file = self.parse_file(file_path)
                    if parsed_file:
                        parsed_files.append(parsed_file)
        
        return parsed_files
    
    def _parse_content(self, content: str, file_path: str) -> PHPFile:
        """Parse PHP content and extract structure."""
        php_file = PHPFile(file_path=file_path)
        
        # Remove comments to avoid false matches
        cleaned_content = self._remove_comments(content)
        
        # Extract namespace
        php_file.namespace = self._extract_namespace(cleaned_content)
        
        # Extract use statements
        php_file.uses = self._extract_uses(cleaned_content)
        
        # Extract includes
        php_file.includes = self._extract_includes(cleaned_content)
        
        # Extract classes
        php_file.classes = self._extract_classes(cleaned_content, file_path)
        
        # Extract standalone functions (not in classes)
        php_file.functions = self._extract_standalone_functions(cleaned_content, file_path)
        
        # Extract constants
        php_file.constants = self._extract_constants(cleaned_content)
        
        # Detect PHP version features
        php_file.php_version_features = self._detect_php_features(content)
        
        return php_file
    
    def _remove_comments(self, content: str) -> str:
        """Remove PHP comments from content."""
        # Remove single-line comments
        content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
        content = re.sub(r'#.*?$', '', content, flags=re.MULTILINE)
        
        # Remove multi-line comments
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        return content
    
    def _extract_namespace(self, content: str) -> Optional[str]:
        """Extract namespace from PHP content."""
        match = self.namespace_pattern.search(content)
        return match.group(1) if match else None
    
    def _extract_uses(self, content: str) -> List[str]:
        """Extract use statements from PHP content."""
        uses = []
        for match in self.use_pattern.finditer(content):
            namespace = match.group(1)
            alias = match.group(2)
            uses.append(f"{namespace} as {alias}" if alias else namespace)
        return uses
    
    def _extract_includes(self, content: str) -> List[str]:
        """Extract include/require statements."""
        includes = []
        for match in self.include_pattern.finditer(content):
            includes.append(match.group(1))
        return includes
    
    def _extract_classes(self, content: str, file_path: str) -> List[PHPClass]:
        """Extract classes from PHP content."""
        classes = []
        
        for match in self.class_pattern.finditer(content):
            class_name = match.group('name')
            class_type = match.group('type')
            
            php_class = PHPClass(
                name=class_name,
                file_path=file_path,
                line_number=content[:match.start()].count('\n') + 1,
                is_abstract=bool(match.group('abstract')),
                is_interface=class_type == 'interface',
                is_trait=class_type == 'trait'
            )
            
            if match.group('extends'):
                php_class.extends = match.group('extends')
            
            if match.group('implements'):
                implements = match.group('implements').strip()
                php_class.implements = [impl.strip() for impl in implements.split(',')]
            
            # Extract class body
            class_body = self._extract_class_body(content, match.end())
            if class_body:
                # Extract methods
                php_class.methods = self._extract_methods(class_body, file_path, class_name)
                
                # Extract properties
                php_class.properties = self._extract_properties(class_body)
                
                # Extract constants
                php_class.constants = self._extract_class_constants(class_body)
                
                # Extract docstring
                php_class.docstring = self._extract_docstring_before(content, match.start())
            
            classes.append(php_class)
        
        return classes
    
    def _extract_class_body(self, content: str, start_pos: int) -> Optional[str]:
        """Extract the body of a class."""
        # Find the opening brace
        brace_pos = content.find('{', start_pos)
        if brace_pos == -1:
            return None
        
        # Find the matching closing brace
        brace_count = 0
        pos = brace_pos
        
        while pos < len(content):
            if content[pos] == '{':
                brace_count += 1
            elif content[pos] == '}':
                brace_count -= 1
                if brace_count == 0:
                    return content[brace_pos + 1:pos]
            pos += 1
        
        return None
    
    def _extract_methods(self, class_body: str, file_path: str, class_name: str) -> List[PHPFunction]:
        """Extract methods from class body."""
        methods = []
        
        for match in self.function_pattern.finditer(class_body):
            method = PHPFunction(
                name=match.group('name'),
                file_path=file_path,
                line_number=class_body[:match.start()].count('\n') + 1,
                visibility=match.group('visibility') or 'public',
                is_static=bool(match.group('static')),
                return_type=match.group('return_type')
            )
            
            # Parse parameters
            params_str = match.group('params')
            if params_str:
                method.parameters = self._parse_parameters(params_str)
            
            # Extract method body
            method.body = self._extract_function_body(class_body, match.end())
            
            # Extract docstring
            method.docstring = self._extract_docstring_before(class_body, match.start())
            
            methods.append(method)
        
        return methods
    
    def _extract_standalone_functions(self, content: str, file_path: str) -> List[PHPFunction]:
        """Extract standalone functions (not in classes)."""
        functions = []
        
        # Remove class bodies to avoid finding methods
        content_without_classes = self._remove_class_bodies(content)
        
        for match in self.function_pattern.finditer(content_without_classes):
            function = PHPFunction(
                name=match.group('name'),
                file_path=file_path,
                line_number=content_without_classes[:match.start()].count('\n') + 1,
                visibility='public',  # Standalone functions are always public
                return_type=match.group('return_type')
            )
            
            # Parse parameters
            params_str = match.group('params')
            if params_str:
                function.parameters = self._parse_parameters(params_str)
            
            # Extract function body
            function.body = self._extract_function_body(content_without_classes, match.end())
            
            # Extract docstring
            function.docstring = self._extract_docstring_before(content_without_classes, match.start())
            
            functions.append(function)
        
        return functions
    
    def _remove_class_bodies(self, content: str) -> str:
        """Remove class bodies from content to isolate standalone functions."""
        result = []
        in_class = 0
        i = 0
        
        while i < len(content):
            if content[i:i+5] == 'class' and (i == 0 or not content[i-1].isalnum()):
                # Found start of class
                brace_pos = content.find('{', i)
                if brace_pos != -1:
                    result.append(content[i:brace_pos + 1])
                    i = brace_pos + 1
                    brace_count = 1
                    
                    # Skip class body
                    while i < len(content) and brace_count > 0:
                        if content[i] == '{':
                            brace_count += 1
                        elif content[i] == '}':
                            brace_count -= 1
                        i += 1
                    
                    result.append('}')
                    continue
            
            result.append(content[i])
            i += 1
        
        return ''.join(result)
    
    def _parse_parameters(self, params_str: str) -> List[str]:
        """Parse function parameters."""
        params = []
        if not params_str.strip():
            return params
        
        # Split by comma, but be careful with nested arrays/objects
        param_parts = []
        current_param = ""
        paren_count = 0
        
        for char in params_str:
            if char == '(' or char == '[':
                paren_count += 1
            elif char == ')' or char == ']':
                paren_count -= 1
            elif char == ',' and paren_count == 0:
                param_parts.append(current_param.strip())
                current_param = ""
                continue
            
            current_param += char
        
        if current_param.strip():
            param_parts.append(current_param.strip())
        
        for param in param_parts:
            # Extract parameter name and type
            param = param.strip()
            if param:
                # Remove default values for simplicity
                if '=' in param:
                    param = param.split('=')[0].strip()
                params.append(param)
        
        return params
    
    def _extract_function_body(self, content: str, start_pos: int) -> str:
        """Extract function body."""
        # Find the opening brace
        brace_pos = content.find('{', start_pos)
        if brace_pos == -1:
            return ""
        
        # Find the matching closing brace
        brace_count = 0
        pos = brace_pos
        
        while pos < len(content):
            if content[pos] == '{':
                brace_count += 1
            elif content[pos] == '}':
                brace_count -= 1
                if brace_count == 0:
                    return content[brace_pos + 1:pos].strip()
            pos += 1
        
        return ""
    
    def _extract_properties(self, class_body: str) -> List[Dict[str, Any]]:
        """Extract class properties."""
        properties = []
        
        for match in self.property_pattern.finditer(class_body):
            prop = {
                'name': match.group('type'),
                'visibility': match.group('visibility'),
                'is_static': bool(match.group('static')),
                'default_value': match.group('default')
            }
            properties.append(prop)
        
        return properties
    
    def _extract_constants(self, content: str) -> List[Dict[str, Any]]:
        """Extract constants from content."""
        constants = []
        const_pattern = re.compile(r'define\s*\(\s*["\'](\w+)["\']\s*,\s*([^)]+)\)')
        
        for match in const_pattern.finditer(content):
            const = {
                'name': match.group(1),
                'value': match.group(2).strip()
            }
            constants.append(const)
        
        return constants
    
    def _extract_class_constants(self, class_body: str) -> List[Dict[str, Any]]:
        """Extract class constants."""
        constants = []
        const_pattern = re.compile(r'const\s+(\w+)\s*=\s*([^;]+);')
        
        for match in const_pattern.finditer(class_body):
            const = {
                'name': match.group(1),
                'value': match.group(2).strip()
            }
            constants.append(const)
        
        return constants
    
    def _extract_docstring_before(self, content: str, pos: int) -> Optional[str]:
        """Extract docstring comment before a position."""
        # Look backwards for /** ... */ comment
        lines = content[:pos].split('\n')
        
        # Look for docstring in the last few lines
        docstring_lines = []
        for line in reversed(lines[-10:]):  # Check last 10 lines
            line = line.strip()
            if line.endswith('*/'):
                docstring_lines.insert(0, line[:-2].strip())
                break
            elif line.startswith('*'):
                docstring_lines.insert(0, line[1:].strip())
            elif line.startswith('/**'):
                docstring_lines.insert(0, line[3:].strip())
                break
            elif line and not line.startswith('*'):
                # Hit non-comment line
                break
        
        return '\n'.join(docstring_lines) if docstring_lines else None
    
    def _detect_php_features(self, content: str) -> List[str]:
        """Detect PHP version-specific features."""
        features = []
        
        # PHP 7.0+ features
        if re.search(r'\?\?', content):  # Null coalescing operator
            features.append('null_coalescing_operator')
        
        if re.search(r'function.*?:\s*\w+', content):  # Return type declarations
            features.append('return_type_declarations')
        
        # PHP 7.1+ features
        if re.search(r'function.*?:\s*void', content):  # Void return type
            features.append('void_return_type')
        
        if re.search(r'\[\]', content):  # Short array syntax
            features.append('short_array_syntax')
        
        # PHP 7.4+ features
        if re.search(r'fn\s*\(.*?\)\s*=>', content):  # Arrow functions
            features.append('arrow_functions')
        
        # PHP 8.0+ features
        if re.search(r'match\s*\(', content):  # Match expressions
            features.append('match_expressions')
        
        if re.search(r'#\[.*?\]', content):  # Attributes
            features.append('attributes')
        
        # Namespaces
        if re.search(r'namespace\s+', content):
            features.append('namespaces')
        
        # Traits
        if re.search(r'trait\s+\w+', content):
            features.append('traits')
        
        return features
    
    def get_analysis_summary(self, parsed_files: List[PHPFile]) -> Dict[str, Any]:
        """Get summary analysis of parsed files."""
        summary = {
            'total_files': len(parsed_files),
            'total_classes': 0,
            'total_functions': 0,
            'total_methods': 0,
            'namespaces': set(),
            'php_features': set(),
            'file_types': {
                'with_classes': 0,
                'with_functions': 0,
                'configuration': 0,
                'views': 0
            },
            'complexity_metrics': {
                'avg_methods_per_class': 0,
                'avg_functions_per_file': 0,
                'max_class_methods': 0
            }
        }
        
        total_methods = 0
        total_classes_with_methods = 0
        max_methods_in_class = 0
        
        for php_file in parsed_files:
            # Count classes
            summary['total_classes'] += len(php_file.classes)
            
            # Count functions
            summary['total_functions'] += len(php_file.functions)
            
            # Count methods
            for php_class in php_file.classes:
                method_count = len(php_class.methods)
                total_methods += method_count
                if method_count > 0:
                    total_classes_with_methods += 1
                max_methods_in_class = max(max_methods_in_class, method_count)
            
            # Collect namespaces
            if php_file.namespace:
                summary['namespaces'].add(php_file.namespace)
            
            # Collect PHP features
            summary['php_features'].update(php_file.php_version_features)
            
            # Classify file types
            if php_file.classes:
                summary['file_types']['with_classes'] += 1
            if php_file.functions:
                summary['file_types']['with_functions'] += 1
            
            file_path_lower = php_file.file_path.lower()
            if any(keyword in file_path_lower for keyword in ['config', 'setting']):
                summary['file_types']['configuration'] += 1
            elif any(keyword in file_path_lower for keyword in ['view', 'template']):
                summary['file_types']['views'] += 1
        
        # Calculate averages
        summary['total_methods'] = total_methods
        
        if total_classes_with_methods > 0:
            summary['complexity_metrics']['avg_methods_per_class'] = total_methods / total_classes_with_methods
        
        if len(parsed_files) > 0:
            summary['complexity_metrics']['avg_functions_per_file'] = summary['total_functions'] / len(parsed_files)
        
        summary['complexity_metrics']['max_class_methods'] = max_methods_in_class
        
        # Convert sets to lists for JSON serialization
        summary['namespaces'] = list(summary['namespaces'])
        summary['php_features'] = list(summary['php_features'])
        
        return summary