"""Generates configuration files for FastAPI application."""

import os
from typing import Dict, List, Any, Optional
from .shared import GeneratedFile 


class ConfigGenerator:
    """Generates configuration files for FastAPI application."""
    
    def __init__(self):
        self.default_config = {
            'PROJECT_NAME': 'FastAPI Application',
            'VERSION': '1.0.0',
            'DESCRIPTION': 'API converted from PHP',
            'API_V1_STR': '/api/v1',
            'DEBUG': False,
            'PORT': 8000,
            'HOST': '0.0.0.0',
            'SECRET_KEY': 'your-secret-key-change-in-production',
            'DATABASE_URL': 'sqlite:///./app.db',
            'CORS_ORIGINS': '["http://localhost:3000", "http://localhost:8080"]',
            'ACCESS_TOKEN_EXPIRE_MINUTES': 30,
            'JWT_ALGORITHM': 'HS256',
            'ENVIRONMENT': 'development'
        }
    
    def generate_config_files(self, 
                            analysis_result: Dict[str, Any], 
                            planning_result: Dict[str, Any]) -> List[GeneratedFile]:
        """Generate all configuration files."""
        files = []
        
        # Generate core config
        config_content = self._generate_core_config(analysis_result, planning_result)
        files.append(GeneratedFile(
            path="app/core/config.py",
            content=config_content,
            file_type="python",
            description="Core application configuration"
        ))
        
        # Generate security config
        security_content = self._generate_security_config(analysis_result, planning_result)
        files.append(GeneratedFile(
            path="app/core/security.py",
            content=security_content,
            file_type="python",
            description="Security and authentication configuration"
        ))
        
        # Generate core __init__.py
        core_init_content = self._generate_core_init()
        files.append(GeneratedFile(
            path="app/core/__init__.py",
            content=core_init_content,
            file_type="python",
            description="Core package initialization"
        ))
        
        # Generate .env file
        env_content = self._generate_env_file(analysis_result, planning_result)
        files.append(GeneratedFile(
            path=".env",
            content=env_content,
            file_type="config",
            description="Environment variables configuration"
        ))
        
        # Generate .env.example file
        env_example_content = self._generate_env_example_file(analysis_result, planning_result)
        files.append(GeneratedFile(
            path=".env.example",
            content=env_example_content,
            file_type="config",
            description="Environment variables template"
        ))
        
        # Generate Dockerfile
        dockerfile_content = self._generate_dockerfile(analysis_result, planning_result)
        files.append(GeneratedFile(
            path="Dockerfile",
            content=dockerfile_content,
            file_type="config",
            description="Docker configuration"
        ))
        
        # Generate docker-compose.yml
        docker_compose_content = self._generate_docker_compose(analysis_result, planning_result)
        files.append(GeneratedFile(
            path="docker-compose.yml",
            content=docker_compose_content,
            file_type="config",
            description="Docker Compose configuration"
        ))
        
        # Generate .dockerignore
        dockerignore_content = self._generate_dockerignore()
        files.append(GeneratedFile(
            path=".dockerignore",
            content=dockerignore_content,
            file_type="config",
            description="Docker ignore file"
        ))
        
        # Generate .gitignore
        gitignore_content = self._generate_gitignore()
        files.append(GeneratedFile(
            path=".gitignore",
            content=gitignore_content,
            file_type="config",
            description="Git ignore file"
        ))
        
        # Generate README.md
        readme_content = self._generate_readme(analysis_result, planning_result)
        files.append(GeneratedFile(
            path="README.md",
            content=readme_content,
            file_type="markdown",
            description="Project README file"
        ))
        
        # Generate requirements.txt
        requirements_content = self._generate_requirements(analysis_result, planning_result)
        files.append(GeneratedFile(
            path="requirements.txt",
            content=requirements_content,
            file_type="text",
            description="Python dependencies"
        ))
        
        # Generate Alembic configuration if database is used
        database_analysis = analysis_result.get('database_analysis', {})
        if database_analysis.get('total_connections', 0) > 0:
            alembic_files = self._generate_alembic_config(analysis_result, planning_result)
            files.extend(alembic_files)
        
        return files
    
    def _generate_core_config(self, 
                            analysis_result: Dict[str, Any], 
                            planning_result: Dict[str, Any]) -> str:
        """Generate core configuration file."""
        project_info = analysis_result.get('project_info', {})
        database_analysis = analysis_result.get('database_analysis', {})
        endpoint_analysis = analysis_result.get('endpoint_analysis', {})
        
        # Determine database URL pattern
        db_connections = database_analysis.get('connections', [])
        db_type = 'sqlite'
        if db_connections:
            db_type = db_connections[0].get('type', 'sqlite')
        
        # Check for authentication requirements
        auth_methods = endpoint_analysis.get('authentication_methods', [])
        needs_jwt = any('jwt' in method.lower() or 'token' in method.lower() for method in auth_methods)
        
        # Get project name from analysis or use default
        project_name = project_info.get('name', self.default_config['PROJECT_NAME'])
        
        # JWT configuration section
        jwt_config = ''
        if needs_jwt:
            jwt_config = '''ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    JWT_SECRET_KEY: str = Field(env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")'''
        else:
            jwt_config = '# JWT_SECRET_KEY: str = Field(env="JWT_SECRET_KEY")  # Uncomment if using JWT'
        
        template = f'''"""
Core application configuration.
Generated from PHP project analysis.
"""

import os
from typing import List, Optional, Union
from pydantic import AnyHttpUrl, BaseSettings, validator, Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Project Information
    PROJECT_NAME: str = Field(default="{project_name}", env="PROJECT_NAME")
    VERSION: str = Field(default="1.0.0", env="VERSION")
    DESCRIPTION: str = Field(default="API converted from PHP", env="DESCRIPTION")
    
    # API Configuration
    API_V1_STR: str = Field(default="/api/v1", env="API_V1_STR")
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Server Configuration
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    # Security
    SECRET_KEY: str = Field(env="SECRET_KEY")
    
    # Database Configuration
    DATABASE_URL: str = Field(
        default="sqlite:///./app.db",
        env="DATABASE_URL",
        description="Database connection URL"
    )
    
    # CORS Configuration
    CORS_ORIGINS: List[AnyHttpUrl] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="CORS_ORIGINS"
    )
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """Parse CORS origins from environment variable."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Authentication Configuration
    {jwt_config}
    
    # Email Configuration (if needed)
    # SMTP_TLS: bool = Field(default=True, env="SMTP_TLS")
    # SMTP_PORT: Optional[int] = Field(default=None, env="SMTP_PORT")
    # SMTP_HOST: Optional[str] = Field(default=None, env="SMTP_HOST")
    # SMTP_USER: Optional[str] = Field(default=None, env="SMTP_USER")
    # SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    
    # Redis Configuration (if needed)
    # REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # File Upload Configuration
    UPLOAD_DIR: str = Field(default="./uploads", env="UPLOAD_DIR")
    MAX_UPLOAD_SIZE: int = Field(default=10 * 1024 * 1024, env="MAX_UPLOAD_SIZE")  # 10MB
    
    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # Pagination Defaults
    DEFAULT_PAGE_SIZE: int = Field(default=20, env="DEFAULT_PAGE_SIZE")
    MAX_PAGE_SIZE: int = Field(default=100, env="MAX_PAGE_SIZE")
    
    @validator("SECRET_KEY", pre=True)
    def validate_secret_key(cls, v: str) -> str:
        """Validate secret key is set."""
        if not v:
            raise ValueError("SECRET_KEY must be set")
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
    
    @validator("DATABASE_URL", pre=True)
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL format."""
        if not v:
            raise ValueError("DATABASE_URL must be set")
        return v
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() == "development"
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        validate_assignment = True


# Global settings instance
settings = Settings()
'''
        
        return template.strip()
    
    def _generate_security_config(self, 
                                analysis_result: Dict[str, Any], 
                                planning_result: Dict[str, Any]) -> str:
        """Generate security configuration."""
        endpoint_analysis = analysis_result.get('endpoint_analysis', {})
        auth_methods = endpoint_analysis.get('authentication_methods', [])
        needs_jwt = any('jwt' in method.lower() or 'token' in method.lower() for method in auth_methods)
        
        # JWT imports
        jwt_imports = ''
        if needs_jwt:
            jwt_imports = 'from jose import JWTError, jwt'
        else:
            jwt_imports = '# from jose import JWTError, jwt  # Uncomment if using JWT'
        
        # JWT token creation
        jwt_create_token = ''
        if needs_jwt:
            jwt_create_token = '''if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt'''
        else:
            jwt_create_token = '''# JWT token creation logic goes here
    # Uncomment and implement if using JWT authentication
    pass'''
        
        # JWT token verification
        jwt_verify_token = ''
        if needs_jwt:
            jwt_verify_token = '''try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload.get("sub")
    except JWTError:
        return None'''
        else:
            jwt_verify_token = '''# JWT token verification logic goes here
    # Uncomment and implement if using JWT authentication
    return None'''
        
        template = f'''"""
Security utilities and authentication.
Generated from PHP authentication analysis.
"""

from datetime import datetime, timedelta
from typing import Any, Union, Optional

{jwt_imports}
from passlib.context import CryptContext
from passlib.hash import bcrypt

from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    subject: Union[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create access token for authentication."""
    {jwt_create_token}


def verify_token(token: str) -> Optional[str]:
    """Verify and decode access token."""
    {jwt_verify_token}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def generate_password_reset_token(email: str) -> str:
    """Generate password reset token."""
    delta = timedelta(hours=24)  # Token valid for 24 hours
    return create_access_token(subject=email, expires_delta=delta)


def verify_password_reset_token(token: str) -> Optional[str]:
    """Verify password reset token and return email."""
    return verify_token(token)


def create_api_key() -> str:
    """Generate API key for service authentication."""
    import secrets
    return secrets.token_urlsafe(32)


def verify_api_key(api_key: str) -> bool:
    """Verify API key (implement your logic here)."""
    # TODO: Implement API key verification logic
    # This could involve database lookup, cache check, etc.
    return False


# Security headers
SECURITY_HEADERS = {{
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Referrer-Policy": "strict-origin-when-cross-origin"
}}


def add_security_headers(response):
    """Add security headers to response."""
    for header, value in SECURITY_HEADERS.items():
        response.headers[header] = value
    return response
'''
        
        return template.strip()
    
    def _generate_core_init(self) -> str:
        """Generate core package initialization."""
        template = '''"""
Core package containing configuration and security utilities.
"""

from .config import settings
from .security import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token
)

__all__ = [
    "settings",
    "verify_password", 
    "get_password_hash",
    "create_access_token",
    "verify_token"
]
'''
        
        return template.strip()
    
    def _generate_env_file(self, 
                          analysis_result: Dict[str, Any], 
                          planning_result: Dict[str, Any]) -> str:
        """Generate .env file with environment variables."""
        project_info = analysis_result.get('project_info', {})
        database_analysis = analysis_result.get('database_analysis', {})
        endpoint_analysis = analysis_result.get('endpoint_analysis', {})
        
        # Determine database type
        db_connections = database_analysis.get('connections', [])
        db_type = 'sqlite'
        db_url = 'sqlite:///./app.db'
        
        if db_connections:
            connection = db_connections[0]
            db_type = connection.get('type', 'sqlite')
            
            if db_type == 'mysql':
                db_url = 'mysql+pymysql://user:password@localhost/dbname'
            elif db_type == 'postgresql':
                db_url = 'postgresql://user:password@localhost/dbname'
            elif db_type == 'mongodb':
                db_url = 'mongodb://localhost:27017/dbname'
        
        # Check for authentication
        auth_methods = endpoint_analysis.get('authentication_methods', [])
        needs_jwt = any('jwt' in method.lower() or 'token' in method.lower() for method in auth_methods)
        
        # Get project name
        project_name = project_info.get('name', 'FastAPI Application')
        
        lines = [
            "# Environment Configuration",
            "# This file contains actual values - do not commit to version control!",
            "",
            "# Project Configuration",
            f'PROJECT_NAME="{project_name}"',
            'VERSION="1.0.0"',
            'DESCRIPTION="API converted from PHP"',
            "",
            "# Environment",
            'ENVIRONMENT="development"',
            'DEBUG=true',
            "",
            "# Server Configuration", 
            'HOST="0.0.0.0"',
            'PORT=8000',
            "",
            "# Security",
            'SECRET_KEY="your-super-secret-key-change-this-in-production-minimum-32-characters-long"',
            "",
            "# Database Configuration",
            f'DATABASE_URL="{db_url}"',
            "",
            "# CORS Configuration",
            'CORS_ORIGINS="http://localhost:3000,http://localhost:8080"',
            ""
        ]
        
        if needs_jwt:
            lines.extend([
                "# JWT Authentication",
                'JWT_SECRET_KEY="your-jwt-secret-key-change-this-in-production-minimum-32-characters"',
                'JWT_ALGORITHM="HS256"',
                'ACCESS_TOKEN_EXPIRE_MINUTES=30',
                ""
            ])
        
        lines.extend([
            "# File Upload Configuration",
            'UPLOAD_DIR="./uploads"',
            'MAX_UPLOAD_SIZE=10485760  # 10MB in bytes',
            "",
            "# Logging Configuration",
            'LOG_LEVEL="INFO"',
            '# LOG_FILE="./logs/app.log"',
            "",
            "# Pagination",
            'DEFAULT_PAGE_SIZE=20',
            'MAX_PAGE_SIZE=100',
        ])
        
        return '\n'.join(lines)
    
    def _generate_env_example_file(self, 
                                  analysis_result: Dict[str, Any], 
                                  planning_result: Dict[str, Any]) -> str:
        """Generate .env.example file template."""
        project_info = analysis_result.get('project_info', {})
        database_analysis = analysis_result.get('database_analysis', {})
        endpoint_analysis = analysis_result.get('endpoint_analysis', {})
        
        # Determine database type
        db_connections = database_analysis.get('connections', [])
        db_type = 'sqlite'
        db_url = 'sqlite:///./app.db'
        
        if db_connections:
            connection = db_connections[0]
            db_type = connection.get('type', 'sqlite')
            
            if db_type == 'mysql':
                db_url = 'mysql+pymysql://username:password@localhost/database_name'
            elif db_type == 'postgresql':
                db_url = 'postgresql://username:password@localhost/database_name'
            elif db_type == 'mongodb':
                db_url = 'mongodb://localhost:27017/database_name'
        
        # Check for authentication
        auth_methods = endpoint_analysis.get('authentication_methods', [])
        needs_jwt = any('jwt' in method.lower() or 'token' in method.lower() for method in auth_methods)
        
        lines = [
            "# Environment Configuration Template",
            "# Copy this file to .env and update the values",
            "# Do not commit .env to version control!",
            "",
            "# Project Configuration",
            'PROJECT_NAME="Your FastAPI Application"',
            'VERSION="1.0.0"',
            'DESCRIPTION="Your API description"',
            "",
            "# Environment",
            'ENVIRONMENT="development"  # development, staging, production',
            'DEBUG=true',
            "",
            "# Server Configuration", 
            'HOST="0.0.0.0"',
            'PORT=8000',
            "",
            "# Security (REQUIRED - Generate strong random keys)",
            'SECRET_KEY="generate-a-random-secret-key-at-least-32-characters-long"',
            "",
            "# Database Configuration",
            f'DATABASE_URL="{db_url}"',
            "",
            "# CORS Configuration",
            'CORS_ORIGINS="http://localhost:3000,http://localhost:8080"',
            ""
        ]
        
        if needs_jwt:
            lines.extend([
                "# JWT Authentication (REQUIRED if using JWT)",
                'JWT_SECRET_KEY="generate-another-random-secret-key-for-jwt-tokens"',
                'JWT_ALGORITHM="HS256"',
                'ACCESS_TOKEN_EXPIRE_MINUTES=30',
                ""
            ])
        
        lines.extend([
            "# File Upload Configuration",
            'UPLOAD_DIR="./uploads"',
            'MAX_UPLOAD_SIZE=10485760  # 10MB in bytes',
            "",
            "# Logging Configuration",
            'LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL',
            '# LOG_FILE="./logs/app.log"',
            "",
            "# Pagination",
            'DEFAULT_PAGE_SIZE=20',
            'MAX_PAGE_SIZE=100',
            "",
            "# Email Configuration (optional)",
            '# SMTP_TLS=true',
            '# SMTP_PORT=587',
            '# SMTP_HOST="smtp.gmail.com"',
            '# SMTP_USER="your-email@gmail.com"',
            '# SMTP_PASSWORD="your-app-password"',
            "",
            "# Redis Configuration (optional)",
            '# REDIS_URL="redis://localhost:6379"',
        ])
        
        return '\n'.join(lines)
    
    def _generate_requirements(self, 
                             analysis_result: Dict[str, Any], 
                             planning_result: Dict[str, Any]) -> str:
        """Generate requirements.txt file."""
        database_analysis = analysis_result.get('database_analysis', {})
        endpoint_analysis = analysis_result.get('endpoint_analysis', {})
        
        # Base requirements
        requirements = [
            "# FastAPI and core dependencies",
            "fastapi>=0.104.1",
            "uvicorn[standard]>=0.24.0",
            "pydantic>=2.5.0",
            "pydantic-settings>=2.1.0",
            "",
            "# Password hashing",
            "passlib[bcrypt]>=1.7.4",
            "",
            "# CORS middleware",
            "python-multipart>=0.0.6",
            "",
        ]
        
        # Add JWT if needed
        auth_methods = endpoint_analysis.get('authentication_methods', [])
        needs_jwt = any('jwt' in method.lower() or 'token' in method.lower() for method in auth_methods)
        
        if needs_jwt:
            requirements.extend([
                "# JWT Authentication",
                "python-jose[cryptography]>=3.3.0",
                "",
            ])
        
        # Add database dependencies
        db_connections = database_analysis.get('connections', [])
        if db_connections:
            requirements.append("# Database dependencies")
            requirements.append("sqlalchemy>=2.0.23")
            requirements.append("alembic>=1.13.0")
            
            db_types = {conn.get('type', 'sqlite') for conn in db_connections}
            
            if 'postgresql' in db_types:
                requirements.append("psycopg2-binary>=2.9.9")
            if 'mysql' in db_types:
                requirements.append("pymysql>=1.1.0")
            if 'sqlite' in db_types:
                requirements.append("# SQLite is included with Python")
            
            requirements.append("")
        
        # Add optional dependencies
        requirements.extend([
            "# Optional dependencies",
            "# redis>=5.0.1  # For caching",
            "# celery>=5.3.4  # For background tasks",
            "# python-dotenv>=1.0.0  # Already included in pydantic-settings",
            "",
            "# Development dependencies (install with: pip install -r requirements-dev.txt)",
            "# pytest>=7.4.3",
            "# pytest-asyncio>=0.21.1",
            "# httpx>=0.25.2  # For testing",
            "# black>=23.11.0  # Code formatting",
            "# flake8>=6.1.0  # Linting",
            "# mypy>=1.7.1  # Type checking",
        ])
        
        return '\n'.join(requirements)
    
    def _generate_readme(self, 
                        analysis_result: Dict[str, Any], 
                        planning_result: Dict[str, Any]) -> str:
        """Generate README.md file."""
        project_info = analysis_result.get('project_info', {})
        project_name = project_info.get('name', 'FastAPI Application')
        project_slug = project_name.lower().replace(' ', '-')
        
        content = f"""# {project_name}

This FastAPI application was automatically converted from a PHP web API project.

## Features

- **FastAPI Framework**: Modern, fast, and intuitive API framework
- **Automatic API Documentation**: Interactive docs at `/docs` and `/redoc`
- **Authentication**: JWT-based authentication system
- **Database Integration**: SQLAlchemy ORM with Alembic migrations
- **Docker Support**: Container-ready with Docker and Docker Compose
- **Environment Configuration**: Flexible configuration with environment variables

## Quick Start

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository** (if applicable):
   ```bash
   git clone <repository-url>
   cd {project_slug}
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run database migrations** (if using a database):
   ```bash
   alembic upgrade head
   ```

6. **Start the development server**:
   ```bash
   uvicorn main:app --reload
   ```

The API will be available at `http://localhost:8000`

## API Documentation

- **Interactive API docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

## Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Build and run the application
docker-compose up --build

# Run in background
docker-compose up -d --build
```

### Using Docker directly

```bash
# Build the image
docker build -t {project_slug} .

# Run the container
docker run -p 8000:8000 --env-file .env {project_slug}
```

## Configuration

The application uses environment variables for configuration. See `.env.example` for all available options.

### Required Environment Variables

- `SECRET_KEY`: Secret key for security (minimum 32 characters)
- `DATABASE_URL`: Database connection string
- `JWT_SECRET_KEY`: Secret key for JWT tokens (if using authentication)

### Optional Environment Variables

- `DEBUG`: Enable debug mode (default: false)
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `LOG_LEVEL`: Logging level (default: INFO)

## Database

This application uses SQLAlchemy for database operations and Alembic for migrations.

### Running Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migrations
alembic downgrade -1
```

## Development

### Code Style

This project follows Python best practices:

- **Code formatting**: Use `black` for code formatting
- **Linting**: Use `flake8` for linting
- **Type checking**: Use `mypy` for type checking

```bash
# Install development dependencies
pip install black flake8 mypy pytest

# Format code
black .

# Lint code
flake8 .

# Type check
mypy .
```

### Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# Run tests with coverage
pytest --cov=app
```

## Project Structure

```
{project_slug}/
├── app/
│   ├── core/           # Core configuration and security
│   ├── models/         # Database models
│   ├── routers/        # API route handlers
│   ├── schemas/        # Pydantic schemas
│   └── __init__.py
├── alembic/            # Database migrations
├── uploads/            # File uploads (created at runtime)
├── .env.example        # Environment variables template
├── .gitignore         # Git ignore rules
├── docker-compose.yml # Docker Compose configuration
├── Dockerfile         # Docker configuration
├── main.py            # Application entry point
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

## Migration from PHP

This FastAPI application was converted from a PHP web API. Key changes include:

- **Language**: PHP → Python
- **Framework**: Custom PHP → FastAPI
- **Database**: Direct SQL → SQLAlchemy ORM
- **Authentication**: PHP sessions → JWT tokens
- **Documentation**: Manual → Automatic OpenAPI/Swagger

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions and support, please open an issue in the project repository.
"""
        
        return content.strip()
    
    def _generate_dockerfile(self, 
                           analysis_result: Dict[str, Any], 
                           planning_result: Dict[str, Any]) -> str:
        """Generate Dockerfile."""
        content = """# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \\
    PYTHONUNBUFFERED=1 \\
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update \\
    && apt-get install -y --no-install-recommends \\
        gcc \\
        libpq-dev \\
        curl \\
        && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \\
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory and set permissions
RUN mkdir -p uploads logs \\
    && chmod 755 uploads logs

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser \\
    && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
        
        return content.strip()
    
    def _generate_dockerignore(self) -> str:
        """Generate .dockerignore file."""
        content = """# Git
.git
.gitignore

# Python
__pycache__
*.pyc
*.pyo
*.pyd
.Python
pip-log.txt
pip-delete-this-directory.txt
.pytest_cache

# Virtual environments
venv/
env/
.venv/
.env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Environment files
.env
.env.local
.env.example

# Documentation
README.md
CHANGELOG.md
docs/

# Testing
.coverage
htmlcov/
.tox/
.cache
nosetests.xml
coverage.xml

# Build artifacts
build/
dist/
*.egg-info/

# Temporary files
tmp/
temp/
*.tmp
*.temp

# Backups
*.bak
*.backup
"""
        
        return content.strip()
    
    def _generate_gitignore(self) -> str:
        """Generate .gitignore file."""
        content = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Environment variables
.env
.env.local
.env.*.local

# Virtual environments
venv/
env/
.venv/
.env/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite
*.sqlite3

# Uploads
uploads/

# Temporary files
*.tmp
*.temp
temp/
tmp/

# Backup files
*.bak
*.backup

# Local configuration
local_settings.py
"""
        
        return content.strip()
    
    def _generate_docker_compose(self, 
                                analysis_result: Dict[str, Any], 
                                planning_result: Dict[str, Any]) -> str:
        """Generate docker-compose.yml."""
        database_analysis = analysis_result.get('database_analysis', {})
        db_connections = database_analysis.get('connections', [])
        
        # Determine if we need a database service
        needs_postgres = any(conn.get('type') == 'postgresql' for conn in db_connections)
        needs_mysql = any(conn.get('type') == 'mysql' for conn in db_connections)
        needs_redis = any(conn.get('type') == 'redis' for conn in db_connections)
        
        content = """version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=${DEBUG}
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    depends_on:"""
        
        services = []
        if needs_postgres:
            services.append('      - postgres')
        if needs_mysql:
            services.append('      - mysql')
        if needs_redis:
            services.append('      - redis')
        
        if services:
            content += '\n' + '\n'.join(services)
        else:
            content += '\n      []  # No external services needed'
        
        # Add database services
        if needs_postgres:
            content += """

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-password}
      POSTGRES_DB: ${DB_NAME:-fastapi_db}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-postgres}"]
      interval: 30s
      timeout: 10s
      retries: 5"""
        
        if needs_mysql:
            content += """

  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_PASSWORD:-password}
      MYSQL_DATABASE: ${DB_NAME:-fastapi_db}
      MYSQL_USER: ${DB_USER:-user}
      MYSQL_PASSWORD: ${DB_PASSWORD:-password}
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 30s
      timeout: 10s
      retries: 5"""
        
        if needs_redis:
            content += """

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5"""
        
        # Add volumes section
        if needs_postgres or needs_mysql or needs_redis:
            content += """

volumes:"""
            
            if needs_postgres:
                content += """
  postgres_data:"""
            if needs_mysql:
                content += """
  mysql_data:"""
            if needs_redis:
                content += """
  redis_data:"""
        
        return content.strip()
    
    def _generate_alembic_config(self, 
                                analysis_result: Dict[str, Any], 
                                planning_result: Dict[str, Any]) -> List[GeneratedFile]:
        """Generate Alembic configuration files."""
        files = []
        
        # Generate alembic.ini
        alembic_ini_content = self._generate_alembic_ini()
        files.append(GeneratedFile(
            path="alembic.ini",
            content=alembic_ini_content,
            file_type="config",
            description="Alembic configuration"
        ))
        
        # Generate alembic/env.py
        alembic_env_content = self._generate_alembic_env()
        files.append(GeneratedFile(
            path="alembic/env.py",
            content=alembic_env_content,
            file_type="python",
            description="Alembic environment configuration"
        ))
        
        # Generate alembic/script.py.mako
        alembic_script_content = self._generate_alembic_script_template()
        files.append(GeneratedFile(
            path="alembic/script.py.mako",
            content=alembic_script_content,
            file_type="template",
            description="Alembic migration script template"
        ))
        
        return files
    
    def _generate_alembic_ini(self) -> str:
        """Generate alembic.ini configuration."""
        content = """# A generic, single database configuration.

[alembic]
# path to migration scripts
script_location = alembic

# template used to generate migration file names; The default value is %%(rev)s_%%(slug)s
# Uncomment the line below if you want the files to be prepended with date and time
# file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s

# sys.path path, will be prepended to sys.path if present.
# defaults to the current working directory.
prepend_sys_path = .

# timezone to use when rendering the date within the migration file
# as well as the filename.
# If specified, requires the python-dateutil library that can be
# installed by adding `alembic[tz]` to the pip requirements
# string value is passed to dateutil.tz.gettz()
# leave blank for localtime
# timezone =

# max length of characters to apply to the
# "slug" field
# max_length = 40

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
# revision_environment = false

# set to 'true' to allow .pyc and .pyo files without
# a source .py file to be detected as revisions in the
# versions/ directory
# sourceless = false

# version number format
version_num_format = %04d

# version path separator; As mentioned above, this is the string used to split
# version_locations. The default within new alembic.ini files is "os", which uses
# os.pathsep. If this key is omitted entirely, it falls back to the legacy
# behavior of splitting on spaces and/or commas.
# Valid values for version_path_separator are:
#
# version_path_separator = :
# version_path_separator = ;
# version_path_separator = space
version_path_separator = os

# the output encoding used when revision files
# are written from script.py.mako
# output_encoding = utf-8

sqlalchemy.url = sqlite:///./app.db


[post_write_hooks]
# post_write_hooks defines scripts or Python functions that are run
# on newly generated revision scripts.  See the documentation for further
# detail and examples

# format using "black" - use the console_scripts runner, against the "black" entrypoint
# hooks = black
# black.type = console_scripts
# black.entrypoint = black
# black.options = -l 79 REVISION_SCRIPT_FILENAME

# lint with attempts to fix using "ruff" - use the exec runner, execute a binary
# hooks = ruff
# ruff.type = exec
# ruff.executable = %(here)s/.venv/bin/ruff
# ruff.options = --fix REVISION_SCRIPT_FILENAME

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""
        
        return content.strip()
    
    def _generate_alembic_env(self) -> str:
        """Generate alembic/env.py."""
        content = """\"\"\"Alembic environment configuration.\"\"\"

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.config import settings
from app.models import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Set the database URL from settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    \"\"\"Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    \"\"\"
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    \"\"\"Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    \"\"\"
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
"""
        
        return content.strip()
    
    def _generate_alembic_script_template(self) -> str:
        """Generate alembic/script.py.mako template."""
        content = """\"\"\"${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

\"\"\"
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    \"\"\"Upgrade database schema.\"\"\"
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    \"\"\"Downgrade database schema.\"\"\"
    ${downgrades if downgrades else "pass"}
"""
        
        return content.strip()