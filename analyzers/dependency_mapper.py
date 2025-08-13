# analyzers/dependency_mapper.py
"""Maps PHP dependencies to Python equivalents for FastAPI conversion."""

import json
import re
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DependencyMapping:
    """Represents a dependency mapping from PHP to Python."""
    php_package: str
    python_package: str
    version_constraint: Optional[str] = None
    purpose: str = ""
    installation_notes: Optional[str] = None
    compatibility_notes: Optional[str] = None
    alternatives: List[str] = field(default_factory=list)
    migration_complexity: str = "low"  # low, medium, high


@dataclass
class DependencyAnalysis:
    """Analysis result for project dependencies."""
    total_dependencies: int
    mapped_dependencies: List[DependencyMapping]
    unmapped_dependencies: List[str]
    framework_dependencies: List[str]
    development_dependencies: List[str]
    complexity_score: float
    migration_recommendations: List[str]


class DependencyMapper:
    """Maps PHP dependencies to Python equivalents."""
    
    def __init__(self):
        self.mappings = self._initialize_mappings()
        self.framework_mappings = self._initialize_framework_mappings()
        self.development_mappings = self._initialize_development_mappings()
    
    def _initialize_mappings(self) -> Dict[str, DependencyMapping]:
        """Initialize core dependency mappings."""
        mappings = {}
        
        # Database libraries
        mappings.update({
            'doctrine/dbal': DependencyMapping(
                php_package='doctrine/dbal',
                python_package='sqlalchemy',
                version_constraint='>=2.0.0',
                purpose='Database abstraction layer',
                migration_complexity='medium'
            ),
            'illuminate/database': DependencyMapping(
                php_package='illuminate/database',
                python_package='sqlalchemy',
                version_constraint='>=2.0.0',
                purpose='Database ORM',
                alternatives=['tortoise-orm', 'databases'],
                migration_complexity='medium'
            ),
            'propel/propel': DependencyMapping(
                php_package='propel/propel',
                python_package='sqlalchemy',
                version_constraint='>=2.0.0',
                purpose='ORM framework',
                migration_complexity='high'
            ),
            'mongodb/mongodb': DependencyMapping(
                php_package='mongodb/mongodb',
                python_package='motor',
                version_constraint='>=3.0.0',
                purpose='MongoDB async driver',
                alternatives=['pymongo'],
                migration_complexity='low'
            ),
            'predis/predis': DependencyMapping(
                php_package='predis/predis',
                python_package='redis',
                version_constraint='>=5.0.0',
                purpose='Redis client',
                migration_complexity='low'
            )
        })
        
        # HTTP clients
        mappings.update({
            'guzzlehttp/guzzle': DependencyMapping(
                php_package='guzzlehttp/guzzle',
                python_package='httpx',
                version_constraint='>=0.25.0',
                purpose='HTTP client',
                alternatives=['aiohttp', 'requests'],
                migration_complexity='low'
            ),
            'rmccue/requests': DependencyMapping(
                php_package='rmccue/requests',
                python_package='httpx',
                version_constraint='>=0.25.0',
                purpose='HTTP requests library',
                migration_complexity='low'
            )
        })
        
        # Authentication & Security
        mappings.update({
            'firebase/php-jwt': DependencyMapping(
                php_package='firebase/php-jwt',
                python_package='python-jose[cryptography]',
                version_constraint='>=3.3.0',
                purpose='JWT handling',
                alternatives=['pyjwt'],
                migration_complexity='low'
            ),
            'league/oauth2-server': DependencyMapping(
                php_package='league/oauth2-server',
                python_package='authlib',
                version_constraint='>=1.2.0',
                purpose='OAuth2 server',
                migration_complexity='high'
            ),
            'defuse/php-encryption': DependencyMapping(
                php_package='defuse/php-encryption',
                python_package='cryptography',
                version_constraint='>=41.0.0',
                purpose='Encryption library',
                migration_complexity='medium'
            )
        })
        
        # Validation
        mappings.update({
            'respect/validation': DependencyMapping(
                php_package='respect/validation',
                python_package='pydantic',
                version_constraint='>=2.0.0',
                purpose='Data validation',
                migration_complexity='medium'
            ),
            'vlucas/valitron': DependencyMapping(
                php_package='vlucas/valitron',
                python_package='pydantic',
                version_constraint='>=2.0.0',
                purpose='Simple validation',
                migration_complexity='low'
            )
        })
        
        # Logging
        mappings.update({
            'monolog/monolog': DependencyMapping(
                php_package='monolog/monolog',
                python_package='loguru',
                version_constraint='>=0.7.0',
                purpose='Logging framework',
                alternatives=['structlog', 'logging'],
                migration_complexity='low'
            ),
            'psr/log': DependencyMapping(
                php_package='psr/log',
                python_package='loguru',
                version_constraint='>=0.7.0',
                purpose='Logging interface',
                migration_complexity='low'
            )
        })
        
        # Date/Time
        mappings.update({
            'nesbot/carbon': DependencyMapping(
                php_package='nesbot/carbon',
                python_package='arrow',
                version_constraint='>=1.3.0',
                purpose='Date manipulation',
                alternatives=['pendulum', 'python-dateutil'],
                migration_complexity='low'
            ),
            'cakephp/chronos': DependencyMapping(
                php_package='cakephp/chronos',
                python_package='arrow',
                version_constraint='>=1.3.0',
                purpose='Date/time library',
                migration_complexity='low'
            )
        })
        
        # Template engines
        mappings.update({
            'twig/twig': DependencyMapping(
                php_package='twig/twig',
                python_package='jinja2',
                version_constraint='>=3.1.0',
                purpose='Template engine',
                migration_complexity='medium'
            ),
            'smarty/smarty': DependencyMapping(
                php_package='smarty/smarty',
                python_package='jinja2',
                version_constraint='>=3.1.0',
                purpose='Template engine',
                migration_complexity='high'
            )
        })
        
        # File handling
        mappings.update({
            'league/flysystem': DependencyMapping(
                php_package='league/flysystem',
                python_package='boto3',
                version_constraint='>=1.28.0',
                purpose='File storage abstraction',
                alternatives=['aiofiles'],
                migration_complexity='medium'
            ),
            'intervention/image': DependencyMapping(
                php_package='intervention/image',
                python_package='pillow',
                version_constraint='>=10.0.0',
                purpose='Image manipulation',
                migration_complexity='medium'
            )
        })
        
        # Testing
        mappings.update({
            'phpunit/phpunit': DependencyMapping(
                php_package='phpunit/phpunit',
                python_package='pytest',
                version_constraint='>=7.4.0',
                purpose='Testing framework',
                migration_complexity='medium'
            ),
            'mockery/mockery': DependencyMapping(
                php_package='mockery/mockery',
                python_package='pytest-mock',
                version_constraint='>=3.11.0',
                purpose='Mocking library',
                migration_complexity='low'
            ),
            'fakerphp/faker': DependencyMapping(
                php_package='fakerphp/faker',
                python_package='faker',
                version_constraint='>=19.0.0',
                purpose='Fake data generation',
                migration_complexity='low'
            )
        })
        
        # Utilities
        mappings.update({
            'ramsey/uuid': DependencyMapping(
                php_package='ramsey/uuid',
                python_package='uuid',
                purpose='UUID generation',
                installation_notes='Built into Python standard library',
                migration_complexity='low'
            ),
            'mtdowling/cron-expression': DependencyMapping(
                php_package='mtdowling/cron-expression',
                python_package='croniter',
                version_constraint='>=1.4.0',
                purpose='Cron expression parsing',
                migration_complexity='low'
            ),
            'league/csv': DependencyMapping(
                php_package='league/csv',
                python_package='pandas',
                version_constraint='>=2.0.0',
                purpose='CSV handling',
                alternatives=['csv'],
                migration_complexity='low'
            )
        })
        
        # Serialization
        mappings.update({
            'jms/serializer': DependencyMapping(
                php_package='jms/serializer',
                python_package='pydantic',
                version_constraint='>=2.0.0',
                purpose='Object serialization',
                alternatives=['marshmallow'],
                migration_complexity='medium'
            ),
            'symfony/serializer': DependencyMapping(
                php_package='symfony/serializer',
                python_package='pydantic',
                version_constraint='>=2.0.0',
                purpose='Serialization component',
                migration_complexity='medium'
            )
        })
        
        return mappings
    
    def _initialize_framework_mappings(self) -> Dict[str, DependencyMapping]:
        """Initialize framework-specific mappings."""
        return {
            'laravel/framework': DependencyMapping(
                php_package='laravel/framework',
                python_package='fastapi',
                version_constraint='>=0.104.0',
                purpose='Web framework',
                alternatives=['django', 'flask'],
                migration_complexity='high',
                compatibility_notes='Laravel features need manual conversion'
            ),
            'symfony/symfony': DependencyMapping(
                php_package='symfony/symfony',
                python_package='fastapi',
                version_constraint='>=0.104.0',
                purpose='Web framework',
                migration_complexity='high'
            ),
            'codeigniter/framework': DependencyMapping(
                php_package='codeigniter/framework',
                python_package='fastapi',
                version_constraint='>=0.104.0',
                purpose='Web framework',
                migration_complexity='medium'
            ),
            'slim/slim': DependencyMapping(
                php_package='slim/slim',
                python_package='fastapi',
                version_constraint='>=0.104.0',
                purpose='Micro framework',
                migration_complexity='low'
            )
        }
    
    def _initialize_development_mappings(self) -> Dict[str, DependencyMapping]:
        """Initialize development tool mappings."""
        return {
            'squizlabs/php_codesniffer': DependencyMapping(
                php_package='squizlabs/php_codesniffer',
                python_package='black',
                version_constraint='>=23.0.0',
                purpose='Code formatting',
                alternatives=['autopep8', 'yapf'],
                migration_complexity='low'
            ),
            'friendsofphp/php-cs-fixer': DependencyMapping(
                php_package='friendsofphp/php-cs-fixer',
                python_package='black',
                version_constraint='>=23.0.0',
                purpose='Code style fixer',
                migration_complexity='low'
            ),
            'phpstan/phpstan': DependencyMapping(
                php_package='phpstan/phpstan',
                python_package='mypy',
                version_constraint='>=1.5.0',
                purpose='Static analysis',
                alternatives=['pylint', 'flake8'],
                migration_complexity='medium'
            ),
            'vimeo/psalm': DependencyMapping(
                php_package='vimeo/psalm',
                python_package='mypy',
                version_constraint='>=1.5.0',
                purpose='Static analysis',
                migration_complexity='medium'
            )
        }
    
    def analyze_composer_json(self, composer_json_path: str) -> DependencyAnalysis:
        """Analyze composer.json file and map dependencies."""
        try:
            with open(composer_json_path, 'r') as f:
                composer_data = json.load(f)
        except Exception:
            return DependencyAnalysis(
                total_dependencies=0,
                mapped_dependencies=[],
                unmapped_dependencies=[],
                framework_dependencies=[],
                development_dependencies=[],
                complexity_score=0.0,
                migration_recommendations=[]
            )
        
        # Extract dependencies
        require = composer_data.get('require', {})
        require_dev = composer_data.get('require-dev', {})
        
        all_deps = {**require, **require_dev}
        
        # Analyze dependencies
        mapped_deps = []
        unmapped_deps = []
        framework_deps = []
        dev_deps = []
        
        for package, version in all_deps.items():
            if package == 'php':
                continue  # Skip PHP version constraint
            
            # Check if it's a framework
            if package in self.framework_mappings:
                framework_deps.append(package)
                mapped_deps.append(self.framework_mappings[package])
            # Check if it's a development tool
            elif package in self.development_mappings:
                dev_deps.append(package)
                mapped_deps.append(self.development_mappings[package])
            # Check if it's in our mappings
            elif package in self.mappings:
                mapped_deps.append(self.mappings[package])
            else:
                unmapped_deps.append(package)
        
        # Calculate complexity score
        complexity_score = self._calculate_complexity_score(
            all_deps, mapped_deps, unmapped_deps, framework_deps
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            mapped_deps, unmapped_deps, framework_deps
        )
        
        return DependencyAnalysis(
            total_dependencies=len(all_deps),
            mapped_dependencies=mapped_deps,
            unmapped_dependencies=unmapped_deps,
            framework_dependencies=framework_deps,
            development_dependencies=dev_deps,
            complexity_score=complexity_score,
            migration_recommendations=recommendations
        )
    
    def analyze_code_dependencies(self, php_files: List[str]) -> List[str]:
        """Analyze PHP code to find implicit dependencies."""
        dependencies = set()
        
        # Patterns for common PHP extensions/functions
        extension_patterns = {
            'curl': [r'curl_init', r'curl_exec', r'curl_setopt'],
            'gd': [r'imagecreate', r'imagejpeg', r'imagepng'],
            'json': [r'json_encode', r'json_decode'],
            'mysqli': [r'mysqli_connect', r'mysqli_query'],
            'pdo': [r'new PDO', r'PDO::'],
            'redis': [r'new Redis', r'Redis::'],
            'xml': [r'simplexml_load', r'DOMDocument'],
            'zip': [r'ZipArchive'],
            'bcmath': [r'bcadd', r'bcsub', r'bcmul', r'bcdiv'],
            'mbstring': [r'mb_strlen', r'mb_substr'],
            'openssl': [r'openssl_encrypt', r'openssl_decrypt'],
            'hash': [r'hash\(', r'hash_hmac'],
            'session': [r'session_start', r'\$_SESSION'],
            'fileinfo': [r'finfo_open', r'mime_content_type']
        }
        
        for file_path in php_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                for extension, patterns in extension_patterns.items():
                    if any(re.search(pattern, content, re.IGNORECASE) for pattern in patterns):
                        dependencies.add(extension)
                        
            except Exception:
                continue
        
        return list(dependencies)
    
    def _calculate_complexity_score(self, 
                                   all_deps: Dict[str, str],
                                   mapped_deps: List[DependencyMapping],
                                   unmapped_deps: List[str],
                                   framework_deps: List[str]) -> float:
        """Calculate migration complexity score."""
        total_deps = len(all_deps)
        if total_deps == 0:
            return 0.0
        
        # Base score from number of dependencies
        base_score = min(total_deps / 20, 5.0)  # Cap at 5
        
        # Add complexity from unmapped dependencies
        unmapped_penalty = len(unmapped_deps) * 0.5
        
        # Add complexity from individual mappings
        mapping_complexity = 0
        for mapping in mapped_deps:
            if mapping.migration_complexity == 'high':
                mapping_complexity += 2
            elif mapping.migration_complexity == 'medium':
                mapping_complexity += 1
            # 'low' adds 0
        
        # Framework complexity
        framework_complexity = len(framework_deps) * 3
        
        total_score = base_score + unmapped_penalty + mapping_complexity + framework_complexity
        return min(total_score, 10.0)  # Cap at 10
    
    def _generate_recommendations(self,
                                 mapped_deps: List[DependencyMapping],
                                 unmapped_deps: List[str],
                                 framework_deps: List[str]) -> List[str]:
        """Generate migration recommendations."""
        recommendations = []
        
        # Framework recommendations
        if framework_deps:
            recommendations.append(
                f"Major framework migration required for: {', '.join(framework_deps)}. "
                "Plan for significant architectural changes."
            )
        
        # High complexity dependencies
        high_complexity = [dep for dep in mapped_deps if dep.migration_complexity == 'high']
        if high_complexity:
            packages = [dep.php_package for dep in high_complexity]
            recommendations.append(
                f"High complexity migrations needed for: {', '.join(packages)}. "
                "Consider manual implementation or alternative approaches."
            )
        
        # Unmapped dependencies
        if unmapped_deps:
            if len(unmapped_deps) <= 3:
                recommendations.append(
                    f"Research Python alternatives for: {', '.join(unmapped_deps)}"
                )
            else:
                recommendations.append(
                    f"Research Python alternatives for {len(unmapped_deps)} unmapped dependencies. "
                    "Consider if all are necessary for the API."
                )
        
        # Alternative suggestions
        alternatives_available = [dep for dep in mapped_deps if dep.alternatives]
        if alternatives_available:
            recommendations.append(
                "Multiple Python alternatives available for some dependencies. "
                "Evaluate based on your specific needs and performance requirements."
            )
        
        # General recommendations
        if len(mapped_deps) > 15:
            recommendations.append(
                "Large number of dependencies detected. Consider reducing scope "
                "for initial conversion and adding features incrementally."
            )
        
        return recommendations
    
    def generate_requirements_txt(self, mapped_deps: List[DependencyMapping]) -> str:
        """Generate requirements.txt content from mapped dependencies."""
        lines = ["# Requirements generated from PHP dependencies\n"]
        
        # Group by category
        categories = {
            'Web Framework': [],
            'Database': [],
            'HTTP': [],
            'Authentication': [],
            'Validation': [],
            'Utilities': [],
            'Development': []
        }
        
        # Categorize dependencies
        for dep in mapped_deps:
            purpose = dep.purpose.lower()
            if 'framework' in purpose:
                categories['Web Framework'].append(dep)
            elif any(word in purpose for word in ['database', 'orm', 'sql']):
                categories['Database'].append(dep)
            elif any(word in purpose for word in ['http', 'client', 'request']):
                categories['HTTP'].append(dep)
            elif any(word in purpose for word in ['auth', 'jwt', 'oauth', 'security']):
                categories['Authentication'].append(dep)
            elif any(word in purpose for word in ['validation', 'serialize']):
                categories['Validation'].append(dep)
            elif any(word in purpose for word in ['test', 'mock', 'format']):
                categories['Development'].append(dep)
            else:
                categories['Utilities'].append(dep)
        
        # Generate requirements by category
        for category, deps in categories.items():
            if deps:
                lines.append(f"\n# {category}")
                for dep in deps:
                    if dep.version_constraint:
                        lines.append(f"{dep.python_package}{dep.version_constraint}")
                    else:
                        lines.append(dep.python_package)
                    
                    if dep.installation_notes:
                        lines.append(f"# {dep.installation_notes}")
        
        return '\n'.join(lines)
    
    def get_migration_summary(self, analysis: DependencyAnalysis) -> Dict[str, Any]:
        """Get summary of dependency migration."""
        return {
            'total_dependencies': analysis.total_dependencies,
            'successfully_mapped': len(analysis.mapped_dependencies),
            'unmapped_count': len(analysis.unmapped_dependencies),
            'framework_dependencies': len(analysis.framework_dependencies),
            'complexity_score': analysis.complexity_score,
            'complexity_level': self._get_complexity_level(analysis.complexity_score),
            'recommendations_count': len(analysis.migration_recommendations),
            'migration_effort': self._estimate_migration_effort(analysis)
        }
    
    def _get_complexity_level(self, score: float) -> str:
        """Convert numeric complexity score to level."""
        if score < 3:
            return 'low'
        elif score < 6:
            return 'medium'
        else:
            return 'high'
    
    def _estimate_migration_effort(self, analysis: DependencyAnalysis) -> str:
        """Estimate overall migration effort."""
        if analysis.complexity_score < 2:
            return '1-2 days'
        elif analysis.complexity_score < 4:
            return '3-5 days'
        elif analysis.complexity_score < 7:
            return '1-2 weeks'
        else:
            return '2+ weeks'