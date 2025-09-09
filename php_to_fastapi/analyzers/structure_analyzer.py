# analyzers/structure_analyzer.py - Fixed version
"""Analyzes PHP project structure and organization patterns."""

import os
import re
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from pathlib import Path
from collections import defaultdict


@dataclass
class DirectoryInfo:
    """Information about a directory in the project."""
    path: str
    name: str
    file_count: int = 0
    php_file_count: int = 0
    subdirectory_count: int = 0
    purpose: Optional[str] = None
    framework_role: Optional[str] = None


@dataclass
class FileInfo:
    """Information about a file in the project."""
    path: str
    name: str
    extension: str
    size: int = 0
    purpose: Optional[str] = None
    framework_role: Optional[str] = None


@dataclass
class StructureAnalysis:
    """Analysis result for project structure."""
    project_root: str
    total_files: int = 0
    total_php_files: int = 0
    total_directories: int = 0
    organization_pattern: str = "unknown"
    framework_type: Optional[str] = None
    entry_points: List[str] = field(default_factory=list)
    config_files: List[str] = field(default_factory=list)
    directories: List[DirectoryInfo] = field(default_factory=list)
    architecture_score: float = 0.0
    separation_quality: str = "unknown"
    complexity_indicators: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


class StructureAnalyzer:
    """Analyzes PHP project structure and organization."""
    
    def __init__(self):
        # Framework-specific directory patterns
        self.framework_patterns = {
            'laravel': {
                'app': 'application_logic',
                'app/Http/Controllers': 'controllers',
                'app/Models': 'models', 
                'app/Http/Middleware': 'middleware',
                'routes': 'routing',
                'config': 'configuration',
                'database': 'database_files',
                'resources/views': 'templates',
                'public': 'web_root',
                'storage': 'storage',
                'tests': 'tests'
            },
            'symfony': {
                'src': 'application_logic',
                'src/Controller': 'controllers',
                'src/Entity': 'models',
                'config': 'configuration',
                'templates': 'templates',
                'public': 'web_root',
                'var': 'cache_logs',
                'tests': 'tests'
            },
            'codeigniter': {
                'application': 'application_logic',
                'application/controllers': 'controllers',
                'application/models': 'models',
                'application/views': 'templates',
                'application/config': 'configuration',
                'system': 'framework_core',
                'user_guide': 'documentation'
            },
            'slim': {
                'src': 'application_logic',
                'public': 'web_root',
                'templates': 'templates',
                'config': 'configuration'
            },
            'vanilla': {
                'includes': 'shared_code',
                'lib': 'libraries',
                'classes': 'class_files',
                'config': 'configuration',
                'templates': 'templates',
                'assets': 'static_files'
            }
        }
        
        # Common directory purposes
        self.directory_purposes = {
            'controller': ['controller', 'ctrl', 'handlers'],
            'model': ['model', 'entity', 'entities', 'domain'],
            'view': ['view', 'template', 'tpl', 'presentation'],
            'config': ['config', 'configuration', 'settings', 'conf'],
            'library': ['lib', 'library', 'libraries', 'vendor'],
            'utility': ['util', 'utils', 'utility', 'utilities', 'helper', 'helpers'],
            'test': ['test', 'tests', 'testing', 'spec', 'specs'],
            'documentation': ['doc', 'docs', 'documentation'],
            'asset': ['asset', 'assets', 'static', 'public', 'css', 'js', 'img', 'images'],
            'cache': ['cache', 'tmp', 'temp', 'temporary'],
            'log': ['log', 'logs', 'logging'],
            'upload': ['upload', 'uploads', 'files', 'media'],
            'migration': ['migration', 'migrations', 'schema'],
            'middleware': ['middleware', 'filter', 'filters'],
            'service': ['service', 'services', 'business'],
            'repository': ['repository', 'repositories', 'repo', 'repos'],
            'api': ['api', 'rest', 'endpoints', 'webservice']
        }
        
        # File type patterns
        self.file_purposes = {
            'entry_point': ['index.php', 'app.php', 'bootstrap.php', 'front.php'],
            'configuration': ['config.php', 'settings.php', 'database.php', '.env'],
            'routing': ['routes.php', 'web.php', 'api.php'],
            'autoloader': ['autoload.php', 'vendor/autoload.php'],
            'composer': ['composer.json', 'composer.lock'],
            'deployment': ['Dockerfile', 'docker-compose.yml', '.htaccess', 'nginx.conf']
        }
    
    def analyze_structure(self, project_root: str) -> StructureAnalysis:
        """Analyze the structure of a PHP project."""
        # First, scan to get basic counts and directory info
        scan_results = self._scan_directories_for_counts(project_root)
        
        # Create analysis object with required fields
        analysis = StructureAnalysis(
            project_root=project_root,
            total_files=scan_results['total_files'],
            total_php_files=scan_results['total_php_files'],
            total_directories=scan_results['total_directories'],
            organization_pattern="analyzing"  # Will be updated below
        )
        
        # Now do detailed analysis
        analysis.directories = scan_results['directories']
        
        # Detect framework type
        analysis.framework_type = self._detect_framework(analysis.directories)
        
        # Analyze organization pattern
        analysis.organization_pattern = self._analyze_organization_pattern(
            analysis.directories, analysis.framework_type
        )
        
        # Find entry points
        analysis.entry_points = self._find_entry_points(project_root, analysis.directories)
        
        # Find configuration files
        analysis.config_files = self._find_config_files(project_root, analysis.directories)
        
        # Calculate architecture score
        analysis.architecture_score = self._calculate_architecture_score(analysis)
        
        # Assess separation quality
        analysis.separation_quality = self._assess_separation_quality(analysis)
        
        # Analyze complexity indicators
        analysis.complexity_indicators = self._analyze_complexity_indicators(analysis)
        
        # Generate recommendations
        analysis.recommendations = self._generate_recommendations(analysis)
        
        return analysis
    
    def _scan_directories_for_counts(self, project_root: str) -> Dict[str, Any]:
        """Scan directories and return counts and directory info."""
        ignore_patterns = {
            '.git', '.svn', '.hg',
            'node_modules', 'vendor',
            '.vscode', '.idea',
            '__pycache__', '.pytest_cache',
            'cache', 'logs', 'tmp'
        }
        
        directories = []
        total_files = 0
        total_php_files = 0
        total_directories = 0
        
        for root, dirs, files in os.walk(project_root):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if d not in ignore_patterns]
            
            rel_path = os.path.relpath(root, project_root)
            if rel_path == '.':
                rel_path = ''
            
            # Count files
            php_files = [f for f in files if f.endswith(('.php', '.phtml', '.inc'))]
            
            # Create directory info
            dir_info = DirectoryInfo(
                path=rel_path,
                name=os.path.basename(root) if rel_path else 'root',
                file_count=len(files),
                php_file_count=len(php_files),
                subdirectory_count=len(dirs)
            )
            
            # Determine directory purpose
            dir_info.purpose = self._determine_directory_purpose(dir_info.name, rel_path)
            
            directories.append(dir_info)
            total_files += len(files)
            total_php_files += len(php_files)
            total_directories += 1
        
        return {
            'directories': directories,
            'total_files': total_files,
            'total_php_files': total_php_files,
            'total_directories': total_directories
        }
    
    def _determine_directory_purpose(self, dir_name: str, full_path: str) -> Optional[str]:
        """Determine the purpose of a directory based on its name and path."""
        dir_name_lower = dir_name.lower()
        full_path_lower = full_path.lower()
        
        # Check each purpose category
        for purpose, keywords in self.directory_purposes.items():
            if any(keyword in dir_name_lower for keyword in keywords):
                return purpose
            # Also check full path for nested directories
            if any(keyword in full_path_lower for keyword in keywords):
                return purpose
        
        return None
    
    def _detect_framework(self, directories: List[DirectoryInfo]) -> Optional[str]:
        """Detect the PHP framework based on directory structure."""
        dir_names = {d.name.lower() for d in directories}
        dir_paths = {d.path.lower() for d in directories}
        
        # Laravel detection
        laravel_indicators = ['app', 'routes', 'config', 'database', 'resources', 'artisan']
        if sum(1 for indicator in laravel_indicators if indicator in dir_names or any(indicator in path for path in dir_paths)) >= 4:
            return 'laravel'
        
        # Symfony detection
        symfony_indicators = ['src', 'config', 'templates', 'var', 'bin/console']
        if sum(1 for indicator in symfony_indicators if indicator in dir_names or any(indicator in path for path in dir_paths)) >= 3:
            return 'symfony'
        
        # CodeIgniter detection
        ci_indicators = ['application', 'system']
        if all(indicator in dir_names for indicator in ci_indicators):
            return 'codeigniter'
        
        # Slim detection
        slim_indicators = ['src', 'public', 'vendor']
        if all(indicator in dir_names for indicator in slim_indicators[:2]):
            # Check for Slim-specific files or minimal structure
            return 'slim'
        
        # Custom/Native PHP detection (YOUR CASE)
        custom_indicators = {
            'has_src': 'src' in dir_names,
            'has_public': 'public' in dir_names,
            'has_config': 'config' in dir_names,
            'has_composer': any('composer' in d.name.lower() for d in directories),
            'has_psr4_structure': any('controllers' in path or 'models' in path or 'core' in path for path in dir_paths),
            'minimal_structure': len([d for d in directories if d.php_file_count > 0]) < 10
        }
        
        # If it has modern PHP structure but doesn't match major frameworks
        if (custom_indicators['has_src'] and custom_indicators['has_public'] and 
            custom_indicators['has_config'] and custom_indicators['has_psr4_structure']):
            return 'custom_mvc'
        
        # Check if it's a custom implementation with composer autoloading
        if custom_indicators['has_composer'] and custom_indicators['has_psr4_structure']:
            return 'custom_composer'
        
        return 'vanilla'
    
    def _analyze_organization_pattern(self, 
                                    directories: List[DirectoryInfo], 
                                    framework_type: Optional[str]) -> str:
        """Analyze the overall organization pattern."""
        purposes = [d.purpose for d in directories if d.purpose]
        purpose_counts = {purpose: purposes.count(purpose) for purpose in set(purposes)}
        
        # Check for MVC pattern
        has_controllers = 'controller' in purpose_counts
        has_models = 'model' in purpose_counts  
        has_views = 'view' in purpose_counts
        has_api_structure = 'api' in purpose_counts
        
        # For custom frameworks, also check directory names
        dir_names = {d.name.lower() for d in directories}
        has_mvc_dirs = any(mvc_dir in dir_names for mvc_dir in ['controllers', 'models', 'views'])
        has_core_dirs = any(core_dir in dir_names for core_dir in ['core', 'src', 'app'])
        
        # Custom MVC detection (like your code)
        if framework_type in ['custom_mvc', 'custom_composer']:
            if has_controllers and has_models:
                return 'custom_mvc'
            elif has_mvc_dirs and has_core_dirs:
                return 'custom_mvc'
            elif has_api_structure:
                return 'api_focused'
        
        # Standard MVC detection
        if has_controllers and has_models and has_views:
            return 'mvc'
        elif has_controllers and has_models:
            return 'mvc_partial'
        
        # Check for domain-driven design
        if 'service' in purpose_counts and 'repository' in purpose_counts:
            return 'domain_driven'
        
        # Check for layered architecture
        layers = ['controller', 'service', 'repository', 'model']
        if sum(1 for layer in layers if layer in purpose_counts) >= 3:
            return 'layered'
        
        # Check for component-based
        if len(purpose_counts) > 8:  # Many different types of directories
            return 'component_based'
        
        # Check for flat structure
        if len([d for d in directories if d.subdirectory_count == 0]) > len(directories) * 0.8:
            return 'flat'
        
        return 'mixed'
    
    def _find_entry_points(self, project_root: str, directories: List[DirectoryInfo]) -> List[str]:
        """Find application entry points."""
        entry_points = []
        
        # Check common entry point files
        for file_pattern in self.file_purposes['entry_point']:
            file_path = os.path.join(project_root, file_pattern)
            if os.path.exists(file_path):
                entry_points.append(file_pattern)
        
        # Check in public directory
        public_dirs = [d for d in directories if 'public' in d.name.lower() or d.purpose == 'asset']
        for pub_dir in public_dirs:
            for file_pattern in ['index.php', 'app.php']:
                file_path = os.path.join(project_root, pub_dir.path, file_pattern)
                if os.path.exists(file_path):
                    entry_points.append(os.path.join(pub_dir.path, file_pattern))
        
        return entry_points
    
    def _find_config_files(self, project_root: str, directories: List[DirectoryInfo]) -> List[str]:
        """Find configuration files."""
        config_files = []
        
        # Check root directory
        for file_pattern in self.file_purposes['configuration']:
            file_path = os.path.join(project_root, file_pattern)
            if os.path.exists(file_path):
                config_files.append(file_pattern)
        
        # Check config directories
        config_dirs = [d for d in directories if d.purpose == 'config']
        for config_dir in config_dirs:
            config_dir_path = os.path.join(project_root, config_dir.path)
            if os.path.exists(config_dir_path):
                for file_name in os.listdir(config_dir_path):
                    if file_name.endswith('.php'):
                        config_files.append(os.path.join(config_dir.path, file_name))
        
        return config_files
    
    def _calculate_architecture_score(self, analysis: StructureAnalysis) -> float:
        """Calculate architecture quality score (0-10)."""
        score = 0.0
        
        # Organization pattern scoring
        pattern_scores = {
            'mvc': 8.0,
            'domain_driven': 9.0,
            'layered': 7.0,
            'mvc_partial': 5.0,
            'component_based': 6.0,
            'mixed': 3.0,
            'flat': 2.0
        }
        score += pattern_scores.get(analysis.organization_pattern, 1.0)
        
        # Framework bonus
        if analysis.framework_type and analysis.framework_type != 'vanilla':
            score += 1.0
        
        # Directory structure bonus
        purposes = [d.purpose for d in analysis.directories if d.purpose]
        unique_purposes = len(set(purposes))
        if unique_purposes >= 5:
            score += 1.0
        elif unique_purposes >= 3:
            score += 0.5
        
        # Entry points penalty (too many is bad)
        if len(analysis.entry_points) == 1:
            score += 1.0
        elif len(analysis.entry_points) <= 3:
            score += 0.5
        elif len(analysis.entry_points) > 5:
            score -= 1.0
        
        # Configuration organization
        if len(analysis.config_files) > 0:
            config_dirs = len([d for d in analysis.directories if d.purpose == 'config'])
            if config_dirs > 0:
                score += 1.0  # Organized config
            elif len(analysis.config_files) <= 3:
                score += 0.5  # Reasonable number of config files
        
        return min(max(score, 0.0), 10.0)  # Clamp between 0 and 10
    
    def _assess_separation_quality(self, analysis: StructureAnalysis) -> str:
        """Assess separation of concerns quality."""
        purposes = [d.purpose for d in analysis.directories if d.purpose]
        purpose_counts = {purpose: purposes.count(purpose) for purpose in set(purposes)}
        
        # Check for key separations
        has_controller_separation = 'controller' in purpose_counts
        has_model_separation = 'model' in purpose_counts
        has_view_separation = 'view' in purpose_counts
        has_config_separation = 'config' in purpose_counts
        
        separation_score = sum([
            has_controller_separation,
            has_model_separation, 
            has_view_separation,
            has_config_separation
        ])
        
        if separation_score >= 4:
            return 'excellent'
        elif separation_score >= 3:
            return 'good'
        elif separation_score >= 2:
            return 'fair'
        else:
            return 'poor'
    
    def _analyze_complexity_indicators(self, analysis: StructureAnalysis) -> Dict[str, Any]:
        """Analyze various complexity indicators."""
        indicators = {}
        
        # Directory depth
        max_depth = max(len(d.path.split(os.sep)) for d in analysis.directories if d.path) if analysis.directories else 0
        indicators['max_directory_depth'] = max_depth
        
        # File distribution
        avg_files_per_dir = analysis.total_files / max(analysis.total_directories, 1)
        indicators['avg_files_per_directory'] = avg_files_per_dir
        
        # PHP file ratio
        php_ratio = analysis.total_php_files / max(analysis.total_files, 1)
        indicators['php_file_ratio'] = php_ratio
        
        # Large directories (potential hotspots)
        large_dirs = [d for d in analysis.directories if d.file_count > 20]
        indicators['large_directories'] = len(large_dirs)
        
        # Empty directories
        empty_dirs = [d for d in analysis.directories if d.file_count == 0]
        indicators['empty_directories'] = len(empty_dirs)
        
        # Complexity level
        complexity_factors = [
            max_depth > 5,
            avg_files_per_dir > 15,
            len(large_dirs) > 3,
            analysis.total_directories > 50,
            len(analysis.entry_points) > 3
        ]
        
        complexity_score = sum(complexity_factors)
        if complexity_score <= 1:
            indicators['complexity_level'] = 'low'
        elif complexity_score <= 3:
            indicators['complexity_level'] = 'medium'
        else:
            indicators['complexity_level'] = 'high'
        
        return indicators
    
    def _generate_recommendations(self, analysis: StructureAnalysis) -> List[str]:
        """Generate recommendations for structure improvement."""
        recommendations = []
        
        # Organization pattern recommendations
        if analysis.organization_pattern == 'flat':
            recommendations.append(
                "Consider organizing code into directories by functionality (controllers, models, views)"
            )
        elif analysis.organization_pattern == 'mixed':
            recommendations.append(
                "Consider standardizing the directory structure for better maintainability"
            )
        
        # Separation of concerns
        if analysis.separation_quality in ['poor', 'fair']:
            recommendations.append(
                "Improve separation of concerns by organizing code into distinct layers"
            )
        
        # Entry points
        if len(analysis.entry_points) > 3:
            recommendations.append(
                "Consider consolidating multiple entry points for simpler routing"
            )
        elif len(analysis.entry_points) == 0:
            recommendations.append(
                "No clear entry points found - ensure there's a main application entry point"
            )
        
        # Configuration
        if len(analysis.config_files) > 10:
            recommendations.append(
                "Consider consolidating configuration files or organizing them better"
            )
        elif len(analysis.config_files) == 0:
            recommendations.append(
                "No configuration files found - consider externalizing configuration"
            )
        
        # Complexity indicators
        complexity = analysis.complexity_indicators
        
        if complexity.get('max_directory_depth', 0) > 6:
            recommendations.append(
                "Directory structure is very deep - consider flattening some levels"
            )
        
        if complexity.get('large_directories', 0) > 5:
            recommendations.append(
                "Several directories contain many files - consider breaking them down"
            )
        
        if complexity.get('complexity_level') == 'high':
            recommendations.append(
                "High structural complexity detected - consider refactoring for maintainability"
            )
        
        # Framework-specific recommendations
        if analysis.framework_type == 'vanilla':
            recommendations.append(
                "Consider adopting a framework structure for better organization and conventions"
            )
        
        return recommendations
    
    def get_fastapi_structure_mapping(self, analysis: StructureAnalysis) -> Dict[str, str]:
        """Map current PHP structure to recommended FastAPI structure."""
        mapping = {}
        
        # Default FastAPI structure
        fastapi_structure = {
            'app/': 'Main application package',
            'app/api/': 'API routes and endpoints', 
            'app/api/v1/': 'API version 1',
            'app/core/': 'Core functionality and config',
            'app/models/': 'Database models',
            'app/schemas/': 'Pydantic schemas',
            'app/services/': 'Business logic',
            'app/db/': 'Database configuration',
            'tests/': 'Test files',
            'alembic/': 'Database migrations'
        }
        
        # Map existing directories to FastAPI structure
        for directory in analysis.directories:
            if directory.purpose == 'controller':
                mapping[directory.path] = 'app/api/v1/endpoints/'
            elif directory.purpose == 'model':
                mapping[directory.path] = 'app/models/'
            elif directory.purpose == 'view':
                mapping[directory.path] = 'templates/ (if needed)'
            elif directory.purpose == 'config':
                mapping[directory.path] = 'app/core/'
            elif directory.purpose == 'test':
                mapping[directory.path] = 'tests/'
            elif directory.purpose == 'service':
                mapping[directory.path] = 'app/services/'
            elif directory.purpose == 'api':
                mapping[directory.path] = 'app/api/'
            elif directory.purpose == 'migration':
                mapping[directory.path] = 'alembic/versions/'
            else:
                mapping[directory.path] = 'app/ (review placement)'
        
        return mapping
    
    def generate_structure_report(self, analysis: StructureAnalysis) -> str:
        """Generate a human-readable structure analysis report."""
        report = []
        
        report.append("# PHP Project Structure Analysis")
        report.append("=" * 50)
        report.append(f"Project Root: {analysis.project_root}")
        report.append(f"Framework: {analysis.framework_type or 'None detected'}")
        report.append(f"Organization Pattern: {analysis.organization_pattern}")
        report.append(f"Architecture Score: {analysis.architecture_score:.1f}/10")
        report.append(f"Separation Quality: {analysis.separation_quality}")
        report.append("")
        
        report.append("## Statistics")
        report.append(f"- Total Files: {analysis.total_files}")
        report.append(f"- PHP Files: {analysis.total_php_files}")
        report.append(f"- Directories: {analysis.total_directories}")
        report.append(f"- Entry Points: {len(analysis.entry_points)}")
        report.append(f"- Config Files: {len(analysis.config_files)}")
        report.append("")
        
        if analysis.complexity_indicators:
            report.append("## Complexity Indicators")
            for key, value in analysis.complexity_indicators.items():
                report.append(f"- {key.replace('_', ' ').title()}: {value}")
            report.append("")
        
        if analysis.recommendations:
            report.append("## Recommendations")
            for i, rec in enumerate(analysis.recommendations, 1):
                report.append(f"{i}. {rec}")
            report.append("")
        
        report.append("## Directory Structure")
        purposes = {}
        for directory in analysis.directories:
            purpose = directory.purpose or 'other'
            if purpose not in purposes:
                purposes[purpose] = []
            purposes[purpose].append(directory)
        
        for purpose, dirs in sorted(purposes.items()):
            report.append(f"### {purpose.title()}")
            for directory in dirs:
                report.append(f"- {directory.path or 'root'} ({directory.php_file_count} PHP files)")
            report.append("")
        
        return "\n".join(report)# analyzers/structure_analyzer.py - Fixed version
"""Analyzes PHP project structure and organization patterns."""

import os
import re
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from pathlib import Path
from collections import defaultdict


@dataclass
class DirectoryInfo:
    """Information about a directory in the project."""
    path: str
    name: str
    file_count: int = 0
    php_file_count: int = 0
    subdirectory_count: int = 0
    purpose: Optional[str] = None
    framework_role: Optional[str] = None


@dataclass
class FileInfo:
    """Information about a file in the project."""
    path: str
    name: str
    extension: str
    size: int = 0
    purpose: Optional[str] = None
    framework_role: Optional[str] = None


@dataclass
class StructureAnalysis:
    """Analysis result for project structure."""
    project_root: str
    total_files: int = 0
    total_php_files: int = 0
    total_directories: int = 0
    organization_pattern: str = "unknown"
    framework_type: Optional[str] = None
    entry_points: List[str] = field(default_factory=list)
    config_files: List[str] = field(default_factory=list)
    directories: List[DirectoryInfo] = field(default_factory=list)
    architecture_score: float = 0.0
    separation_quality: str = "unknown"
    complexity_indicators: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


class StructureAnalyzer:
    """Analyzes PHP project structure and organization."""
    
    def __init__(self):
        # Framework-specific directory patterns
        self.framework_patterns = {
            'laravel': {
                'app': 'application_logic',
                'app/Http/Controllers': 'controllers',
                'app/Models': 'models', 
                'app/Http/Middleware': 'middleware',
                'routes': 'routing',
                'config': 'configuration',
                'database': 'database_files',
                'resources/views': 'templates',
                'public': 'web_root',
                'storage': 'storage',
                'tests': 'tests'
            },
            'symfony': {
                'src': 'application_logic',
                'src/Controller': 'controllers',
                'src/Entity': 'models',
                'config': 'configuration',
                'templates': 'templates',
                'public': 'web_root',
                'var': 'cache_logs',
                'tests': 'tests'
            },
            'codeigniter': {
                'application': 'application_logic',
                'application/controllers': 'controllers',
                'application/models': 'models',
                'application/views': 'templates',
                'application/config': 'configuration',
                'system': 'framework_core',
                'user_guide': 'documentation'
            },
            'slim': {
                'src': 'application_logic',
                'public': 'web_root',
                'templates': 'templates',
                'config': 'configuration'
            },
            'vanilla': {
                'includes': 'shared_code',
                'lib': 'libraries',
                'classes': 'class_files',
                'config': 'configuration',
                'templates': 'templates',
                'assets': 'static_files'
            }
        }
        
        # Common directory purposes
        self.directory_purposes = {
            'controller': ['controller', 'ctrl', 'handlers'],
            'model': ['model', 'entity', 'entities', 'domain'],
            'view': ['view', 'template', 'tpl', 'presentation'],
            'config': ['config', 'configuration', 'settings', 'conf'],
            'library': ['lib', 'library', 'libraries', 'vendor'],
            'utility': ['util', 'utils', 'utility', 'utilities', 'helper', 'helpers'],
            'test': ['test', 'tests', 'testing', 'spec', 'specs'],
            'documentation': ['doc', 'docs', 'documentation'],
            'asset': ['asset', 'assets', 'static', 'public', 'css', 'js', 'img', 'images'],
            'cache': ['cache', 'tmp', 'temp', 'temporary'],
            'log': ['log', 'logs', 'logging'],
            'upload': ['upload', 'uploads', 'files', 'media'],
            'migration': ['migration', 'migrations', 'schema'],
            'middleware': ['middleware', 'filter', 'filters'],
            'service': ['service', 'services', 'business'],
            'repository': ['repository', 'repositories', 'repo', 'repos'],
            'api': ['api', 'rest', 'endpoints', 'webservice']
        }
        
        # File type patterns
        self.file_purposes = {
            'entry_point': ['index.php', 'app.php', 'bootstrap.php', 'front.php'],
            'configuration': ['config.php', 'settings.php', 'database.php', '.env'],
            'routing': ['routes.php', 'web.php', 'api.php'],
            'autoloader': ['autoload.php', 'vendor/autoload.php'],
            'composer': ['composer.json', 'composer.lock'],
            'deployment': ['Dockerfile', 'docker-compose.yml', '.htaccess', 'nginx.conf']
        }
    
    def analyze_structure(self, project_root: str) -> StructureAnalysis:
        """Analyze the structure of a PHP project."""
        # First, scan to get basic counts and directory info
        scan_results = self._scan_directories_for_counts(project_root)
        
        # Create analysis object with required fields
        analysis = StructureAnalysis(
            project_root=project_root,
            total_files=scan_results['total_files'],
            total_php_files=scan_results['total_php_files'],
            total_directories=scan_results['total_directories'],
            organization_pattern="analyzing"  # Will be updated below
        )
        
        # Now do detailed analysis
        analysis.directories = scan_results['directories']
        
        # Detect framework type
        analysis.framework_type = self._detect_framework(analysis.directories)
        
        # Analyze organization pattern
        analysis.organization_pattern = self._analyze_organization_pattern(
            analysis.directories, analysis.framework_type
        )
        
        # Find entry points
        analysis.entry_points = self._find_entry_points(project_root, analysis.directories)
        
        # Find configuration files
        analysis.config_files = self._find_config_files(project_root, analysis.directories)
        
        # Calculate architecture score
        analysis.architecture_score = self._calculate_architecture_score(analysis)
        
        # Assess separation quality
        analysis.separation_quality = self._assess_separation_quality(analysis)
        
        # Analyze complexity indicators
        analysis.complexity_indicators = self._analyze_complexity_indicators(analysis)
        
        # Generate recommendations
        analysis.recommendations = self._generate_recommendations(analysis)
        
        return analysis
    
    def _scan_directories_for_counts(self, project_root: str) -> Dict[str, Any]:
        """Scan directories and return counts and directory info."""
        ignore_patterns = {
            '.git', '.svn', '.hg',
            'node_modules', 'vendor',
            '.vscode', '.idea',
            '__pycache__', '.pytest_cache',
            'cache', 'logs', 'tmp'
        }
        
        directories = []
        total_files = 0
        total_php_files = 0
        total_directories = 0
        
        for root, dirs, files in os.walk(project_root):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if d not in ignore_patterns]
            
            rel_path = os.path.relpath(root, project_root)
            if rel_path == '.':
                rel_path = ''
            
            # Count files
            php_files = [f for f in files if f.endswith(('.php', '.phtml', '.inc'))]
            
            # Create directory info
            dir_info = DirectoryInfo(
                path=rel_path,
                name=os.path.basename(root) if rel_path else 'root',
                file_count=len(files),
                php_file_count=len(php_files),
                subdirectory_count=len(dirs)
            )
            
            # Determine directory purpose
            dir_info.purpose = self._determine_directory_purpose(dir_info.name, rel_path)
            
            directories.append(dir_info)
            total_files += len(files)
            total_php_files += len(php_files)
            total_directories += 1
        
        return {
            'directories': directories,
            'total_files': total_files,
            'total_php_files': total_php_files,
            'total_directories': total_directories
        }
    
    def _determine_directory_purpose(self, dir_name: str, full_path: str) -> Optional[str]:
        """Determine the purpose of a directory based on its name and path."""
        dir_name_lower = dir_name.lower()
        full_path_lower = full_path.lower()
        
        # Check each purpose category
        for purpose, keywords in self.directory_purposes.items():
            if any(keyword in dir_name_lower for keyword in keywords):
                return purpose
            # Also check full path for nested directories
            if any(keyword in full_path_lower for keyword in keywords):
                return purpose
        
        return None
    
    def _detect_framework(self, directories: List[DirectoryInfo]) -> Optional[str]:
        """Enhanced framework detection with custom PHP pattern recognition."""
        dir_names = {d.name.lower() for d in directories}
        dir_paths = {d.path.lower() for d in directories if d.path}
        all_paths = set(dir_paths) | set(dir_names)
        
        # Check for composer.json to confirm modern PHP project
        has_composer = any('composer' in d.name.lower() for d in directories)
        
        # Laravel detection (needs 4+ indicators)
        laravel_indicators = ['app', 'routes', 'config', 'database', 'resources', 'artisan', 'bootstrap']
        laravel_score = sum(1 for indicator in laravel_indicators if indicator in all_paths)
        if laravel_score >= 4:
            return 'laravel'
        
        # Symfony detection (needs 3+ indicators)
        symfony_indicators = ['src', 'config', 'templates', 'var', 'public', 'bin']
        symfony_score = sum(1 for indicator in symfony_indicators if indicator in all_paths)
        if symfony_score >= 4 and 'app' not in dir_names:  # Distinguish from Laravel
            return 'symfony'
        
        # CodeIgniter detection
        if 'application' in dir_names and 'system' in dir_names:
            return 'codeigniter'
        
        # Slim framework detection (typical Slim structure)
        if ('src' in dir_names and 'public' in dir_names and 
            len([d for d in directories if d.php_file_count > 0]) < 15):  # Minimal structure
            return 'slim'
        
        # CUSTOM/NATIVE PHP DETECTION (Your case)
        custom_indicators = {
            'modern_structure': has_composer and 'src' in dir_names and 'public' in dir_names,
            'mvc_structure': any(mvc in all_paths for mvc in ['controller', 'model', 'core']),
            'psr4_namespacing': has_composer and 'src' in dir_names,
            'config_separation': 'config' in dir_names,
            'not_framework': laravel_score < 3 and symfony_score < 3
        }
        
        # Strong indicators of custom implementation
        if (custom_indicators['modern_structure'] and 
            custom_indicators['mvc_structure'] and 
            custom_indicators['not_framework']):
            return 'custom_mvc'
        
        # Fallback for composer-based custom projects
        if (has_composer and custom_indicators['psr4_namespacing'] and 
            custom_indicators['not_framework']):
            return 'custom_composer'
        
        # Traditional vanilla PHP
        return 'vanilla'
    
    def _analyze_organization_pattern(self, 
                                     directories: List[DirectoryInfo], 
                                     framework_type: Optional[str]) -> str:
        """Analyze the overall organization pattern."""
        purposes = [d.purpose for d in directories if d.purpose]
        purpose_counts = {purpose: purposes.count(purpose) for purpose in set(purposes)}
        
        # Check for MVC pattern
        has_controllers = 'controller' in purpose_counts
        has_models = 'model' in purpose_counts  
        has_views = 'view' in purpose_counts
        
        if has_controllers and has_models and has_views:
            return 'mvc'
        elif has_controllers and has_models:
            return 'mvc_partial'
        
        # Check for domain-driven design
        if 'service' in purpose_counts and 'repository' in purpose_counts:
            return 'domain_driven'
        
        # Check for layered architecture
        layers = ['controller', 'service', 'repository', 'model']
        if sum(1 for layer in layers if layer in purpose_counts) >= 3:
            return 'layered'
        
        # Check for component-based
        if len(purpose_counts) > 8:  # Many different types of directories
            return 'component_based'
        
        # Check for flat structure
        if len([d for d in directories if d.subdirectory_count == 0]) > len(directories) * 0.8:
            return 'flat'
        
        return 'mixed'
    
    def _find_entry_points(self, project_root: str, directories: List[DirectoryInfo]) -> List[str]:
        """Find application entry points."""
        entry_points = []
        
        # Check common entry point files
        for file_pattern in self.file_purposes['entry_point']:
            file_path = os.path.join(project_root, file_pattern)
            if os.path.exists(file_path):
                entry_points.append(file_pattern)
        
        # Check in public directory
        public_dirs = [d for d in directories if 'public' in d.name.lower() or d.purpose == 'asset']
        for pub_dir in public_dirs:
            for file_pattern in ['index.php', 'app.php']:
                file_path = os.path.join(project_root, pub_dir.path, file_pattern)
                if os.path.exists(file_path):
                    entry_points.append(os.path.join(pub_dir.path, file_pattern))
        
        return entry_points
    
    def _find_config_files(self, project_root: str, directories: List[DirectoryInfo]) -> List[str]:
        """Find configuration files."""
        config_files = []
        
        # Check root directory
        for file_pattern in self.file_purposes['configuration']:
            file_path = os.path.join(project_root, file_pattern)
            if os.path.exists(file_path):
                config_files.append(file_pattern)
        
        # Check config directories
        config_dirs = [d for d in directories if d.purpose == 'config']
        for config_dir in config_dirs:
            config_dir_path = os.path.join(project_root, config_dir.path)
            if os.path.exists(config_dir_path):
                for file_name in os.listdir(config_dir_path):
                    if file_name.endswith('.php'):
                        config_files.append(os.path.join(config_dir.path, file_name))
        
        return config_files
    
    def _calculate_architecture_score(self, analysis: StructureAnalysis) -> float:
        """Calculate architecture quality score (0-10)."""
        score = 0.0
        
        # Organization pattern scoring (updated)
        pattern_scores = {
            'mvc': 8.0,
            'custom_mvc': 8.5,  # Add this
            'domain_driven': 9.0,
            'layered': 7.0,
            'mvc_partial': 5.0,
            'component_based': 6.0,
            'mixed': 3.0,
            'flat': 2.0
        }
        score += pattern_scores.get(analysis.organization_pattern, 1.0)
        
        # Framework bonus (updated)
        framework_scores = {
            'laravel': 1.0,
            'symfony': 1.0,
            'custom_mvc': 1.2,  # Bonus for well-structured custom
            'custom_composer': 1.0,
            'codeigniter': 0.8,
            'slim': 0.7,
            'vanilla': 0.0
        }
        score += framework_scores.get(analysis.framework_type, 0.0)
        
        # Rest of the method stays the same...
        # Directory structure bonus
        purposes = [d.purpose for d in analysis.directories if d.purpose]
        unique_purposes = len(set(purposes))
        if unique_purposes >= 5:
            score += 1.0
        elif unique_purposes >= 3:
            score += 0.5
        
        # Entry points penalty (too many is bad)
        if len(analysis.entry_points) == 1:
            score += 1.0
        elif len(analysis.entry_points) <= 3:
            score += 0.5
        elif len(analysis.entry_points) > 5:
            score -= 1.0
        
        # Configuration organization
        if len(analysis.config_files) > 0:
            config_dirs = len([d for d in analysis.directories if d.purpose == 'config'])
            if config_dirs > 0:
                score += 1.0  # Organized config
            elif len(analysis.config_files) <= 3:
                score += 0.5  # Reasonable number of config files
        
        return min(max(score, 0.0), 10.0)  # Clamp between 0 and 10
    
    def _assess_separation_quality(self, analysis: StructureAnalysis) -> str:
        """Assess separation of concerns quality."""
        purposes = [d.purpose for d in analysis.directories if d.purpose]
        purpose_counts = {purpose: purposes.count(purpose) for purpose in set(purposes)}
        
        # Check for key separations
        has_controller_separation = 'controller' in purpose_counts
        has_model_separation = 'model' in purpose_counts
        has_view_separation = 'view' in purpose_counts
        has_config_separation = 'config' in purpose_counts
        
        separation_score = sum([
            has_controller_separation,
            has_model_separation, 
            has_view_separation,
            has_config_separation
        ])
        
        if separation_score >= 4:
            return 'excellent'
        elif separation_score >= 3:
            return 'good'
        elif separation_score >= 2:
            return 'fair'
        else:
            return 'poor'
    
    def _analyze_complexity_indicators(self, analysis: StructureAnalysis) -> Dict[str, Any]:
        """Analyze various complexity indicators."""
        indicators = {}
        
        # Directory depth
        max_depth = max(len(d.path.split(os.sep)) for d in analysis.directories if d.path) if analysis.directories else 0
        indicators['max_directory_depth'] = max_depth
        
        # File distribution
        avg_files_per_dir = analysis.total_files / max(analysis.total_directories, 1)
        indicators['avg_files_per_directory'] = avg_files_per_dir
        
        # PHP file ratio
        php_ratio = analysis.total_php_files / max(analysis.total_files, 1)
        indicators['php_file_ratio'] = php_ratio
        
        # Large directories (potential hotspots)
        large_dirs = [d for d in analysis.directories if d.file_count > 20]
        indicators['large_directories'] = len(large_dirs)
        
        # Empty directories
        empty_dirs = [d for d in analysis.directories if d.file_count == 0]
        indicators['empty_directories'] = len(empty_dirs)
        
        # Complexity level
        complexity_factors = [
            max_depth > 5,
            avg_files_per_dir > 15,
            len(large_dirs) > 3,
            analysis.total_directories > 50,
            len(analysis.entry_points) > 3
        ]
        
        complexity_score = sum(complexity_factors)
        if complexity_score <= 1:
            indicators['complexity_level'] = 'low'
        elif complexity_score <= 3:
            indicators['complexity_level'] = 'medium'
        else:
            indicators['complexity_level'] = 'high'
        
        return indicators
    
    def _generate_recommendations(self, analysis: StructureAnalysis) -> List[str]:
        """Generate recommendations for structure improvement."""
        recommendations = []
        
        # Organization pattern recommendations
        if analysis.organization_pattern == 'flat':
            recommendations.append(
                "Consider organizing code into directories by functionality (controllers, models, views)"
            )
        elif analysis.organization_pattern == 'mixed':
            recommendations.append(
                "Consider standardizing the directory structure for better maintainability"
            )
        
        # Separation of concerns
        if analysis.separation_quality in ['poor', 'fair']:
            recommendations.append(
                "Improve separation of concerns by organizing code into distinct layers"
            )
        
        # Entry points
        if len(analysis.entry_points) > 3:
            recommendations.append(
                "Consider consolidating multiple entry points for simpler routing"
            )
        elif len(analysis.entry_points) == 0:
            recommendations.append(
                "No clear entry points found - ensure there's a main application entry point"
            )
        
        # Configuration
        if len(analysis.config_files) > 10:
            recommendations.append(
                "Consider consolidating configuration files or organizing them better"
            )
        elif len(analysis.config_files) == 0:
            recommendations.append(
                "No configuration files found - consider externalizing configuration"
            )
        
        # Complexity indicators
        complexity = analysis.complexity_indicators
        
        if complexity.get('max_directory_depth', 0) > 6:
            recommendations.append(
                "Directory structure is very deep - consider flattening some levels"
            )
        
        if complexity.get('large_directories', 0) > 5:
            recommendations.append(
                "Several directories contain many files - consider breaking them down"
            )
        
        if complexity.get('complexity_level') == 'high':
            recommendations.append(
                "High structural complexity detected - consider refactoring for maintainability"
            )
        
        # Framework-specific recommendations
        if analysis.framework_type == 'vanilla':
            recommendations.append(
                "Consider adopting a framework structure for better organization and conventions"
            )
        
        return recommendations
    
    def get_fastapi_structure_mapping(self, analysis: StructureAnalysis) -> Dict[str, str]:
        """Map current PHP structure to recommended FastAPI structure."""
        mapping = {}
        
        # Default FastAPI structure
        fastapi_structure = {
            'app/': 'Main application package',
            'app/api/': 'API routes and endpoints', 
            'app/api/v1/': 'API version 1',
            'app/core/': 'Core functionality and config',
            'app/models/': 'Database models',
            'app/schemas/': 'Pydantic schemas',
            'app/services/': 'Business logic',
            'app/db/': 'Database configuration',
            'tests/': 'Test files',
            'alembic/': 'Database migrations'
        }
        
        # Map existing directories to FastAPI structure
        for directory in analysis.directories:
            if directory.purpose == 'controller':
                mapping[directory.path] = 'app/api/v1/endpoints/'
            elif directory.purpose == 'model':
                mapping[directory.path] = 'app/models/'
            elif directory.purpose == 'view':
                mapping[directory.path] = 'templates/ (if needed)'
            elif directory.purpose == 'config':
                mapping[directory.path] = 'app/core/'
            elif directory.purpose == 'test':
                mapping[directory.path] = 'tests/'
            elif directory.purpose == 'service':
                mapping[directory.path] = 'app/services/'
            elif directory.purpose == 'api':
                mapping[directory.path] = 'app/api/'
            elif directory.purpose == 'migration':
                mapping[directory.path] = 'alembic/versions/'
            else:
                mapping[directory.path] = 'app/ (review placement)'
        
        return mapping
    
    def generate_structure_report(self, analysis: StructureAnalysis) -> str:
        """Generate a human-readable structure analysis report."""
        report = []
        
        report.append("# PHP Project Structure Analysis")
        report.append("=" * 50)
        report.append(f"Project Root: {analysis.project_root}")
        report.append(f"Framework: {analysis.framework_type or 'None detected'}")
        report.append(f"Organization Pattern: {analysis.organization_pattern}")
        report.append(f"Architecture Score: {analysis.architecture_score:.1f}/10")
        report.append(f"Separation Quality: {analysis.separation_quality}")
        report.append("")
        
        report.append("## Statistics")
        report.append(f"- Total Files: {analysis.total_files}")
        report.append(f"- PHP Files: {analysis.total_php_files}")
        report.append(f"- Directories: {analysis.total_directories}")
        report.append(f"- Entry Points: {len(analysis.entry_points)}")
        report.append(f"- Config Files: {len(analysis.config_files)}")
        report.append("")
        
        if analysis.complexity_indicators:
            report.append("## Complexity Indicators")
            for key, value in analysis.complexity_indicators.items():
                report.append(f"- {key.replace('_', ' ').title()}: {value}")
            report.append("")
        
        if analysis.recommendations:
            report.append("## Recommendations")
            for i, rec in enumerate(analysis.recommendations, 1):
                report.append(f"{i}. {rec}")
            report.append("")
        
        report.append("## Directory Structure")
        purposes = {}
        for directory in analysis.directories:
            purpose = directory.purpose or 'other'
            if purpose not in purposes:
                purposes[purpose] = []
            purposes[purpose].append(directory)
        
        for purpose, dirs in sorted(purposes.items()):
            report.append(f"### {purpose.title()}")
            for directory in dirs:
                report.append(f"- {directory.path or 'root'} ({directory.php_file_count} PHP files)")
            report.append("")
        
        return "\n".join(report)