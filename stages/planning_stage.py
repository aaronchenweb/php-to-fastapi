# stages/planning_stage.py
"""Stage 2: Conversion Planning for PHP to FastAPI using modular planners."""

from typing import Dict, Any, List, Optional

from core.llm_client import LLMClient
from core.user_interface import UserInterface
from config.prompts import Prompts

# Import modular planners
from planners.conversion_planner import ConversionPlanner
from planners.structure_planner import StructurePlanner
from planners.dependency_planner import DependencyPlanner
from planners.migration_planner import MigrationPlanner


class PlanningStage:
    """Handles the planning stage of PHP to FastAPI conversion using modular planners."""
    
    def __init__(self, llm_client: LLMClient, prompts: Prompts, ui: UserInterface):
        self.llm_client = llm_client
        self.prompts = prompts
        self.ui = ui
        
        # Initialize modular planners
        self.conversion_planner = ConversionPlanner()
        self.structure_planner = StructurePlanner()
        self.dependency_planner = DependencyPlanner()
        self.migration_planner = MigrationPlanner()
    
    def prepare_local_planning(self, analysis_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Prepare local planning data based on analysis results using modular planners.
        
        Args:
            analysis_result: Results from the analysis stage
            
        Returns:
            Dictionary containing planning preparation data
        """
        try:
            self.ui.debug("Starting modular planning preparation...")
            
            # 1. Overall Conversion Planning
            self.ui.debug("Creating conversion plan...")
            conversion_plan = self.conversion_planner.create_conversion_plan(analysis_result)
            
            # 2. Project Structure Planning
            self.ui.debug("Planning project structure...")
            structure_plan = self.structure_planner.plan_structure(analysis_result)
            
            # 3. Dependency Planning
            self.ui.debug("Planning dependencies...")
            dependency_plan = self.dependency_planner.plan_dependencies(analysis_result)
            
            # 4. Database Migration Planning
            self.ui.debug("Planning database migration...")
            migration_plan = self.migration_planner.plan_migration(analysis_result)
            
            # 5. Additional Planning (configuration, testing, etc.)
            self.ui.debug("Planning configuration and testing strategies...")
            config_strategy = self._plan_configuration_approach(analysis_result)
            testing_strategy = self._plan_testing_approach(analysis_result)
            
            # Compile comprehensive planning data
            planning_data = {
                'conversion_strategy': {
                    'approach': conversion_plan.approach.value,
                    'complexity_level': conversion_plan.complexity_level,
                    'risk_level': conversion_plan.risk_level,
                    'estimated_duration': conversion_plan.estimated_duration,
                    'conversion_phases': [
                        {
                            'name': phase.get('name', ''),
                            'description': phase.get('description', ''),
                            'duration': phase.get('duration', ''),
                            'deliverables': phase.get('deliverables', []),
                            'prerequisites': phase.get('prerequisites', []),
                            'risks': phase.get('risks', [])
                        }
                        for phase in conversion_plan.phases
                    ],
                    'prerequisites': conversion_plan.prerequisites,
                    'success_criteria': conversion_plan.success_criteria,
                    'rollback_strategy': conversion_plan.rollback_strategy
                },
                'project_structure': {
                    'organization_pattern': structure_plan.organization_pattern,
                    'root_directory': structure_plan.root_directory,
                    'main_directories': [
                        {
                            'name': dir_plan.name,
                            'purpose': dir_plan.purpose,
                            'php_equivalent': ', '.join(dir_plan.php_source_mapping) if dir_plan.php_source_mapping else 'N/A',
                            'files': dir_plan.files,
                            'priority': dir_plan.priority
                        }
                        for dir_plan in structure_plan.directories
                    ],
                    'key_files': [
                        {
                            'filename': file_plan.name,
                            'path': file_plan.path,
                            'purpose': file_plan.purpose,
                            'content_type': file_plan.content_type,
                            'dependencies': file_plan.dependencies,
                            'php_sources': file_plan.php_source_files
                        }
                        for file_plan in structure_plan.files
                    ],
                    'migration_mapping': structure_plan.migration_mapping,
                    'recommendations': structure_plan.recommendations
                },
                'dependency_conversion': {
                    'total_dependencies': dependency_plan.total_dependencies,
                    'estimated_install_time': dependency_plan.estimated_install_time,
                    'requirements_files': dependency_plan.requirements_files,
                    'dependency_groups': [
                        {
                            'name': group.name,
                            'description': group.description,
                            'optional': group.optional,
                            'priority': group.priority,
                            'dependencies': [
                                {
                                    'package': dep.name,
                                    'version': dep.version_spec,
                                    'purpose': dep.purpose,
                                    'category': dep.category,
                                    'php_equivalent': dep.php_equivalent,
                                    'required': dep.is_required,
                                    'alternatives': dep.alternatives,
                                    'migration_complexity': dep.migration_complexity
                                }
                                for dep in group.dependencies
                            ]
                        }
                        for group in dependency_plan.groups
                    ],
                    'potential_conflicts': dependency_plan.potential_conflicts,
                    'migration_notes': dependency_plan.migration_notes
                },
                'database_migration_plan': {
                    'strategy': migration_plan.strategy.value,
                    'data_approach': migration_plan.data_approach.value,
                    'estimated_duration': migration_plan.estimated_total_duration,
                    'downtime_required': migration_plan.downtime_required,
                    'table_migrations': [
                        {
                            'php_table': table.php_table_name,
                            'python_table': table.python_table_name,
                            'python_model': table.python_model_name,
                            'priority': table.migration_priority,
                            'complexity': table.migration_complexity,
                            'schema_changes': table.schema_changes,
                            'data_transformations': table.data_transformations,
                            'validation_queries': table.validation_queries,
                            'rollback_strategy': table.rollback_strategy
                        }
                        for table in migration_plan.table_migrations
                    ],
                    'migration_phases': [
                        {
                            'name': phase.name,
                            'description': phase.description,
                            'tables': phase.tables,
                            'estimated_duration': phase.estimated_duration,
                            'prerequisites': phase.prerequisites,
                            'validation_steps': phase.validation_steps,
                            'rollback_plan': phase.rollback_plan
                        }
                        for phase in migration_plan.migration_phases
                    ],
                    'validation_strategy': migration_plan.validation_strategy,
                    'rollback_strategy': migration_plan.rollback_strategy,
                    'risk_assessment': migration_plan.risk_assessment,
                    'recommendations': migration_plan.recommendations
                },
                'configuration_strategy': config_strategy,
                'testing_strategy': testing_strategy,
                'overall_recommendations': self._compile_overall_recommendations(
                    conversion_plan, structure_plan, dependency_plan, migration_plan
                )
            }
            
            self.ui.debug("Modular planning preparation completed successfully")
            return planning_data
            
        except Exception as e:
            self.ui.error(f"Modular planning preparation failed: {str(e)}")
            import traceback
            self.ui.debug(f"Traceback: {traceback.format_exc()}")
            return None
    
    def get_llm_planning(self, 
                        analysis_result: Dict[str, Any], 
                        local_planning: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Send planning data to LLM for detailed conversion planning.
        
        Args:
            analysis_result: Results from analysis stage
            local_planning: Local planning preparation results
            
        Returns:
            LLM planning results, or None if failed
        """
        try:
            # Display local planning results first
            self._display_local_planning_results(local_planning)
            
            # Ask user if they want to proceed to LLM planning
            if not self.ui.confirm("📤 Send local planning to LLM for enhancement?", default=True):
                self.ui.warning("LLM planning skipped by user.")
                return self._convert_local_to_llm_format(local_planning)
            
            # Get system prompt
            system_prompt = self.prompts.get_system_prompt()
            
            # Get planning prompt with analysis and local planning data
            user_prompt = self.prompts.get_planning_prompt(analysis_result, local_planning)
            
            # Send to LLM
            self.ui.debug("Sending planning request to LLM...")
            response = self.llm_client.generate_response(
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )
            
            if not response.success:
                self.ui.show_llm_error(response.error_message, "planning")
                self.ui.warning("Using local planning results only.")
                return self._convert_local_to_llm_format(local_planning)
            
            # Parse JSON response
            llm_planning = self.llm_client.parse_json_response(response)
            
            # Display LLM results and comparison
            self._display_llm_planning_results(llm_planning)
            self._display_planning_comparison(local_planning, llm_planning)
            
            self.ui.debug("LLM planning completed successfully")
            return llm_planning
            
        except Exception as e:
            self.ui.error(f"LLM planning failed: {str(e)}")
            self.ui.warning("Using local planning results only.")
            return self._convert_local_to_llm_format(local_planning)
    
    def _display_local_planning_results(self, local_planning: Dict[str, Any]) -> None:
        """Display local planning results to the user."""
        self.ui.info("\n" + "=" * 80)
        self.ui.info("📊 LOCAL PLANNING RESULTS (Before LLM Enhancement)")
        self.ui.info("=" * 80)
        
        # Display conversion strategy
        conversion_strategy = local_planning.get('conversion_strategy', {})
        self.ui.info(f"🎯 CONVERSION STRATEGY:")
        self.ui.info(f"   • Approach: {conversion_strategy.get('approach', 'Unknown')}")
        self.ui.info(f"   • Complexity: {conversion_strategy.get('complexity_level', 'Unknown')}")
        self.ui.info(f"   • Risk Level: {conversion_strategy.get('risk_level', 'Unknown')}")
        self.ui.info(f"   • Duration: {conversion_strategy.get('estimated_duration', 'Unknown')}")
        self.ui.info(f"   • Phases: {len(conversion_strategy.get('conversion_phases', []))}")
        
        # Display project structure
        project_structure = local_planning.get('project_structure', {})
        self.ui.info(f"\n🏗️  PROJECT STRUCTURE:")
        self.ui.info(f"   • Pattern: {project_structure.get('organization_pattern', 'Unknown')}")
        self.ui.info(f"   • Directories: {len(project_structure.get('main_directories', []))}")
        self.ui.info(f"   • Files Planned: {len(project_structure.get('key_files', []))}")
        
        # Display dependency planning
        dependency_conversion = local_planning.get('dependency_conversion', {})
        self.ui.info(f"\n📦 DEPENDENCY PLANNING:")
        self.ui.info(f"   • Total Dependencies: {dependency_conversion.get('total_dependencies', 0)}")
        self.ui.info(f"   • Install Time: {dependency_conversion.get('estimated_install_time', 'Unknown')}")
        self.ui.info(f"   • Dependency Groups: {len(dependency_conversion.get('dependency_groups', []))}")
        self.ui.info(f"   • Potential Conflicts: {len(dependency_conversion.get('potential_conflicts', []))}")
        
        # Display database migration
        db_migration = local_planning.get('database_migration_plan', {})
        self.ui.info(f"\n🗄️  DATABASE MIGRATION:")
        self.ui.info(f"   • Strategy: {db_migration.get('strategy', 'Unknown')}")
        self.ui.info(f"   • Data Approach: {db_migration.get('data_approach', 'Unknown')}")
        self.ui.info(f"   • Duration: {db_migration.get('estimated_duration', 'Unknown')}")
        self.ui.info(f"   • Downtime: {db_migration.get('downtime_required', 'Unknown')}")
        self.ui.info(f"   • Tables to Migrate: {len(db_migration.get('table_migrations', []))}")
        
        # Display key recommendations
        recommendations = local_planning.get('overall_recommendations', [])
        if recommendations:
            self.ui.info(f"\n💡 KEY RECOMMENDATIONS:")
            for rec in recommendations[:5]:  # Show top 5
                self.ui.info(f"   • {rec}")
        
        self.ui.info("=" * 80)
    
    def _display_llm_planning_results(self, llm_planning: Dict[str, Any]) -> None:
        """Display LLM planning results."""
        self.ui.info("\n" + "=" * 80)
        self.ui.info("🤖 LLM ENHANCED PLANNING RESULTS")
        self.ui.info("=" * 80)
        
        # Display enhanced conversion strategy
        if 'conversion_strategy' in llm_planning:
            strategy = llm_planning['conversion_strategy']
            self.ui.info(f"🎯 ENHANCED CONVERSION STRATEGY:")
            self.ui.info(f"   • Approach: {strategy.get('approach', 'Unknown')}")
            self.ui.info(f"   • Timeline: {strategy.get('estimated_timeline', 'Unknown')}")
            self.ui.info(f"   • Risk Level: {strategy.get('risk_level', 'Unknown')}")
            
            phases = strategy.get('conversion_order', [])
            if phases:
                self.ui.info(f"   • Conversion Order: {' → '.join(phases)}")
        
        # Display API conversion plan
        if 'api_conversion_plan' in llm_planning:
            api_plan = llm_planning['api_conversion_plan']
            self.ui.info(f"\n🌐 API CONVERSION PLAN:")
            self.ui.info(f"   • Routing Strategy: {api_plan.get('routing_strategy', 'Unknown')}")
            endpoints = api_plan.get('endpoint_mappings', [])
            self.ui.info(f"   • Endpoints to Convert: {len(endpoints)}")
            middleware = api_plan.get('middleware_plan', [])
            self.ui.info(f"   • Middleware Required: {len(middleware)}")
        
        # Display database migration plan
        if 'database_migration_plan' in llm_planning:
            db_plan = llm_planning['database_migration_plan']
            self.ui.info(f"\n🗄️  DATABASE MIGRATION PLAN:")
            self.ui.info(f"   • Setup: {db_plan.get('database_setup', 'Unknown')}")
            self.ui.info(f"   • ORM Choice: {db_plan.get('orm_choice', 'Unknown')}")
            self.ui.info(f"   • Strategy: {db_plan.get('migration_strategy', 'Unknown')}")
        
        self.ui.info("=" * 80)
    
    def _display_planning_comparison(self, local_planning: Dict[str, Any], 
                                   llm_planning: Dict[str, Any]) -> None:
        """Display comparison between local and LLM planning."""
        self.ui.info("\n" + "=" * 80)
        self.ui.info("🔍 LOCAL vs LLM PLANNING COMPARISON")
        self.ui.info("=" * 80)
        
        # Compare conversion approaches
        local_approach = local_planning.get('conversion_strategy', {}).get('approach', 'Unknown')
        llm_approach = llm_planning.get('conversion_strategy', {}).get('approach', 'Unknown')
        
        self.ui.info(f"📊 CONVERSION APPROACH:")
        self.ui.info(f"   • Local Planning:  {local_approach}")
        self.ui.info(f"   • LLM Planning:    {llm_approach}")
        if local_approach != llm_approach:
            self.ui.warning(f"   ⚠️  Conversion approach differs!")
        
        # Compare estimated durations
        local_duration = local_planning.get('conversion_strategy', {}).get('estimated_duration', 'Unknown')
        llm_duration = llm_planning.get('conversion_strategy', {}).get('estimated_timeline', 'Unknown')
        
        self.ui.info(f"\n⏱️  ESTIMATED DURATION:")
        self.ui.info(f"   • Local Estimate:  {local_duration}")
        self.ui.info(f"   • LLM Estimate:    {llm_duration}")
        
        # Compare risk levels
        local_risk = local_planning.get('conversion_strategy', {}).get('risk_level', 'Unknown')
        llm_risk = llm_planning.get('conversion_strategy', {}).get('risk_level', 'Unknown')
        
        self.ui.info(f"\n⚠️  RISK ASSESSMENT:")
        self.ui.info(f"   • Local Assessment: {local_risk}")
        self.ui.info(f"   • LLM Assessment:   {llm_risk}")
        
        # Show LLM enhancements
        self.ui.info(f"\n💡 LLM ENHANCEMENTS:")
        
        # Implementation notes (LLM only)
        impl_notes = llm_planning.get('implementation_notes', {})
        if impl_notes:
            critical_points = impl_notes.get('critical_conversion_points', [])
            if critical_points:
                self.ui.info(f"   • Critical Points Identified: {len(critical_points)}")
            
            breaking_changes = impl_notes.get('potential_breaking_changes', [])
            if breaking_changes:
                self.ui.info(f"   • Breaking Changes Identified: {len(breaking_changes)}")
        
        # Deployment considerations (LLM only)
        deployment = llm_planning.get('deployment_considerations', {})
        if deployment:
            self.ui.info(f"   • Deployment Options: {len(deployment.get('deployment_options', []))}")
            self.ui.info(f"   • Security Implementations: {len(deployment.get('security_implementations', []))}")
        
        self.ui.info("=" * 80)
    
    def _convert_local_to_llm_format(self, local_planning: Dict[str, Any]) -> Dict[str, Any]:
        """Convert local planning to LLM-expected format when LLM is skipped."""
        conversion_strategy = local_planning.get('conversion_strategy', {})
        project_structure = local_planning.get('project_structure', {})
        dependency_conversion = local_planning.get('dependency_conversion', {})
        db_migration = local_planning.get('database_migration_plan', {})
        
        return {
            'conversion_strategy': {
                'approach': conversion_strategy.get('approach', 'incremental'),
                'conversion_order': [phase.get('name', f'Phase {i+1}') 
                                   for i, phase in enumerate(conversion_strategy.get('conversion_phases', []))],
                'estimated_timeline': conversion_strategy.get('estimated_duration', '4-6 weeks'),
                'risk_level': conversion_strategy.get('risk_level', 'medium')
            },
            'project_structure': {
                'root_directory': project_structure.get('root_directory', 'fastapi_project'),
                'main_directories': project_structure.get('main_directories', []),
                'key_files': project_structure.get('key_files', [])
            },
            'api_conversion_plan': {
                'routing_strategy': 'fastapi_router',
                'endpoint_mappings': [],  # Would be populated from analysis
                'middleware_plan': [
                    {
                        'middleware_type': 'authentication',
                        'implementation': 'JWT Bearer Token',
                        'php_equivalent': 'PHP auth middleware'
                    },
                    {
                        'middleware_type': 'cors',
                        'implementation': 'FastAPI CORSMiddleware',
                        'php_equivalent': 'CORS headers'
                    }
                ]
            },
            'database_migration_plan': {
                'database_setup': db_migration.get('strategy', 'direct_conversion'),
                'orm_choice': 'sqlalchemy',
                'migration_strategy': db_migration.get('data_approach', 'full_export_import'),
                'model_mappings': db_migration.get('table_migrations', [])
            },
            'dependency_conversion': {
                'requirements_txt': dependency_conversion.get('dependency_groups', []),
                'dev_dependencies': [
                    'pytest>=7.4.0',
                    'pytest-asyncio>=0.21.0',
                    'black>=23.0.0',
                    'isort>=5.12.0'
                ],
                'optional_dependencies': ['redis>=5.0.0', 'celery>=5.3.0']
            },
            'configuration_plan': local_planning.get('configuration_strategy', {}),
            'testing_strategy': local_planning.get('testing_strategy', {}),
            'deployment_considerations': {
                'deployment_options': ['docker', 'gunicorn', 'uvicorn'],
                'performance_optimizations': ['async endpoints', 'connection pooling'],
                'security_implementations': ['JWT authentication', 'input validation'],
                'monitoring_setup': ['logging', 'health checks']
            },
            'implementation_notes': {
                'critical_conversion_points': ['Authentication system', 'Database migration', 'API endpoints'],
                'potential_breaking_changes': ['API response format changes', 'Authentication method changes'],
                'fallback_strategies': ['Rollback to PHP', 'Gradual migration'],
                'validation_checkpoints': ['Unit tests', 'Integration tests', 'Performance tests']
            }
        }
    
    def _compile_overall_recommendations(self, conversion_plan, structure_plan, 
                                       dependency_plan, migration_plan) -> List[str]:
        """Compile overall recommendations from all planners."""
        recommendations = []
        
        # From conversion planner
        recommendations.extend([
            f"Follow {conversion_plan.approach.value} approach for conversion",
            f"Plan for {conversion_plan.estimated_duration} conversion timeline",
            f"Risk level is {conversion_plan.risk_level} - plan accordingly"
        ])
        
        # From structure planner
        recommendations.extend(structure_plan.recommendations[:3])  # Top 3
        
        # From dependency planner
        if dependency_plan.potential_conflicts:
            recommendations.append("Review dependency conflicts before installation")
        if dependency_plan.total_dependencies > 20:
            recommendations.append("Consider using dependency groups for organized installation")
        
        # From migration planner
        recommendations.extend(migration_plan.recommendations[:3])  # Top 3
        
        # Remove duplicates and limit
        unique_recommendations = list(dict.fromkeys(recommendations))
        return unique_recommendations[:10]  # Top 10 overall
    
    def _plan_configuration_approach(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Plan configuration management approach."""
        project_info = analysis_result.get('project_info', {})
        config_files = project_info.get('config_files', [])
        
        # Basic configuration strategy
        environment_variables = [
            {
                'name': 'DATABASE_URL',
                'purpose': 'Database connection string',
                'default_value': 'sqlite:///./app.db'
            },
            {
                'name': 'SECRET_KEY',
                'purpose': 'Application secret key',
                'default_value': 'your-secret-key-here'
            },
            {
                'name': 'DEBUG',
                'purpose': 'Debug mode flag',
                'default_value': 'false'
            }
        ]
        
        return {
            'environment_variables': environment_variables,
            'config_files': [
                {
                    'filename': '.env',
                    'format': 'env',
                    'purpose': 'Environment-specific variables'
                },
                {
                    'filename': 'app/core/config.py',
                    'format': 'python',
                    'purpose': 'Application configuration class'
                }
            ],
            'configuration_strategy': 'pydantic_settings'
        }
    
    def _plan_testing_approach(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Plan testing strategy."""
        endpoint_analysis = analysis_result.get('endpoint_analysis', {})
        total_endpoints = endpoint_analysis.get('total_endpoints', 0)
        
        coverage_target = 80 if total_endpoints > 10 else 90
        
        return {
            'testing_framework': 'pytest',
            'test_types': ['unit', 'integration', 'api'],
            'coverage_target': f'{coverage_target}%',
            'test_file_structure': 'mirror_app_structure',
            'testing_tools': [
                'pytest-asyncio for async testing',
                'httpx for API testing',
                'pytest-cov for coverage reporting'
            ]
        }