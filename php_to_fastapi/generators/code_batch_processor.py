# generators/code_batch_processor.py
"""Handles large codebases by processing them in intelligent batches for LLM conversion."""

import os
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path

from ..config.settings import Settings
from ..core.user_interface import UserInterface


@dataclass
class CodeBatch:
    """Represents a batch of code for processing."""
    name: str
    php_code: str
    file_path: str
    batch_type: str  # 'endpoint', 'model', 'logic', 'auth', etc.
    priority: int = 1  # 1=high, 2=medium, 3=low
    dependencies: List[str] = field(default_factory=list)
    estimated_complexity: str = "medium"  # low, medium, high
    line_count: int = 0
    character_count: int = 0


@dataclass
class BatchGroup:
    """Group of related batches."""
    name: str
    description: str
    batches: List[CodeBatch] = field(default_factory=list)
    total_lines: int = 0
    processing_order: int = 1


class CodeBatchProcessor:
    """Processes large codebases by creating intelligent batches for LLM conversion."""
    
    def __init__(self, settings: Settings, ui: UserInterface):
        self.settings = settings
        self.ui = ui
        
        # Batch size limits (adjustable based on LLM context window)
        self.max_lines_per_batch = 500
        self.max_chars_per_batch = 15000  # Conservative estimate for LLM context
        self.optimal_lines_per_batch = 300
        self.optimal_chars_per_batch = 10000
        
        # Code patterns for intelligent batching
        self.endpoint_patterns = [
            r'function\s+\w+\s*\([^)]*\)\s*{[^}]*(?:header|json_encode|echo|print)[^}]*}',
            r'Route::[a-zA-Z]+\s*\(',
            r'\$app->[a-zA-Z]+\s*\(',
            r'@Route\s*\(',
            r'\$_(?:GET|POST|PUT|DELETE|REQUEST)'
        ]
        
        self.model_patterns = [
            r'class\s+\w+\s+extends\s+(?:Model|Eloquent|ActiveRecord)',
            r'protected\s+\$table\s*=',
            r'protected\s+\$fillable\s*=',
            r'public\s+function\s+\w+\s*\([^)]*\)\s*{\s*return\s+\$this->(?:hasMany|hasOne|belongsTo)',
            r'Schema::create\s*\(',
            r'class\s+\w+\s+extends\s+Migration'
        ]
        
        self.auth_patterns = [
            r'authenticate|authorization|jwt|token|login|logout|register',
            r'Auth::|Passport::|JWT::|Guard::',
            r'middleware.*auth',
            r'class\s+\w*Auth\w*',
            r'function\s+(?:login|logout|register|authenticate)'
        ]
    
    def group_endpoints_for_conversion(self, endpoints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Group endpoints by functionality for batch processing."""
        try:
            # Group endpoints by category or prefix
            groups = {}
            
            for endpoint in endpoints:
                route = endpoint.get('route', '/')
                method = endpoint.get('method', 'GET')
                
                # Determine grouping key
                group_key = self._determine_endpoint_group(route)
                
                if group_key not in groups:
                    groups[group_key] = {
                        'name': group_key,
                        'endpoints': [],
                        'estimated_lines': 0
                    }
                
                groups[group_key]['endpoints'].append(endpoint)
                # Estimate lines based on endpoint complexity
                estimated_lines = self._estimate_endpoint_lines(endpoint)
                groups[group_key]['estimated_lines'] += estimated_lines
            
            # Convert to list and sort by complexity
            group_list = list(groups.values())
            group_list.sort(key=lambda g: g['estimated_lines'])
            
            return group_list
            
        except Exception as e:
            self.ui.error(f"Failed to group endpoints: {str(e)}")
            return []
    
    def create_logic_batches(self, php_files: List[str], 
                           analysis_result: Dict[str, Any]) -> List[BatchGroup]:
        """Create batches for business logic conversion."""
        try:
            batch_groups = []
            
            # Process each PHP file
            for file_path in php_files:
                if not os.path.exists(file_path):
                    continue
                
                # Read file content
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                except Exception as e:
                    self.ui.debug(f"Failed to read {file_path}: {str(e)}")
                    continue
                
                # Determine file type and processing approach
                file_batches = self._process_file_content(file_path, content)
                
                if file_batches:
                    # Create batch group for this file
                    group = BatchGroup(
                        name=os.path.basename(file_path),
                        description=f"Batches from {file_path}",
                        batches=file_batches,
                        total_lines=sum(batch.line_count for batch in file_batches)
                    )
                    batch_groups.append(group)
            
            # Sort batch groups by processing priority
            batch_groups.sort(key=lambda g: (
                min(batch.priority for batch in g.batches),
                g.total_lines
            ))
            
            return batch_groups
            
        except Exception as e:
            self.ui.error(f"Failed to create logic batches: {str(e)}")
            return []
    
    def split_large_file(self, file_path: str, content: str) -> List[CodeBatch]:
        """Split a large file into manageable batches."""
        try:
            lines = content.split('\n')
            total_lines = len(lines)
            
            if total_lines <= self.max_lines_per_batch:
                # File is small enough, return as single batch
                return [CodeBatch(
                    name=f"{os.path.basename(file_path)}_main",
                    php_code=content,
                    file_path=file_path,
                    batch_type=self._determine_batch_type(content),
                    line_count=total_lines,
                    character_count=len(content)
                )]
            
            # Split large file intelligently
            batches = []
            current_batch_lines = []
            current_batch_name = ""
            batch_number = 1
            
            i = 0
            while i < total_lines:
                line = lines[i]
                
                # Check if we're starting a new logical section
                section_info = self._detect_logical_section(line, lines, i)
                
                if section_info and current_batch_lines:
                    # Save current batch and start new one
                    batch_content = '\n'.join(current_batch_lines)
                    batches.append(CodeBatch(
                        name=f"{os.path.basename(file_path)}_batch_{batch_number}",
                        php_code=batch_content,
                        file_path=file_path,
                        batch_type=self._determine_batch_type(batch_content),
                        line_count=len(current_batch_lines),
                        character_count=len(batch_content)
                    ))
                    
                    current_batch_lines = []
                    batch_number += 1
                
                current_batch_lines.append(line)
                
                # Check if batch is getting too large
                if (len(current_batch_lines) >= self.optimal_lines_per_batch or
                    len('\n'.join(current_batch_lines)) >= self.optimal_chars_per_batch):
                    
                    # Find a good break point
                    break_point = self._find_break_point(current_batch_lines)
                    
                    if break_point > 0:
                        # Split at break point
                        batch_content = '\n'.join(current_batch_lines[:break_point])
                        batches.append(CodeBatch(
                            name=f"{os.path.basename(file_path)}_batch_{batch_number}",
                            php_code=batch_content,
                            file_path=file_path,
                            batch_type=self._determine_batch_type(batch_content),
                            line_count=break_point,
                            character_count=len(batch_content)
                        ))
                        
                        # Keep remaining lines for next batch
                        current_batch_lines = current_batch_lines[break_point:]
                        batch_number += 1
                
                i += 1
            
            # Add remaining lines as final batch
            if current_batch_lines:
                batch_content = '\n'.join(current_batch_lines)
                batches.append(CodeBatch(
                    name=f"{os.path.basename(file_path)}_batch_{batch_number}",
                    php_code=batch_content,
                    file_path=file_path,
                    batch_type=self._determine_batch_type(batch_content),
                    line_count=len(current_batch_lines),
                    character_count=len(batch_content)
                ))
            
            return batches
            
        except Exception as e:
            self.ui.error(f"Failed to split large file {file_path}: {str(e)}")
            return []
    
    def analyze_batch_dependencies(self, batches: List[CodeBatch]) -> List[CodeBatch]:
        """Analyze dependencies between batches and set processing order."""
        try:
            # Extract dependencies from each batch
            for batch in batches:
                batch.dependencies = self._extract_dependencies(batch.php_code)
            
            # Sort batches by dependency order
            # Simple approach: process models first, then auth, then endpoints, then logic
            type_priority = {
                'model': 1,
                'auth': 2,
                'endpoint': 3,
                'logic': 4,
                'config': 5
            }
            
            batches.sort(key=lambda b: (
                type_priority.get(b.batch_type, 6),
                b.priority,
                b.line_count
            ))
            
            return batches
            
        except Exception as e:
            self.ui.error(f"Failed to analyze batch dependencies: {str(e)}")
            return batches
    
    def estimate_batch_processing_time(self, batch: CodeBatch) -> str:
        """Estimate processing time for a batch."""
        # Base time estimates (in seconds) per line of code
        base_time_per_line = {
            'endpoint': 2.0,  # Endpoints are complex
            'model': 1.5,     # Models need careful mapping
            'auth': 3.0,      # Auth is security-critical
            'logic': 1.0,     # Business logic varies
            'config': 0.5     # Config is usually straightforward
        }
        
        time_per_line = base_time_per_line.get(batch.batch_type, 1.0)
        estimated_seconds = batch.line_count * time_per_line
        
        # Add complexity multiplier
        complexity_multiplier = {
            'low': 0.8,
            'medium': 1.0,
            'high': 1.5
        }
        
        estimated_seconds *= complexity_multiplier.get(batch.estimated_complexity, 1.0)
        
        # Convert to human-readable format
        if estimated_seconds < 60:
            return f"{int(estimated_seconds)} seconds"
        elif estimated_seconds < 3600:
            return f"{int(estimated_seconds / 60)} minutes"
        else:
            return f"{estimated_seconds / 3600:.1f} hours"
    
    def _process_file_content(self, file_path: str, content: str) -> List[CodeBatch]:
        """Process file content and create appropriate batches."""
        # Check if file is small enough for single batch
        lines = content.split('\n')
        char_count = len(content)
        
        if (len(lines) <= self.max_lines_per_batch and 
            char_count <= self.max_chars_per_batch):
            # Single batch
            return [CodeBatch(
                name=os.path.basename(file_path),
                php_code=content,
                file_path=file_path,
                batch_type=self._determine_batch_type(content),
                line_count=len(lines),
                character_count=char_count,
                estimated_complexity=self._estimate_complexity(content)
            )]
        else:
            # Split into multiple batches
            return self.split_large_file(file_path, content)
    
    def _determine_endpoint_group(self, route: str) -> str:
        """Determine which group an endpoint belongs to."""
        # Remove leading slash and get first path segment
        route = route.lstrip('/')
        parts = route.split('/')
        
        if len(parts) == 0:
            return 'root'
        
        first_part = parts[0].lower()
        
        # Common API groupings
        if first_part in ['api', 'v1', 'v2']:
            if len(parts) > 1:
                return parts[1].lower()
            else:
                return 'api'
        
        # Resource-based grouping
        resource_patterns = {
            'users': 'user_management',
            'user': 'user_management',
            'auth': 'authentication',
            'login': 'authentication',
            'logout': 'authentication',
            'register': 'authentication',
            'products': 'product_management',
            'product': 'product_management',
            'orders': 'order_management',
            'order': 'order_management',
            'admin': 'administration',
            'dashboard': 'administration'
        }
        
        return resource_patterns.get(first_part, first_part)
    
    def _estimate_endpoint_lines(self, endpoint: Dict[str, Any]) -> int:
        """Estimate lines of code for an endpoint."""
        base_lines = 10  # Basic endpoint structure
        
        # Add complexity based on parameters
        params = endpoint.get('parameters', [])
        base_lines += len(params) * 2
        
        # Add complexity based on middleware
        middleware = endpoint.get('middleware', [])
        base_lines += len(middleware) * 3
        
        # Add complexity based on authentication
        if endpoint.get('authentication'):
            base_lines += 5
        
        # Add complexity based on method
        method = endpoint.get('method', 'GET').upper()
        if method in ['POST', 'PUT', 'PATCH']:
            base_lines += 10  # Request body handling
        elif method == 'DELETE':
            base_lines += 5
        
        return base_lines
    
    def _determine_batch_type(self, content: str) -> str:
        """Determine the type of code in the content."""
        content_lower = content.lower()
        
        # Check for endpoints
        if any(re.search(pattern, content, re.IGNORECASE) for pattern in self.endpoint_patterns):
            return 'endpoint'
        
        # Check for models
        if any(re.search(pattern, content, re.IGNORECASE) for pattern in self.model_patterns):
            return 'model'
        
        # Check for auth
        if any(re.search(pattern, content, re.IGNORECASE) for pattern in self.auth_patterns):
            return 'auth'
        
        # Check for config
        if any(keyword in content_lower for keyword in ['config', 'setting', 'environment', 'database']):
            return 'config'
        
        return 'logic'
    
    def _detect_logical_section(self, line: str, lines: List[str], index: int) -> Optional[Dict[str, str]]:
        """Detect if we're starting a new logical section."""
        line_stripped = line.strip()
        
        # Class definitions
        if re.match(r'^\s*class\s+\w+', line_stripped):
            return {'type': 'class', 'name': line_stripped}
        
        # Function definitions
        if re.match(r'^\s*(?:public|private|protected)?\s*function\s+\w+', line_stripped):
            return {'type': 'function', 'name': line_stripped}
        
        # Route definitions
        if re.match(r'^\s*Route::|^\s*\$app->', line_stripped):
            return {'type': 'route', 'name': line_stripped}
        
        # Large comment blocks (potential section dividers)
        if re.match(r'^\s*/\*\*|\s*//\s*={3,}|\s*#\s*={3,}', line_stripped):
            return {'type': 'comment_section', 'name': line_stripped}
        
        return None
    
    def _find_break_point(self, lines: List[str]) -> int:
        """Find a good break point in a list of lines."""
        # Look for natural break points from end backwards
        for i in range(len(lines) - 1, max(0, len(lines) - 50), -1):
            line = lines[i].strip()
            
            # End of function or class
            if line == '}' and i > 0:
                prev_line = lines[i-1].strip()
                if not prev_line.endswith('{'):  # Not an empty block
                    return i + 1
            
            # End of large comment block
            if line.endswith('*/'):
                return i + 1
            
            # Blank line followed by comment or new function
            if not line and i < len(lines) - 1:
                next_line = lines[i + 1].strip()
                if (next_line.startswith('//') or 
                    next_line.startswith('/*') or
                    'function' in next_line or
                    'class' in next_line):
                    return i + 1
        
        # If no good break point found, use middle
        return len(lines) // 2
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract dependencies from PHP code."""
        dependencies = []
        
        # Look for class dependencies
        class_patterns = [
            r'extends\s+(\w+)',
            r'implements\s+(\w+)',
            r'use\s+([\\A-Za-z0-9_]+)',
            r'new\s+(\w+)\s*\(',
            r'(\w+)::'
        ]
        
        for pattern in class_patterns:
            matches = re.findall(pattern, content)
            dependencies.extend(matches)
        
        # Remove common PHP built-ins
        builtins = {'stdClass', 'Exception', 'PDO', 'DateTime', 'self', 'parent', 'static'}
        dependencies = [dep for dep in dependencies if dep not in builtins]
        
        return list(set(dependencies))  # Remove duplicates
    
    def _estimate_complexity(self, content: str) -> str:
        """Estimate complexity of code content."""
        complexity_indicators = [
            len(re.findall(r'if\s*\(', content)),  # Conditional statements
            len(re.findall(r'for\s*\(|foreach\s*\(|while\s*\(', content)),  # Loops
            len(re.findall(r'try\s*\{|catch\s*\(', content)),  # Exception handling
            len(re.findall(r'function\s+\w+\s*\(', content)),  # Functions
            len(re.findall(r'class\s+\w+', content)),  # Classes
            len(re.findall(r'\$\w+->\w+\s*\(', content)),  # Method calls
        ]
        
        total_complexity = sum(complexity_indicators)
        
        if total_complexity < 10:
            return 'low'
        elif total_complexity < 30:
            return 'medium'
        else:
            return 'high'