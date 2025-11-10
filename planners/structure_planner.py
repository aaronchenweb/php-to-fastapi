# planners/structure_planner.py
"""Plans FastAPI project structure based on PHP project analysis."""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DirectoryPlan:
    """Plan for a directory in the FastAPI project."""
    name: str
    purpose: str
    description: str
    files: List[str] = field(default_factory=list)
    subdirectories: List['DirectoryPlan'] = field(default_factory=list)
    php_source_mapping: List[str] = field(default_factory=list)
    priority: int = 1  # 1=high, 2=medium, 3=low


@dataclass
class FilePlan:
    """Plan for a file in the FastAPI project."""
    name: str
    path: str
    purpose: str
    content_type: str  # python, config, template, etc.
    dependencies: List[str] = field(default_factory=list)
    php_source_files: List[str] = field(default_factory=list)
    template_used: Optional[str] = None
    priority: int = 1


@dataclass
class StructurePlan:
    """Complete FastAPI project structure plan."""
    root_directory: str
    organization_pattern: str
    directories: List[DirectoryPlan] = field(default_factory=list)
    files: List[FilePlan] = field(default_factory=list)
    migration_mapping: Dict[str, str] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


class StructurePlanner:
    """Plans FastAPI project structure based on PHP analysis."""
    
    def __init__(self):
        # Standard FastAPI project structure templates
        self.structure_templates = {
            'minimal': self._get_minimal_template(),
            'standard': self._get_standard_template(),
            'enterprise': self._get_enterprise_template(),
            'microservice': self._get_microservice_template()
        }
        
        # File templates
        self.file_templates = {
            'main.py': 'fastapi_main',
            'config.py': 'fastapi_config',
            'database.py': 'sqlalchemy_database',
            'models.py': 'sqlalchemy_models',
            'schemas.py': 'pydantic_schemas',
            'routes.py': 'fastapi_routes',
            'dependencies.py': 'fastapi_dependencies',
            'middleware.py': 'fastapi_middleware',
            'tests.py': 'pytest_tests'
        }
    
    def plan_structure(self, analysis_result: Dict[str, Any]) -> StructurePlan:
        """Plan the FastAPI project structure based on analysis."""
        
        # Determine appropriate template
        template_type = self._select_template(analysis_result)
        base_template = self.structure_templates[template_type]
        
        # Create structure plan
        plan = StructurePlan(
            root_directory="fastapi_project",
            organization_pattern=template_type
        )
        
        # Plan directories
        plan.directories = self._plan_directories(base_template, analysis_result)
        
        # Plan files
        plan.files = self._plan_files(plan.directories, analysis_result)
        
        # Create migration mapping
        plan.migration_mapping = self._create_migration_mapping(analysis_result, plan)
        
        # Generate recommendations
        plan.recommendations = self._generate_structure_recommendations(analysis_result, plan)
        
        return plan
    
    def _select_template(self, analysis_result: Dict[str, Any]) -> str:
        """Select appropriate FastAPI structure template."""
        
        project_info = analysis_result.get('project_info', {})
        endpoint_analysis = analysis_result.get('endpoint_analysis', {})
        file_analysis = analysis_result.get('file_analysis', {})
        
        # Factors for template selection
        total_files = project_info.get('total_php_files', 0)
        total_endpoints = endpoint_analysis.get('total_endpoints', 0)
        total_classes = file_analysis.get('code_metrics', {}).get('total_classes', 0)
        framework = project_info.get('framework', 'vanilla')
        
        # Decision logic
        if total_files < 5 and total_endpoints < 5:
            return 'minimal'
        elif framework in ['laravel', 'symfony'] or total_files > 50 or total_classes > 30:
            return 'enterprise'
        elif total_endpoints > 20 or total_files > 20:
            return 'standard'
        else:
            return 'standard'  # Default
    
    def _get_minimal_template(self) -> Dict[str, Any]:
        """Get minimal FastAPI structure template."""
        return {
            'root_files': ['main.py', 'requirements.txt', '.env', '.gitignore', 'README.md'],
            'directories': {
                'app': {
                    'purpose': 'Main application package',
                    'files': ['__init__.py', 'config.py', 'models.py', 'schemas.py', 'main.py'],
                    'subdirectories': {}
                },
                'tests': {
                    'purpose': 'Test files',
                    'files': ['__init__.py', 'test_main.py'],
                    'subdirectories': {}
                }
            }
        }
    
    def _get_standard_template(self) -> Dict[str, Any]:
        """Get standard FastAPI structure template."""
        return {
            'root_files': ['main.py', 'requirements.txt', '.env', '.gitignore', 'README.md', 'Dockerfile'],
            'directories': {
                'app': {
                    'purpose': 'Main application package',
                    'files': ['__init__.py'],
                    'subdirectories': {
                        'api': {
                            'purpose': 'API routes and endpoints',
                            'files': ['__init__.py', 'dependencies.py'],
                            'subdirectories': {
                                'v1': {
                                    'purpose': 'API version 1',
                                    'files': ['__init__.py', 'api.py'],
                                    'subdirectories': {
                                        'endpoints': {
                                            'purpose': 'Individual endpoint modules',
                                            'files': ['__init__.py'],
                                            'subdirectories': {}
                                        }
                                    }
                                }
                            }
                        },
                        'core': {
                            'purpose': 'Core functionality',
                            'files': ['__init__.py', 'config.py', 'security.py'],
                            'subdirectories': {}
                        },
                        'db': {
                            'purpose': 'Database configuration',
                            'files': ['__init__.py', 'database.py', 'base.py'],
                            'subdirectories': {}
                        },
                        'models': {
                            'purpose': 'Database models',
                            'files': ['__init__.py'],
                            'subdirectories': {}
                        },
                        'schemas': {
                            'purpose': 'Pydantic schemas',
                            'files': ['__init__.py'],
                            'subdirectories': {}
                        },
                        'services': {
                            'purpose': 'Business logic services',
                            'files': ['__init__.py'],
                            'subdirectories': {}
                        }
                    }
                },
                'tests': {
                    'purpose': 'Test files',
                    'files': ['__init__.py', 'conftest.py'],
                    'subdirectories': {
                        'api': {
                            'purpose': 'API tests',
                            'files': ['__init__.py'],
                            'subdirectories': {}
                        },
                        'services': {
                            'purpose': 'Service tests',
                            'files': ['__init__.py'],
                            'subdirectories': {}
                        }
                    }
                },
                'alembic': {
                    'purpose': 'Database migrations',
                    'files': ['env.py', 'script.py.mako'],
                    'subdirectories': {
                        'versions': {
                            'purpose': 'Migration versions',
                            'files': [],
                            'subdirectories': {}
                        }
                    }
                }
            }
        }
    
    def _get_enterprise_template(self) -> Dict[str, Any]:
        """Get enterprise FastAPI structure template."""
        standard = self._get_standard_template()
        
        # Add enterprise-specific directories
        standard['directories']['app']['subdirectories'].update({
            'middleware': {
                'purpose': 'Custom middleware',
                'files': ['__init__.py', 'cors.py', 'auth.py', 'logging.py'],
                'subdirectories': {}
            },
            'utils': {
                'purpose': 'Utility functions',
                'files': ['__init__.py', 'helpers.py', 'validators.py'],
                'subdirectories': {}
            },
            'exceptions': {
                'purpose': 'Custom exceptions',
                'files': ['__init__.py', 'handlers.py'],
                'subdirectories': {}
            },
            'repositories': {
                'purpose': 'Data access layer',
                'files': ['__init__.py', 'base.py'],
                'subdirectories': {}
            }
        })
        
        # Add additional root files
        standard['root_files'].extend([
            'docker-compose.yml',
            'pyproject.toml',
            '.pre-commit-config.yaml',
            'Makefile'
        ])
        
        # Add more test directories
        standard['directories']['tests']['subdirectories'].update({
            'integration': {
                'purpose': 'Integration tests',
                'files': ['__init__.py'],
                'subdirectories': {}
            },
            'unit': {
                'purpose': 'Unit tests',
                'files': ['__init__.py'],
                'subdirectories': {}
            }
        })
        
        return standard
    
    def _get_microservice_template(self) -> Dict[str, Any]:
        """Get microservice FastAPI structure template."""
        return {
            'root_files': [
                'main.py', 'requirements.txt', '.env', '.gitignore', 'README.md',
                'Dockerfile', 'docker-compose.yml', 'k8s-deployment.yml'
            ],
            'directories': {
                'src': {
                    'purpose': 'Source code',
                    'files': ['__init__.py'],
                    'subdirectories': {
                        'api': {
                            'purpose': 'API layer',
                            'files': ['__init__.py', 'routes.py', 'dependencies.py'],
                            'subdirectories': {}
                        },
                        'domain': {
                            'purpose': 'Domain models and logic',
                            'files': ['__init__.py'],
                            'subdirectories': {}
                        },
                        'infrastructure': {
                            'purpose': 'Infrastructure layer',
                            'files': ['__init__.py', 'database.py', 'external_apis.py'],
                            'subdirectories': {}
                        },
                        'config': {
                            'purpose': 'Configuration',
                            'files': ['__init__.py', 'settings.py'],
                            'subdirectories': {}
                        }
                    }
                },
                'tests': {
                    'purpose': 'All tests',
                    'files': ['__init__.py', 'conftest.py'],
                    'subdirectories': {}
                },
                'migrations': {
                    'purpose': 'Database migrations',
                    'files': [],
                    'subdirectories': {}
                }
            }
        }
    
    def _plan_directories(self, template: Dict[str, Any], 
                         analysis_result: Dict[str, Any]) -> List[DirectoryPlan]:
        """Plan directories based on template and analysis."""
        directories = []
        
        # Process template directories
        template_dirs = template.get('directories', {})
        directories.extend(self._process_template_directories(template_dirs, analysis_result))
        
        # Add custom directories based on analysis
        custom_dirs = self._plan_custom_directories(analysis_result)
        directories.extend(custom_dirs)
        
        return directories
    
    def _process_template_directories(self, template_dirs: Dict[str, Any], 
                                    analysis_result: Dict[str, Any], 
                                    parent_path: str = "") -> List[DirectoryPlan]:
        """Process template directories recursively."""
        directories = []
        
        for dir_name, dir_config in template_dirs.items():
            full_path = f"{parent_path}/{dir_name}" if parent_path else dir_name
            
            # Create directory plan
            dir_plan = DirectoryPlan(
                name=dir_name,
                purpose=dir_config.get('purpose', ''),
                description=dir_config.get('purpose', ''),
                files=dir_config.get('files', []).copy()
            )
            
            # Map PHP sources to this directory
            dir_plan.php_source_mapping = self._map_php_sources_to_directory(
                dir_plan, analysis_result
            )
            
            # Process subdirectories
            subdirs = dir_config.get('subdirectories', {})
            if subdirs:
                dir_plan.subdirectories = self._process_template_directories(
                    subdirs, analysis_result, full_path
                )
            
            directories.append(dir_plan)
        
        return directories
    
    def _map_php_sources_to_directory(self, dir_plan: DirectoryPlan, 
                                     analysis_result: Dict[str, Any]) -> List[str]:
        """Map PHP source files to FastAPI directory."""
        mapped_sources = []
        
        structure_analysis = analysis_result.get('structure_analysis', {})
        php_directories = structure_analysis.get('directory_structure', [])
        
        # Directory mapping logic
        purpose_mappings = {
            'API routes and endpoints': ['controller', 'api', 'endpoints'],
            'Database models': ['model', 'entity', 'entities'],
            'Pydantic schemas': ['model', 'entity', 'validation'],
            'Business logic services': ['service', 'business', 'logic'],
            'Database configuration': ['database', 'config'],
            'Core functionality': ['core', 'config', 'helper'],
            'Test files': ['test', 'tests', 'testing'],
            'Custom middleware': ['middleware', 'filter']
        }
        
        purpose_keywords = purpose_mappings.get(dir_plan.purpose, [])
        
        for php_dir in php_directories:
            php_dir_lower = php_dir.lower()
            if any(keyword in php_dir_lower for keyword in purpose_keywords):
                mapped_sources.append(php_dir)
        
        return mapped_sources
    
    def _plan_custom_directories(self, analysis_result: Dict[str, Any]) -> List[DirectoryPlan]:
        """Plan custom directories based on specific analysis findings."""
        custom_dirs = []
        
        # Check for specific PHP patterns that need custom directories
        structure_analysis = analysis_result.get('structure_analysis', {})
        php_dirs = structure_analysis.get('directory_structure', [])
        
        # Look for upload/media directories
        media_dirs = [d for d in php_dirs if any(keyword in d.lower() 
                     for keyword in ['upload', 'media', 'files', 'storage'])]
        if media_dirs:
            custom_dirs.append(DirectoryPlan(
                name='static',
                purpose='Static files and uploads',
                description='Handles file uploads and static content',
                files=['__init__.py'],
                php_source_mapping=media_dirs
            ))
        
        # Look for template/view directories
        template_dirs = [d for d in php_dirs if any(keyword in d.lower() 
                        for keyword in ['template', 'view', 'twig'])]
        if template_dirs:
            custom_dirs.append(DirectoryPlan(
                name='templates',
                purpose='Template files',
                description='Jinja2 templates (if needed)',
                files=[],
                php_source_mapping=template_dirs,
                priority=3  # Low priority for API-only projects
            ))
        
        # Look for job/task directories
        job_dirs = [d for d in php_dirs if any(keyword in d.lower() 
                   for keyword in ['job', 'task', 'queue', 'worker'])]
        if job_dirs:
            custom_dirs.append(DirectoryPlan(
                name='tasks',
                purpose='Background tasks',
                description='Celery tasks and background jobs',
                files=['__init__.py', 'celery.py'],
                php_source_mapping=job_dirs
            ))
        
        return custom_dirs
    
    def _plan_files(self, directories: List[DirectoryPlan], 
                   analysis_result: Dict[str, Any]) -> List[FilePlan]:
        """Plan files for each directory."""
        files = []
        
        # Plan files for each directory
        for directory in directories:
            dir_files = self._plan_directory_files(directory, analysis_result)
            files.extend(dir_files)
        
        # Plan root-level files
        root_files = self._plan_root_files(analysis_result)
        files.extend(root_files)
        
        return files
    
    def _plan_directory_files(self, directory: DirectoryPlan, 
                             analysis_result: Dict[str, Any]) -> List[FilePlan]:
        """Plan files for a specific directory."""
        files = []
        
        # Get base files from directory plan
        for file_name in directory.files:
            file_plan = FilePlan(
                name=file_name,
                path=f"{directory.name}/{file_name}",
                purpose=self._determine_file_purpose(file_name, directory.purpose),
                content_type=self._determine_content_type(file_name)
            )
            
            # Map PHP source files
            file_plan.php_source_files = self._map_php_files_to_fastapi_file(
                file_plan, directory, analysis_result
            )
            
            # Set template
            file_plan.template_used = self.file_templates.get(file_name)
            
            files.append(file_plan)
        
        # Add dynamic files based on analysis
        dynamic_files = self._plan_dynamic_files_for_directory(directory, analysis_result)
        files.extend(dynamic_files)
        
        return files
    
    def _plan_dynamic_files_for_directory(self, directory: DirectoryPlan, 
                                         analysis_result: Dict[str, Any]) -> List[FilePlan]:
        """Plan dynamic files based on analysis for a directory."""
        files = []
        
        if 'endpoints' in directory.name.lower():
            # Create endpoint files based on API analysis
            files.extend(self._plan_endpoint_files(directory, analysis_result))
        elif 'models' in directory.name.lower():
            # Create model files based on database analysis
            files.extend(self._plan_model_files(directory, analysis_result))
        elif 'schemas' in directory.name.lower():
            # Create schema files based on API analysis
            files.extend(self._plan_schema_files(directory, analysis_result))
        elif 'services' in directory.name.lower():
            # Create service files based on business logic analysis
            files.extend(self._plan_service_files(directory, analysis_result))
        
        return files
    
    def _plan_endpoint_files(self, directory: DirectoryPlan, 
                            analysis_result: Dict[str, Any]) -> List[FilePlan]:
        """Plan endpoint files based on API analysis."""
        files = []
        
        endpoint_analysis = analysis_result.get('endpoint_analysis', {})
        endpoint_categories = endpoint_analysis.get('endpoint_categories', [])
        
        for category in endpoint_categories:
            category_name = category.get('category', 'general').lower()
            file_name = f"{category_name.replace(' ', '_')}.py"
            
            file_plan = FilePlan(
                name=file_name,
                path=f"{directory.name}/{file_name}",
                purpose=f"Endpoints for {category.get('category', 'general')}",
                content_type='python',
                template_used='fastapi_routes',
                priority=1 if category.get('complexity') == 'high' else 2
            )
            
            files.append(file_plan)
        
        return files
    
    def _plan_model_files(self, directory: DirectoryPlan, 
                         analysis_result: Dict[str, Any]) -> List[FilePlan]:
        """Plan model files based on database analysis."""
        files = []
        
        database_analysis = analysis_result.get('database_analysis', {})
        tables = database_analysis.get('tables', [])
        
        # Group tables by domain/category
        table_groups = self._group_tables_by_domain(tables)
        
        for group_name, group_tables in table_groups.items():
            file_name = f"{group_name}.py"
            
            file_plan = FilePlan(
                name=file_name,
                path=f"{directory.name}/{file_name}",
                purpose=f"Models for {group_name} domain",
                content_type='python',
                template_used='sqlalchemy_models'
            )
            
            # Map PHP source tables
            file_plan.php_source_files = [table.get('name', '') for table in group_tables]
            
            files.append(file_plan)
        
        return files
    
    def _plan_schema_files(self, directory: DirectoryPlan, 
                          analysis_result: Dict[str, Any]) -> List[FilePlan]:
        """Plan schema files based on API analysis."""
        files = []
        
        endpoint_analysis = analysis_result.get('endpoint_analysis', {})
        endpoint_categories = endpoint_analysis.get('endpoint_categories', [])
        
        for category in endpoint_categories:
            category_name = category.get('category', 'general').lower()
            file_name = f"{category_name.replace(' ', '_')}.py"
            
            file_plan = FilePlan(
                name=file_name,
                path=f"{directory.name}/{file_name}",
                purpose=f"Schemas for {category.get('category', 'general')}",
                content_type='python',
                template_used='pydantic_schemas'
            )
            
            files.append(file_plan)
        
        return files
    
    def _plan_service_files(self, directory: DirectoryPlan, 
                           analysis_result: Dict[str, Any]) -> List[FilePlan]:
        """Plan service files based on business logic analysis."""
        files = []
        
        # Create services based on endpoint categories
        endpoint_analysis = analysis_result.get('endpoint_analysis', {})
        endpoint_categories = endpoint_analysis.get('endpoint_categories', [])
        
        for category in endpoint_categories:
            category_name = category.get('category', 'general').lower()
            file_name = f"{category_name.replace(' ', '_')}_service.py"
            
            file_plan = FilePlan(
                name=file_name,
                path=f"{directory.name}/{file_name}",
                purpose=f"Service for {category.get('category', 'general')} business logic",
                content_type='python'
            )
            
            files.append(file_plan)
        
        return files
    
    def _plan_root_files(self, analysis_result: Dict[str, Any]) -> List[FilePlan]:
        """Plan root-level files."""
        files = []
        
        root_files = [
            ('main.py', 'Application entry point', 'python', 'fastapi_main'),
            ('requirements.txt', 'Python dependencies', 'text', None),
            ('.env', 'Environment variables', 'config', None),
            ('.gitignore', 'Git ignore rules', 'text', None),
            ('README.md', 'Project documentation', 'markdown', None),
            ('Dockerfile', 'Docker configuration', 'config', None)
        ]
        
        for file_name, purpose, content_type, template in root_files:
            file_plan = FilePlan(
                name=file_name,
                path=file_name,
                purpose=purpose,
                content_type=content_type,
                template_used=template
            )
            files.append(file_plan)
        
        # Add conditional files
        database_analysis = analysis_result.get('database_analysis', {})
        if database_analysis.get('migration_files'):
            files.append(FilePlan(
                name='alembic.ini',
                path='alembic.ini',
                purpose='Alembic configuration',
                content_type='config'
            ))
        
        return files
    
    def _group_tables_by_domain(self, tables: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group database tables by domain/functionality."""
        groups = {
            'user': [],
            'auth': [],
            'content': [],
            'system': [],
            'other': []
        }
        
        for table in tables:
            table_name = table.get('name', '').lower()
            
            if any(keyword in table_name for keyword in ['user', 'profile', 'account']):
                groups['user'].append(table)
            elif any(keyword in table_name for keyword in ['auth', 'token', 'session', 'login']):
                groups['auth'].append(table)
            elif any(keyword in table_name for keyword in ['post', 'article', 'content', 'page']):
                groups['content'].append(table)
            elif any(keyword in table_name for keyword in ['config', 'setting', 'system', 'log']):
                groups['system'].append(table)
            else:
                groups['other'].append(table)
        
        # Remove empty groups
        return {k: v for k, v in groups.items() if v}
    
    def _determine_file_purpose(self, file_name: str, directory_purpose: str) -> str:
        """Determine the purpose of a file."""
        if file_name == '__init__.py':
            return f"Package initialization for {directory_purpose}"
        elif file_name.endswith('.py'):
            base_name = file_name[:-3]
            return f"{base_name.title()} module for {directory_purpose}"
        else:
            return f"Configuration file for {directory_purpose}"
    
    def _determine_content_type(self, file_name: str) -> str:
        """Determine the content type of a file."""
        if file_name.endswith('.py'):
            return 'python'
        elif file_name.endswith(('.yml', '.yaml')):
            return 'yaml'
        elif file_name.endswith('.json'):
            return 'json'
        elif file_name.endswith('.md'):
            return 'markdown'
        elif file_name.endswith('.txt'):
            return 'text'
        elif file_name in ['.env', '.gitignore', 'Dockerfile']:
            return 'config'
        else:
            return 'text'
    
    def _map_php_files_to_fastapi_file(self, file_plan: FilePlan, 
                                      directory: DirectoryPlan, 
                                      analysis_result: Dict[str, Any]) -> List[str]:
        """Map PHP source files to FastAPI file."""
        mapped_files = []
        
        # Use directory mappings
        for php_source in directory.php_source_mapping:
            # Find actual PHP files in this source directory
            # This would need to be implemented based on file analysis
            mapped_files.append(php_source)
        
        return mapped_files
    
    def _create_migration_mapping(self, analysis_result: Dict[str, Any], 
                                 plan: StructurePlan) -> Dict[str, str]:
        """Create mapping from PHP structure to FastAPI structure."""
        mapping = {}
        
        structure_analysis = analysis_result.get('structure_analysis', {})
        php_directories = structure_analysis.get('directory_structure', [])
        
        # Map PHP directories to FastAPI directories
        for php_dir in php_directories:
            php_dir_lower = php_dir.lower()
            
            # Find matching FastAPI directory
            for fastapi_dir in plan.directories:
                if any(php_keyword in php_dir_lower 
                      for php_keyword in fastapi_dir.php_source_mapping):
                    mapping[php_dir] = fastapi_dir.name
                    break
            else:
                # Default mapping for unmapped directories
                if 'controller' in php_dir_lower:
                    mapping[php_dir] = 'app/api/v1/endpoints'
                elif 'model' in php_dir_lower:
                    mapping[php_dir] = 'app/models'
                elif 'view' in php_dir_lower:
                    mapping[php_dir] = 'templates'
                elif 'config' in php_dir_lower:
                    mapping[php_dir] = 'app/core'
                else:
                    mapping[php_dir] = 'app'
        
        return mapping
    
    def _generate_structure_recommendations(self, analysis_result: Dict[str, Any], 
                                          plan: StructurePlan) -> List[str]:
        """Generate recommendations for the structure plan."""
        recommendations = []
        
        # Template-based recommendations
        if plan.organization_pattern == 'minimal':
            recommendations.append(
                "Consider upgrading to standard structure as the project grows"
            )
        elif plan.organization_pattern == 'enterprise':
            recommendations.append(
                "Enterprise structure chosen due to project complexity - ensure team is familiar with the architecture"
            )
        
        # File organization recommendations
        endpoint_analysis = analysis_result.get('endpoint_analysis', {})
        total_endpoints = endpoint_analysis.get('total_endpoints', 0)
        
        if total_endpoints > 30:
            recommendations.append(
                "Consider grouping endpoints by feature/domain rather than just by category"
            )
        
        # Database recommendations
        database_analysis = analysis_result.get('database_analysis', {})
        total_tables = len(database_analysis.get('tables', []))
        
        if total_tables > 20:
            recommendations.append(
                "Consider organizing models into separate modules by domain"
            )
        
        # Testing recommendations
        recommendations.append(
            "Implement comprehensive test coverage with unit, integration, and API tests"
        )
        
        # Documentation recommendations
        recommendations.append(
            "Maintain clear API documentation using FastAPI's automatic OpenAPI generation"
        )
        
        # Security recommendations
        endpoint_analysis = analysis_result.get('endpoint_analysis', {})
        auth_methods = endpoint_analysis.get('authentication_methods', [])
        
        if auth_methods:
            recommendations.append(
                "Implement proper authentication and authorization middleware"
            )
        
        return recommendations
    
    def get_directory_tree_visualization(self, plan: StructurePlan) -> str:
        """Generate a text-based directory tree visualization."""
        lines = []
        lines.append(f"{plan.root_directory}/")
        
        # Add root files
        root_files = [f for f in plan.files if '/' not in f.path]
        for file_plan in sorted(root_files, key=lambda x: x.name):
            lines.append(f"├── {file_plan.name}")
        
        # Add directories
        root_dirs = [d for d in plan.directories if '/' not in d.name]
        for i, directory in enumerate(sorted(root_dirs, key=lambda x: x.name)):
            is_last_dir = i == len(root_dirs) - 1
            prefix = "└── " if is_last_dir else "├── "
            lines.append(f"{prefix}{directory.name}/")
            
            # Add directory files
            dir_files = [f for f in plan.files if f.path.startswith(f"{directory.name}/") 
                        and f.path.count('/') == 1]
            
            for j, file_plan in enumerate(sorted(dir_files, key=lambda x: x.name)):
                file_prefix = "    " if is_last_dir else "│   "
                is_last_file = j == len(dir_files) - 1 and not directory.subdirectories
                file_char = "└── " if is_last_file else "├── "
                lines.append(f"{file_prefix}{file_char}{file_plan.name}")
            
            # Add subdirectories (simplified for readability)
            for k, subdir in enumerate(directory.subdirectories):
                subdir_prefix = "    " if is_last_dir else "│   "
                is_last_subdir = k == len(directory.subdirectories) - 1
                subdir_char = "└── " if is_last_subdir else "├── "
                lines.append(f"{subdir_prefix}{subdir_char}{subdir.name}/")
        
        return "\n".join(lines)