# stages/generation_stage.py
"""Stage 3: FastAPI Code Generation based on approved analysis and planning using modular generators."""

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

from config.settings import Settings
from core.user_interface import UserInterface

# Import from generators using the fixed structure
from generators.shared import GeneratedFile, GenerationResult
from generators.fastapi_generator import FastAPIGenerator


class GenerationStage:
    """Handles the generation stage of PHP to FastAPI conversion using modular generators."""
    
    def __init__(self, settings: Settings, ui: UserInterface):
        self.settings = settings
        self.ui = ui
        
        # Initialize the main generator (which will handle sub-generators internally)
        self.fastapi_generator = FastAPIGenerator()
        
        # Track generation progress
        self.generated_files = []
        self.generation_stats = {
            'total_files': 0,
            'total_lines': 0,
            'errors': 0,
            'warnings': 0
        }
    
    def generate_fastapi_project(self, 
                                analysis_result: Dict[str, Any],
                                planning_result: Dict[str, Any],
                                output_path: str) -> List[str]:
        """
        Generate complete FastAPI project based on approved planning using modular generators.
        
        Args:
            analysis_result: Results from analysis stage
            planning_result: Results from planning stage  
            output_path: Path where project will be generated
            
        Returns:
            List of generated file paths
        """
        try:
            self.ui.info("🎯 Starting modular code generation...")
            self.generated_files = []
            
            # Display generation plan
            self._display_generation_plan(analysis_result, planning_result)
            
            # Use FastAPIGenerator as the main coordinator
            self.ui.show_progress("Generating FastAPI project using modular generators...")
            generation_result = self.fastapi_generator.generate_project(
                analysis_result=analysis_result,
                planning_result=planning_result,
                output_path=output_path
            )
            
            if not generation_result.success:
                self.ui.error("❌ FastAPI project generation failed!")
                for error in generation_result.errors:
                    self.ui.error(f"   • {error}")
                return []
            
            # Convert GeneratedFile objects to file paths for return
            generated_file_paths = [
                os.path.join(output_path, generated_file.path) 
                for generated_file in generation_result.generated_files
            ]
            
            # Update internal tracking
            self.generated_files = generated_file_paths
            self.generation_stats.update({
                'total_files': generation_result.total_files,
                'total_lines': generation_result.total_lines,
                'errors': len(generation_result.errors),
                'warnings': len(generation_result.warnings)
            })
            
            # Display generation results
            self._display_generation_results(generation_result, output_path)
            
            # Generate additional files based on settings
            additional_files = self._generate_additional_files(
                output_path, analysis_result, planning_result
            )
            generated_file_paths.extend(additional_files)
            
            # Create backup of original PHP project if requested
            if self.settings.conversion.backup_original:
                self._create_php_backup(analysis_result)
            
            # Generate post-generation documentation
            self._generate_post_generation_docs(output_path, analysis_result, planning_result)
            
            self.ui.success(f"✅ Successfully generated {len(generated_file_paths)} files!")
            return generated_file_paths
            
        except Exception as e:
            self.ui.error(f"Code generation failed: {str(e)}")
            import traceback
            self.ui.debug(f"Traceback: {traceback.format_exc()}")
            return []
    
    def _display_generation_plan(self, 
                               analysis_result: Dict[str, Any], 
                               planning_result: Dict[str, Any]) -> None:
        """Display what will be generated."""
        self.ui.info("\n" + "=" * 80)
        self.ui.info("📋 GENERATION PLAN")
        self.ui.info("=" * 80)
        
        # Show project structure overview
        project_structure = planning_result.get('project_structure', {})
        directories = project_structure.get('main_directories', [])
        
        self.ui.info(f"🏗️  PROJECT STRUCTURE:")
        self.ui.info(f"   • Organization: Standard FastAPI structure")
        self.ui.info(f"   • Core Directories: app/, tests/, alembic/")
        
        # Show what will be generated
        endpoint_analysis = analysis_result.get('endpoint_analysis', {})
        database_analysis = analysis_result.get('database_analysis', {})
        
        self.ui.info(f"\n📁 FILES TO GENERATE:")
        
        endpoint_categories = endpoint_analysis.get('endpoint_categories', [])
        if endpoint_categories:
            self.ui.info(f"   • API Endpoints: {len(endpoint_categories)} categories")
        else:
            self.ui.info(f"   • API Endpoints: Example endpoints (no PHP endpoints found)")
            
        tables = database_analysis.get('tables', [])
        if tables:
            self.ui.info(f"   • Database Models: {len(tables)} tables")
        else:
            self.ui.info(f"   • Database Models: Example models")
            
        self.ui.info(f"   • Configuration Files: ~12 files")
        
        if self.settings.conversion.generate_tests:
            self.ui.info(f"   • Test Files: Basic test structure")
        
        # Show dependency summary
        dependency_conversion = planning_result.get('dependency_conversion', {})
        requirements = dependency_conversion.get('requirements_txt', [])
        if requirements:
            self.ui.info(f"   • Dependencies: {len(requirements)} packages")
        else:
            self.ui.info(f"   • Dependencies: Standard FastAPI packages")
        
        self.ui.info("=" * 80)
    
    def _display_generation_results(self, 
                                  generation_result: GenerationResult, 
                                  output_path: str) -> None:
        """Display generation results."""
        self.ui.info("\n" + "=" * 80)
        self.ui.info("🎉 GENERATION RESULTS")
        self.ui.info("=" * 80)
        
        self.ui.success(f"✅ Generation Status: {'SUCCESS' if generation_result.success else 'FAILED'}")
        self.ui.info(f"📁 Output Directory: {output_path}")
        self.ui.info(f"📄 Files Generated: {generation_result.total_files}")
        self.ui.info(f"📝 Lines of Code: {generation_result.total_lines}")
        
        if generation_result.errors:
            self.ui.info(f"❌ Errors: {len(generation_result.errors)}")
            for error in generation_result.errors:
                self.ui.error(f"   • {error}")
        
        if generation_result.warnings:
            self.ui.info(f"⚠️  Warnings: {len(generation_result.warnings)}")
            for warning in generation_result.warnings:
                self.ui.warning(f"   • {warning}")
        
        # Show file breakdown by type
        file_types = {}
        for file in generation_result.generated_files:
            file_type = file.file_type
            file_types[file_type] = file_types.get(file_type, 0) + 1
        
        if file_types:
            self.ui.info(f"\n📊 FILES BY TYPE:")
            for file_type, count in sorted(file_types.items()):
                self.ui.info(f"   • {file_type}: {count} files")
        
        # Show generated files if verbose
        if self.ui.verbose and generation_result.generated_files:
            self.ui.info(f"\n📋 GENERATED FILES:")
            for file in generation_result.generated_files:
                self.ui.info(f"   • {file.path} - {file.description}")
        
        self.ui.info("=" * 80)
    
    def _generate_additional_files(self, 
                                 output_path: str,
                                 analysis_result: Dict[str, Any], 
                                 planning_result: Dict[str, Any]) -> List[str]:
        """Generate additional files based on settings and requirements."""
        additional_files = []
        
        try:
            # Generate development requirements if needed
            if self.settings.conversion.generate_tests:
                dev_requirements_content = self._generate_dev_requirements(planning_result)
                dev_req_path = os.path.join(output_path, "requirements-dev.txt")
                self._write_file(dev_req_path, dev_requirements_content)
                additional_files.append(dev_req_path)
                self.ui.debug("Generated requirements-dev.txt")
            
            # Generate Makefile for common tasks
            makefile_content = self._generate_makefile(analysis_result, planning_result)
            makefile_path = os.path.join(output_path, "Makefile")
            self._write_file(makefile_path, makefile_content)
            additional_files.append(makefile_path)
            self.ui.debug("Generated Makefile")
            
            # Generate pyproject.toml for modern Python tooling
            pyproject_content = self._generate_pyproject_toml(analysis_result, planning_result)
            pyproject_path = os.path.join(output_path, "pyproject.toml")
            self._write_file(pyproject_path, pyproject_content)
            additional_files.append(pyproject_path)
            self.ui.debug("Generated pyproject.toml")
            
        except Exception as e:
            self.ui.warning(f"Failed to generate some additional files: {str(e)}")
        
        return additional_files
    
    def _generate_dev_requirements(self, planning_result: Dict[str, Any]) -> str:
        """Generate development requirements file."""
        content = """# Development Dependencies
# Install with: pip install -r requirements-dev.txt

# Testing
pytest>=7.4.3
pytest-asyncio>=0.21.1
pytest-cov>=4.1.0
httpx>=0.25.2

# Code quality
black>=23.11.0
isort>=5.12.0
flake8>=6.1.0
mypy>=1.7.1

# Pre-commit hooks
pre-commit>=3.6.0

# Documentation
sphinx>=7.2.6
sphinx-rtd-theme>=1.3.0

# Development utilities
watchdog>=3.0.0
python-dotenv>=1.0.0
"""
        
        return content.strip()
    
    def _generate_makefile(self, 
                         analysis_result: Dict[str, Any], 
                         planning_result: Dict[str, Any]) -> str:
        """Generate Makefile for common development tasks."""
        content = """# Makefile for FastAPI project
# Generated from PHP to FastAPI conversion

.PHONY: help install install-dev test lint format run clean

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \\033[36m%-20s\\033[0m %s\\n", $$1, $$2}'

install:  ## Install production dependencies
	pip install -r requirements.txt

install-dev:  ## Install development dependencies
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

test:  ## Run tests
	pytest

test-cov:  ## Run tests with coverage
	pytest --cov=app --cov-report=html --cov-report=term

lint:  ## Run linting
	flake8 app tests
	mypy app

format:  ## Format code
	black app tests
	isort app tests

run:  ## Run development server
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

clean:  ## Clean up temporary files
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
"""
        
        return content.strip()
    
    def _generate_pyproject_toml(self, 
                               analysis_result: Dict[str, Any], 
                               planning_result: Dict[str, Any]) -> str:
        """Generate pyproject.toml for modern Python tooling."""
        project_info = analysis_result.get('project_info', {})
        project_name = project_info.get('name', 'fastapi-app')
        
        content = f"""[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{project_name}"
version = "1.0.0"
description = "FastAPI application converted from PHP"
readme = "README.md"
requires-python = ">=3.8"

[tool.black]
line-length = 88
target-version = ['py38']

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88

[tool.mypy]
python_version = "3.8"
check_untyped_defs = true
disallow_any_generics = true

[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q --strict-markers"
testpaths = ["tests"]
"""
        
        return content.strip()
    
    def _create_php_backup(self, analysis_result: Dict[str, Any]) -> None:
        """Create backup of original PHP project."""
        try:
            project_info = analysis_result.get('project_info', {})
            php_root = project_info.get('root_path', '')
            
            if php_root and os.path.exists(php_root):
                import shutil
                from datetime import datetime
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"{php_root}_backup_{timestamp}"
                
                self.ui.show_progress(f"Creating backup of PHP project...")
                shutil.copytree(php_root, backup_path, ignore=shutil.ignore_patterns(
                    'vendor', 'node_modules', '.git', '*.log', 'cache', 'tmp'
                ))
                
                self.ui.success(f"PHP project backed up to: {backup_path}")
                
        except Exception as e:
            self.ui.warning(f"Failed to create PHP backup: {str(e)}")
    
    def _generate_post_generation_docs(self, 
                                     output_path: str,
                                     analysis_result: Dict[str, Any], 
                                     planning_result: Dict[str, Any]) -> None:
        """Generate post-generation documentation and instructions."""
        try:
            # Generate setup instructions
            setup_content = self._generate_setup_instructions(analysis_result, planning_result)
            setup_path = os.path.join(output_path, "SETUP.md")
            self._write_file(setup_path, setup_content)
            
            self.ui.debug("Generated post-generation documentation")
            
        except Exception as e:
            self.ui.warning(f"Failed to generate post-generation docs: {str(e)}")
    
    def _generate_setup_instructions(self, 
                                   analysis_result: Dict[str, Any], 
                                   planning_result: Dict[str, Any]) -> str:
        """Generate detailed setup instructions."""
        content = """# FastAPI Setup Instructions

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment tool (recommended)

## Step-by-Step Setup

### 1. Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\\Scripts\\activate
```

### 2. Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
nano .env  # or use your preferred editor
```

**Important:** Update these values in `.env`:
- `SECRET_KEY`: Generate a secure random key (minimum 32 characters)
- `DATABASE_URL`: Your database connection string
- `JWT_SECRET_KEY`: Another secure random key for JWT tokens

### 4. Database Setup

```bash
# Run database migrations
alembic upgrade head
```

### 5. Run the Application

```bash
# Development mode (with auto-reload)
uvicorn main:app --reload

# Or using make
make run
```

The API will be available at:
- **Application:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc

### 6. Verify Installation

```bash
# Check health endpoint
curl http://localhost:8000/health

# Run tests
pytest
```

## Next Steps

1. Review and customize the generated code
2. Implement your specific business logic
3. Add comprehensive tests
4. Set up continuous integration/deployment
5. Configure monitoring and logging
"""
        
        return content.strip()
    
    def _write_file(self, file_path: str, content: str) -> None:
        """Write content to file."""
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            self.ui.error(f"Failed to write file {file_path}: {str(e)}")
            raise
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get generation statistics."""
        return {
            'files_generated': len(self.generated_files),
            'total_lines': self.generation_stats.get('total_lines', 0),
            'errors': self.generation_stats.get('errors', 0),
            'warnings': self.generation_stats.get('warnings', 0),
            'file_paths': self.generated_files
        }
    
    def display_final_instructions(self, output_path: str) -> None:
        """Display final instructions to user."""
        self.ui.info("\n" + "🎉" * 20)
        self.ui.info("🎉 FASTAPI PROJECT GENERATED SUCCESSFULLY! 🎉")
        self.ui.info("🎉" * 20)
        
        self.ui.info(f"\n📁 Your FastAPI project is ready at: {output_path}")
        
        self.ui.info("\n🚀 NEXT STEPS:")
        self.ui.info("1. Navigate to the project directory:")
        self.ui.info(f"   cd {output_path}")
        
        self.ui.info("\n2. Set up your environment:")
        self.ui.info("   python -m venv venv")
        self.ui.info("   source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
        
        self.ui.info("\n3. Install dependencies:")
        self.ui.info("   pip install -r requirements.txt")
        
        self.ui.info("\n4. Configure environment:")
        self.ui.info("   cp .env.example .env")
        self.ui.info("   # Edit .env with your database and secret keys")
        
        self.ui.info("\n5. Run database migrations (if using a database):")
        self.ui.info("   alembic upgrade head")
        
        self.ui.info("\n6. Start the application:")
        self.ui.info("   uvicorn main:app --reload")
        
        self.ui.info("\n📚 DOCUMENTATION:")
        self.ui.info("   • API Docs: http://localhost:8000/docs")
        self.ui.info("   • Alternative Docs: http://localhost:8000/redoc")
        self.ui.info("   • Setup Guide: SETUP.md")
        
        self.ui.info("\n✅ WHAT WAS GENERATED:")
        self.ui.info(f"   • {self.generation_stats.get('total_files', 0)} files")
        self.ui.info(f"   • {self.generation_stats.get('total_lines', 0)} lines of code")
        self.ui.info("   • Complete FastAPI project structure")
        self.ui.info("   • Database models and migrations")
        self.ui.info("   • API endpoints with documentation")
        self.ui.info("   • Configuration and deployment files")
        if self.settings.conversion.generate_tests:
            self.ui.info("   • Comprehensive test suite")
        
        self.ui.info("\n📝 IMPORTANT REMINDERS:")
        self.ui.info("   • Update SECRET_KEY and JWT_SECRET_KEY in .env")
        self.ui.info("   • Review generated models for accuracy")
        self.ui.info("   • Test all endpoints thoroughly")
        self.ui.info("   • Add your specific business logic")
        self.ui.info("   • Set up proper logging and monitoring")
        
        self.ui.info("\n" + "=" * 80)