# generators/auth_converter.py
"""Converts PHP authentication systems to FastAPI security schemes."""

import os
import re
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

from ..config.settings import Settings
from ..core.user_interface import UserInterface
from ..generators.llm_assisted_generator import LLMAssistedGenerator, ConversionRequest, ConversionContext


class AuthConverter:
    """Converts PHP authentication systems to FastAPI security."""
    
    def __init__(self, settings: Settings, ui: UserInterface):
        self.settings = settings
        self.ui = ui
        self.llm_generator = LLMAssistedGenerator(settings, ui)
        
        # Authentication method patterns
        self.auth_patterns = {
            'jwt': [
                r'jwt|JSON Web Token',
                r'firebase/php-jwt',
                r'lcobucci/jwt',
                r'tymon/jwt-auth',
                r'Authorization:\s*Bearer',
                r'token.*verify|verify.*token'
            ],
            'session': [
                r'session_start|$_SESSION',
                r'session.*auth|auth.*session',
                r'login.*session|session.*login',
                r'setcookie|$_COOKIE'
            ],
            'api_key': [
                r'api.*key|key.*api',
                r'X-API-KEY|API-KEY',
                r'Authorization:\s*ApiKey',
                r'Bearer.*[a-zA-Z0-9]{32,}'
            ],
            'basic': [
                r'Authorization:\s*Basic',
                r'HTTP_AUTHORIZATION.*Basic',
                r'$_SERVER.*PHP_AUTH'
            ],
            'oauth': [
                r'oauth|OAuth',
                r'laravel/passport',
                r'league/oauth2',
                r'Authorization:\s*Bearer.*oauth'
            ]
        }
    
    def convert_auth_system(self, auth_info: List[str], planning_result: Dict[str, Any], 
                           output_path: str) -> List[str]:
        """Convert PHP authentication system to FastAPI security."""
        try:
            if not auth_info:
                self.ui.debug("No authentication methods detected, skipping auth generation")
                return []
            
            self.ui.debug(f"Converting authentication methods: {auth_info}")
            
            # Analyze authentication methods
            auth_analysis = self._analyze_auth_methods(auth_info)
            
            # Create conversion context
            context = self._create_auth_context(planning_result)
            
            generated_files = []
            
            # Generate auth dependencies
            auth_deps_file = self._generate_auth_dependencies(auth_analysis, context, output_path)
            if auth_deps_file:
                generated_files.append(auth_deps_file)
            
            # Generate security schemes
            security_file = self._generate_security_schemes(auth_analysis, context, output_path)
            if security_file:
                generated_files.append(security_file)
            
            # Generate auth models if needed
            if auth_analysis.get('needs_user_model', False):
                user_model_file = self._generate_user_model(auth_analysis, context, output_path)
                if user_model_file:
                    generated_files.append(user_model_file)
            
            # Generate auth routes
            auth_routes_file = self._generate_auth_routes(auth_analysis, context, output_path)
            if auth_routes_file:
                generated_files.append(auth_routes_file)
            
            # Generate auth utilities
            auth_utils_file = self._generate_auth_utils(auth_analysis, context, output_path)
            if auth_utils_file:
                generated_files.append(auth_utils_file)
            
            return generated_files
            
        except Exception as e:
            self.ui.error(f"Failed to convert authentication system: {str(e)}")
            return []
    
    def _analyze_auth_methods(self, auth_info: List[str]) -> Dict[str, Any]:
        """Analyze authentication methods to determine conversion approach."""
        analysis = {
            'methods': [],
            'primary_method': 'jwt',  # Default
            'needs_user_model': True,
            'supports_refresh': False,
            'has_roles': False,
            'has_permissions': False,
            'middleware_required': True
        }
        
        # Combine all auth info into text for pattern matching
        auth_text = ' '.join(auth_info).lower()
        
        # Detect authentication methods
        for method, patterns in self.auth_patterns.items():
            for pattern in patterns:
                if re.search(pattern, auth_text, re.IGNORECASE):
                    if method not in analysis['methods']:
                        analysis['methods'].append(method)
        
        # Set primary method (prefer JWT, then API key, then session)
        if 'jwt' in analysis['methods']:
            analysis['primary_method'] = 'jwt'
            analysis['supports_refresh'] = True
        elif 'api_key' in analysis['methods']:
            analysis['primary_method'] = 'api_key'
        elif 'oauth' in analysis['methods']:
            analysis['primary_method'] = 'oauth'
            analysis['supports_refresh'] = True
        elif 'session' in analysis['methods']:
            analysis['primary_method'] = 'session'
        elif 'basic' in analysis['methods']:
            analysis['primary_method'] = 'basic'
        
        # Check for role/permission systems
        if any(keyword in auth_text for keyword in ['role', 'permission', 'acl', 'rbac']):
            analysis['has_roles'] = True
            analysis['has_permissions'] = True
        
        self.ui.debug(f"Auth analysis: {analysis}")
        return analysis
    
    def _create_auth_context(self, planning_result: Dict[str, Any]) -> ConversionContext:
        """Create conversion context for authentication."""
        return ConversionContext(
            framework='fastapi',
            database_type='postgresql',  # Default
            auth_method='jwt',
            python_dependencies=['fastapi', 'python-jose', 'passlib', 'python-multipart'],
            endpoint_style='fastapi_security',
            project_structure='auth_system'
        )
    
    def _generate_auth_dependencies(self, auth_analysis: Dict[str, Any], 
                                   context: ConversionContext, output_path: str) -> Optional[str]:
        """Generate FastAPI authentication dependencies."""
        try:
            # Create auth dependencies based on primary method
            primary_method = auth_analysis.get('primary_method', 'jwt')
            
            # Generate appropriate auth code
            auth_code = self._create_auth_dependencies_code(primary_method, auth_analysis)
            
            # Create conversion request for LLM enhancement
            request = ConversionRequest(
                php_code=f"// PHP Authentication converted to FastAPI dependencies\n{auth_code}",
                conversion_type='auth',
                context=context,
                file_path='auth_deps.py',
                additional_instructions=f"Create FastAPI authentication dependencies for {primary_method} authentication with proper error handling and security best practices."
            )
            
            result = self.llm_generator.convert_php_batch(request)
            
            if not result.success:
                # Fallback to template-based generation
                auth_code = self._get_auth_dependencies_template(primary_method, auth_analysis)
            else:
                auth_code = result.python_code
            
            # Write dependencies file
            deps_dir = os.path.join(output_path, 'app', 'core')
            os.makedirs(deps_dir, exist_ok=True)
            
            file_path = os.path.join(deps_dir, 'deps.py')
            
            # Enhance with proper imports
            enhanced_code = self._enhance_auth_deps_code(auth_code, primary_method)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(enhanced_code)
            
            self.ui.debug(f"Generated auth dependencies: {file_path}")
            return file_path
            
        except Exception as e:
            self.ui.error(f"Failed to generate auth dependencies: {str(e)}")
            return None
    
    def _generate_security_schemes(self, auth_analysis: Dict[str, Any],
                                  context: ConversionContext, output_path: str) -> Optional[str]:
        """Generate FastAPI security schemes."""
        try:
            primary_method = auth_analysis.get('primary_method', 'jwt')
            
            # Generate security schemes code
            security_code = self._get_security_schemes_template(primary_method, auth_analysis)
            
            # Write security file
            security_dir = os.path.join(output_path, 'app', 'core')
            os.makedirs(security_dir, exist_ok=True)
            
            file_path = os.path.join(security_dir, 'security.py')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(security_code)
            
            self.ui.debug(f"Generated security schemes: {file_path}")
            return file_path
            
        except Exception as e:
            self.ui.error(f"Failed to generate security schemes: {str(e)}")
            return None
    
    def _generate_user_model(self, auth_analysis: Dict[str, Any],
                            context: ConversionContext, output_path: str) -> Optional[str]:
        """Generate user model for authentication."""
        try:
            # Generate user model based on auth requirements
            user_model_code = self._get_user_model_template(auth_analysis)
            
            # Write user model
            models_dir = os.path.join(output_path, 'app', 'models')
            os.makedirs(models_dir, exist_ok=True)
            
            file_path = os.path.join(models_dir, 'user.py')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(user_model_code)
            
            self.ui.debug(f"Generated user model: {file_path}")
            return file_path
            
        except Exception as e:
            self.ui.error(f"Failed to generate user model: {str(e)}")
            return None
    
    def _generate_auth_routes(self, auth_analysis: Dict[str, Any],
                             context: ConversionContext, output_path: str) -> Optional[str]:
        """Generate authentication routes (login, register, etc.)."""
        try:
            primary_method = auth_analysis.get('primary_method', 'jwt')
            
            # Generate auth routes code
            auth_routes_code = self._get_auth_routes_template(primary_method, auth_analysis)
            
            # Write auth routes
            routes_dir = os.path.join(output_path, 'app', 'api', 'v1', 'endpoints')
            os.makedirs(routes_dir, exist_ok=True)
            
            file_path = os.path.join(routes_dir, 'auth.py')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(auth_routes_code)
            
            self.ui.debug(f"Generated auth routes: {file_path}")
            return file_path
            
        except Exception as e:
            self.ui.error(f"Failed to generate auth routes: {str(e)}")
            return None
    
    def _generate_auth_utils(self, auth_analysis: Dict[str, Any],
                            context: ConversionContext, output_path: str) -> Optional[str]:
        """Generate authentication utilities."""
        try:
            primary_method = auth_analysis.get('primary_method', 'jwt')
            
            # Generate auth utils code
            auth_utils_code = self._get_auth_utils_template(primary_method, auth_analysis)
            
            # Write auth utils
            utils_dir = os.path.join(output_path, 'app', 'core')
            os.makedirs(utils_dir, exist_ok=True)
            
            file_path = os.path.join(utils_dir, 'auth.py')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(auth_utils_code)
            
            self.ui.debug(f"Generated auth utils: {file_path}")
            return file_path
            
        except Exception as e:
            self.ui.error(f"Failed to generate auth utils: {str(e)}")
            return None
    
    def _create_auth_dependencies_code(self, method: str, analysis: Dict[str, Any]) -> str:
        """Create basic auth dependencies code for LLM enhancement."""
        if method == 'jwt':
            return """
<?php
// JWT Authentication
function authenticateJWT() {
    $token = getBearerToken();
    if (!$token) {
        http_response_code(401);
        echo json_encode(['error' => 'Token required']);
        exit;
    }
    
    $decoded = JWT::decode($token, $secret_key, ['HS256']);
    return $decoded;
}

function getBearerToken() {
    $headers = getallheaders();
    if (isset($headers['Authorization'])) {
        return str_replace('Bearer ', '', $headers['Authorization']);
    }
    return null;
}
"""
        elif method == 'api_key':
            return """
<?php
// API Key Authentication
function authenticateApiKey() {
    $api_key = $_SERVER['HTTP_X_API_KEY'] ?? $_GET['api_key'] ?? null;
    if (!$api_key) {
        http_response_code(401);
        echo json_encode(['error' => 'API key required']);
        exit;
    }
    
    if (!validateApiKey($api_key)) {
        http_response_code(401);
        echo json_encode(['error' => 'Invalid API key']);
        exit;
    }
    
    return getUserByApiKey($api_key);
}
"""
        else:
            return """
<?php
// Basic Authentication
function authenticateBasic() {
    if (!isset($_SERVER['PHP_AUTH_USER'])) {
        http_response_code(401);
        header('WWW-Authenticate: Basic realm="API"');
        echo json_encode(['error' => 'Authentication required']);
        exit;
    }
    
    $user = authenticateUser($_SERVER['PHP_AUTH_USER'], $_SERVER['PHP_AUTH_PW']);
    if (!$user) {
        http_response_code(401);
        echo json_encode(['error' => 'Invalid credentials']);
        exit;
    }
    
    return $user;
}
"""
    
    def _enhance_auth_deps_code(self, code: str, method: str) -> str:
        """Enhance auth dependencies code with proper imports."""
        imports = """from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

security = HTTPBearer()
"""
        
        if 'from ' not in code:
            return imports + '\n\n' + code
        return code
    
    def _get_auth_dependencies_template(self, method: str, analysis: Dict[str, Any]) -> str:
        """Get template for auth dependencies."""
        if method == 'jwt':
            return '''from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token."""
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user'''
        
        elif method == 'api_key':
            return '''from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User

def get_api_key(x_api_key: str = Header(...)) -> str:
    """Extract API key from header."""
    return x_api_key

def get_current_user(
    api_key: str = Depends(get_api_key),
    db: Session = Depends(get_db)
) -> User:
    """Get current user by API key."""
    user = db.query(User).filter(User.api_key == api_key).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user'''
        
        else:
            return '''from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.core.auth import verify_password

security = HTTPBasic()

def get_current_user(
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current user with basic auth."""
    user = db.query(User).filter(User.username == credentials.username).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user'''
    
    def _get_security_schemes_template(self, method: str, analysis: Dict[str, Any]) -> str:
        """Get security schemes template."""
        return '''"""FastAPI security schemes configuration."""

from fastapi.security import HTTPBearer, HTTPBasic, APIKeyHeader
from fastapi import status

# Security schemes
bearer_scheme = HTTPBearer()
basic_scheme = HTTPBasic()
api_key_scheme = APIKeyHeader(name="X-API-Key")

# Error responses
CREDENTIALS_EXCEPTION = {
    "status_code": status.HTTP_401_UNAUTHORIZED,
    "detail": "Could not validate credentials",
    "headers": {"WWW-Authenticate": "Bearer"},
}

INACTIVE_USER_EXCEPTION = {
    "status_code": status.HTTP_400_BAD_REQUEST,
    "detail": "Inactive user"
}

API_KEY_EXCEPTION = {
    "status_code": status.HTTP_401_UNAUTHORIZED,
    "detail": "Invalid API key"
}'''
    
    def _get_user_model_template(self, analysis: Dict[str, Any]) -> str:
        """Get user model template."""
        has_roles = analysis.get('has_roles', False)
        
        base_model = '''"""User model for authentication."""

from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())'''
        
        if analysis.get('primary_method') == 'api_key':
            base_model += '''
    api_key = Column(String(255), unique=True, index=True)'''
        
        if has_roles:
            base_model += '''
    
    # Add relationships for roles/permissions if needed
    # roles = relationship("UserRole", back_populates="user")'''
        
        return base_model
    
    def _get_auth_routes_template(self, method: str, analysis: Dict[str, Any]) -> str:
        """Get auth routes template."""
        if method == 'jwt':
            return '''"""Authentication routes."""

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import Token, UserCreate, UserResponse
from app.core.deps import get_current_user

router = APIRouter()

@router.post("/login", response_model=Token)
def login_for_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """OAuth2 compatible token login, get an access token for future requests."""
    user = security.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/register", response_model=UserResponse)
def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """Create new user."""
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = security.create_user(db, user_in)
    return user

@router.get("/me", response_model=UserResponse)
def read_users_me(
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get current user."""
    return current_user'''
        
        else:
            return '''"""Authentication routes."""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import UserCreate, UserResponse
from app.core.deps import get_current_user

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """Create new user."""
    # Implementation here
    pass

@router.get("/me", response_model=UserResponse)
def read_users_me(
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get current user."""
    return current_user'''
    
    def _get_auth_utils_template(self, method: str, analysis: Dict[str, Any]) -> str:
        """Get auth utils template."""
        if method == 'jwt':
            return '''"""Authentication utilities."""

from datetime import datetime, timedelta
from typing import Any, Union

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.schemas.auth import UserCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    """Create access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Get password hash."""
    return pwd_context.hash(password)

def authenticate_user(db: Session, username: str, password: str) -> Union[User, bool]:
    """Authenticate user."""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_user(db: Session, user: UserCreate) -> User:
    """Create new user."""
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user'''
        
        else:
            return '''"""Authentication utilities."""

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import UserCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Get password hash."""
    return pwd_context.hash(password)

def create_user(db: Session, user: UserCreate) -> User:
    """Create new user."""
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user'''