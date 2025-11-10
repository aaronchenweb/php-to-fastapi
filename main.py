#!/usr/bin/env python3
"""
PHP to FastAPI Converter
Main CLI entry point for converting PHP web APIs to FastAPI applications.
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Optional

from .php_to_fastapi.config.settings import Settings
from .php_to_fastapi.config.prompts import Prompts
from .php_to_fastapi.core.detector import PHPProjectDetector
from .php_to_fastapi.core.orchestrator import ConversionOrchestrator
from .php_to_fastapi.core.user_interface import UserInterface
# from utils.validation import ProjectValidator


def setup_argument_parser() -> argparse.ArgumentParser:
    """Set up command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Convert PHP web APIs to FastAPI applications",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s convert /path/to/php/project
  %(prog)s convert /path/to/php/project --output /custom/output/path
  %(prog)s convert /path/to/php/project --llm-provider anthropic
  %(prog)s --help

Environment Variables:
  LLM_API_KEY         API key for LLM service (required)
  LLM_PROVIDER        LLM provider (openai|anthropic|gemini) [default: openai]  
  LLM_MODEL           Model name [default: gpt-4]
  LLM_BASE_URL        Custom base URL for LLM provider (optional)
  DEFAULT_OUTPUT_DIR  Default output directory [default: ./fastapi_output]
        """
    )
    
    # Main command
    parser.add_argument(
        "command",
        choices=["convert"],
        help="Command to execute"
    )
    
    # Required arguments
    parser.add_argument(
        "php_project_path",
        type=str,
        help="Path to the PHP project directory to convert"
    )
    
    # Optional arguments
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output directory for the generated FastAPI project (default: ./fastapi_output)"
    )
    
    parser.add_argument(
        "--llm-provider",
        choices=["openai", "anthropic", "gemini"],
        help="LLM provider to use (overrides LLM_PROVIDER env var)"
    )
    
    parser.add_argument(
        "--llm-model",
        type=str,
        help="LLM model to use (overrides LLM_MODEL env var)"
    )
    
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip creating backup of original PHP project"
    )
    
    parser.add_argument(
        "--no-tests",
        action="store_true", 
        help="Skip generating test files"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform analysis and planning without generating files"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    return parser


def validate_environment() -> bool:
    """Validate that the environment is properly configured."""
    settings = Settings()
    
    if not settings.validate():
        print("❌ Configuration validation failed!")
        print("\nRequired environment variables:")
        print("  LLM_API_KEY - API key for your LLM provider")
        print("\nOptional environment variables:")
        print("  LLM_PROVIDER - LLM provider (openai|anthropic|gemini) [default: openai]")
        print("  LLM_MODEL - Model name [default: gpt-4]")
        print("  DEFAULT_OUTPUT_DIR - Output directory [default: ./fastapi_output]")
        return False
    
    return True


def validate_php_project(project_path: str) -> bool:
    """Validate that the PHP project path is valid and contains a PHP project."""
    if not os.path.exists(project_path):
        print(f"❌ Error: Path '{project_path}' does not exist")
        return False
    
    if not os.path.isdir(project_path):
        print(f"❌ Error: Path '{project_path}' is not a directory")
        return False
    
    detector = PHPProjectDetector()
    validation_result = detector.validate_project(project_path)
    
    if not validation_result.is_valid:
        print(f"❌ Error: '{project_path}' does not appear to be a valid PHP web API project")
        print(f"   Reason: {validation_result.reason}")
        if validation_result.suggestions:
            print("   Suggestions:")
            for suggestion in validation_result.suggestions:
                print(f"   • {suggestion}")
        return False
    
    return True


def apply_argument_overrides(args: argparse.Namespace) -> None:
    """Apply command line argument overrides to settings."""
    settings = Settings()
    
    # Override LLM settings
    if args.llm_provider:
        settings.llm.provider = args.llm_provider
    
    if args.llm_model:
        settings.llm.model = args.llm_model
    
    # Override conversion settings
    if args.output:
        settings.conversion.default_output_dir = args.output
    
    if args.no_backup:
        settings.conversion.backup_original = False
    
    if args.no_tests:
        settings.conversion.generate_tests = False


def main() -> int:
    """Main entry point."""
    try:
        # Parse arguments
        parser = setup_argument_parser()
        args = parser.parse_args()
        
        # Validate environment
        if not validate_environment():
            return 1
        
        # Apply argument overrides
        apply_argument_overrides(args)
        
        # Validate PHP project
        if not validate_php_project(args.php_project_path):
            return 1
        
        # Initialize components
        settings = Settings()
        ui = UserInterface(verbose=args.verbose)
        
        # Show welcome message
        ui.show_welcome_message()
        ui.show_project_info(args.php_project_path, settings.conversion.default_output_dir)
        
        # Confirm before starting
        if not args.dry_run:
            if not ui.confirm("Do you want to proceed with the conversion?"):
                ui.info("Conversion cancelled by user.")
                return 0
        
        # Initialize orchestrator and start conversion
        orchestrator = ConversionOrchestrator(settings, ui)
        
        if args.command == "convert":
            success = orchestrator.convert_project(
                php_project_path=args.php_project_path,
                output_path=settings.conversion.default_output_dir,
                dry_run=args.dry_run
            )
            
            if success:
                ui.success("✅ Conversion completed successfully!")
                if not args.dry_run:
                    ui.info(f"📁 FastAPI project generated in: {settings.conversion.default_output_dir}")
                    ui.info("🚀 Next steps:")
                    ui.info("   1. Review the generated code")
                    ui.info("   2. Install dependencies: pip install -r requirements.txt")
                    ui.info("   3. Run the API: uvicorn main:app --reload")
                return 0
            else:
                ui.error("❌ Conversion failed!")
                return 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Conversion interrupted by user.")
        return 130
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        if hasattr(args, 'verbose') and args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())