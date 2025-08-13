# core/user_interface.py - Enhanced for local analysis display
"""User interface for interactive conversion process with enhanced local analysis display."""

import json
import sys
from typing import Dict, Any, Optional, List
from datetime import datetime
import textwrap


class UserInterface:
    """Handles user interaction during conversion process."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.width = 80  # Terminal width for formatting
    
    def show_welcome_message(self) -> None:
        """Display welcome message."""
        print("=" * self.width)
        print("🔄 PHP to FastAPI Converter".center(self.width))
        print("=" * self.width)
        print()
        print("This tool will help you convert your PHP web API to a FastAPI application.")
        print("The process involves analysis, planning, and generation stages with LLM assistance.")
        print()
    
    def show_project_info(self, php_path: str, output_path: str) -> None:
        """Display project information."""
        print("📁 Project Information:")
        print(f"   Source PHP Project: {php_path}")
        print(f"   Output Directory:   {output_path}")
        print()
    
    def info(self, message: str) -> None:
        """Display info message."""
        print(f"ℹ️  {message}")
    
    def success(self, message: str) -> None:
        """Display success message."""
        print(f"✅ {message}")
    
    def warning(self, message: str) -> None:
        """Display warning message."""
        print(f"⚠️  {message}")
    
    def error(self, message: str) -> None:
        """Display error message."""
        print(f"❌ {message}")
    
    def debug(self, message: str) -> None:
        """Display debug message if verbose mode is enabled."""
        if self.verbose:
            print(f"🔍 DEBUG: {message}")
    
    def show_stage_header(self, stage_name: str, stage_number: int) -> None:
        """Display stage header."""
        print("\n" + "=" * self.width)
        print(f"Stage {stage_number}: {stage_name}".center(self.width))
        print("=" * self.width)
        print()
    
    def show_progress(self, message: str) -> None:
        """Show progress message."""
        print(f"⏳ {message}")
    
    def show_section_header(self, title: str, emoji: str = "📊") -> None:
        """Show a section header with emoji."""
        print(f"\n{emoji} {title.upper()}:")
        print("-" * (len(title) + 4))
    
    def show_metric(self, label: str, value: Any, indent: int = 0) -> None:
        """Show a formatted metric."""
        spaces = "   " * indent
        print(f"{spaces}• {label}: {value}")
    
    def show_list_items(self, items: List[str], label: str = "", indent: int = 1) -> None:
        """Show a list of items with proper indentation."""
        if label:
            self.show_metric(label, "", indent - 1)
        spaces = "   " * indent
        for item in items:
            print(f"{spaces}- {item}")
    
    def show_local_analysis_header(self) -> None:
        """Show header for local analysis results."""
        print("\n" + "=" * self.width)
        print("📊 LOCAL ANALYSIS RESULTS (Before LLM Enhancement)".center(self.width))
        print("=" * self.width)
    
    def show_llm_analysis_header(self) -> None:
        """Show header for LLM analysis results."""
        print("\n" + "=" * self.width)
        print("🤖 LLM ENHANCED ANALYSIS RESULTS".center(self.width))
        print("=" * self.width)
    
    def show_comparison_header(self) -> None:
        """Show header for analysis comparison."""
        print("\n" + "=" * self.width)
        print("🔍 LOCAL vs LLM ANALYSIS COMPARISON".center(self.width))
        print("=" * self.width)
    
    def show_analysis_summary(self, analysis_data: Dict[str, Any]) -> None:
        """Display analysis summary to user."""
        print("\n" + "-" * self.width)
        print("📊 ANALYSIS SUMMARY")
        print("-" * self.width)
        
        if 'project_summary' in analysis_data:
            summary = analysis_data['project_summary']
            print(f"Framework Detected:    {summary.get('framework_detected', 'Unknown')}")
            print(f"PHP Version:          {summary.get('php_version_estimated', 'Unknown')}")
            print(f"Architecture Pattern: {summary.get('architecture_pattern', 'Unknown')}")
            print(f"Complexity Level:     {summary.get('complexity_level', 'Unknown')}")
            print(f"API Type:            {summary.get('api_type', 'Unknown')}")
        
        if 'endpoints_analysis' in analysis_data:
            endpoints = analysis_data['endpoints_analysis']
            print(f"\nEndpoints Found:      {endpoints.get('total_endpoints', 0)}")
            print(f"HTTP Methods:         {', '.join(endpoints.get('http_methods_used', []))}")
            print(f"Auth Methods:         {', '.join(endpoints.get('authentication_methods', []))}")
        
        if 'database_analysis' in analysis_data:
            db = analysis_data['database_analysis']
            print(f"\nDatabase Type:        {db.get('database_type', 'Unknown')}")
            print(f"ORM Framework:        {db.get('orm_framework', 'None')}")
            print(f"Tables Estimated:     {db.get('tables_estimated', 0)}")
        
        if 'recommendations' in analysis_data:
            rec = analysis_data['recommendations']
            print(f"\nConversion Effort:    {rec.get('estimated_conversion_effort', 'Unknown')}")
            print(f"Suggested Structure:  {rec.get('suggested_fastapi_structure', 'Standard')}")
        
        print("-" * self.width)
    
    def show_planning_summary(self, planning_data: Dict[str, Any]) -> None:
        """Display planning summary to user."""
        print("\n" + "-" * self.width)
        print("📋 CONVERSION PLAN SUMMARY")
        print("-" * self.width)
        
        if 'conversion_strategy' in planning_data:
            strategy = planning_data['conversion_strategy']
            print(f"Approach:            {strategy.get('approach', 'Unknown')}")
            print(f"Conversion Order:    {' → '.join(strategy.get('conversion_order', []))}")
            print(f"Estimated Timeline:  {strategy.get('estimated_timeline', 'Unknown')}")
            print(f"Risk Level:          {strategy.get('risk_level', 'Unknown')}")
        
        if 'api_conversion_plan' in planning_data:
            api_plan = planning_data['api_conversion_plan']
            print(f"\nRouting Strategy:    {api_plan.get('routing_strategy', 'Unknown')}")
            endpoints = api_plan.get('endpoint_mappings', [])
            print(f"Endpoints to Convert: {len(endpoints)}")
        
        if 'database_migration_plan' in planning_data:
            db_plan = planning_data['database_migration_plan']
            print(f"\nDatabase Setup:      {db_plan.get('database_setup', 'Unknown')}")
            print(f"ORM Choice:          {db_plan.get('orm_choice', 'Unknown')}")
            print(f"Migration Strategy:  {db_plan.get('migration_strategy', 'Unknown')}")
        
        if 'dependency_conversion' in planning_data:
            deps = planning_data['dependency_conversion']
            requirements = deps.get('requirements_txt', [])
            print(f"\nPython Dependencies: {len(requirements)} packages")
        
        print("-" * self.width)
    
    def show_detailed_analysis(self, analysis_data: Dict[str, Any]) -> None:
        """Show detailed analysis information."""
        if not self.verbose:
            return
        
        print("\n" + "=" * self.width)
        print("DETAILED ANALYSIS RESULTS")
        print("=" * self.width)
        
        for key, value in analysis_data.items():
            print(f"\n{key.upper().replace('_', ' ')}:")
            if isinstance(value, dict):
                self._print_dict(value, indent=2)
            elif isinstance(value, list):
                self._print_list(value, indent=2)
            else:
                print(f"  {value}")
    
    def show_detailed_planning(self, planning_data: Dict[str, Any]) -> None:
        """Show detailed planning information."""
        if not self.verbose:
            return
        
        print("\n" + "=" * self.width)
        print("DETAILED CONVERSION PLAN")
        print("=" * self.width)
        
        for key, value in planning_data.items():
            print(f"\n{key.upper().replace('_', ' ')}:")
            if isinstance(value, dict):
                self._print_dict(value, indent=2)
            elif isinstance(value, list):
                self._print_list(value, indent=2)
            else:
                print(f"  {value}")
    
    def show_comparison_metric(self, label: str, local_value: str, llm_value: str, differs: bool = False) -> None:
        """Show a comparison metric between local and LLM analysis."""
        print(f"\n📊 {label.upper()}:")
        print(f"   • Local Analysis:  {local_value}")
        print(f"   • LLM Analysis:    {llm_value}")
        if differs:
            print(f"   ⚠️  Values differ!")
    
    def show_enhancement_section(self, title: str, items: List[str]) -> None:
        """Show LLM enhancements section."""
        if items:
            print(f"\n💡 {title.upper()}:")
            for item in items:
                print(f"   • {item}")
    
    def show_json_preview(self, data: Dict[str, Any], title: str, max_length: int = 1000) -> None:
        """Show a preview of JSON data."""
        print(f"\n🔧 {title}:")
        json_str = json.dumps(data, indent=2, default=str)
        if len(json_str) > max_length:
            json_str = json_str[:max_length] + "..."
        print(json_str)
    
    def _print_dict(self, data: Dict[str, Any], indent: int = 0) -> None:
        """Print dictionary with proper indentation."""
        prefix = " " * indent
        for key, value in data.items():
            if isinstance(value, dict):
                print(f"{prefix}{key}:")
                self._print_dict(value, indent + 2)
            elif isinstance(value, list):
                print(f"{prefix}{key}:")
                self._print_list(value, indent + 2)
            else:
                print(f"{prefix}{key}: {value}")
    
    def _print_list(self, data: List[Any], indent: int = 0) -> None:
        """Print list with proper indentation."""
        prefix = " " * indent
        for item in data:
            if isinstance(item, dict):
                print(f"{prefix}-")
                self._print_dict(item, indent + 2)
            elif isinstance(item, list):
                print(f"{prefix}-")
                self._print_list(item, indent + 2)
            else:
                print(f"{prefix}- {item}")
    
    def confirm(self, message: str, default: bool = True) -> bool:
        """Ask user for confirmation."""
        default_text = "Y/n" if default else "y/N"
        
        while True:
            try:
                response = input(f"\n❓ {message} [{default_text}]: ").strip().lower()
                
                if not response:
                    return default
                
                if response in ['y', 'yes', 'true', '1']:
                    return True
                elif response in ['n', 'no', 'false', '0']:
                    return False
                else:
                    print("   Please enter 'y' for yes or 'n' for no.")
                    
            except KeyboardInterrupt:
                print("\n\nOperation cancelled by user.")
                return False
            except EOFError:
                print("\nUsing default value.")
                return default
    
    def get_user_approval(self, stage_name: str, data: Dict[str, Any]) -> bool:
        """Get user approval for stage results."""
        print(f"\n🔍 Please review the {stage_name} results above.")
        print("\nOptions:")
        print("  ✅ Approve and continue to next stage")
        print("  ❌ Reject and stop conversion")
        
        if self.verbose:
            print("  📄 Show detailed results")
        
        while True:
            try:
                choice = input(f"\nWhat would you like to do? [approve/reject{'  /details' if self.verbose else ''}]: ").strip().lower()
                
                if choice in ['a', 'approve', 'yes', 'y']:
                    return True
                elif choice in ['r', 'reject', 'no', 'n']:
                    return False
                elif self.verbose and choice in ['d', 'details', 'show']:
                    if stage_name.lower() == 'analysis':
                        self.show_detailed_analysis(data)
                    else:
                        self.show_detailed_planning(data)
                    continue
                else:
                    valid_options = "approve/reject"
                    if self.verbose:
                        valid_options += "/details"
                    print(f"   Please enter one of: {valid_options}")
                    
            except KeyboardInterrupt:
                print("\n\nOperation cancelled by user.")
                return False
            except EOFError:
                print("\nRejecting by default.")
                return False
    
    def show_llm_error(self, error_message: str, stage_name: str) -> None:
        """Display LLM error message."""
        print(f"\n❌ LLM Error in {stage_name} stage:")
        print(f"   {error_message}")
        print("\nPossible solutions:")
        print("   • Check your API key and internet connection")
        print("   • Verify the LLM provider configuration")
        print("   • Try again in a few moments")
        print("   • Switch to a different LLM provider")
    
    def show_generation_progress(self, current_file: str, total_files: int, current_index: int) -> None:
        """Show file generation progress."""
        percentage = (current_index / total_files) * 100 if total_files > 0 else 0
        print(f"📝 Generating [{current_index}/{total_files}] ({percentage:.1f}%): {current_file}")
    
    def show_completion_summary(self, output_path: str, files_generated: List[str]) -> None:
        """Show conversion completion summary."""
        print("\n" + "=" * self.width)
        print("🎉 CONVERSION COMPLETED SUCCESSFULLY!")
        print("=" * self.width)
        print(f"\n📁 Generated FastAPI project in: {output_path}")
        print(f"📄 Files created: {len(files_generated)}")
        
        if self.verbose and files_generated:
            print("\nGenerated files:")
            for file_path in files_generated:
                print(f"   • {file_path}")
        
        print("\n🚀 Next steps:")
        print("   1. Navigate to the output directory")
        print("   2. Review the generated code")
        print("   3. Install dependencies: pip install -r requirements.txt")
        print("   4. Configure environment variables")
        print("   5. Run the API: uvicorn main:app --reload")
        print()
    
    def show_dry_run_summary(self, analysis_data: Dict[str, Any], planning_data: Dict[str, Any]) -> None:
        """Show dry run summary without generating files."""
        print("\n" + "=" * self.width)
        print("📋 DRY RUN COMPLETED")
        print("=" * self.width)
        print("\nThe conversion analysis and planning have been completed.")
        print("No files were generated because this was a dry run.")
        print("\nTo generate the actual FastAPI project, run the command again without --dry-run.")
        print()
    
    def ask_retry(self, operation: str) -> bool:
        """Ask user if they want to retry an operation."""
        return self.confirm(f"Would you like to retry the {operation}?", default=True)