# planners/dependency_planner.py
"""Plans Python dependency migration and requirements for FastAPI conversion."""

from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from packaging import version
import re


@dataclass
class PythonDependency:
    """Represents a Python package dependency."""
    name: str
    version_spec: str
    purpose: str
    category: str  # core, database, auth, utils, dev, etc.
    is_required: bool = True
    alternatives: List[str] = field(default_factory=list)
    installation_notes: Optional[str] = None
    php_equivalent: Optional[str] = None
    migration_complexity: str = "low"  # low, medium, high


@dataclass
class DependencyGroup:
    """Group of related dependencies."""
    name: str
    description: str
    dependencies: List[PythonDependency] = field(default_factory=list)
    optional: bool = False
    priority: int = 1  # 1=high, 2=medium, 3=low


@dataclass
class DependencyPlan:
    """Complete dependency migration plan."""
    groups: List[DependencyGroup] = field(default_factory=list)
    total_dependencies: int = 0
    estimated_install_time: str = ""
    potential_conflicts: List[str] = field(default_factory=list)
    migration_notes: List[str] = field(default_factory=list)
    requirements_files: Dict[str, List[str]] = field(default_factory=dict)


class DependencyPlanner:
    """Plans Python dependencies for FastAPI conversion."""
    
    def __init__(self):
        self.core_fastapi_deps = self._get_core_fastapi_dependencies()
        self.database_deps = self._get_database_dependencies()
        self.auth_deps = self._get_authentication_dependencies()
        self.utility_deps = self._get_utility_dependencies()
        self.dev_deps = self._get_development_dependencies()
        self.optional_deps = self._get_optional_dependencies()
    
    def plan_dependencies(self, analysis_result: Dict[str, Any]) -> DependencyPlan:
        """Plan Python dependencies based on PHP project analysis."""
        
        plan = DependencyPlan()
        
        # Analyze requirements from PHP project
        requirements = self._analyze_requirements(analysis_result)
        
        # Plan core dependencies
        plan.groups.append(self._plan_core_dependencies(requirements))
        
        # Plan database dependencies
        db_group = self._plan_database_dependencies(analysis_result, requirements)
        if db_group.dependencies:
            plan.groups.append(db_group)
        
        # Plan authentication dependencies
        auth_group = self._plan_authentication_dependencies(analysis_result, requirements)
        if auth_group.dependencies:
            plan.groups.append(auth_group)
        
        # Plan utility dependencies
        util_group = self._plan_utility_dependencies(analysis_result, requirements)
        if util_group.dependencies:
            plan.groups.append(util_group)
        
        # Plan development dependencies
        plan.groups.append(self._plan_development_dependencies(analysis_result, requirements))
        
        # Plan optional dependencies
        optional_group = self._plan_optional_dependencies(analysis_result, requirements)
        if optional_group.dependencies:
            plan.groups.append(optional_group)
        
        # Calculate totals and metadata
        plan.total_dependencies = sum(len(group.dependencies) for group in plan.groups)
        plan.estimated_install_time = self._estimate_install_time(plan)
        plan.potential_conflicts = self._detect_potential_conflicts(plan)
        plan.migration_notes = self._generate_migration_notes(analysis_result, plan)
        plan.requirements_files = self._generate_requirements_files(plan)
        
        return plan
    
    def _analyze_requirements(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze what features are needed based on PHP project analysis."""
        requirements = {
            'web_framework': True,  # Always need FastAPI
            'database': False,
            'authentication': False,
            'file_uploads': False,
            'background_tasks': False,
            'caching': False,
            'email': False,
            'templates': False,
            'testing': True,  # Always recommend testing
            'documentation': True,  # Always need docs
            'logging': True,  # Always need logging
            'validation': True,  # Always need validation
            'serialization': True,  # Always need for APIs
            'http_client': False,
            'image_processing': False,
            'pdf_generation': False,
            'excel_processing': False,
            'encryption': False,
            'monitoring': False
        }
        
        # Analyze database needs
        database_analysis = analysis_result.get('database_analysis', {})
        if database_analysis.get('total_connections', 0) > 0:
            requirements['database'] = True
        
        # Analyze authentication needs
        endpoint_analysis = analysis_result.get('endpoint_analysis', {})
        auth_methods = endpoint_analysis.get('authentication_methods', [])
        if auth_methods:
            requirements['authentication'] = True
        
        # Analyze file upload needs
        endpoints = endpoint_analysis.get('endpoints', [])
        if any('upload' in ep.get('route', '').lower() or 'file' in ep.get('route', '').lower() 
               for ep in endpoints):
            requirements['file_uploads'] = True
        
        # Analyze dependency patterns
        dependency_analysis = analysis_result.get('dependency_analysis', {})
        php_deps = dependency_analysis.get('python_mappings', {})
        
        # Check for specific features based on PHP dependencies
        for php_dep, python_dep in php_deps.items():
            if any(keyword in php_dep.lower() for keyword in ['guzzle', 'curl', 'http']):
                requirements['http_client'] = True
            elif any(keyword in php_dep.lower() for keyword in ['image', 'gd', 'imagick']):
                requirements['image_processing'] = True
            elif any(keyword in php_dep.lower() for keyword in ['pdf', 'dompdf', 'tcpdf']):
                requirements['pdf_generation'] = True
            elif any(keyword in php_dep.lower() for keyword in ['excel', 'spreadsheet', 'csv']):
                requirements['excel_processing'] = True
            elif any(keyword in php_dep.lower() for keyword in ['encrypt', 'crypto', 'hash']):
                requirements['encryption'] = True
            elif any(keyword in php_dep.lower() for keyword in ['redis', 'memcache', 'cache']):
                requirements['caching'] = True
            elif any(keyword in php_dep.lower() for keyword in ['mail', 'email', 'smtp']):
                requirements['email'] = True
            elif any(keyword in php_dep.lower() for keyword in ['twig', 'smarty', 'template']):
                requirements['templates'] = True
            elif any(keyword in php_dep.lower() for keyword in ['queue', 'job', 'worker']):
                requirements['background_tasks'] = True
        
        return requirements
    
    def _plan_core_dependencies(self, requirements: Dict[str, Any]) -> DependencyGroup:
        """Plan core FastAPI dependencies."""
        dependencies = []
        
        # Core FastAPI dependencies
        for dep_name, dep_info in self.core_fastapi_deps.items():
            dependencies.append(PythonDependency(
                name=dep_name,
                version_spec=dep_info['version'],
                purpose=dep_info['purpose'],
                category='core',
                is_required=dep_info.get('required', True)
            ))
        
        return DependencyGroup(
            name="Core Web Framework",
            description="Essential FastAPI and web framework dependencies",
            dependencies=dependencies,
            priority=1
        )
    
    def _plan_database_dependencies(self, analysis_result: Dict[str, Any], 
                                   requirements: Dict[str, Any]) -> DependencyGroup:
        """Plan database-related dependencies."""
        dependencies = []
        
        if not requirements.get('database'):
            return DependencyGroup(name="Database", description="Database dependencies")
        
        database_analysis = analysis_result.get('database_analysis', {})
        connections = database_analysis.get('connections', [])
        
        # Determine database types used
        db_types = set()
        for conn in connections:
            db_types.add(conn.get('type', 'sqlite'))
        
        # Add SQLAlchemy (always for SQL databases)
        if any(db_type in ['mysql', 'postgresql', 'sqlite'] for db_type in db_types):
            dependencies.append(PythonDependency(
                name="sqlalchemy",
                version_spec=">=2.0.0",
                purpose="SQL ORM and database toolkit",
                category="database",
                alternatives=["tortoise-orm", "databases"]
            ))
            
            dependencies.append(PythonDependency(
                name="alembic",
                version_spec=">=1.12.0",
                purpose="Database migration tool",
                category="database"
            ))
        
        # Add database-specific drivers
        for db_type in db_types:
            if db_type == 'mysql':
                dependencies.append(PythonDependency(
                    name="mysql-connector-python",
                    version_spec=">=8.1.0",
                    purpose="MySQL database driver",
                    category="database",
                    alternatives=["aiomysql", "PyMySQL"],
                    php_equivalent="mysqli"
                ))
            elif db_type == 'postgresql':
                dependencies.append(PythonDependency(
                    name="psycopg2-binary",
                    version_spec=">=2.9.0",
                    purpose="PostgreSQL database driver",
                    category="database",
                    alternatives=["asyncpg"],
                    php_equivalent="pdo_pgsql"
                ))
            elif db_type == 'mongodb':
                dependencies.append(PythonDependency(
                    name="motor",
                    version_spec=">=3.3.0",
                    purpose="Async MongoDB driver",
                    category="database",
                    alternatives=["pymongo"],
                    php_equivalent="mongodb/mongodb"
                ))
        
        # Add Redis if caching is needed
        if requirements.get('caching'):
            dependencies.append(PythonDependency(
                name="redis",
                version_spec=">=5.0.0",
                purpose="Redis client for caching",
                category="database",
                php_equivalent="predis/predis"
            ))
        
        return DependencyGroup(
            name="Database",
            description="Database drivers, ORM, and related tools",
            dependencies=dependencies,
            priority=1
        )
    
    def _plan_authentication_dependencies(self, analysis_result: Dict[str, Any], 
                                        requirements: Dict[str, Any]) -> DependencyGroup:
        """Plan authentication and security dependencies."""
        dependencies = []
        
        if not requirements.get('authentication'):
            return DependencyGroup(name="Authentication", description="Authentication dependencies")
        
        endpoint_analysis = analysis_result.get('endpoint_analysis', {})
        auth_methods = endpoint_analysis.get('authentication_methods', [])
        
        # JWT authentication
        if any('jwt' in method.lower() or 'token' in method.lower() for method in auth_methods):
            dependencies.extend([
                PythonDependency(
                    name="python-jose[cryptography]",
                    version_spec=">=3.3.0",
                    purpose="JWT token handling",
                    category="auth",
                    alternatives=["pyjwt"],
                    php_equivalent="firebase/php-jwt"
                ),
                PythonDependency(
                    name="passlib[bcrypt]",
                    version_spec=">=1.7.4",
                    purpose="Password hashing and verification",
                    category="auth",
                    php_equivalent="password_hash/password_verify"
                )
            ])
        
        # OAuth dependencies
        if any('oauth' in method.lower() for method in auth_methods):
            dependencies.append(PythonDependency(
                name="authlib",
                version_spec=">=1.2.0",
                purpose="OAuth 2.0 and OpenID Connect",
                category="auth",
                php_equivalent="league/oauth2-server",
                migration_complexity="medium"
            ))
        
        # Session-based auth
        if any('session' in method.lower() for method in auth_methods):
            dependencies.append(PythonDependency(
                name="python-multipart",
                version_spec=">=0.0.6",
                purpose="Form data parsing for login",
                category="auth"
            ))
        
        # General security
        if requirements.get('encryption'):
            dependencies.append(PythonDependency(
                name="cryptography",
                version_spec=">=41.0.0",
                purpose="Cryptographic operations",
                category="auth",
                php_equivalent="defuse/php-encryption"
            ))
        
        return DependencyGroup(
            name="Authentication & Security",
            description="Authentication, authorization, and security libraries",
            dependencies=dependencies,
            priority=1
        )
    
    def _plan_utility_dependencies(self, analysis_result: Dict[str, Any], 
                                  requirements: Dict[str, Any]) -> DependencyGroup:
        """Plan utility and helper dependencies."""
        dependencies = []
        
        # HTTP client
        if requirements.get('http_client'):
            dependencies.append(PythonDependency(
                name="httpx",
                version_spec=">=0.25.0",
                purpose="Async HTTP client",
                category="utils",
                alternatives=["aiohttp", "requests"],
                php_equivalent="guzzlehttp/guzzle"
            ))
        
        # File handling and uploads
        if requirements.get('file_uploads'):
            dependencies.append(PythonDependency(
                name="python-multipart",
                version_spec=">=0.0.6",
                purpose="File upload handling",
                category="utils"
            ))
        
        # Image processing
        if requirements.get('image_processing'):
            dependencies.append(PythonDependency(
                name="pillow",
                version_spec=">=10.0.0",
                purpose="Image processing and manipulation",
                category="utils",
                php_equivalent="intervention/image"
            ))
        
        # Excel processing
        if requirements.get('excel_processing'):
            dependencies.extend([
                PythonDependency(
                    name="openpyxl",
                    version_spec=">=3.1.0",
                    purpose="Excel file processing",
                    category="utils",
                    php_equivalent="phpoffice/phpspreadsheet"
                ),
                PythonDependency(
                    name="pandas",
                    version_spec=">=2.0.0",
                    purpose="Data manipulation and analysis",
                    category="utils",
                    alternatives=["polars"]
                )
            ])
        
        # PDF generation
        if requirements.get('pdf_generation'):
            dependencies.append(PythonDependency(
                name="reportlab",
                version_spec=">=4.0.0",
                purpose="PDF generation",
                category="utils",
                alternatives=["weasyprint"],
                php_equivalent="dompdf/dompdf"
            ))
        
        # Email
        if requirements.get('email'):
            dependencies.append(PythonDependency(
                name="fastapi-mail",
                version_spec=">=1.4.0",
                purpose="Email sending functionality",
                category="utils",
                alternatives=["emails"],
                php_equivalent="swiftmailer/swiftmailer"
            ))
        
        # Templates (if needed for server-side rendering)
        if requirements.get('templates'):
            dependencies.append(PythonDependency(
                name="jinja2",
                version_spec=">=3.1.0",
                purpose="Template engine",
                category="utils",
                php_equivalent="twig/twig"
            ))
        
        # Background tasks
        if requirements.get('background_tasks'):
            dependencies.extend([
                PythonDependency(
                    name="celery",
                    version_spec=">=5.3.0",
                    purpose="Distributed task queue",
                    category="utils",
                    alternatives=["rq", "arq"]
                ),
                PythonDependency(
                    name="redis",
                    version_spec=">=5.0.0",
                    purpose="Message broker for Celery",
                    category="utils"
                )
            ])
        
        # Date/time utilities
        dependencies.append(PythonDependency(
            name="python-dateutil",
            version_spec=">=2.8.0",
            purpose="Date and time utilities",
            category="utils",
            alternatives=["arrow", "pendulum"],
            php_equivalent="nesbot/carbon"
        ))
        
        # Logging
        if requirements.get('logging'):
            dependencies.append(PythonDependency(
                name="loguru",
                version_spec=">=0.7.0",
                purpose="Advanced logging",
                category="utils",
                alternatives=["structlog"],
                php_equivalent="monolog/monolog"
            ))
        
        return DependencyGroup(
            name="Utilities",
            description="Utility libraries for various functionality",
            dependencies=dependencies,
            priority=2
        )
    
    def _plan_development_dependencies(self, analysis_result: Dict[str, Any], 
                                     requirements: Dict[str, Any]) -> DependencyGroup:
        """Plan development and testing dependencies."""
        dependencies = []
        
        # Testing framework
        if requirements.get('testing'):
            dependencies.extend([
                PythonDependency(
                    name="pytest",
                    version_spec=">=7.4.0",
                    purpose="Testing framework",
                    category="dev",
                    php_equivalent="phpunit/phpunit"
                ),
                PythonDependency(
                    name="pytest-asyncio",
                    version_spec=">=0.21.0",
                    purpose="Async testing support",
                    category="dev"
                ),
                PythonDependency(
                    name="httpx",
                    version_spec=">=0.25.0",
                    purpose="HTTP client for testing APIs",
                    category="dev"
                ),
                PythonDependency(
                    name="pytest-cov",
                    version_spec=">=4.1.0",
                    purpose="Test coverage reporting",
                    category="dev"
                )
            ])
        
        # Code formatting and linting
        dependencies.extend([
            PythonDependency(
                name="black",
                version_spec=">=23.0.0",
                purpose="Code formatter",
                category="dev",
                php_equivalent="friendsofphp/php-cs-fixer"
            ),
            PythonDependency(
                name="isort",
                version_spec=">=5.12.0",
                purpose="Import sorting",
                category="dev"
            ),
            PythonDependency(
                name="flake8",
                version_spec=">=6.0.0",
                purpose="Code linting",
                category="dev",
                alternatives=["pylint", "ruff"]
            )
        ])
        
        # Type checking
        dependencies.append(PythonDependency(
            name="mypy",
            version_spec=">=1.5.0",
            purpose="Static type checking",
            category="dev",
            php_equivalent="phpstan/phpstan"
        ))
        
        # Pre-commit hooks
        dependencies.append(PythonDependency(
            name="pre-commit",
            version_spec=">=3.4.0",
            purpose="Git pre-commit hooks",
            category="dev"
        ))
        
        return DependencyGroup(
            name="Development Tools",
            description="Development, testing, and code quality tools",
            dependencies=dependencies,
            priority=2
        )
    
    def _plan_optional_dependencies(self, analysis_result: Dict[str, Any], 
                                   requirements: Dict[str, Any]) -> DependencyGroup:
        """Plan optional dependencies for enhanced functionality."""
        dependencies = []
        
        # Performance monitoring
        if requirements.get('monitoring'):
            dependencies.extend([
                PythonDependency(
                    name="prometheus-client",
                    version_spec=">=0.17.0",
                    purpose="Metrics collection",
                    category="optional"
                ),
                PythonDependency(
                    name="sentry-sdk[fastapi]",
                    version_spec=">=1.32.0",
                    purpose="Error tracking and performance monitoring",
                    category="optional"
                )
            ])
        
        # Enhanced validation
        dependencies.append(PythonDependency(
            name="email-validator",
            version_spec=">=2.0.0",
            purpose="Email validation for Pydantic",
            category="optional"
        ))
        
        # CORS middleware (usually included with FastAPI)
        dependencies.append(PythonDependency(
            name="python-multipart",
            version_spec=">=0.0.6",
            purpose="Form data and file upload support",
            category="optional",
            is_required=False
        ))
        
        # Advanced JSON handling
        dependencies.append(PythonDependency(
            name="orjson",
            version_spec=">=3.9.0",
            purpose="Fast JSON serialization",
            category="optional",
            alternatives=["ujson"]
        ))
        
        # Rate limiting
        dependencies.append(PythonDependency(
            name="slowapi",
            version_spec=">=0.1.9",
            purpose="Rate limiting for FastAPI",
            category="optional"
        ))
        
        return DependencyGroup(
            name="Optional Enhancements",
            description="Optional dependencies for enhanced functionality",
            dependencies=dependencies,
            optional=True,
            priority=3
        )
    
    def _get_core_fastapi_dependencies(self) -> Dict[str, Dict[str, Any]]:
        """Get core FastAPI dependencies."""
        return {
            "fastapi": {
                "version": ">=0.104.0",
                "purpose": "Web framework for building APIs",
                "required": True
            },
            "uvicorn[standard]": {
                "version": ">=0.24.0",
                "purpose": "ASGI server for running FastAPI",
                "required": True
            },
            "pydantic": {
                "version": ">=2.5.0",
                "purpose": "Data validation and serialization",
                "required": True
            },
            "python-multipart": {
                "version": ">=0.0.6",
                "purpose": "Form data and file upload support",
                "required": False
            }
        }
    
    def _get_database_dependencies(self) -> Dict[str, Dict[str, Any]]:
        """Get database-related dependencies."""
        return {
            "sqlalchemy": {"version": ">=2.0.0", "purpose": "SQL ORM"},
            "alembic": {"version": ">=1.12.0", "purpose": "Database migrations"},
            "mysql-connector-python": {"version": ">=8.1.0", "purpose": "MySQL driver"},
            "psycopg2-binary": {"version": ">=2.9.0", "purpose": "PostgreSQL driver"},
            "motor": {"version": ">=3.3.0", "purpose": "Async MongoDB driver"},
            "redis": {"version": ">=5.0.0", "purpose": "Redis client"}
        }
    
    def _get_authentication_dependencies(self) -> Dict[str, Dict[str, Any]]:
        """Get authentication-related dependencies."""
        return {
            "python-jose[cryptography]": {"version": ">=3.3.0", "purpose": "JWT handling"},
            "passlib[bcrypt]": {"version": ">=1.7.4", "purpose": "Password hashing"},
            "authlib": {"version": ">=1.2.0", "purpose": "OAuth implementation"},
            "cryptography": {"version": ">=41.0.0", "purpose": "Cryptographic operations"}
        }
    
    def _get_utility_dependencies(self) -> Dict[str, Dict[str, Any]]:
        """Get utility dependencies."""
        return {
            "httpx": {"version": ">=0.25.0", "purpose": "HTTP client"},
            "pillow": {"version": ">=10.0.0", "purpose": "Image processing"},
            "openpyxl": {"version": ">=3.1.0", "purpose": "Excel processing"},
            "reportlab": {"version": ">=4.0.0", "purpose": "PDF generation"},
            "fastapi-mail": {"version": ">=1.4.0", "purpose": "Email functionality"},
            "jinja2": {"version": ">=3.1.0", "purpose": "Template engine"},
            "celery": {"version": ">=5.3.0", "purpose": "Background tasks"},
            "python-dateutil": {"version": ">=2.8.0", "purpose": "Date utilities"},
            "loguru": {"version": ">=0.7.0", "purpose": "Logging"}
        }
    
    def _get_development_dependencies(self) -> Dict[str, Dict[str, Any]]:
        """Get development dependencies."""
        return {
            "pytest": {"version": ">=7.4.0", "purpose": "Testing framework"},
            "pytest-asyncio": {"version": ">=0.21.0", "purpose": "Async testing"},
            "pytest-cov": {"version": ">=4.1.0", "purpose": "Coverage reporting"},
            "black": {"version": ">=23.0.0", "purpose": "Code formatting"},
            "isort": {"version": ">=5.12.0", "purpose": "Import sorting"},
            "flake8": {"version": ">=6.0.0", "purpose": "Code linting"},
            "mypy": {"version": ">=1.5.0", "purpose": "Type checking"},
            "pre-commit": {"version": ">=3.4.0", "purpose": "Git hooks"}
        }
    
    def _get_optional_dependencies(self) -> Dict[str, Dict[str, Any]]:
        """Get optional dependencies."""
        return {
            "prometheus-client": {"version": ">=0.17.0", "purpose": "Metrics"},
            "sentry-sdk[fastapi]": {"version": ">=1.32.0", "purpose": "Error tracking"},
            "email-validator": {"version": ">=2.0.0", "purpose": "Email validation"},
            "orjson": {"version": ">=3.9.0", "purpose": "Fast JSON"},
            "slowapi": {"version": ">=0.1.9", "purpose": "Rate limiting"}
        }
    
    def _estimate_install_time(self, plan: DependencyPlan) -> str:
        """Estimate installation time for dependencies."""
        total_deps = plan.total_dependencies
        
        if total_deps <= 10:
            return "2-3 minutes"
        elif total_deps <= 20:
            return "3-5 minutes"
        elif total_deps <= 30:
            return "5-8 minutes"
        else:
            return "8-12 minutes"
    
    def _detect_potential_conflicts(self, plan: DependencyPlan) -> List[str]:
        """Detect potential dependency conflicts."""
        conflicts = []
        
        # Check for common conflict patterns
        all_deps = []
        for group in plan.groups:
            all_deps.extend(group.dependencies)
        
        dep_names = [dep.name for dep in all_deps]
        
        # Check for mutually exclusive packages
        exclusive_pairs = [
            ('mysql-connector-python', 'PyMySQL'),
            ('psycopg2-binary', 'asyncpg'),
            ('pymongo', 'motor'),
            ('requests', 'httpx'),
            ('orjson', 'ujson')
        ]
        
        for pkg1, pkg2 in exclusive_pairs:
            if pkg1 in dep_names and pkg2 in dep_names:
                conflicts.append(f"Consider choosing between {pkg1} and {pkg2}")
        
        # Check for version conflicts with common packages
        if 'pydantic' in dep_names:
            conflicts.append("Ensure all packages are compatible with Pydantic v2")
        
        return conflicts
    
    def _generate_migration_notes(self, analysis_result: Dict[str, Any], 
                                 plan: DependencyPlan) -> List[str]:
        """Generate migration notes for dependencies."""
        notes = []
        
        # PHP-specific migration notes
        dependency_analysis = analysis_result.get('dependency_analysis', {})
        php_mappings = dependency_analysis.get('python_mappings', {})
        
        if 'composer.json' in str(analysis_result):
            notes.append("Review composer.json for any missed dependencies")
        
        # Framework-specific notes
        project_info = analysis_result.get('project_info', {})
        framework = project_info.get('framework', 'vanilla')
        
        if framework == 'laravel':
            notes.append("Laravel's Eloquent ORM patterns can be replicated with SQLAlchemy")
            notes.append("Laravel's middleware system maps well to FastAPI dependencies")
        elif framework == 'symfony':
            notes.append("Symfony's dependency injection can be replaced with FastAPI's Depends")
            notes.append("Symfony's event system may need custom implementation")
        
        # Database migration notes
        database_analysis = analysis_result.get('database_analysis', {})
        if database_analysis.get('orm_framework') == 'eloquent':
            notes.append("Eloquent models should be converted to SQLAlchemy models")
            notes.append("Eloquent relationships map to SQLAlchemy relationships")
        
        # General notes
        notes.extend([
            "Install dependencies in a virtual environment",
            "Pin exact versions in production",
            "Review security advisories for all dependencies",
            "Consider using pip-tools for dependency management"
        ])
        
        return notes
    
    def _generate_requirements_files(self, plan: DependencyPlan) -> Dict[str, List[str]]:
        """Generate different requirements files."""
        files = {
            'requirements.txt': [],
            'requirements-dev.txt': [],
            'requirements-optional.txt': []
        }
        
        for group in plan.groups:
            for dep in group.dependencies:
                req_line = f"{dep.name}{dep.version_spec}"
                
                if dep.category == 'dev':
                    files['requirements-dev.txt'].append(req_line)
                elif group.optional or not dep.is_required:
                    files['requirements-optional.txt'].append(req_line)
                else:
                    files['requirements.txt'].append(req_line)
        
        # Remove empty files
        return {k: v for k, v in files.items() if v}
    
    def generate_pip_install_commands(self, plan: DependencyPlan) -> List[str]:
        """Generate pip install commands for each group."""
        commands = []
        
        for group in plan.groups:
            if not group.dependencies:
                continue
            
            deps = [f"{dep.name}{dep.version_spec}" for dep in group.dependencies]
            
            if group.optional:
                cmd = f"# Optional - {group.description}\n"
                cmd += f"pip install {' '.join(deps)}"
            else:
                cmd = f"# {group.description}\n"
                cmd += f"pip install {' '.join(deps)}"
            
            commands.append(cmd)
        
        return commands
    
    def get_dependency_summary(self, plan: DependencyPlan) -> Dict[str, Any]:
        """Get summary statistics for the dependency plan."""
        summary = {
            'total_dependencies': plan.total_dependencies,
            'groups': len(plan.groups),
            'required_dependencies': 0,
            'optional_dependencies': 0,
            'estimated_install_time': plan.estimated_install_time,
            'potential_conflicts': len(plan.potential_conflicts),
            'categories': {}
        }
        
        for group in plan.groups:
            for dep in group.dependencies:
                if dep.is_required and not group.optional:
                    summary['required_dependencies'] += 1
                else:
                    summary['optional_dependencies'] += 1
                
                category = dep.category
                if category not in summary['categories']:
                    summary['categories'][category] = 0
                summary['categories'][category] += 1
        
        return summary