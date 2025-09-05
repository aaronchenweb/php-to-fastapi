# core/detector.py - Updated to use enhanced settings
"""PHP project detection and validation with enhanced settings integration."""

import os
import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Set, Optional, Tuple

from config.settings import Settings


@dataclass
class ProjectValidationResult:
    """Result of PHP project validation."""
    is_valid: bool
    reason: str = ""
    suggestions: List[str] = None
    detected_framework: Optional[str] = None
    php_version: Optional[str] = None
    confidence_score: float = 0.0
    files_analyzed: int = 0
    api_files_found: int = 0
    
    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []


@dataclass
class PHPProjectInfo:
    """Information about detected PHP project."""
    root_path: str
    framework: Optional[str] = None
    php_version: Optional[str] = None
    entry_points: List[str] = None
    config_files: List[str] = None
    php_files: List[str] = None
    api_files: List[str] = None
    database_configs: List[str] = None
    dependencies: Dict[str, str] = None
    
    def __post_init__(self):
        if self.entry_points is None:
            self.entry_points = []
        if self.config_files is None:
            self.config_files = []
        if self.php_files is None:
            self.php_files = []
        if self.api_files is None:
            self.api_files = []
        if self.database_configs is None:
            self.database_configs = []
        if self.dependencies is None:
            self.dependencies = {}


class PHPProjectDetector:
    """Enhanced PHP project detector using comprehensive settings."""
    
    def __init__(self):
        self.settings = Settings()
        
        # Framework detection patterns
        self.framework_patterns = {
            'laravel': [
                'artisan',
                'app/Http/Controllers',
                'routes/api.php',
                'composer.json',
                'bootstrap/app.php',
                'config/app.php'
            ],
            'codeigniter': [
                'system/CodeIgniter.php',
                'application/controllers',
                'index.php',
                'application/config'
            ],
            'symfony': [
                'composer.json',
                'src/Controller',
                'config/routes.yaml',
                'bin/console',
                'symfony.lock'
            ],
            'slim': [
                'composer.json',
                'public/index.php',
                'src/'
            ],
            'zend': [
                'composer.json',
                'module/',
                'config/application.config.php'
            ],
            'cakephp': [
                'composer.json',
                'src/Controller/',
                'config/app.php',
                'bin/cake'
            ],
            'yii': [
                'composer.json',
                'protected/controllers/',
                'protected/config/',
                'yii'
            ],
            'vanilla_php': [
                'index.php',
                '*.php'
            ]
        }
        
        # API endpoint patterns
        self.api_patterns = [
            r'header\s*\(\s*["\']Content-Type:\s*application/json["\']',
            r'json_encode\s*\(',
            r'json_decode\s*\(',
            r'\$_GET|\$_POST|\$_PUT|\$_DELETE|\$_REQUEST',
            r'header\s*\(\s*["\']HTTP/1\.\d+\s+\d{3}',
            r'http_response_code\s*\(',
            r'REST|API|endpoint',
            r'Route::(get|post|put|delete|patch)',
            r'\$app->(get|post|put|delete|patch)',
            r'@Route\s*\(',
            r'JsonResponse',
            r'->json\s*\(',
            r'response\(\)->json',
            r'return.*json'
        ]
        
        # Framework-specific API patterns
        self.framework_api_indicators = {
            'laravel': {
                'directories': ['app/Http/Controllers', 'routes'],
                'files': ['routes/api.php', 'routes/web.php'],
                'patterns': [
                    r'Route::(get|post|put|delete|patch)',
                    r'->json\s*\(',
                    r'response\(\)->json',
                    r'JsonResponse',
                    r'ApiController',
                    r'namespace App\\Http\\Controllers',
                    r'Illuminate\\Http\\Response',
                    r'use Illuminate\\Http'
                ]
            },
            'codeigniter': {
                'directories': ['application/controllers', 'controllers'],
                'files': [],
                'patterns': [
                    r'class\s+\w+\s+extends\s+CI_Controller',
                    r'\$this->output->set_content_type\(["\']application/json["\']',
                    r'\$this->load->helper\(["\']url["\']',
                    r'show_404\(',
                    r'\$this->input->(get|post)'
                ]
            },
            'symfony': {
                'directories': ['src/Controller'],
                'files': ['config/routes.yaml', 'config/routes.yml'],
                'patterns': [
                    r'@Route\(',
                    r'JsonResponse',
                    r'extends AbstractController',
                    r'use Symfony\\Component\\HttpFoundation',
                    r'use Symfony\\Bundle\\FrameworkBundle'
                ]
            },
            'slim': {
                'directories': ['src'],
                'files': ['public/index.php'],
                'patterns': [
                    r'\$app->(get|post|put|delete|patch)',
                    r'->withJson\(',
                    r'Slim\\App',
                    r'Psr\\Http\\Message'
                ]
            }
        }
    
    def validate_project(self, project_path: str) -> ProjectValidationResult:
        """Validate if the given path contains a PHP web API project."""
        if not os.path.exists(project_path):
            return ProjectValidationResult(
                is_valid=False,
                reason="Project path does not exist"
            )
        
        if not os.path.isdir(project_path):
            return ProjectValidationResult(
                is_valid=False,
                reason="Project path is not a directory"
            )
        
        # First, detect framework
        framework = self._detect_framework(project_path)
        
        # Find PHP files with smart filtering
        php_files = self._find_php_files(project_path)
        if not php_files:
            return ProjectValidationResult(
                is_valid=False,
                reason="No PHP files found in the project",
                suggestions=[
                    "Ensure the directory contains .php files",
                    "Check if you're pointing to the correct project root",
                    "Verify the directory is not being filtered by ignore patterns"
                ]
            )
        
        # Use framework-aware API validation
        api_score, api_files_count = self._calculate_framework_aware_api_score(
            project_path, php_files, framework
        )
        
        # Get threshold from settings
        threshold = self.settings.detection.api_score_thresholds.get(framework, 0.20)
        
        files_analyzed = min(len(php_files), self.settings.detection.max_files_for_api_detection)
        
        if api_score < threshold:
            suggestions = [
                "Ensure the project contains API endpoints",
                "Look for files that handle HTTP requests and return JSON",
                "Check for REST API patterns",
            ]
            
            if framework != 'vanilla_php':
                suggestions.append(f"Framework detected: {framework}")
                if framework == 'laravel':
                    suggestions.extend([
                        "Check routes/api.php for API routes",
                        "Look for Controllers in app/Http/Controllers",
                        "Verify Laravel project structure is complete"
                    ])
            else:
                suggestions.append("No framework detected - analyzing as vanilla PHP")
            
            return ProjectValidationResult(
                is_valid=False,
                reason=f"Project does not appear to be a web API (score: {api_score:.3f}, threshold: {threshold:.3f})",
                suggestions=suggestions,
                detected_framework=framework,
                confidence_score=api_score,
                files_analyzed=files_analyzed,
                api_files_found=api_files_count
            )
        
        return ProjectValidationResult(
            is_valid=True,
            reason="Valid PHP web API project detected",
            detected_framework=framework,
            confidence_score=api_score,
            files_analyzed=files_analyzed,
            api_files_found=api_files_count
        )
    
    def _calculate_framework_aware_api_score(self, project_path: str, php_files: List[str], framework: str) -> Tuple[float, int]:
        """Calculate API score with framework awareness. Returns (score, api_files_count)."""
        if framework in ['custom_mvc', 'vanilla_php']:
            return self._analyze_custom_php_api_patterns(project_path, php_files)
        
        if not php_files:
            return 0.0, 0
        
        # Check framework-specific indicators first
        if framework in self.framework_api_indicators:
            framework_score, api_files = self._check_framework_api_indicators(project_path, framework)
            if framework_score > 0:
                return framework_score, api_files
        
        # Filter files to focus on API-relevant ones
        relevant_files = self._filter_relevant_api_files(php_files, framework, project_path)
        
        if not relevant_files:
            # If no relevant files, check if framework structure exists
            if framework != 'vanilla_php':
                structure_score, api_files = self._check_framework_structure_only(project_path, framework)
                return structure_score, api_files
            return 0.0, 0
        
        # Limit files for performance
        max_files = self.settings.detection.max_files_for_api_detection
        files_to_check = relevant_files[:max_files]
        
        api_indicators = 0
        api_files_found = 0
        
        for file_path in files_to_check:
            if self._file_contains_api_patterns(file_path):
                api_indicators += 1
                api_files_found += 1
        
        score = min(api_indicators / len(files_to_check), 1.0) if files_to_check else 0.0
        return score, api_files_found
    
    def _analyze_custom_php_api_patterns(self, project_path: str, php_files: List[str]) -> Tuple[float, int]:
        """Analyze custom PHP for API patterns."""
        api_indicators = 0
        api_files_found = 0
        
        # Enhanced patterns for custom PHP
        custom_api_patterns = [
            r'\$this->router->(get|post|put|delete)',
            r'class.*Controller',
            r'json_encode\s*\(',
            r'header\s*\(\s*["\']Content-Type:\s*application/json',
            r'http_response_code\s*\(',
            r'PDO\s*\(',
            r'Database::getInstance',
            r'->query\s*\(',
            r'->prepare\s*\('
        ]
        
        for file_path in php_files[:50]:  # Limit for performance
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                matches = 0
                for pattern in custom_api_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        matches += 1
                
                if matches >= 2:  # At least 2 patterns must match
                    api_indicators += 1
                    api_files_found += 1
                    
            except Exception:
                continue
        
        score = min(api_indicators / len(php_files), 1.0) if php_files else 0.0
        return score, api_files_found

    def _check_framework_api_indicators(self, project_path: str, framework: str) -> Tuple[float, int]:
        """Check for framework-specific API indicators. Returns (score, api_files_count)."""
        indicators = self.framework_api_indicators.get(framework, {})
        score = 0.0
        total_api_files = 0
        
        # Check API directories
        api_dirs = indicators.get('directories', [])
        for dir_path in api_dirs:
            full_path = os.path.join(project_path, dir_path)
            if os.path.exists(full_path) and os.path.isdir(full_path):
                dir_score, dir_api_files = self._check_directory_for_api_patterns(
                    full_path, indicators.get('patterns', [])
                )
                score = max(score, dir_score)
                total_api_files += dir_api_files
        
        # Check specific API files
        api_files = indicators.get('files', [])
        for file_path in api_files:
            full_path = os.path.join(project_path, file_path)
            if os.path.exists(full_path):
                file_score = self._check_file_for_api_patterns(
                    full_path, indicators.get('patterns', [])
                )
                if file_score > 0:
                    total_api_files += 1
                score = max(score, file_score)
        
        return score, total_api_files
    
    def _check_directory_for_api_patterns(self, directory: str, patterns: List[str]) -> Tuple[float, int]:
        """Check directory for API patterns. Returns (score, api_files_count)."""
        php_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if any(file.endswith(ext) for ext in self.settings.get_php_extensions()):
                    php_files.append(os.path.join(root, file))
        
        if not php_files:
            return 0.0, 0
        
        # Limit files for performance
        max_files = min(len(php_files), 20)
        files_to_check = php_files[:max_files]
        
        matches = 0
        for file_path in files_to_check:
            if self._file_contains_patterns(file_path, patterns):
                matches += 1
        
        score = min(matches / len(files_to_check), 1.0) if files_to_check else 0.0
        return score, matches
    
    def _check_file_for_api_patterns(self, file_path: str, patterns: List[str]) -> float:
        """Check single file for API patterns."""
        return 1.0 if self._file_contains_patterns(file_path, patterns) else 0.0
    
    def _file_contains_patterns(self, file_path: str, patterns: List[str]) -> bool:
        """Check if file contains any of the given patterns."""
        try:
            # Check file size before reading
            if os.path.getsize(file_path) > self.settings.detection.max_file_size_for_analysis * 1024 * 1024:
                return False
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        return True
        except Exception:
            pass
        return False
    
    def _file_contains_api_patterns(self, file_path: str) -> bool:
        """Check if file contains any API patterns."""
        return self._file_contains_patterns(file_path, self.api_patterns)
    
    def _filter_relevant_api_files(self, php_files: List[str], framework: str, project_root: str) -> List[str]:
        """Filter PHP files to focus on those likely to contain API code."""
        relevant_files = []
        
        # Get framework-specific API directories
        framework_api_dirs = self.settings.get_framework_api_directories(framework)
        
        # Check each file
        for file_path in php_files:
            # Skip if should be ignored
            if self.settings.should_ignore_file(file_path, project_root):
                continue
            
            # Check if it's API relevant
            if self.settings.is_api_relevant_file(file_path, project_root):
                relevant_files.append(file_path)
                continue
            
            # Check if in framework-specific API directory
            rel_path = os.path.relpath(file_path, project_root)
            for api_dir in framework_api_dirs:
                if rel_path.startswith(api_dir + '/'):
                    relevant_files.append(file_path)
                    break
        
        # If we found relevant files, use them
        if relevant_files:
            return relevant_files
        
        # Fallback: return non-ignored files
        fallback_files = []
        for file_path in php_files:
            if not self.settings.should_ignore_file(file_path, project_root):
                fallback_files.append(file_path)
        
        # Limit for performance
        max_files = self.settings.detection.max_files_for_api_detection
        return fallback_files[:max_files]
    
    def _check_framework_structure_only(self, project_path: str, framework: str) -> Tuple[float, int]:
        """Check if framework structure suggests it's an API project. Returns (score, api_files_count)."""
        api_files_count = 0
        
        if framework == 'laravel':
            # Check for Laravel API indicators
            api_route_path = os.path.join(project_path, 'routes', 'api.php')
            controller_dir = os.path.join(project_path, 'app', 'Http', 'Controllers')
            
            if os.path.exists(api_route_path):
                api_files_count += 1
                # Check if routes/api.php actually contains routes
                if self._file_contains_api_patterns(api_route_path):
                    return 0.8, api_files_count
                return 0.4, api_files_count
            elif os.path.exists(controller_dir):
                # Count controllers in the directory
                try:
                    controllers = [f for f in os.listdir(controller_dir) 
                                 if f.endswith('Controller.php')]
                    api_files_count = len(controllers)
                    return 0.3 if controllers else 0.1, api_files_count
                except OSError:
                    return 0.1, 0
        
        elif framework == 'codeigniter':
            controller_dir = os.path.join(project_path, 'application', 'controllers')
            if os.path.exists(controller_dir):
                try:
                    controllers = [f for f in os.listdir(controller_dir) if f.endswith('.php')]
                    api_files_count = len(controllers)
                    return 0.4 if controllers else 0.1, api_files_count
                except OSError:
                    return 0.1, 0
        
        elif framework == 'symfony':
            controller_dir = os.path.join(project_path, 'src', 'Controller')
            if os.path.exists(controller_dir):
                try:
                    controllers = [f for f in os.listdir(controller_dir) if f.endswith('.php')]
                    api_files_count = len(controllers)
                    return 0.4 if controllers else 0.1, api_files_count
                except OSError:
                    return 0.1, 0
        
        return 0.0, 0
    
    def _find_php_files(self, project_path: str) -> List[str]:
        """Find all relevant PHP files in the project."""
        php_files = []
        ignore_patterns = self.settings.get_ignore_patterns()
        php_extensions = self.settings.get_php_extensions()
        max_files = self.settings.conversion.max_files_to_analyze
        
        files_found = 0
        
        for root, dirs, files in os.walk(project_path):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if not any(
                d.startswith(pattern.rstrip('/')) for pattern in ignore_patterns
            )]
            
            for file in files:
                if files_found >= max_files:
                    break
                
                if any(file.endswith(ext) for ext in php_extensions):
                    file_path = os.path.join(root, file)
                    
                    # Use settings to check if file should be ignored
                    if not self.settings.should_ignore_file(file_path, project_path):
                        php_files.append(file_path)
                        files_found += 1
            
            if files_found >= max_files:
                break
        
        return php_files
    
    def _detect_framework(self, project_path: str) -> Optional[str]:
        """Detect PHP framework used in the project."""
        
        # Check for custom/native PHP patterns FIRST (before generic ones)
        custom_indicators = self._check_custom_php_patterns(project_path)
        if custom_indicators['is_custom']:
            return 'custom_mvc'
        
        # Then check specific frameworks
        for framework, patterns in self.framework_patterns.items():
            if framework in ['vanilla_php', 'slim']:  # Skip generic ones for now
                continue
                
            matches = 0
            for pattern in patterns:
                if '*' in pattern:
                    if self._has_files_matching_pattern(project_path, pattern):
                        matches += 1
                else:
                    full_path = os.path.join(project_path, pattern)
                    if os.path.exists(full_path):
                        matches += 1
            
            threshold = len(patterns) * 0.6
            if matches >= threshold:
                return framework
        
        # Finally check generic frameworks
        if self._check_slim_specific_patterns(project_path):
            return 'slim'
        
        return 'vanilla_php'

    def _check_custom_php_patterns(self, project_path: str) -> Dict[str, bool]:
        """Check for custom PHP implementation patterns."""
        indicators = {
            'has_composer': os.path.exists(os.path.join(project_path, 'composer.json')),
            'has_src_structure': os.path.exists(os.path.join(project_path, 'src')),
            'has_custom_router': False,
            'has_psr4_structure': False,
            'is_custom': False
        }
        
        # Check for custom router implementation
        src_path = os.path.join(project_path, 'src')
        if os.path.exists(src_path):
            for root, dirs, files in os.walk(src_path):
                for file in files:
                    if file.endswith('.php'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                            
                            # Look for custom router patterns
                            if any(pattern in content for pattern in [
                                'class Router', 'class App', '$this->router->',
                                'setupRoutes', 'addRoute'
                            ]):
                                indicators['has_custom_router'] = True
                            
                            # Check for PSR-4 namespacing
                            if 'namespace' in content and '\\' in content:
                                indicators['has_psr4_structure'] = True
                                
                        except Exception:
                            continue
        
        # Determine if it's custom
        indicators['is_custom'] = (
            indicators['has_composer'] and 
            indicators['has_src_structure'] and
            (indicators['has_custom_router'] or indicators['has_psr4_structure'])
        )
        
        return indicators

    def _check_slim_specific_patterns(self, project_path: str) -> bool:
        """Check for Slim-specific patterns to avoid false positives."""
        # Look for actual Slim framework usage
        composer_path = os.path.join(project_path, 'composer.json')
        if os.path.exists(composer_path):
            try:
                import json
                with open(composer_path, 'r') as f:
                    composer_data = json.load(f)
                
                # Check for Slim in dependencies
                require = composer_data.get('require', {})
                require_dev = composer_data.get('require-dev', {})
                all_deps = {**require, **require_dev}
                
                return any('slim' in dep.lower() for dep in all_deps.keys())
            except Exception:
                pass
        
        return False
    
    def _has_files_matching_pattern(self, project_path: str, pattern: str) -> bool:
        """Check if files matching pattern exist."""
        if pattern == '*.php':
            return len(self._find_php_files(project_path)) > 0
        return False
    
    def analyze_project(self, project_path: str) -> PHPProjectInfo:
        """Perform detailed analysis of PHP project."""
        info = PHPProjectInfo(root_path=project_path)
        
        # Find all PHP files
        info.php_files = self._find_php_files(project_path)
        
        # Detect framework
        info.framework = self._detect_framework(project_path)
        
        # Find entry points
        info.entry_points = self._find_entry_points(project_path, info.framework)
        
        # Find config files
        info.config_files = self._find_config_files(project_path)
        
        # Find API files using enhanced logic
        info.api_files = self._find_api_files(info.php_files, project_path)
        
        # Find database configs
        info.database_configs = self._find_database_configs(project_path)
        
        # Parse dependencies
        info.dependencies = self._parse_dependencies(project_path)
        
        # Detect PHP version
        info.php_version = self._detect_php_version(project_path, info.php_files)
        
        return info
    
    def _find_api_files(self, php_files: List[str], project_root: str) -> List[str]:
        """Find files that likely contain API endpoints using enhanced logic."""
        api_files = []
        
        for file_path in php_files:
            # Check if it's API relevant according to settings
            if self.settings.is_api_relevant_file(file_path, project_root):
                # Double-check by looking for actual API patterns
                if self._file_contains_api_patterns(file_path):
                    api_files.append(file_path)
        
        return api_files
    
    # Keep existing methods for entry points, config files, etc.
    def _find_entry_points(self, project_path: str, framework: Optional[str]) -> List[str]:
        """Find main entry points for the application."""
        entry_points = []
        
        common_entry_files = ['index.php', 'app.php', 'bootstrap.php', 'api.php']
        
        for entry_file in common_entry_files:
            full_path = os.path.join(project_path, entry_file)
            if os.path.exists(full_path):
                entry_points.append(os.path.relpath(full_path, project_path))
        
        # Framework-specific entry points
        if framework == 'laravel':
            laravel_entries = ['public/index.php', 'artisan', 'routes/api.php']
            for entry in laravel_entries:
                full_path = os.path.join(project_path, entry)
                if os.path.exists(full_path):
                    entry_points.append(entry)
        
        elif framework == 'codeigniter':
            ci_entries = ['index.php', 'application/controllers/']
            for entry in ci_entries:
                full_path = os.path.join(project_path, entry)
                if os.path.exists(full_path):
                    entry_points.append(entry)
        
        return entry_points
    
    def _find_config_files(self, project_path: str) -> List[str]:
        """Find configuration files."""
        config_files = []
        config_patterns = [
            'config.php', 'config.inc.php', 'settings.php',
            'database.php', 'db.php', '.env', 'composer.json',
            'config/', 'application/config/', 'app/config/'
        ]
        
        for pattern in config_patterns:
            full_path = os.path.join(project_path, pattern)
            if os.path.exists(full_path):
                config_files.append(os.path.relpath(full_path, project_path))
        
        return config_files
    
    def _find_database_configs(self, project_path: str) -> List[str]:
        """Find database configuration files."""
        db_configs = []
        db_patterns = [
            'database.php', 'db.php', 'database.inc.php',
            'config/database.php', 'application/config/database.php',
            '.env'
        ]
        
        for pattern in db_patterns:
            full_path = os.path.join(project_path, pattern)
            if os.path.exists(full_path):
                db_configs.append(os.path.relpath(full_path, project_path))
        
        return db_configs
    
    def _parse_dependencies(self, project_path: str) -> Dict[str, str]:
        """Parse project dependencies from composer.json."""
        dependencies = {}
        composer_path = os.path.join(project_path, 'composer.json')
        
        if os.path.exists(composer_path):
            try:
                import json
                with open(composer_path, 'r') as f:
                    composer_data = json.load(f)
                    
                    # Get both require and require-dev dependencies
                    for dep_section in ['require', 'require-dev']:
                        if dep_section in composer_data:
                            dependencies.update(composer_data[dep_section])
                            
            except Exception:
                pass
        
        return dependencies
    
    def _detect_php_version(self, project_path: str, php_files: List[str]) -> Optional[str]:
        """Attempt to detect PHP version requirements."""
        # Check composer.json first
        composer_path = os.path.join(project_path, 'composer.json')
        if os.path.exists(composer_path):
            try:
                import json
                with open(composer_path, 'r') as f:
                    composer_data = json.load(f)
                    if 'require' in composer_data and 'php' in composer_data['require']:
                        return composer_data['require']['php']
            except Exception:
                pass
        
        # Analyze code for version-specific features
        version_indicators = [
            ('8.3', [r'readonly\s+class', r'json_validate\s*\(']),
            ('8.2', [r'readonly\s+(?:public|private|protected)', r'enum\s+\w+:\s*string']),
            ('8.1', [r'enum\s+\w+', r'readonly\s+class']),
            ('8.0', [r'\bmatch\s*\([^)]*\)\s*{', r'#\[\w+.*\]']),
            ('7.4', [r'fn\s*\([^)]*\)\s*=>[^=]', r'\?\?\=']),
            ('7.1', [r'function\s+\w+\([^)]*\)\s*:\s*void', r'\?\w+\s+\$\w+']),
            ('7.0', [r'function\s+\w+\([^)]*\)\s*:\s*\w+', r'declare\s*\(\s*strict_types\s*=\s*1\s*\)']),
            ('5.6', [r'\.\.\.\$\w+', r'const\s+\w+\s*=.*\[']),
            ('5.5', [r'password_hash\s*\(', r'finally\s*{']),
            ('5.4', [r'\[\s*[\'"\w$]', r'trait\s+\w+']),
            ('5.3', [r'namespace\s+\w+', r'use\s+\w+\\', r'__DIR__']),
        ]
        
        # Check up to 15 files for performance
        files_to_check = php_files[:15] if len(php_files) > 15 else php_files
        
        for file_path in files_to_check:
            try:
                # Skip large files
                if os.path.getsize(file_path) > 1024 * 1024:  # 1MB limit
                    continue
                
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Check for version indicators from newest to oldest
                    for version, patterns in version_indicators:
                        for pattern in patterns:
                            if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                                return version
                                
            except Exception:
                continue
        
        return '7.4'  # Default to a modern but stable version
    
    def get_debug_info(self, project_path: str) -> Dict[str, any]:
        """Get debug information about the detection process."""
        php_files = self._find_php_files(project_path)
        framework = self._detect_framework(project_path)
        api_score, api_files_count = self._calculate_framework_aware_api_score(
            project_path, php_files, framework
        )
        threshold = self.settings.detection.api_score_thresholds.get(framework, 0.20)
        
        return {
            "project_path": project_path,
            "framework_detected": framework,
            "total_php_files": len(php_files),
            "api_score": api_score,
            "api_threshold": threshold,
            "api_files_found": api_files_count,
            "passes_validation": api_score >= threshold,
            "settings_info": self.settings.get_debug_info()
        }