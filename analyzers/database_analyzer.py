# analyzers/database_analyzer.py
"""Analyzes database usage, schemas, and ORM patterns in PHP projects."""

import re
import os
import json
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DatabaseConnection:
    """Represents a database connection configuration."""
    name: str
    type: str  # mysql, postgresql, sqlite, mongodb, etc.
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    charset: Optional[str] = None
    options: Dict[str, Any] = field(default_factory=dict)
    file_path: str = ""


@dataclass
class TableInfo:
    """Information about a database table."""
    name: str
    estimated_columns: List[str] = field(default_factory=list)
    relationships: List[str] = field(default_factory=list)
    indexes: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    model_class: Optional[str] = None
    file_references: List[str] = field(default_factory=list)


@dataclass
class DatabaseQuery:
    """Represents a database query found in code."""
    query_type: str  # SELECT, INSERT, UPDATE, DELETE, etc.
    table: Optional[str] = None
    raw_sql: Optional[str] = None
    orm_method: Optional[str] = None
    file_path: str = ""
    line_number: int = 0
    context: str = ""


@dataclass
class DatabaseAnalysis:
    """Complete database analysis result."""
    connections: List[DatabaseConnection] = field(default_factory=list)
    tables: List[TableInfo] = field(default_factory=list)
    queries: List[DatabaseQuery] = field(default_factory=list)
    orm_framework: Optional[str] = None
    migration_files: List[str] = field(default_factory=list)
    schema_files: List[str] = field(default_factory=list)
    complexity_metrics: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


class DatabaseAnalyzer:
    """Analyzes database usage in PHP projects."""
    
    def __init__(self):
        # Database configuration patterns
        self.config_patterns = {
            'mysql': [
                r'mysql:host=([^;]+)',
                r'["\']?host["\']?\s*=>\s*["\']([^"\']+)["\']',
                r'DB_HOST\s*=\s*["\']?([^"\']+)["\']?'
            ],
            'postgresql': [
                r'pgsql:host=([^;]+)',
                r'["\']?driver["\']?\s*=>\s*["\']pgsql["\']'
            ],
            'sqlite': [
                r'sqlite:([^"\']+)',
                r'["\']?database["\']?\s*=>\s*["\']([^"\']+\.sqlite?)["\']'
            ],
            'mongodb': [
                r'mongodb://([^"\']+)',
                r'new\s+MongoClient'
            ]
        }
        
        # ORM framework patterns
        self.orm_patterns = {
            'eloquent': [
                r'use\s+Illuminate\\Database',
                r'extends\s+Model',
                r'Eloquent::'
            ],
            'doctrine': [
                r'use\s+Doctrine\\',
                r'@Entity',
                r'@Table',
                r'EntityManager'
            ],
            'propel': [
                r'use\s+Propel',
                r'extends\s+BaseObject',
                r'Propel::'
            ],
            'active_record': [
                r'extends\s+ActiveRecord',
                r'find_by_',
                r'->save\(\)'
            ]
        }
        
        # Query patterns
        self.query_patterns = {
            'raw_sql': [
                re.compile(r'(SELECT|INSERT|UPDATE|DELETE)\s+.*?FROM\s+(\w+)', re.IGNORECASE | re.DOTALL),
                re.compile(r'mysql_query\s*\(\s*["\']([^"\']+)["\']', re.IGNORECASE),
                re.compile(r'mysqli_query\s*\([^,]+,\s*["\']([^"\']+)["\']', re.IGNORECASE)
            ],
            'pdo': [
                re.compile(r'\$\w+->query\s*\(\s*["\']([^"\']+)["\']', re.IGNORECASE),
                re.compile(r'\$\w+->prepare\s*\(\s*["\']([^"\']+)["\']', re.IGNORECASE)
            ],
            'eloquent': [
                re.compile(r'(\w+)::find\(', re.IGNORECASE),
                re.compile(r'(\w+)::where\(', re.IGNORECASE),
                re.compile(r'DB::table\s*\(\s*["\'](\w+)["\']', re.IGNORECASE)
            ]
        }
        
        # Migration patterns
        self.migration_patterns = [
            re.compile(r'Schema::create\s*\(\s*["\'](\w+)["\']', re.IGNORECASE),
            re.compile(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)', re.IGNORECASE),
            re.compile(r'\$table->(\w+)\s*\(\s*["\'](\w+)["\']', re.IGNORECASE)
        ]
    
    def analyze_database_usage(self, project_path: str) -> DatabaseAnalysis:
        """Analyze database usage in the entire project."""
        analysis = DatabaseAnalysis()
        
        # Find configuration files
        config_files = self._find_config_files(project_path)
        
        # Analyze database connections
        for config_file in config_files:
            connections = self._analyze_config_file(config_file)
            analysis.connections.extend(connections)
        
        # Find and analyze PHP files
        php_files = self._find_php_files(project_path)
        
        # Detect ORM framework
        analysis.orm_framework = self._detect_orm_framework(php_files)
        
        # Analyze queries and table usage
        for php_file in php_files:
            queries = self._analyze_file_queries(php_file)
            analysis.queries.extend(queries)
        
        # Extract table information
        analysis.tables = self._extract_table_info(analysis.queries, php_files)
        
        # Find migration files
        analysis.migration_files = self._find_migration_files(project_path)
        
        # Analyze migration files for schema info
        self._analyze_migration_files(analysis.migration_files, analysis)
        
        # Calculate complexity metrics
        analysis.complexity_metrics = self._calculate_complexity_metrics(analysis)
        
        # Generate recommendations
        analysis.recommendations = self._generate_recommendations(analysis)
        
        return analysis
    
    def _find_config_files(self, project_path: str) -> List[str]:
        """Find database configuration files."""
        config_files = []
        
        # Common config file patterns
        config_patterns = [
            'config/database.php',
            'application/config/database.php',
            'config/db.php',
            'database.php',
            'config.php',
            '.env',
            'config.ini'
        ]
        
        for pattern in config_patterns:
            file_path = os.path.join(project_path, pattern)
            if os.path.exists(file_path):
                config_files.append(file_path)
        
        # Search for additional config files
        for root, dirs, files in os.walk(project_path):
            # Skip vendor and node_modules
            dirs[:] = [d for d in dirs if d not in ['vendor', 'node_modules', '.git']]
            
            for file in files:
                if any(keyword in file.lower() for keyword in ['config', 'database', 'db']) and \
                   file.endswith(('.php', '.ini', '.env', '.json')):
                    file_path = os.path.join(root, file)
                    if file_path not in config_files:
                        config_files.append(file_path)
        
        return config_files
    
    def _find_php_files(self, project_path: str) -> List[str]:
        """Find all PHP files in the project."""
        php_files = []
        
        for root, dirs, files in os.walk(project_path):
            # Skip vendor and other directories
            dirs[:] = [d for d in dirs if d not in ['vendor', 'node_modules', '.git', 'cache', 'logs']]
            
            for file in files:
                if file.endswith(('.php', '.phtml', '.inc')):
                    php_files.append(os.path.join(root, file))
        
        return php_files
    
    def _analyze_config_file(self, config_file: str) -> List[DatabaseConnection]:
        """Analyze a configuration file for database connections."""
        connections = []
        
        try:
            with open(config_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception:
            return connections
        
        # Detect database type and extract connection info
        for db_type, patterns in self.config_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    # Create connection object
                    connection = DatabaseConnection(
                        name=f"{db_type}_connection",
                        type=db_type,
                        file_path=config_file
                    )
                    
                    # Extract additional details
                    self._extract_connection_details(content, connection)
                    connections.append(connection)
                    break  # Found this DB type, move to next
        
        # Special handling for .env files
        if config_file.endswith('.env'):
            env_connections = self._parse_env_file(content, config_file)
            connections.extend(env_connections)
        
        return connections
    
    def _extract_connection_details(self, content: str, connection: DatabaseConnection) -> None:
        """Extract detailed connection information."""
        # Extract host
        host_patterns = [
            r'["\']?host["\']?\s*[=:>]\s*["\']([^"\']+)["\']',
            r'DB_HOST\s*=\s*["\']?([^"\']+)["\']?'
        ]
        for pattern in host_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                connection.host = match.group(1)
                break
        
        # Extract port
        port_patterns = [
            r'["\']?port["\']?\s*[=:>]\s*["\']?(\d+)["\']?',
            r'DB_PORT\s*=\s*["\']?(\d+)["\']?'
        ]
        for pattern in port_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                connection.port = int(match.group(1))
                break
        
        # Extract database name
        db_patterns = [
            r'["\']?database["\']?\s*[=:>]\s*["\']([^"\']+)["\']',
            r'DB_DATABASE\s*=\s*["\']?([^"\']+)["\']?',
            r'["\']?dbname["\']?\s*[=:>]\s*["\']([^"\']+)["\']'
        ]
        for pattern in db_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                connection.database = match.group(1)
                break
        
        # Extract username
        user_patterns = [
            r'["\']?username["\']?\s*[=:>]\s*["\']([^"\']+)["\']',
            r'DB_USERNAME\s*=\s*["\']?([^"\']+)["\']?',
            r'["\']?user["\']?\s*[=:>]\s*["\']([^"\']+)["\']'
        ]
        for pattern in user_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                connection.username = match.group(1)
                break
        
        # Extract charset
        charset_patterns = [
            r'["\']?charset["\']?\s*[=:>]\s*["\']([^"\']+)["\']',
            r'DB_CHARSET\s*=\s*["\']?([^"\']+)["\']?'
        ]
        for pattern in charset_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                connection.charset = match.group(1)
                break
    
    def _parse_env_file(self, content: str, file_path: str) -> List[DatabaseConnection]:
        """Parse .env file for database configuration."""
        connections = []
        
        # Look for DB_CONNECTION to determine type
        db_type_match = re.search(r'DB_CONNECTION\s*=\s*["\']?(\w+)["\']?', content, re.IGNORECASE)
        if db_type_match:
            db_type = db_type_match.group(1).lower()
            
            connection = DatabaseConnection(
                name=f"{db_type}_env_connection",
                type=db_type,
                file_path=file_path
            )
            
            self._extract_connection_details(content, connection)
            connections.append(connection)
        
        return connections
    
    def _detect_orm_framework(self, php_files: List[str]) -> Optional[str]:
        """Detect which ORM framework is being used."""
        orm_scores = {orm: 0 for orm in self.orm_patterns.keys()}
        
        # Sample files to avoid processing everything
        sample_files = php_files[:50] if len(php_files) > 50 else php_files
        
        for file_path in sample_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                for orm, patterns in self.orm_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            orm_scores[orm] += 1
                            
            except Exception:
                continue
        
        # Return the ORM with highest score
        if any(score > 0 for score in orm_scores.values()):
            return max(orm_scores, key=orm_scores.get)
        
        return None
    
    def _analyze_file_queries(self, file_path: str) -> List[DatabaseQuery]:
        """Analyze a PHP file for database queries."""
        queries = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception:
            return queries
        
        lines = content.split('\n')
        
        # Analyze different query types
        for query_type, patterns in self.query_patterns.items():
            for pattern in patterns:
                for match in pattern.finditer(content):
                    line_number = content[:match.start()].count('\n') + 1
                    
                    query = DatabaseQuery(
                        query_type=query_type,
                        file_path=file_path,
                        line_number=line_number,
                        context=lines[line_number - 1].strip() if line_number <= len(lines) else ""
                    )
                    
                    # Extract table name and SQL
                    if query_type == 'raw_sql':
                        query.raw_sql = match.group(0)
                        # Try to extract table name
                        table_match = re.search(r'FROM\s+(\w+)', match.group(0), re.IGNORECASE)
                        if table_match:
                            query.table = table_match.group(1)
                    elif query_type == 'eloquent':
                        query.table = match.group(1)
                        query.orm_method = match.group(0)
                    
                    queries.append(query)
        
        return queries
    
    def _extract_table_info(self, queries: List[DatabaseQuery], php_files: List[str]) -> List[TableInfo]:
        """Extract table information from queries and model files."""
        tables = {}
        
        # Extract table names from queries
        for query in queries:
            if query.table:
                table_name = query.table.lower()
                if table_name not in tables:
                    tables[table_name] = TableInfo(name=table_name)
                
                tables[table_name].file_references.append(query.file_path)
        
        # Look for model classes
        self._find_model_classes(php_files, tables)
        
        # Analyze table relationships
        self._analyze_relationships(php_files, tables)
        
        return list(tables.values())
    
    def _find_model_classes(self, php_files: List[str], tables: Dict[str, TableInfo]) -> None:
        """Find model classes associated with tables."""
        model_patterns = [
            re.compile(r'class\s+(\w+)\s+extends\s+Model', re.IGNORECASE),
            re.compile(r'class\s+(\w+)\s+extends\s+Eloquent', re.IGNORECASE),
            re.compile(r'class\s+(\w+)\s+extends\s+ActiveRecord', re.IGNORECASE)
        ]
        
        table_property_pattern = re.compile(r'protected\s+\$table\s*=\s*["\'](\w+)["\']', re.IGNORECASE)
        
        for file_path in php_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Find model classes
                for pattern in model_patterns:
                    for match in pattern.finditer(content):
                        model_name = match.group(1)
                        
                        # Look for explicit table name
                        table_match = table_property_pattern.search(content)
                        if table_match:
                            table_name = table_match.group(1).lower()
                        else:
                            # Convert model name to table name (convention)
                            table_name = self._model_to_table_name(model_name)
                        
                        if table_name in tables:
                            tables[table_name].model_class = model_name
                        elif table_name:
                            # Create new table info
                            tables[table_name] = TableInfo(
                                name=table_name,
                                model_class=model_name,
                                file_references=[file_path]
                            )
                            
            except Exception:
                continue
    
    def _model_to_table_name(self, model_name: str) -> str:
        """Convert model name to conventional table name."""
        # Convert PascalCase to snake_case and pluralize
        # This is a simplified version
        table_name = re.sub(r'(?<!^)(?=[A-Z])', '_', model_name).lower()
        
        # Simple pluralization
        if table_name.endswith('y'):
            table_name = table_name[:-1] + 'ies'
        elif table_name.endswith(('s', 'sh', 'ch', 'x', 'z')):
            table_name += 'es'
        else:
            table_name += 's'
        
        return table_name
    
    def _analyze_relationships(self, php_files: List[str], tables: Dict[str, TableInfo]) -> None:
        """Analyze relationships between tables."""
        relationship_patterns = [
            re.compile(r'belongsTo\s*\(\s*["\']?(\w+)["\']?', re.IGNORECASE),
            re.compile(r'hasMany\s*\(\s*["\']?(\w+)["\']?', re.IGNORECASE),
            re.compile(r'hasOne\s*\(\s*["\']?(\w+)["\']?', re.IGNORECASE),
            re.compile(r'belongsToMany\s*\(\s*["\']?(\w+)["\']?', re.IGNORECASE)
        ]
        
        foreign_key_pattern = re.compile(r'(\w+)_id', re.IGNORECASE)
        
        for file_path in php_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Find relationship definitions
                for pattern in relationship_patterns:
                    for match in pattern.finditer(content):
                        related_model = match.group(1)
                        related_table = self._model_to_table_name(related_model)
                        
                        # Find which table this belongs to
                        class_match = re.search(r'class\s+(\w+)', content[:match.start()], re.IGNORECASE)
                        if class_match:
                            current_model = class_match.group(1)
                            current_table = self._model_to_table_name(current_model)
                            
                            if current_table in tables:
                                relationship = f"{match.group(0)} -> {related_model}"
                                if relationship not in tables[current_table].relationships:
                                    tables[current_table].relationships.append(relationship)
                
                # Look for foreign key patterns
                for match in foreign_key_pattern.finditer(content):
                    fk_name = match.group(1)
                    # This would need more context to be useful
                    
            except Exception:
                continue
    
    def _find_migration_files(self, project_path: str) -> List[str]:
        """Find database migration files."""
        migration_files = []
        
        # Common migration directories
        migration_dirs = [
            'database/migrations',
            'application/migrations',
            'migrations',
            'db/migrate'
        ]
        
        for migration_dir in migration_dirs:
            full_path = os.path.join(project_path, migration_dir)
            if os.path.exists(full_path):
                for file in os.listdir(full_path):
                    if file.endswith('.php'):
                        migration_files.append(os.path.join(full_path, file))
        
        return migration_files
    
    def _analyze_migration_files(self, migration_files: List[str], analysis: DatabaseAnalysis) -> None:
        """Analyze migration files for schema information."""
        for file_path in migration_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Find table creation
                for pattern in self.migration_patterns:
                    for match in pattern.finditer(content):
                        if 'Schema::create' in match.group(0) or 'CREATE TABLE' in match.group(0):
                            table_name = match.group(1).lower()
                            
                            # Find or create table info
                            table_info = None
                            for table in analysis.tables:
                                if table.name == table_name:
                                    table_info = table
                                    break
                            
                            if not table_info:
                                table_info = TableInfo(name=table_name)
                                analysis.tables.append(table_info)
                            
                            # Extract column information from migration
                            self._extract_migration_columns(content, table_info)
                            
            except Exception:
                continue
    
    def _extract_migration_columns(self, content: str, table_info: TableInfo) -> None:
        """Extract column information from migration content."""
        column_patterns = [
            re.compile(r'\$table->(\w+)\s*\(\s*["\'](\w+)["\']', re.IGNORECASE),
            re.compile(r'(\w+)\s+(\w+)(?:\(\d+\))?(?:\s+NOT\s+NULL)?', re.IGNORECASE)
        ]
        
        for pattern in column_patterns:
            for match in pattern.finditer(content):
                if len(match.groups()) >= 2:
                    column_type = match.group(1)
                    column_name = match.group(2)
                    
                    column_def = f"{column_name} ({column_type})"
                    if column_def not in table_info.estimated_columns:
                        table_info.estimated_columns.append(column_def)
    
    def _calculate_complexity_metrics(self, analysis: DatabaseAnalysis) -> Dict[str, Any]:
        """Calculate database complexity metrics."""
        metrics = {}
        
        # Basic counts
        metrics['total_connections'] = len(analysis.connections)
        metrics['total_tables'] = len(analysis.tables)
        metrics['total_queries'] = len(analysis.queries)
        metrics['migration_files'] = len(analysis.migration_files)
        
        # Query type distribution
        query_types = {}
        for query in analysis.queries:
            query_types[query.query_type] = query_types.get(query.query_type, 0) + 1
        metrics['query_type_distribution'] = query_types
        
        # Table complexity
        avg_relationships = 0
        max_relationships = 0
        if analysis.tables:
            total_relationships = sum(len(table.relationships) for table in analysis.tables)
            avg_relationships = total_relationships / len(analysis.tables)
            max_relationships = max(len(table.relationships) for table in analysis.tables)
        
        metrics['avg_relationships_per_table'] = avg_relationships
        metrics['max_relationships_per_table'] = max_relationships
        
        # Complexity score
        complexity_factors = [
            len(analysis.connections) > 1,  # Multiple databases
            len(analysis.tables) > 20,      # Many tables
            len(analysis.queries) > 100,    # Many queries
            avg_relationships > 3,          # Complex relationships
            'raw_sql' in query_types and query_types['raw_sql'] > 10  # Many raw SQL queries
        ]
        
        complexity_score = sum(complexity_factors)
        if complexity_score <= 1:
            metrics['complexity_level'] = 'low'
        elif complexity_score <= 3:
            metrics['complexity_level'] = 'medium'
        else:
            metrics['complexity_level'] = 'high'
        
        metrics['complexity_score'] = complexity_score
        
        return metrics
    
    def _generate_recommendations(self, analysis: DatabaseAnalysis) -> List[str]:
        """Generate recommendations for database migration."""
        recommendations = []
        
        # Connection recommendations
        if len(analysis.connections) == 0:
            recommendations.append("No database connections found. Verify configuration files.")
        elif len(analysis.connections) > 2:
            recommendations.append("Multiple database connections detected. Consider consolidating if possible.")
        
        # ORM recommendations
        if not analysis.orm_framework:
            recommendations.append("No ORM framework detected. Consider using SQLAlchemy for Python conversion.")
        elif analysis.orm_framework == 'eloquent':
            recommendations.append("Eloquent ORM detected. Plan migration to SQLAlchemy with similar model patterns.")
        elif analysis.orm_framework == 'doctrine':
            recommendations.append("Doctrine ORM detected. SQLAlchemy provides similar functionality.")
        
        # Query analysis recommendations
        raw_sql_count = sum(1 for q in analysis.queries if q.query_type == 'raw_sql')
        if raw_sql_count > 20:
            recommendations.append(f"{raw_sql_count} raw SQL queries found. Consider converting to ORM methods for better maintainability.")
        
        # Table recommendations
        tables_without_models = [t for t in analysis.tables if not t.model_class]
        if tables_without_models:
            recommendations.append(f"{len(tables_without_models)} tables found without associated models. Create Pydantic/SQLAlchemy models for these.")
        
        # Migration recommendations
        if not analysis.migration_files:
            recommendations.append("No migration files found. Consider creating Alembic migrations for schema management.")
        
        # Complexity recommendations
        complexity = analysis.complexity_metrics.get('complexity_level', 'unknown')
        if complexity == 'high':
            recommendations.append("High database complexity detected. Plan for careful migration and thorough testing.")
        
        # Database type recommendations
        db_types = {conn.type for conn in analysis.connections}
        if 'mysql' in db_types:
            recommendations.append("MySQL detected. Use mysql-connector-python or aiomysql for FastAPI.")
        if 'postgresql' in db_types:
            recommendations.append("PostgreSQL detected. Use psycopg2 or asyncpg for FastAPI.")
        if 'sqlite' in db_types:
            recommendations.append("SQLite detected. Consider upgrading to PostgreSQL for production.")
        if 'mongodb' in db_types:
            recommendations.append("MongoDB detected. Use Motor (async MongoDB driver) for FastAPI.")
        
        return recommendations
    
    def generate_sqlalchemy_models(self, analysis: DatabaseAnalysis) -> str:
        """Generate basic SQLAlchemy model code from analysis."""
        model_code = []
        
        model_code.append("# Generated SQLAlchemy models")
        model_code.append("# Please review and adjust as needed")
        model_code.append("")
        model_code.append("from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean")
        model_code.append("from sqlalchemy.orm import relationship")
        model_code.append("from sqlalchemy.sql import func")
        model_code.append("from app.db.base import BaseModel")
        model_code.append("")
        
        for table in analysis.tables:
            model_name = table.model_class or self._table_to_model_name(table.name)
            
            model_code.append(f"class {model_name}(BaseModel):")
            model_code.append(f'    """Model for {table.name} table."""')
            model_code.append("")
            model_code.append(f'    __tablename__ = "{table.name}"')
            model_code.append("")
            
            # Add basic columns
            if table.estimated_columns:
                for column in table.estimated_columns:
                    # Parse column definition
                    if '(' in column:
                        col_name = column.split('(')[0].strip()
                        col_type = column.split('(')[1].split(')')[0].strip()
                    else:
                        col_name = column
                        col_type = 'string'
                    
                    # Map to SQLAlchemy types
                    sqlalchemy_type = self._map_to_sqlalchemy_type(col_type)
                    model_code.append(f"    {col_name} = Column({sqlalchemy_type})")
            else:
                # Add generic columns
                model_code.append("    name = Column(String(100), nullable=False)")
                model_code.append("    description = Column(Text)")
            
            # Add relationships
            for relationship in table.relationships:
                rel_name = relationship.split('->')[0].strip().replace('()', '')
                model_code.append(f"    # {relationship}")
                model_code.append(f"    # {rel_name} = relationship(...)")
            
            model_code.append("")
            model_code.append("")
        
        return "\n".join(model_code)
    
    def _table_to_model_name(self, table_name: str) -> str:
        """Convert table name to model class name."""
        # Remove plural suffix and convert to PascalCase
        name = table_name
        if name.endswith('ies'):
            name = name[:-3] + 'y'
        elif name.endswith('es'):
            name = name[:-2]
        elif name.endswith('s'):
            name = name[:-1]
        
        # Convert snake_case to PascalCase
        return ''.join(word.capitalize() for word in name.split('_'))
    
    def _map_to_sqlalchemy_type(self, php_type: str) -> str:
        """Map PHP/MySQL type to SQLAlchemy type."""
        type_mapping = {
            'int': 'Integer',
            'integer': 'Integer',
            'bigint': 'BigInteger',
            'string': 'String(255)',
            'varchar': 'String(255)',
            'text': 'Text',
            'datetime': 'DateTime',
            'timestamp': 'DateTime',
            'boolean': 'Boolean',
            'bool': 'Boolean',
            'decimal': 'Numeric',
            'float': 'Float',
            'json': 'JSON'
        }
        
        return type_mapping.get(php_type.lower(), 'String(255)')