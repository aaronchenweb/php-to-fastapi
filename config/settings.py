# config/settings.py
"""Enhanced configuration settings for PHP to FastAPI converter."""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from pathlib import Path

# Load .env file automatically
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # If python-dotenv is not installed, try to load .env manually
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    try:
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value.strip('"\'')
                    except ValueError:
                        continue


@dataclass
class LLMConfig:
    """LLM configuration settings."""
    provider: str = "gemini"  
    model: str = "gemini-1.5-pro"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    max_tokens: int = 4000
    temperature: float = 0.1
    timeout: int = 60
    retry_attempts: int = 3
    retry_delay: float = 2.0
    
    def __post_init__(self):
        """Initialize fields from environment variables."""
        if self.api_key is None:
            self.api_key = os.environ.get("LLM_API_KEY", "")
        if self.base_url is None:
            self.base_url = os.environ.get("LLM_BASE_URL", "")


@dataclass
class ConversionConfig:
    """Conversion behavior settings."""
    default_output_dir: str = "./fastapi_output"
    backup_original: bool = True
    preserve_comments: bool = True
    generate_tests: bool = True
    use_async: bool = True
    include_middleware: bool = True
    create_dockerfile: bool = True
    create_requirements_txt: bool = True
    create_readme: bool = True
    max_file_size_mb: int = 10  # Skip files larger than this
    max_files_to_analyze: int = 1000  # Limit for performance


@dataclass
class DetectionConfig:
    """Configuration for PHP project detection and analysis."""
    # API score thresholds per framework
    api_score_thresholds: Dict[str, float] = field(default_factory=lambda: {
        'laravel': 0.05,
        'codeigniter': 0.15,
        'symfony': 0.10,
        'slim': 0.25,
        'vanilla_php': 0.30,
        'custom': 0.20
    })
    
    # Maximum files to analyze for performance
    max_files_for_api_detection: int = 100
    max_files_for_parsing: int = 200
    
    # File size limits (in MB)
    max_file_size_for_analysis: int = 5
    
    # Whether to analyze vendor/third-party code
    analyze_vendor_code: bool = False
    analyze_test_files: bool = False


@dataclass
class SupportedFeatures:
    """Supported PHP features and frameworks."""
    frameworks: List[str] = field(default_factory=lambda: [
        "vanilla_php",
        "codeigniter", 
        "laravel",
        "symfony",
        "slim",
        "zend",
        "cakephp",
        "yii",
        "custom"
    ])
    
    php_versions: List[str] = field(default_factory=lambda: [
        "5.6", "7.0", "7.1", "7.2", "7.3", "7.4", 
        "8.0", "8.1", "8.2", "8.3", "8.4"
    ])
    
    databases: List[str] = field(default_factory=lambda: [
        "mysql", "postgresql", "sqlite", "mongodb", 
        "redis", "mariadb", "oracle", "mssql"
    ])
    
    orm_frameworks: List[str] = field(default_factory=lambda: [
        "eloquent", "doctrine", "propel", "paris", 
        "idiorm", "medoo", "none"
    ])


class Settings:
    """Enhanced settings class for the converter."""
    
    def __init__(self):
        self.llm = LLMConfig()
        self.conversion = ConversionConfig()
        self.detection = DetectionConfig()
        self.supported = SupportedFeatures()
        self._load_from_env()
    
    def _load_from_env(self):
        """Load settings from environment variables."""
        # LLM Settings
        self.llm.provider = os.getenv("LLM_PROVIDER", self.llm.provider)
        self.llm.model = os.getenv("LLM_MODEL", self.llm.model)
        self.llm.api_key = os.getenv("LLM_API_KEY", self.llm.api_key)
        self.llm.base_url = os.getenv("LLM_BASE_URL", self.llm.base_url)
        
        # Provider-specific environment variables
        if self.llm.provider.lower() == "gemini":
            self.llm.api_key = os.getenv("GEMINI_API_KEY", self.llm.api_key)
            if not self.llm.base_url or "generateContent" not in self.llm.base_url:
                self.llm.base_url = os.getenv("GEMINI_BASE_URL", 
                    "https://generativelanguage.googleapis.com/v1beta")
        elif self.llm.provider.lower() == "openai":
            self.llm.api_key = os.getenv("OPENAI_API_KEY", self.llm.api_key)
        elif self.llm.provider.lower() == "anthropic":
            self.llm.api_key = os.getenv("ANTHROPIC_API_KEY", self.llm.api_key)
        
        # Numeric settings with validation
        try:
            if os.getenv("LLM_MAX_TOKENS"):
                self.llm.max_tokens = int(os.getenv("LLM_MAX_TOKENS"))
            if os.getenv("LLM_TEMPERATURE"):
                self.llm.temperature = float(os.getenv("LLM_TEMPERATURE"))
            if os.getenv("LLM_TIMEOUT"):
                self.llm.timeout = int(os.getenv("LLM_TIMEOUT"))
        except (ValueError, TypeError):
            pass  # Keep defaults if invalid values
        
        # Conversion Settings
        self.conversion.default_output_dir = os.getenv(
            "DEFAULT_OUTPUT_DIR", self.conversion.default_output_dir
        )
        
        # Boolean settings
        bool_settings = [
            ("BACKUP_ORIGINAL", "backup_original"),
            ("GENERATE_TESTS", "generate_tests"),
            ("USE_ASYNC", "use_async"),
            ("INCLUDE_MIDDLEWARE", "include_middleware"),
            ("CREATE_DOCKERFILE", "create_dockerfile"),
            ("PRESERVE_COMMENTS", "preserve_comments")
        ]
        
        for env_key, attr_name in bool_settings:
            if os.getenv(env_key):
                setattr(self.conversion, attr_name, 
                       os.getenv(env_key).lower() in ("true", "1", "yes", "on"))
    
    def validate(self) -> bool:
        """Validate current settings."""
        if not self.llm.api_key:
            return False
        
        if self.llm.provider not in ["openai", "anthropic", "gemini"]:
            return False
        
        if not os.path.exists(os.path.dirname(self.conversion.default_output_dir)):
            try:
                os.makedirs(os.path.dirname(self.conversion.default_output_dir), exist_ok=True)
            except (OSError, PermissionError):
                return False
        
        return True
    
    def get_php_extensions(self) -> List[str]:
        """Get supported PHP file extensions."""
        return [".php", ".phtml", ".inc", ".php3", ".php4", ".php5", ".phps"]
    
    def get_ignore_patterns(self) -> List[str]:
        """Get comprehensive patterns to ignore during analysis."""
        base_patterns = [
            # Version control
            ".git/", ".svn/", ".hg/", ".bzr/",
            
            # Dependencies and packages
            "vendor/", "node_modules/", "bower_components/",
            "composer.phar", "composer.lock", "package-lock.json", "yarn.lock",
            
            # Environment and config
            ".env", ".env.*", "config.php", "config.inc.php",
            
            # Logs and temporary files
            "*.log", "logs/", "log/", "temp/", "tmp/", "cache/",
            
            # Build and compiled files
            "build/", "dist/", "*.min.js", "*.min.css", "*.map",
            
            # IDE and editor files
            ".vscode/", ".idea/", "*.swp", "*.swo", "*~", ".DS_Store",
            "Thumbs.db", "desktop.ini",
            
            # OS files
            "__MACOSX/", ".Spotlight-V100/", ".Trashes/",
            
            # Test coverage and reports
            "coverage/", "coverage.xml", "phpunit.xml", "phpunit.xml.dist",
            ".phpunit.result.cache",
            
            # Documentation
            "docs/", "documentation/", "*.md", "README*", "CHANGELOG*",
            "LICENSE*", "CONTRIBUTING*",
        ]
        
        # Framework-specific ignore patterns
        framework_patterns = self.get_framework_ignore_patterns()
        
        return base_patterns + framework_patterns
    
    def get_framework_ignore_patterns(self) -> List[str]:
        """Get framework-specific ignore patterns."""
        return [
            # Laravel
            "storage/logs/", "storage/cache/", "storage/framework/",
            "storage/app/", "storage/debugbar/",
            "bootstrap/cache/", "resources/lang/", "resources/views/",
            "database/migrations/", "database/seeds/", "database/factories/",
            "public/css/", "public/js/", "public/images/", "public/fonts/",
            "public/storage/", "public/mix-manifest.json",
            ".env.example", "artisan", "server.php", "webpack.mix.js",
            
            # CodeIgniter
            "system/", "application/logs/", "application/cache/",
            "application/views/", "assets/",
            
            # Symfony
            "var/cache/", "var/logs/", "var/sessions/",
            "public/bundles/", "translations/",
            
            # CakePHP
            "tmp/", "webroot/css/", "webroot/js/", "webroot/img/",
            
            # Zend/Laminas
            "data/cache/", "data/logs/", "public/css/", "public/js/",
            
            # WordPress (if analyzing WP sites)
            "wp-content/uploads/", "wp-content/cache/", 
            "wp-includes/", "wp-admin/",
        ]
    
    def get_api_relevant_patterns(self) -> List[str]:
        """Get patterns that indicate API-relevant files."""
        return [
            # Generic API patterns
            r".*[Aa]pi.*\.php$",
            r".*[Cc]ontroller.*\.php$", 
            r".*[Rr]oute.*\.php$",
            r".*[Ee]ndpoint.*\.php$",
            r".*[Hh]andler.*\.php$",
            r".*[Ss]ervice.*\.php$",
            r".*[Rr]esource.*\.php$",
            r".*[Mm]iddleware.*\.php$",
            r".*[Rr]equest.*\.php$",
            r".*[Rr]esponse.*\.php$",
            
            # Directory patterns
            r".*/api/.*\.php$",
            r".*/controllers?/.*\.php$",
            r".*/routes?/.*\.php$",
            r".*/endpoints?/.*\.php$",
            r".*/v\d+/.*\.php$",  # Versioned APIs
            r".*/rest/.*\.php$",
            r".*/graphql/.*\.php$",
            
            # Framework-specific
            r".*/Http/.*\.php$",  # Laravel
            r".*/Controllers?/.*\.php$",
            r"routes/api\.php$",
            r"routes/web\.php$",
        ]
    
    def get_framework_api_directories(self, framework: str) -> List[str]:
        """Get framework-specific directories that typically contain API code."""
        directories = {
            'laravel': [
                'app/Http/Controllers',
                'app/Http/Controllers/Api', 
                'app/Http/Controllers/API',
                'routes',
                'app/Http/Middleware',
                'app/Http/Requests',
                'app/Http/Resources',
                'app/Models',
                'app/Services',
                'app/Repositories'
            ],
            'codeigniter': [
                'application/controllers',
                'application/controllers/api',
                'controllers',
                'controllers/api',
                'application/models',
                'application/libraries'
            ],
            'symfony': [
                'src/Controller',
                'src/Controller/Api',
                'src/Entity',
                'src/Repository', 
                'src/Service',
                'config'
            ],
            'slim': [
                'src',
                'src/Controller',
                'src/Controllers',
                'src/Routes',
                'src/Middleware',
                'public'
            ],
            'vanilla_php': [
                'api',
                'includes',
                'controllers',
                'classes',
                'lib',
                'src'
            ]
        }
        
        return directories.get(framework, directories['vanilla_php'])
    
    def get_non_api_directories(self) -> List[str]:
        """Get directories that typically don't contain API code."""
        return [
            'vendor', 'node_modules', '.git', 'storage', 'cache', 'logs',
            'tmp', 'temp', 'tests', 'test', 'spec', 'docs', 'documentation',
            'resources/views', 'resources/lang', 'public/css', 'public/js',
            'public/images', 'public/fonts', 'assets', 'static', 'media',
            'uploads', 'files', 'backup', 'backups', 'migrations',
            'database/migrations', 'database/seeds', 'database/factories',
            'config', 'bootstrap', 'build', 'dist'
        ]
    
    def get_dependency_mappings(self) -> Dict[str, str]:
        """Get comprehensive PHP to Python dependency mappings."""
        return {
            # Core PHP to Python
            "php": "python",
            
            # Database Drivers
            "mysqli": "mysql-connector-python",
            "pdo": "sqlalchemy",
            "pdo_mysql": "pymysql",
            "pdo_pgsql": "psycopg2",
            "pdo_sqlite": "sqlite3",
            "mongodb/mongodb": "pymongo",
            "predis/predis": "redis",
            "redis": "redis",
            
            # HTTP/Web Clients
            "guzzlehttp/guzzle": "httpx",
            "curl": "httpx",
            "buzz/buzz": "requests",
            "kriswallsmith/buzz": "requests",
            
            # JSON/Serialization
            "jms/serializer": "pydantic",
            "symfony/serializer": "pydantic",
            
            # Logging
            "monolog/monolog": "loguru",
            "psr/log": "logging",
            
            # Date/Time
            "nesbot/carbon": "arrow",
            "carbon": "arrow",
            "datetime": "datetime",
            
            # Testing
            "phpunit/phpunit": "pytest",
            "mockery/mockery": "unittest.mock",
            "faker": "faker",
            "fzaninotto/faker": "faker",
            
            # Validation
            "respect/validation": "pydantic",
            "illuminate/validation": "pydantic",
            "symfony/validator": "cerberus",
            
            # Template Engines
            "twig/twig": "jinja2",
            "smarty/smarty": "jinja2",
            
            # Authentication/JWT
            "firebase/php-jwt": "pyjwt",
            "lcobucci/jwt": "pyjwt",
            "tymon/jwt-auth": "pyjwt",
            
            # Image Processing
            "intervention/image": "pillow",
            "imagine/imagine": "pillow",
            
            # File Handling
            "league/flysystem": "boto3",
            "symfony/filesystem": "pathlib",
            
            # Caching
            "doctrine/cache": "redis",
            "symfony/cache": "redis",
            "predis/predis": "redis",
            
            # Queue/Jobs
            "bernard/bernard": "celery",
            "php-resque/php-resque": "celery",
            
            # Configuration
            "vlucas/phpdotenv": "python-dotenv",
            "symfony/dotenv": "python-dotenv",
            
            # Utilities
            "ramsey/uuid": "uuid",
            "symfony/console": "click",
            "league/csv": "pandas",
            "maatwebsite/excel": "openpyxl",
            
            # Laravel Specific
            "laravel/framework": "fastapi",
            "illuminate/database": "sqlalchemy",
            "illuminate/http": "fastapi",
            "illuminate/routing": "fastapi",
            "illuminate/container": "dependency-injector",
            
            # Symfony Specific  
            "symfony/http-foundation": "fastapi",
            "symfony/routing": "fastapi",
            "symfony/dependency-injection": "dependency-injector",
            "doctrine/orm": "sqlalchemy",
            
            # API Documentation
            "zircote/swagger-php": "fastapi",  # FastAPI has built-in OpenAPI
            "cebe/openapi": "fastapi",
            
            # Email
            "swiftmailer/swiftmailer": "smtplib",
            "phpmailer/phpmailer": "smtplib",
            "symfony/mailer": "fastapi-mail",
            
            # Encryption
            "defuse/php-encryption": "cryptography",
            "paragonie/halite": "cryptography",
            
            # API Rate Limiting
            "graham-campbell/throttle": "slowapi",
            
            # CORS
            "fruitcake/laravel-cors": "fastapi-cors",
            "nelmio/cors-bundle": "fastapi-cors"
        }
    
    def get_fastapi_package_recommendations(self) -> Dict[str, List[str]]:
        """Get recommended FastAPI packages for different use cases."""
        return {
            "core": [
                "fastapi>=0.104.0",
                "uvicorn[standard]>=0.24.0",
                "pydantic>=2.5.0"
            ],
            "database": [
                "sqlalchemy>=2.0.0",
                "alembic>=1.13.0",  # For migrations
                "asyncpg>=0.29.0",  # For PostgreSQL
                "aiomysql>=0.2.0",  # For MySQL
                "aiosqlite>=0.19.0"  # For SQLite
            ],
            "authentication": [
                "python-jose[cryptography]>=3.3.0",
                "passlib[bcrypt]>=1.7.4",
                "python-multipart>=0.0.6"
            ],
            "http_client": [
                "httpx>=0.25.0",
                "aiohttp>=3.9.0"
            ],
            "validation": [
                "email-validator>=2.1.0",
                "pydantic-settings>=2.1.0"
            ],
            "testing": [
                "pytest>=7.4.0",
                "pytest-asyncio>=0.21.0",
                "httpx>=0.25.0"  # For test client
            ],
            "utilities": [
                "python-dotenv>=1.0.0",
                "loguru>=0.7.0",
                "arrow>=1.3.0"
            ],
            "middleware": [
                "slowapi>=0.1.9",  # Rate limiting
                "fastapi-cors>=0.1.0"  # CORS
            ]
        }
    
    def should_ignore_file(self, file_path: str, project_root: str) -> bool:
        """Check if a file should be ignored based on patterns."""
        rel_path = os.path.relpath(file_path, project_root)
        
        # Check file size
        try:
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if file_size_mb > self.conversion.max_file_size_mb:
                return True
        except (OSError, FileNotFoundError):
            return True
        
        # Check against ignore patterns
        ignore_patterns = self.get_ignore_patterns()
        
        for pattern in ignore_patterns:
            if pattern.endswith('/'):
                # Directory pattern
                if f'/{pattern}' in f'/{rel_path}/' or rel_path.startswith(pattern):
                    return True
            elif '*' in pattern:
                # Wildcard pattern
                import fnmatch
                if fnmatch.fnmatch(rel_path, pattern):
                    return True
            else:
                # Exact match or substring
                if pattern in rel_path or rel_path.endswith(pattern):
                    return True
        
        return False
    
    def is_api_relevant_file(self, file_path: str, project_root: str) -> bool:
        """Check if a file is likely to contain API-relevant code."""
        rel_path = os.path.relpath(file_path, project_root)
        
        # Check against API relevant patterns
        api_patterns = self.get_api_relevant_patterns()
        
        import re
        for pattern in api_patterns:
            if re.search(pattern, rel_path, re.IGNORECASE):
                return True
        
        # Check if in API-relevant directory
        non_api_dirs = self.get_non_api_directories()
        for non_api_dir in non_api_dirs:
            if f'/{non_api_dir}/' in f'/{rel_path}/' or rel_path.startswith(f'{non_api_dir}/'):
                return False
        
        return True
    
    def get_debug_info(self) -> Dict[str, any]:
        """Get debug information about current settings."""
        return {
            "llm_provider": self.llm.provider,
            "llm_model": self.llm.model,
            "api_key_set": bool(self.llm.api_key),
            "api_key_length": len(self.llm.api_key) if self.llm.api_key else 0,
            "output_dir": self.conversion.default_output_dir,
            "ignore_patterns_count": len(self.get_ignore_patterns()),
            "dependency_mappings_count": len(self.get_dependency_mappings()),
            "supported_frameworks": self.supported.frameworks,
            "api_score_thresholds": self.detection.api_score_thresholds
        }