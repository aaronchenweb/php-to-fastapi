# stages/generation_stage.py
"""Stage 3: FastAPI Code Generation with user review and transparency."""

import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

from config.settings import Settings
from core.user_interface import UserInterface

# Import generators
from generators.llm_assisted_generator import LLMAssistedGenerator
from generators.code_batch_processor import CodeBatchProcessor
from generators.endpoint_converter import EndpointConverter
from generators.business_logic_translator import BusinessLogicTranslator
from generators.auth_converter import AuthConverter
from generators.model_generator import ModelGenerator
from generators.schema_generator import SchemaGenerator
from generators.project_assembler import ProjectAssembler


class GenerationStage:
    """Handles the generation stage of PHP to FastAPI conversion with user review."""
    
    def __init__(self, settings: Settings, ui: UserInterface):
        self.settings = settings
        self.ui = ui
        
        # Initialize generators
        self.llm_generator = LLMAssistedGenerator(settings, ui)
        self.batch_processor = CodeBatchProcessor(settings, ui)
        self.endpoint_converter = EndpointConverter(settings, ui)
        self.business_logic_translator = BusinessLogicTranslator(settings, ui)
        self.auth_converter = AuthConverter(settings, ui)
        self.model_generator = ModelGenerator(settings, ui)
        self.schema_generator = SchemaGenerator(settings, ui)
        self.project_assembler = ProjectAssembler(settings, ui)
        
        # Track generated files and results for final summary
        self.generation_results = {
            'structure_files': [],
            'auth_files': [],
            'model_files': [],
            'schema_files': [],
            'endpoint_files': [],
            'logic_files': [],
            'config_files': [],
            'main_files': [],
            'support_files': [],
            'total_files': 0
        }
    
    def generate_fastapi_project(self, 
                                analysis_result: Dict[str, Any],
                                planning_result: Dict[str, Any], 
                                output_path: str) -> List[str]:
        """
        Generate complete FastAPI project with user review at each stage.
        
        Args:
            analysis_result: Results from analysis stage
            planning_result: Results from planning stage
            output_path: Output directory path
            
        Returns:
            List of generated file paths
        """
        try:
            self.ui.info("🚀 Starting FastAPI code generation with user review...")
            
            # Show generation plan overview
            self._show_generation_plan(analysis_result, planning_result)
            
            # if not self.ui.confirm("📋 Proceed with this generation plan?", default=True):
            #     self.ui.warning("Generation cancelled by user.")
            #     return []
            
            all_generated_files = []
            
            # Phase 1: Project Structure
            if not self._execute_structure_phase(planning_result, output_path, all_generated_files):
                return all_generated_files
            
            # Phase 2: Authentication System
            if not self._execute_auth_phase(analysis_result, planning_result, output_path, all_generated_files):
                return all_generated_files
            
            # Phase 3: Database Models
            if not self._execute_models_phase(analysis_result, planning_result, output_path, all_generated_files):
                return all_generated_files
            
            # Phase 4: Pydantic Schemas
            if not self._execute_schemas_phase(analysis_result, planning_result, output_path, all_generated_files):
                return all_generated_files
            
            # Phase 5: API Endpoints
            if not self._execute_endpoints_phase(analysis_result, planning_result, output_path, all_generated_files):
                return all_generated_files
            
            # Phase 6: Business Logic
            if not self._execute_logic_phase(analysis_result, planning_result, output_path, all_generated_files):
                return all_generated_files
            
            # Phase 7: Configuration
            if not self._execute_config_phase(analysis_result, planning_result, output_path, all_generated_files):
                return all_generated_files
            
            # Phase 8: Main Application
            if not self._execute_main_app_phase(analysis_result, planning_result, output_path, all_generated_files):
                return all_generated_files
            
            # Phase 9: Supporting Files
            if not self._execute_support_phase(analysis_result, planning_result, output_path, all_generated_files):
                return all_generated_files
            
            # Final summary and review
            self._show_generation_summary(all_generated_files, output_path)
            
            self.ui.success(f"✅ Generated {len(all_generated_files)} files successfully!")
            return all_generated_files
            
        except Exception as e:
            self.ui.error(f"Generation failed: {str(e)}")
            import traceback
            self.ui.debug(f"Traceback: {traceback.format_exc()}")
            return []
    
    def _show_generation_plan(self, analysis_result: Dict[str, Any], 
                             planning_result: Dict[str, Any]) -> None:
        """Show the generation plan to the user."""
        self.ui.info("\n" + "=" * 80)
        self.ui.info("📋 FASTAPI GENERATION PLAN")
        self.ui.info("=" * 80)
    
    def _show_project_structure_preview(self, output_path: str) -> None:
        """Show a comprehensive preview of the generated project structure."""
        try:
            self.ui.info(f"\n🏗️  PROJECT STRUCTURE PREVIEW:")
            self.ui.info("   " + "=" * 60)
            
            # Walk through the generated structure
            for root, dirs, files in os.walk(output_path):
                # Skip hidden directories and __pycache__
                dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
                
                level = root.replace(output_path, '').count(os.sep)
                indent = '   ' + '  ' * level
                folder_name = os.path.basename(root) or os.path.basename(output_path)
                
                # Show more levels (up to 4 instead of 3)
                if level <= 4:
                    self.ui.info(f"{indent}📁 {folder_name}/")
                    
                    # Show files in this directory  
                    file_indent = '   ' + '  ' * (level + 1)
                    for file in sorted(files):
                        if not file.startswith('.') and not file.endswith('.pyc'):
                            # Show files for more levels (up to 3 instead of 2)
                            if level <= 3:
                                icon = self._get_file_icon(file)
                                file_size = ""
                                try:
                                    if os.path.exists(os.path.join(root, file)):
                                        size_bytes = os.path.getsize(os.path.join(root, file))
                                        if size_bytes > 1024:
                                            file_size = f" ({size_bytes//1024}KB)"
                                        elif size_bytes > 0:
                                            file_size = f" ({size_bytes}B)"
                                except:
                                    pass
                                self.ui.info(f"{file_indent}{icon} {file}{file_size}")
                            elif level == 4:
                                # Just show count for deeper levels
                                file_count = len([f for f in files if not f.startswith('.') and not f.endswith('.pyc')])
                                if file_count > 0:
                                    self.ui.info(f"{file_indent}📄 {file_count} files")
                                break
            
            self.ui.info("   " + "=" * 60)
            
            # Show summary statistics
            total_files = 0
            total_size = 0
            file_types = {}
            
            for root, dirs, files in os.walk(output_path):
                for file in files:
                    if not file.startswith('.') and not file.endswith('.pyc'):
                        total_files += 1
                        ext = os.path.splitext(file)[1] or 'no extension'
                        file_types[ext] = file_types.get(ext, 0) + 1
                        
                        try:
                            total_size += os.path.getsize(os.path.join(root, file))
                        except:
                            pass
            
            self.ui.info(f"\n📊 PROJECT STATISTICS:")
            self.ui.info(f"   Total files: {total_files}")
            self.ui.info(f"   Total size: {total_size//1024}KB" if total_size > 1024 else f"   Total size: {total_size}B")
            
            if file_types:
                self.ui.info(f"   File types:")
                for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True):
                    self.ui.info(f"   • {ext}: {count} files")
            
        except Exception as e:
            self.ui.debug(f"Failed to show project structure: {str(e)}")
    
    def _get_file_icon(self, filename: str) -> str:
        """Get an appropriate icon for a file type."""
        if filename.endswith('.py'):
            return '🐍'
        elif filename.endswith('.md'):
            return '📄'
        elif filename.endswith('.txt'):
            return '📄'
        elif filename.endswith('.json'):
            return '⚙️'
        elif filename.endswith('.yml') or filename.endswith('.yaml'):
            return '⚙️'
        elif filename == 'Dockerfile':
            return '🐳'
        elif filename.startswith('.env'):
            return '🔧'
        elif filename == '.gitignore':
            return '📄'
        else:
            return '📄'
        
        # Show what will be generated
        project_summary = analysis_result.get('project_summary', {})
        endpoints_analysis = analysis_result.get('endpoints_analysis', {})
        db_analysis = analysis_result.get('database_analysis', {})
        
        self.ui.info(f"🏗️  Original Framework: {project_summary.get('framework_detected', 'Unknown')}")
        self.ui.info(f"🌐 API Endpoints: {endpoints_analysis.get('total_endpoints', 0)}")
        self.ui.info(f"🗄️  Database Tables: {len(db_analysis.get('table_references', []))}")
        self.ui.info(f"🔐 Authentication: {', '.join(endpoints_analysis.get('authentication_methods', ['None']))}")
        
        self.ui.info(f"\n📦 GENERATION PHASES:")
        phases = [
            "1. Project Structure & Directories",
            "2. Authentication System",
            "3. Database Models (SQLAlchemy)",
            "4. API Schemas (Pydantic)",
            "5. API Endpoints (FastAPI)",
            "6. Business Logic Services",
            "7. Configuration Files",
            "8. Main Application Setup",
            "9. Supporting Files (Docker, tests, etc.)"
        ]
        
        for phase in phases:
            self.ui.info(f"   {phase}")
        
        self.ui.info("\n💡 You'll review each phase before proceeding to the next.")
        self.ui.info("=" * 80)
    
    def _execute_structure_phase(self, planning_result: Dict[str, Any], 
                                output_path: str, all_files: List[str]) -> bool:
        """Execute Phase 1: Project Structure."""
        self.ui.show_progress("📁 Phase 1: Creating project structure...")
        
        try:
            structure_files = self.project_assembler.create_directory_structure(
                planning_result, output_path
            )
            
            if structure_files:
                self.generation_results['structure_files'] = structure_files
                all_files.extend(structure_files)
                
                self._show_phase_results("Project Structure", structure_files, 
                                       "Created FastAPI project directory structure")
                
                if not self.ui.confirm("✅ Approve project structure and continue?", default=True):
                    return False
            
            return True
            
        except Exception as e:
            self.ui.error(f"Failed to create project structure: {str(e)}")
            return False
    
    def _execute_auth_phase(self, analysis_result: Dict[str, Any], 
                           planning_result: Dict[str, Any], 
                           output_path: str, all_files: List[str]) -> bool:
        """Execute Phase 2: Authentication System."""
        self.ui.show_progress("🔐 Phase 2: Converting authentication system...")
        
        try:
            auth_info = analysis_result.get('endpoints_analysis', {}).get('authentication_methods', [])
            
            if not auth_info:
                self.ui.info("ℹ️  No authentication detected, skipping auth generation")
                return True
            
            auth_files = self.auth_converter.convert_auth_system(
                auth_info, planning_result, output_path
            )
            
            if auth_files:
                self.generation_results['auth_files'] = auth_files
                all_files.extend(auth_files)
                
                # Show generated auth code
                self._show_auth_conversion_results(auth_files, auth_info)
                
                if not self.ui.confirm("✅ Approve authentication system and continue?", default=True):
                    return False
            
            return True
            
        except Exception as e:
            self.ui.error(f"Failed to generate auth system: {str(e)}")
            return self.ui.confirm("⚠️  Continue without authentication system?", default=True)
    
    def _execute_models_phase(self, analysis_result: Dict[str, Any], 
                             planning_result: Dict[str, Any], 
                             output_path: str, all_files: List[str]) -> bool:
        """Execute Phase 3: Database Models."""
        self.ui.show_progress("🗄️  Phase 3: Generating database models...")
        
        try:
            db_info = analysis_result.get('database_analysis', {})
            
            if not db_info.get('table_references'):
                self.ui.info("ℹ️  No database tables detected, skipping model generation")
                return True
            
            model_files = self.model_generator.generate_models(
                db_info, planning_result, output_path
            )
            
            if model_files:
                self.generation_results['model_files'] = model_files
                all_files.extend(model_files)
                
                # Show generated models
                self._show_models_conversion_results(model_files, db_info)
                
                if not self.ui.confirm("✅ Approve database models and continue?", default=True):
                    return False
            
            return True
            
        except Exception as e:
            self.ui.error(f"Failed to generate database models: {str(e)}")
            return self.ui.confirm("⚠️  Continue without database models?", default=True)
    
    def _execute_schemas_phase(self, analysis_result: Dict[str, Any], 
                              planning_result: Dict[str, Any], 
                              output_path: str, all_files: List[str]) -> bool:
        """Execute Phase 4: Pydantic Schemas."""
        self.ui.show_progress("📋 Phase 4: Generating Pydantic schemas...")
        
        try:
            api_info = analysis_result.get('api_analysis', {})
            
            schema_files = self.schema_generator.generate_schemas(
                api_info, planning_result, output_path
            )
            
            if schema_files:
                self.generation_results['schema_files'] = schema_files
                all_files.extend(schema_files)
                
                # Show generated schemas
                self._show_schemas_conversion_results(schema_files, api_info)
                
                if not self.ui.confirm("✅ Approve Pydantic schemas and continue?", default=True):
                    return False
            
            return True
            
        except Exception as e:
            self.ui.error(f"Failed to generate schemas: {str(e)}")
            return self.ui.confirm("⚠️  Continue without schemas?", default=True)
    
    def _execute_endpoints_phase(self, analysis_result: Dict[str, Any], 
                                planning_result: Dict[str, Any], 
                                output_path: str, all_files: List[str]) -> bool:
        """Execute Phase 5: API Endpoints."""
        self.ui.show_progress("🌐 Phase 5: Converting API endpoints...")
        
        try:
            api_analysis = analysis_result.get('api_analysis', {})
            endpoints = api_analysis.get('endpoints_detail', [])
            
            if not endpoints:
                self.ui.warning("No API endpoints found for conversion")
                return True
            
            # Group endpoints for batch processing
            endpoint_groups = self.batch_processor.group_endpoints_for_conversion(endpoints)
            
            endpoint_files = []
            total_groups = len(endpoint_groups)
            
            for i, group in enumerate(endpoint_groups):
                self.ui.show_generation_progress(
                    f"Converting endpoint group: {group['name']}", 
                    total_groups, i + 1
                )
                
                group_files = self.endpoint_converter.convert_endpoint_group(
                    group, analysis_result, planning_result, output_path
                )
                
                if group_files:
                    endpoint_files.extend(group_files)
                    
                    # Show conversion results for this group
                    self._show_endpoint_group_results(group, group_files)
                    
                    if not self.ui.confirm(f"✅ Approve {group['name']} endpoints?", default=True):
                        # User can choose to skip this group or stop
                        if not self.ui.confirm("⚠️  Skip this group and continue?", default=True):
                            return False
            
            if endpoint_files:
                self.generation_results['endpoint_files'] = endpoint_files
                all_files.extend(endpoint_files)
                
                self._show_endpoints_summary(endpoint_files, endpoint_groups)
            
            return True
            
        except Exception as e:
            self.ui.error(f"Failed to convert API endpoints: {str(e)}")
            return self.ui.confirm("⚠️  Continue without API endpoints?", default=True)
    
    def _execute_logic_phase(self, analysis_result: Dict[str, Any], 
                            planning_result: Dict[str, Any], 
                            output_path: str, all_files: List[str]) -> bool:
        """Execute Phase 6: Business Logic."""
        self.ui.show_progress("⚙️ Phase 6: Converting business logic...")
        
        try:
            # Get PHP files for business logic conversion
            project_info = analysis_result.get('project_info', {})
            php_files = project_info.get('config_files', []) + project_info.get('entry_points', [])
            
            if not php_files:
                self.ui.info("ℹ️  No business logic files found for conversion")
                return True
            
            # Process business logic files in batches
            logic_batches = self.batch_processor.create_logic_batches(
                php_files, analysis_result
            )
            
            logic_files = []
            
            for i, batch_group in enumerate(logic_batches):
                self.ui.show_generation_progress(
                    f"Converting logic batch: {batch_group.name}", 
                    len(logic_batches), i + 1
                )
                
                for batch in batch_group.batches:
                    batch_files = self.business_logic_translator.convert_logic_batch(
                        batch, analysis_result, planning_result, output_path
                    )
                    
                    if batch_files:
                        logic_files.extend(batch_files)
                        
                        # Show conversion results for this batch
                        self._show_logic_batch_results(batch, batch_files)
            
            if logic_files:
                self.generation_results['logic_files'] = logic_files
                all_files.extend(logic_files)
                
                if not self.ui.confirm("✅ Approve business logic conversion and continue?", default=True):
                    return False
            
            return True
            
        except Exception as e:
            self.ui.error(f"Failed to convert business logic: {str(e)}")
            return self.ui.confirm("⚠️  Continue without business logic?", default=True)
    
    def _execute_config_phase(self, analysis_result: Dict[str, Any], 
                             planning_result: Dict[str, Any], 
                             output_path: str, all_files: List[str]) -> bool:
        """Execute Phase 7: Configuration."""
        self.ui.show_progress("⚙️ Phase 7: Generating configuration...")
        
        try:
            config_strategy = planning_result.get('configuration_strategy', {})
            
            config_files = self.project_assembler.generate_config_files(
                config_strategy, analysis_result, output_path
            )
            
            if config_files:
                self.generation_results['config_files'] = config_files
                all_files.extend(config_files)
                
                self._show_config_results(config_files, config_strategy)
                
                if not self.ui.confirm("✅ Approve configuration and continue?", default=True):
                    return False
            
            return True
            
        except Exception as e:
            self.ui.error(f"Failed to generate configuration: {str(e)}")
            return self.ui.confirm("⚠️  Continue without custom configuration?", default=True)
    
    def _execute_main_app_phase(self, analysis_result: Dict[str, Any], 
                               planning_result: Dict[str, Any], 
                               output_path: str, all_files: List[str]) -> bool:
        """Execute Phase 8: Main Application."""
        self.ui.show_progress("🎯 Phase 8: Generating main application...")
        
        try:
            main_files = self.project_assembler.generate_main_app(
                analysis_result, planning_result, output_path
            )
            
            if main_files:
                self.generation_results['main_files'] = main_files
                all_files.extend(main_files)
                
                self._show_main_app_results(main_files, analysis_result)
                
                if not self.ui.confirm("✅ Approve main application and continue?", default=True):
                    return False
            
            return True
            
        except Exception as e:
            self.ui.error(f"Failed to generate main application: {str(e)}")
            return False
    
    def _execute_support_phase(self, analysis_result: Dict[str, Any], 
                              planning_result: Dict[str, Any], 
                              output_path: str, all_files: List[str]) -> bool:
        """Execute Phase 9: Supporting Files."""
        self.ui.show_progress("📄 Phase 9: Generating supporting files...")
        
        try:
            support_files = self.project_assembler.generate_supporting_files(
                analysis_result, planning_result, output_path
            )
            
            if support_files:
                self.generation_results['support_files'] = support_files
                all_files.extend(support_files)
                
                self._show_support_files_results(support_files)
                
                if not self.ui.confirm("✅ Approve supporting files and finalize?", default=True):
                    return False
            
            return True
            
        except Exception as e:
            self.ui.error(f"Failed to generate supporting files: {str(e)}")
            return self.ui.confirm("⚠️  Finalize without some supporting files?", default=True)
    
    # Result display methods
    
    def _show_phase_results(self, phase_name: str, files: List[str], description: str) -> None:
        """Show results of a generation phase."""
        self.ui.info(f"\n📋 {phase_name.upper()} RESULTS:")
        self.ui.info(f"   {description}")
        self.ui.info(f"   Generated {len(files)} files:")
        
        # Show ALL files, not just first 5
        for file_path in files:
            relative_path = os.path.relpath(file_path) if os.path.exists(file_path) else file_path
            self.ui.info(f"   • {relative_path}")
    
    def _show_auth_conversion_results(self, auth_files: List[str], auth_info: List[str]) -> None:
        """Show authentication conversion results."""
        self.ui.info(f"\n🔐 AUTHENTICATION SYSTEM GENERATED:")
        self.ui.info(f"   Detected methods: {', '.join(auth_info)}")
        self.ui.info(f"   Generated {len(auth_files)} authentication files:")
        
        # Show ALL files
        for file_path in auth_files:
            file_name = os.path.basename(file_path)
            self.ui.info(f"   • {file_name}")
        
        # Show code snippets for key files
        key_files_shown = 0
        for file_path in auth_files:
            file_name = os.path.basename(file_path)
            if 'deps.py' in file_name and os.path.exists(file_path):
                self._show_file_snippet(file_path, "Authentication Dependencies")
                key_files_shown += 1
            elif 'auth.py' in file_name and 'routes' in file_path and os.path.exists(file_path):
                self._show_file_snippet(file_path, "Auth Routes")  
                key_files_shown += 1
            elif 'security.py' in file_name and os.path.exists(file_path):
                self._show_file_snippet(file_path, "Security Configuration")
                key_files_shown += 1
            
            # In verbose mode, show all files
            if self.ui.verbose and key_files_shown < 2:
                if file_name.endswith('.py') and os.path.exists(file_path):
                    self._show_file_snippet(file_path, f"Auth File: {file_name}")
                    key_files_shown += 1
    
    def _show_models_conversion_results(self, model_files: List[str], db_info: Dict[str, Any]) -> None:
        """Show database models conversion results."""
        table_refs = db_info.get('table_references', [])
        
        self.ui.info(f"\n🗄️  DATABASE MODELS GENERATED:")
        self.ui.info(f"   Tables converted: {len(table_refs)}")
        self.ui.info(f"   Generated {len(model_files)} model files:")
        
        # Show ALL model files
        for file_path in model_files:
            file_name = os.path.basename(file_path)
            self.ui.info(f"   • {file_name}")
        
        # Show snippets of model files (not just one)
        model_files_shown = 0
        for file_path in model_files:
            file_name = os.path.basename(file_path)
            if file_name.endswith('.py') and file_name != '__init__.py' and os.path.exists(file_path):
                self._show_file_snippet(file_path, f"Model: {file_name}")
                model_files_shown += 1
                
                # Show first 3 models, or all in verbose mode
                if not self.ui.verbose and model_files_shown >= 3:
                    remaining = len([f for f in model_files if f.endswith('.py') and '__init__' not in f]) - model_files_shown
                    if remaining > 0:
                        self.ui.info(f"   📋 {remaining} additional model files generated (use --verbose to see all)")
                    break
    
    def _show_schemas_conversion_results(self, schema_files: List[str], api_info: Dict[str, Any]) -> None:
        """Show Pydantic schemas conversion results."""
        self.ui.info(f"\n📋 PYDANTIC SCHEMAS GENERATED:")
        self.ui.info(f"   Generated {len(schema_files)} schema files:")
        
        # Show ALL schema files
        for file_path in schema_files:
            file_name = os.path.basename(file_path)
            self.ui.info(f"   • {file_name}")
        
        # Show snippets of schema files
        schema_files_shown = 0
        for file_path in schema_files:
            file_name = os.path.basename(file_path)
            if file_name.endswith('.py') and file_name != '__init__.py' and os.path.exists(file_path):
                self._show_file_snippet(file_path, f"Schema: {file_name}")
                schema_files_shown += 1
                
                # Show first 3 schemas, or all in verbose mode  
                if not self.ui.verbose and schema_files_shown >= 3:
                    remaining = len([f for f in schema_files if f.endswith('.py') and '__init__' not in f]) - schema_files_shown
                    if remaining > 0:
                        self.ui.info(f"   📋 {remaining} additional schema files generated (use --verbose to see all)")
                    break
    
    def _show_endpoint_group_results(self, group: Dict[str, Any], files: List[str]) -> None:
        """Show endpoint group conversion results."""
        group_name = group.get('name', 'Unknown')
        endpoints = group.get('endpoints', [])
        
        self.ui.info(f"\n🌐 ENDPOINT GROUP: {group_name.upper()}")
        self.ui.info(f"   Converted {len(endpoints)} endpoints:")
        
        # Show ALL endpoints, not just first 3
        for endpoint in endpoints:
            method = endpoint.get('method', 'GET')
            route = endpoint.get('route', '/')
            self.ui.info(f"   • {method} {route}")
        
        # Show generated file snippet
        if files and os.path.exists(files[0]):
            self._show_file_snippet(files[0], f"FastAPI Routes: {group_name}")
        
        # Show all files in this group
        if len(files) > 1:
            self.ui.info(f"   📁 Additional files in this group:")
            for file_path in files[1:]:
                self.ui.info(f"   • {os.path.basename(file_path)}")
                if self.ui.verbose and os.path.exists(file_path):
                    self._show_file_snippet(file_path, f"Additional File: {os.path.basename(file_path)}")
    
    def _show_endpoints_summary(self, endpoint_files: List[str], endpoint_groups: List[Dict[str, Any]]) -> None:
        """Show summary of all endpoint conversions."""
        total_endpoints = sum(len(group.get('endpoints', [])) for group in endpoint_groups)
        
        self.ui.info(f"\n🌐 ENDPOINTS CONVERSION SUMMARY:")
        self.ui.info(f"   Total endpoints converted: {total_endpoints}")
        self.ui.info(f"   Organized into {len(endpoint_groups)} route modules")
        self.ui.info(f"   Generated {len(endpoint_files)} endpoint files")
    
    def _show_logic_batch_results(self, batch, files: List[str]) -> None:
        """Show business logic batch conversion results."""
        if self.ui.verbose:  # Only show detailed batch results in verbose mode
            self.ui.debug(f"Converted logic batch: {batch.name}")
            self.ui.debug(f"   Type: {batch.batch_type}")
            self.ui.debug(f"   Lines: {batch.line_count}")
            self.ui.debug(f"   Generated: {len(files)} files")
    
    def _show_config_results(self, config_files: List[str], config_strategy: Dict[str, Any]) -> None:
        """Show configuration generation results."""
        self.ui.info(f"\n⚙️ CONFIGURATION GENERATED:")
        self.ui.info(f"   Generated {len(config_files)} config files")
        
        # Show key config files
        for file_path in config_files:
            if os.path.exists(file_path):
                file_name = os.path.basename(file_path)
                if file_name in ['config.py', '.env.example']:
                    self.ui.info(f"   • {file_name}")
    
    def _show_main_app_results(self, main_files: List[str], analysis_result: Dict[str, Any]) -> None:
        """Show main application generation results."""
        self.ui.info(f"\n🎯 MAIN APPLICATION GENERATED:")
        
        for file_path in main_files:
            if os.path.exists(file_path) and file_path.endswith('main.py'):
                # Show more lines for the main application file since it's crucial
                self._show_file_snippet(file_path, "FastAPI Main Application", lines=30)
            else:
                self.ui.info(f"   • {os.path.basename(file_path)}")
    
    def _show_support_files_results(self, support_files: List[str]) -> None:
        """Show supporting files generation results."""
        self.ui.info(f"\n📄 SUPPORTING FILES GENERATED:")
        self.ui.info(f"   Generated {len(support_files)} supporting files:")
        
        # Show ALL supporting files
        for file_path in support_files:
            file_name = os.path.basename(file_path)
            self.ui.info(f"   • {file_name}")
        
        # Show snippets of key supporting files
        key_files = ['requirements.txt', 'README.md', 'Dockerfile', 'docker-compose.yml', '.gitignore']
        
        for file_path in support_files:
            file_name = os.path.basename(file_path)
            if file_name in key_files and os.path.exists(file_path):
                if file_name == 'requirements.txt':
                    self._show_file_snippet(file_path, "Python Dependencies", lines=20)
                elif file_name == 'README.md':
                    self._show_file_snippet(file_path, "Project README", lines=25) 
                elif file_name == 'Dockerfile':
                    self._show_file_snippet(file_path, "Docker Configuration", lines=15)
                elif self.ui.verbose:  # Show other files only in verbose mode
                    self._show_file_snippet(file_path, f"Supporting File: {file_name}", lines=15)
    
    def _show_file_snippet(self, file_path: str, title: str, lines: int = 25) -> None:
        """Show a snippet of a generated file with full details."""
        try:
            if not os.path.exists(file_path):
                return
                
            self.ui.info(f"\n📄 {title}:")
            self.ui.info("   " + "-" * 50)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                file_lines = f.readlines()
                
                # Show more lines by default, and in verbose mode show even more
                display_lines = lines
                if self.ui.verbose:
                    display_lines = min(len(file_lines), 50)  # Show up to 50 lines in verbose mode
                
                for i, line in enumerate(file_lines[:display_lines]):
                    # Remove trailing newline and add indentation with line numbers
                    clean_line = line.rstrip('\n')
                    line_num = f"{i+1:3d}"
                    self.ui.info(f"   {line_num} │ {clean_line}")
                
                if len(file_lines) > display_lines:
                    remaining = len(file_lines) - display_lines
                    self.ui.info(f"   ... │ ... ({remaining} more lines)")
                    
                    # In verbose mode, offer to show the rest
                    if self.ui.verbose and remaining > 0:
                        if self.ui.confirm(f"📄 Show remaining {remaining} lines of {os.path.basename(file_path)}?", default=False):
                            for i, line in enumerate(file_lines[display_lines:], start=display_lines):
                                clean_line = line.rstrip('\n')
                                line_num = f"{i+1:3d}"
                                self.ui.info(f"   {line_num} │ {clean_line}")
            
            self.ui.info("   " + "-" * 50)
            
        except Exception as e:
            self.ui.debug(f"Failed to show file snippet for {file_path}: {str(e)}")
    
    def _show_generation_summary(self, all_files: List[str], output_path: str) -> None:
        """Show final generation summary."""
        self.ui.info("\n" + "=" * 80)
        self.ui.info("📊 GENERATION SUMMARY")
        self.ui.info("=" * 80)
        
        results = self.generation_results
        
        self.ui.info(f"📁 Project Structure:     {len(results['structure_files'])} files")
        self.ui.info(f"🔐 Authentication:        {len(results['auth_files'])} files")
        self.ui.info(f"🗄️  Database Models:       {len(results['model_files'])} files")
        self.ui.info(f"📋 API Schemas:           {len(results['schema_files'])} files")
        self.ui.info(f"🌐 API Endpoints:         {len(results['endpoint_files'])} files")
        self.ui.info(f"⚙️ Business Logic:        {len(results['logic_files'])} files")
        self.ui.info(f"⚙️ Configuration:         {len(results['config_files'])} files")
        self.ui.info(f"🎯 Main Application:      {len(results['main_files'])} files")
        self.ui.info(f"📄 Supporting Files:      {len(results['support_files'])} files")
        
        self.ui.info(f"\n📊 TOTAL FILES GENERATED: {len(all_files)}")
        self.ui.info(f"📁 OUTPUT DIRECTORY:      {output_path}")
        
        # Show project structure preview
        self._show_project_structure_preview(output_path)
        
        # Show option to explore individual files
        if self.ui.verbose:
            if self.ui.confirm("🔍 Explore individual generated files?", default=False):
                self._explore_generated_files(all_files, output_path)
        
        self.ui.info("=" * 80)
    
    def _explore_generated_files(self, all_files: List[str], output_path: str) -> None:
        """Allow user to explore individual generated files."""
        self.ui.info("\n📁 FILE EXPLORER:")
        self.ui.info("   Select files to view (enter number, 'q' to quit):")
        
        # Group files by type
        file_groups = {
            'Core Application': [],
            'API & Routes': [],
            'Models & Schemas': [],
            'Configuration': [],
            'Supporting Files': []
        }
        
        for file_path in all_files:
            file_name = os.path.basename(file_path)
            rel_path = os.path.relpath(file_path, output_path)
            
            if 'main.py' in file_name or 'app.py' in file_name:
                file_groups['Core Application'].append((rel_path, file_path))
            elif '/api/' in file_path or '/endpoints/' in file_path or '/routes/' in file_path:
                file_groups['API & Routes'].append((rel_path, file_path))
            elif '/models/' in file_path or '/schemas/' in file_path:
                file_groups['Models & Schemas'].append((rel_path, file_path))
            elif 'config' in file_name or '.env' in file_name or file_name.endswith('.ini'):
                file_groups['Configuration'].append((rel_path, file_path))
            else:
                file_groups['Supporting Files'].append((rel_path, file_path))
        
        file_index = 1
        file_map = {}
        
        for group_name, files in file_groups.items():
            if files:
                self.ui.info(f"\n   📂 {group_name}:")
                for rel_path, full_path in files:
                    self.ui.info(f"      {file_index}. {rel_path}")
                    file_map[str(file_index)] = (rel_path, full_path)
                    file_index += 1
        
        while True:
            try:
                choice = input(f"\n   Enter file number (1-{len(file_map)}) or 'q' to quit: ").strip()
                
                if choice.lower() == 'q':
                    break
                
                if choice in file_map:
                    rel_path, full_path = file_map[choice]
                    self.ui.show_complete_file(f"Generated File: {rel_path}", full_path)
                else:
                    self.ui.warning(f"   Invalid choice. Enter 1-{len(file_map)} or 'q'")
                    
            except (KeyboardInterrupt, EOFError):
                break