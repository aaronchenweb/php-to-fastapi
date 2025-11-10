# core/orchestrator.py
"""Orchestrator for managing the complete PHP to FastAPI conversion workflow."""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path

from config.settings import Settings
from config.prompts import Prompts
from core.detector import PHPProjectDetector
from core.llm_client import LLMClient
from core.user_interface import UserInterface
from stages.analysis_stage import AnalysisStage
from stages.planning_stage import PlanningStage
from stages.generation_stage import GenerationStage


class ConversionOrchestrator:
    """Orchestrates the complete conversion workflow."""
    
    def __init__(self, settings: Settings, ui: UserInterface):
        self.settings = settings
        self.ui = ui
        self.prompts = Prompts()
        
        # Initialize components
        self.detector = PHPProjectDetector()
        self.llm_client = LLMClient(settings)
        
        # Initialize stages
        self.analysis_stage = AnalysisStage(self.detector, self.llm_client, self.prompts, self.ui)
        self.planning_stage = PlanningStage(self.llm_client, self.prompts, self.ui)
        self.generation_stage = GenerationStage(self.settings, self.ui)
        
        # Workflow state
        self.analysis_result: Optional[Dict[str, Any]] = None
        self.planning_result: Optional[Dict[str, Any]] = None
    
    def convert_project(self, 
                       php_project_path: str, 
                       output_path: str, 
                       dry_run: bool = False) -> bool:
        """
        Execute the complete conversion workflow.
        
        Args:
            php_project_path: Path to PHP project to convert
            output_path: Path where FastAPI project will be generated
            dry_run: If True, only perform analysis and planning without generating files
            
        Returns:
            True if conversion completed successfully, False otherwise
        """
        try:
            self.ui.info(f"Starting conversion of PHP project: {php_project_path}")
            
            # # Validate LLM connection
            # if not self._validate_llm_connection():
            #     return False
            
            # Stage 1: Analysis
            if not self._execute_analysis_stage(php_project_path):
                return False
            
            # Stage 2: Planning
            if not self._execute_planning_stage():
                return False
            
            # Stage 3: Generation (skip if dry run)
            if not dry_run:
                if not self._execute_generation_stage(output_path):
                    return False
            else:
                self.ui.show_dry_run_summary(self.analysis_result, self.planning_result)
            
            return True
            
        except KeyboardInterrupt:
            self.ui.warning("Conversion interrupted by user.")
            return False
        except Exception as e:
            self.ui.error(f"Unexpected error during conversion: {str(e)}")
            if self.ui.verbose:
                import traceback
                traceback.print_exc()
            return False
    
    def _validate_llm_connection(self) -> bool:
        """Validate LLM connection and configuration."""
        self.ui.show_progress("Validating LLM connection...")
        try:
            if not self.llm_client.validate_provider_config():
                self.ui.error("Failed to connect to LLM provider.")
                self.ui.error("Please check your API key and provider configuration.")
                return False
            
            provider_info = self.llm_client.get_provider_info()
            self.ui.success(f"Connected to {provider_info['provider']} with model {provider_info['model']}")
            return True
            
        except Exception as e:
            self.ui.error(f"LLM validation failed: {str(e)}")
            return False
    
    def _execute_analysis_stage(self, php_project_path: str) -> bool:
        """Execute Stage 1: Analysis."""
        self.ui.show_stage_header("Analysis & Understanding", 1)
        
        try:
            # Perform local analysis
            self.ui.show_progress("Analyzing PHP project structure...")
            local_analysis = self.analysis_stage.perform_local_analysis(php_project_path)
            
            if not local_analysis:
                self.ui.error("Failed to analyze PHP project structure.")
                return False
            
            self.ui.success("Local analysis completed.")
            
            # Send to LLM for understanding
            self.ui.show_progress("Sending analysis to LLM for understanding...")
            llm_analysis = self.analysis_stage.get_llm_analysis(local_analysis)
            
            if not llm_analysis:
                self.ui.error("Failed to get LLM analysis.")
                if self.ui.ask_retry("analysis stage"):
                    return self._execute_analysis_stage(php_project_path)
                return False
            
            self.ui.success("LLM analysis completed.")
            
            # Show results to user
            self.ui.show_analysis_summary(llm_analysis)
            if self.ui.verbose:
                self.ui.show_detailed_analysis(llm_analysis)
            
            # Get user approval
            if not self.ui.get_user_approval("analysis", llm_analysis):
                self.ui.warning("Analysis stage rejected by user.")
                return False
            
            self.analysis_result = llm_analysis
            self.ui.success("Analysis stage approved by user.")
            return True
            
        except Exception as e:
            self.ui.error(f"Error in analysis stage: {str(e)}")
            if self.ui.ask_retry("analysis stage"):
                return self._execute_analysis_stage(php_project_path)
            return False
    
    def _execute_planning_stage(self) -> bool:
        """Execute Stage 2: Planning."""
        self.ui.show_stage_header("Conversion Planning", 2)
        
        if not self.analysis_result:
            self.ui.error("No analysis result available for planning stage.")
            return False
        
        try:
            # Perform local planning preparation
            self.ui.show_progress("Preparing conversion planning data...")
            local_planning = self.planning_stage.prepare_local_planning(self.analysis_result)
            
            if not local_planning:
                self.ui.error("Failed to prepare planning data.")
                return False
            
            self.ui.success("Local planning preparation completed.")
            
            # Send to LLM for conversion planning
            self.ui.show_progress("Sending planning data to LLM for conversion strategy...")
            llm_planning = self.planning_stage.get_llm_planning(self.analysis_result, local_planning)
            
            if not llm_planning:
                self.ui.error("Failed to get LLM planning.")
                if self.ui.ask_retry("planning stage"):
                    return self._execute_planning_stage()
                return False
            
            self.ui.success("LLM planning completed.")
            
            # Show results to user
            self.ui.show_planning_summary(llm_planning)
            if self.ui.verbose:
                self.ui.show_detailed_planning(llm_planning)
            
            # Get user approval
            if not self.ui.get_user_approval("planning", llm_planning):
                self.ui.warning("Planning stage rejected by user.")
                return False
            
            self.planning_result = llm_planning
            self.ui.success("Planning stage approved by user.")
            return True
            
        except Exception as e:
            self.ui.error(f"Error in planning stage: {str(e)}")
            if self.ui.ask_retry("planning stage"):
                return self._execute_planning_stage()
            return False
    
    def _execute_generation_stage(self, output_path: str) -> bool:
        """Execute Stage 3: Generation."""
        self.ui.show_stage_header("FastAPI Code Generation", 3)
        
        if not self.analysis_result or not self.planning_result:
            self.ui.error("Analysis or planning results not available for generation.")
            return False
        
        try:
            # Prepare output directory
            self.ui.show_progress("Preparing output directory...")
            if not self._prepare_output_directory(output_path):
                return False
            
            # Generate FastAPI project
            self.ui.show_progress("Generating FastAPI project structure...")
            generated_files = self.generation_stage.generate_fastapi_project(
                analysis_result=self.analysis_result,
                planning_result=self.planning_result,
                output_path=output_path
            )
            
            if not generated_files:
                self.ui.error("Failed to generate FastAPI project.")
                return False
            
            self.ui.success(f"Generated {len(generated_files)} files.")
            
            # Create backup of original PHP project if requested
            if self.settings.conversion.backup_original:
                self.ui.show_progress("Creating backup of original PHP project...")
                # TODO: Implement backup functionality
                self.ui.success("Backup created.")
            
            # Show completion summary
            self.ui.show_completion_summary(output_path, generated_files)
            return True
            
        except Exception as e:
            self.ui.error(f"Error in generation stage: {str(e)}")
            return False
    
    def _prepare_output_directory(self, output_path: str) -> bool:
        """Prepare the output directory for generation."""
        try:
            output_dir = Path(output_path)
            
            # Check if directory exists and is not empty
            if output_dir.exists():
                if any(output_dir.iterdir()):
                    if not self.ui.confirm(
                        f"Output directory '{output_path}' is not empty. "
                        "Files may be overwritten. Continue?"
                    ):
                        return False
            else:
                # Create directory
                output_dir.mkdir(parents=True, exist_ok=True)
                self.ui.debug(f"Created output directory: {output_path}")
            
            # Verify write permissions
            test_file = output_dir / ".write_test"
            try:
                test_file.write_text("test")
                test_file.unlink()
            except Exception:
                self.ui.error(f"No write permission to output directory: {output_path}")
                return False
            
            return True
            
        except Exception as e:
            self.ui.error(f"Failed to prepare output directory: {str(e)}")
            return False
    
    def get_conversion_status(self) -> Dict[str, Any]:
        """Get current conversion status."""
        return {
            'analysis_completed': self.analysis_result is not None,
            'planning_completed': self.planning_result is not None,
            'analysis_result': self.analysis_result,
            'planning_result': self.planning_result,
            'settings': {
                'llm_provider': self.settings.llm.provider,
                'llm_model': self.settings.llm.model,
                'output_dir': self.settings.conversion.default_output_dir,
                'backup_enabled': self.settings.conversion.backup_original,
                'tests_enabled': self.settings.conversion.generate_tests
            }
        }
    
    def reset_conversion_state(self) -> None:
        """Reset conversion state to start fresh."""
        self.analysis_result = None
        self.planning_result = None
        self.ui.info("Conversion state reset.")
    
    def save_session_state(self, file_path: str) -> bool:
        """Save current session state to file."""
        try:
            state = self.get_conversion_status()
            with open(file_path, 'w') as f:
                json.dump(state, f, indent=2)
            self.ui.debug(f"Session state saved to: {file_path}")
            return True
        except Exception as e:
            self.ui.error(f"Failed to save session state: {str(e)}")
            return False
    
    def load_session_state(self, file_path: str) -> bool:
        """Load session state from file."""
        try:
            if not os.path.exists(file_path):
                self.ui.warning(f"Session state file not found: {file_path}")
                return False
            
            with open(file_path, 'r') as f:
                state = json.load(f)
            
            self.analysis_result = state.get('analysis_result')
            self.planning_result = state.get('planning_result')
            
            self.ui.info("Session state loaded successfully.")
            self.ui.debug(f"Analysis completed: {state.get('analysis_completed', False)}")
            self.ui.debug(f"Planning completed: {state.get('planning_completed', False)}")
            return True
            
        except Exception as e:
            self.ui.error(f"Failed to load session state: {str(e)}")
            return False