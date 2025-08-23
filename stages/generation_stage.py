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
        """Show a preview of the generated project structure."""
        try:
            self.ui.info(f"\n🏗️  PROJECT STRUCTURE PREVIEW:")
            self.ui.info("   " + "=" * 50)
            
            # Walk through the generated structure
            for root, dirs, files in os.walk(output_path):
                # Skip hidden directories and __pycache__
                dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
                
                level = root.replace(output_path, '').count(os.sep)
                indent = '   ' + '  ' * level
                folder_name = os.path.basename(root) or os.path.basename(output_path)
                
                if level <= 3:  # Only show first 3 levels
                    self.ui.info(f"{indent}📁 {folder_name}/")
                    
                    # Show files in this directory
                    file_indent = '   ' + '  ' * (level + 1)
                    for file in sorted(files):
                        if not file.startswith('.') and not file.endswith('.pyc'):
                            if level <= 2:  # Only show files for first 2 levels
                                icon = self._get_file_icon(file)
                                self.ui.info(f"{file_indent}{icon} {file}")
            
            self.ui.info("   " + "=" * 50)
            
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
        
        for file_path in files[:5]:  # Show first 5 files
            relative_path = os.path.relpath(file_path) if os.path.exists(file_path) else file_path
            self.ui.info(f"   • {relative_path}")
        
        if len(files) > 5:
            self.ui.info(f"   • ... and {len(files) - 5} more files")
    
    def _show_auth_conversion_results(self, auth_files: List[str], auth_info: List[str]) -> None:
        """Show authentication conversion results."""
        self.ui.info(f"\n🔐 AUTHENTICATION SYSTEM GENERATED:")
        self.ui.info(f"   Detected methods: {', '.join(auth_info)}")
        self.ui.info(f"   Generated {len(auth_files)} authentication files:")
        
        for file_path in auth_files:
            file_name = os.path.basename(file_path)
            self.ui.info(f"   • {file_name}")
            
            # Show a snippet of key files
            if 'deps.py' in file_name and os.path.exists(file_path):
                self._show_file_snippet(file_path, "Authentication Dependencies")
            elif 'auth.py' in file_name and 'routes' in file_path and os.path.exists(file_path):
                self._show_file_snippet(file_path, "Auth Routes")
    
    def _show_models_conversion_results(self, model_files: List[str], db_info: Dict[str, Any]) -> None:
        """Show database models conversion results."""
        table_refs = db_info.get('table_references', [])
        
        self.ui.info(f"\n🗄️  DATABASE MODELS GENERATED:")
        self.ui.info(f"   Tables converted: {len(table_refs)}")
        self.ui.info(f"   Generated {len(model_files)} model files:")
        
        for file_path in model_files:
            file_name = os.path.basename(file_path)
            self.ui.info(f"   • {file_name}")
            
            # Show snippet of a model file
            if file_name.endswith('.py') and file_name != '__init__.py' and os.path.exists(file_path):
                self._show_file_snippet(file_path, f"Model: {file_name}")
                break  # Only show one example
    
    def _show_schemas_conversion_results(self, schema_files: List[str], api_info: Dict[str, Any]) -> None:
        """Show Pydantic schemas conversion results."""
        self.ui.info(f"\n📋 PYDANTIC SCHEMAS GENERATED:")
        self.ui.info(f"   Generated {len(schema_files)} schema files:")
        
        for file_path in schema_files:
            file_name = os.path.basename(file_path)
            self.ui.info(f"   • {file_name}")
            
            # Show snippet of a schema file
            if file_name.endswith('.py') and file_name != '__init__.py' and os.path.exists(file_path):
                self._show_file_snippet(file_path, f"Schema: {file_name}")
                break  # Only show one example
    
    def _show_endpoint_group_results(self, group: Dict[str, Any], files: List[str]) -> None:
        """Show endpoint group conversion results."""
        group_name = group.get('name', 'Unknown')
        endpoints = group.get('endpoints', [])
        
        self.ui.info(f"\n🌐 ENDPOINT GROUP: {group_name.upper()}")
        self.ui.info(f"   Converted {len(endpoints)} endpoints:")
        
        for endpoint in endpoints[:3]:  # Show first 3 endpoints
            method = endpoint.get('method', 'GET')
            route = endpoint.get('route', '/')
            self.ui.info(f"   • {method} {route}")
        
        if len(endpoints) > 3:
            self.ui.info(f"   • ... and {len(endpoints) - 3} more endpoints")
        
        # Show generated file snippet
        if files and os.path.exists(files[0]):
            self._show_file_snippet(files[0], f"FastAPI Routes: {group_name}")
    
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
                self._show_file_snippet(file_path, "FastAPI Main Application", lines=15)
    
    def _show_support_files_results(self, support_files: List[str]) -> None:
        """Show supporting files generation results."""
        self.ui.info(f"\n📄 SUPPORTING FILES GENERATED:")
        self.ui.info(f"   Generated {len(support_files)} supporting files:")
        
        key_files = ['requirements.txt', 'README.md', 'Dockerfile', 'docker-compose.yml']
        
        for file_path in support_files:
            file_name = os.path.basename(file_path)
            if file_name in key_files:
                self.ui.info(f"   • {file_name}")
    
    def _show_file_snippet(self, file_path: str, title: str, lines: int = 10) -> None:
        """Show a snippet of a generated file."""
        try:
            if not os.path.exists(file_path):
                return
                
            self.ui.info(f"\n📄 {title}:")
            self.ui.info("   " + "-" * 50)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                file_lines = f.readlines()
                
                for i, line in enumerate(file_lines[:lines]):
                    # Remove trailing newline and add indentation
                    clean_line = line.rstrip('\n')
                    self.ui.info(f"   {clean_line}")
                
                if len(file_lines) > lines:
                    self.ui.info(f"   ... ({len(file_lines) - lines} more lines)")
            
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
        
        self.ui.info("=" * 80)