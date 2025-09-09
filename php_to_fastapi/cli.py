#!/usr/bin/env python3
"""
PHP to FastAPI Converter CLI
Main command-line interface for the php-to-fastapi conversion tool.
"""

import argparse
import sys
import os
import signal
from pathlib import Path
from typing import Optional, List

# Fixed imports for package structure
from .config.settings import Settings
from .core.detector import PHPProjectDetector
from .core.orchestrator import ConversionOrchestrator
from .core.user_interface import UserInterface
from .utils.validation import validate_project_path


class PHPCLI:
    """Main CLI application class."""
    
    def __init__(self):
        self.parser = self._create_parser()
        
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the main argument parser with subcommands."""
        # Get version
        try:
            import importlib.metadata
            version = importlib.metadata.version("php-to-fastapi")
        except:
            version = "1.0.0-dev"
            
        parser = argparse.ArgumentParser(
            prog="php2fastapi",
            description="Convert PHP web APIs to FastAPI applications with AI assistance",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=self._get_epilog()
        )
        
        parser.add_argument(
            "--version",
            action="version",
            version=f"%(prog)s {version}"
        )
        
        parser.add_argument(
            "-v", "--verbose",
            action="store_true",
            help="Enable verbose output"
        )
        
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Enable debug mode with detailed logging"
        )
        
        # Add subcommands
        subparsers = parser.add_subparsers(
            dest="command",
            help="Available commands",
            metavar="COMMAND"
        )
        
        # Convert command
        self._add_convert_command(subparsers)
        
        # Analyze command (dry run equivalent)
        self._add_analyze_command(subparsers)
        
        # Validate command
        self._add_validate_command(subparsers)
        
        return parser
    
    def _add_convert_command(self, subparsers):
        """Add the convert subcommand."""
        convert_parser = subparsers.add_parser(
            "convert",
            help="Convert PHP project to FastAPI",
            description="Convert a PHP web API project to FastAPI application"
        )
        
        convert_parser.add_argument(
            "php_project_path",
            type=str,
            help="Path to the PHP project directory to convert"
        )
        
        convert_parser.add_argument(
            "-o", "--output",
            type=str,
            help="Output directory for the generated FastAPI project"
        )
        
        convert_parser.add_argument(
            "--llm-provider",
            choices=["openai", "anthropic", "gemini"],
            help="LLM provider to use"
        )
        
        convert_parser.add_argument(
            "--llm-model",
            type=str,
            help="Specific LLM model to use"
        )
        
        convert_parser.add_argument(
            "--no-backup",
            action="store_true",
            help="Skip creating backup of original PHP project"
        )
        
        convert_parser.add_argument(
            "--no-tests",
            action="store_true",
            help="Skip generating test files"
        )
        
        convert_parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Perform analysis and planning without generating files"
        )
        
        convert_parser.add_argument(
            "--force",
            action="store_true",
            help="Force conversion without user confirmation"
        )
    
    def _add_analyze_command(self, subparsers):
        """Add the analyze subcommand (dry run)."""
        analyze_parser = subparsers.add_parser(
            "analyze",
            help="Analyze PHP project without conversion",
            description="Analyze PHP project structure and generate conversion plan"
        )
        
        analyze_parser.add_argument(
            "php_project_path",
            type=str,
            help="Path to the PHP project directory to analyze"
        )
        
        analyze_parser.add_argument(
            "--llm-provider",
            choices=["openai", "anthropic", "gemini"],
            help="LLM provider to use for analysis"
        )
    
    def _add_validate_command(self, subparsers):
        """Add the validate subcommand."""
        validate_parser = subparsers.add_parser(
            "validate",
            help="Validate PHP project compatibility",
            description="Check if PHP project is compatible for conversion"
        )
        
        validate_parser.add_argument(
            "php_project_path",
            type=str,
            help="Path to the PHP project directory to validate"
        )
        
        validate_parser.add_argument(
            "--detailed",
            action="store_true",
            help="Show detailed validation report"
        )
    
    def _get_epilog(self) -> str:
        """Get the epilog text for help."""
        return """
Examples:
  # Convert a PHP project
  php2fastapi convert /path/to/php/project
  
  # Convert with custom output directory
  php2fastapi convert /path/to/php/project -o /custom/output
  
  # Analyze project without conversion
  php2fastapi analyze /path/to/php/project
  
  # Validate project compatibility
  php2fastapi validate /path/to/php/project

Environment Variables:
  LLM_API_KEY         API key for LLM service (required)
  LLM_PROVIDER        LLM provider (openai|anthropic|gemini) [default: gemini]
  LLM_MODEL           Model name [default: gemini-2.0-flash]
        """
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            print(f"\n\nReceived signal {signum}. Shutting down gracefully...")
            sys.exit(130)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def _validate_environment(self) -> bool:
        """Validate environment configuration."""
        try:
            settings = Settings()
            if not settings.validate():
                self._show_environment_help()
                return False
            return True
        except Exception as e:
            print(f"Environment validation failed: {e}")
            self._show_environment_help()
            return False
    
    def _show_environment_help(self):
        """Show environment configuration help."""
        print("\nEnvironment Configuration Required:")
        print("="*50)
        print("Required:")
        print("  export LLM_API_KEY='your-api-key-here'")
        print("\nOptional:")
        print("  export LLM_PROVIDER='gemini'  # or 'openai', 'anthropic'")
        print("  export LLM_MODEL='gemini-2.0-flash'  # or model of choice")
    
    def _apply_argument_overrides(self, args: argparse.Namespace):
        """Apply command line argument overrides to settings."""
        settings = Settings()
        
        if hasattr(args, 'llm_provider') and args.llm_provider:
            settings.llm.provider = args.llm_provider
        
        if hasattr(args, 'llm_model') and args.llm_model:
            settings.llm.model = args.llm_model
        
        if hasattr(args, 'output') and args.output:
            settings.conversion.default_output_dir = args.output
        
        if hasattr(args, 'no_backup') and args.no_backup:
            settings.conversion.backup_original = False
        
        if hasattr(args, 'no_tests') and args.no_tests:
            settings.conversion.generate_tests = False
    
    def handle_convert_command(self, args: argparse.Namespace) -> int:
        """Handle the convert command."""
        # Validate PHP project
        if not validate_project_path(args.php_project_path):
            return 1
        
        # Apply overrides
        self._apply_argument_overrides(args)
        
        # Initialize components
        settings = Settings()
        ui = UserInterface(verbose=args.verbose)
        
        # Show welcome and project info
        ui.show_welcome_message()
        ui.show_project_info(args.php_project_path, 
                           settings.conversion.default_output_dir)
        
        # Confirm before starting (unless forced)
        if not getattr(args, 'force', False):
            if not ui.confirm("Ready to start conversion?"):
                ui.info("Conversion cancelled by user.")
                return 0
        
        # Initialize orchestrator and start conversion
        orchestrator = ConversionOrchestrator(settings, ui)
        
        success = orchestrator.convert_project(
            php_project_path=args.php_project_path,
            output_path=settings.conversion.default_output_dir,
            dry_run=getattr(args, 'dry_run', False)
        )
        
        if success:
            ui.success("Conversion completed successfully!")
            ui.info(f"FastAPI project: {settings.conversion.default_output_dir}")
            ui.info("Next steps:")
            ui.info("   1. cd " + settings.conversion.default_output_dir)
            ui.info("   2. pip install -r requirements.txt")
            ui.info("   3. uvicorn main:app --reload")
            return 0
        else:
            ui.error("Conversion failed!")
            return 1
    
    def handle_analyze_command(self, args: argparse.Namespace) -> int:
        """Handle the analyze command."""
        if not validate_project_path(args.php_project_path):
            return 1
        
        self._apply_argument_overrides(args)
        
        settings = Settings()
        ui = UserInterface(verbose=args.verbose)
        orchestrator = ConversionOrchestrator(settings, ui)
        
        ui.info("Analyzing PHP project...")
        
        # For now, just run with dry_run=True
        success = orchestrator.convert_project(
            php_project_path=args.php_project_path,
            output_path=settings.conversion.default_output_dir,
            dry_run=True
        )
        
        return 0 if success else 1
    
    def handle_validate_command(self, args: argparse.Namespace) -> int:
        """Handle the validate command."""
        detector = PHPProjectDetector()
        validation_result = detector.validate_project(args.php_project_path)
        
        if validation_result.is_valid:
            print("Project is valid for conversion!")
            if args.detailed:
                print(f"Framework detected: {validation_result.detected_framework}")
                print(f"Confidence score: {validation_result.confidence_score:.3f}")
                print(f"Files analyzed: {validation_result.files_analyzed}")
                print(f"API files found: {validation_result.api_files_found}")
        else:
            print("Project validation failed!")
            print(f"   Reason: {validation_result.reason}")
            if validation_result.suggestions:
                print("   Suggestions:")
                for suggestion in validation_result.suggestions:
                    print(f"   • {suggestion}")
        
        return 0 if validation_result.is_valid else 1
    
    def run(self, argv: Optional[List[str]] = None) -> int:
        """Run the CLI application."""
        # Setup signal handlers
        self._setup_signal_handlers()
        
        # Parse arguments
        args = self.parser.parse_args(argv)
        
        # Show help if no command provided
        if not hasattr(args, 'command') or args.command is None:
            self.parser.print_help()
            return 0
        
        # Validate environment for commands that need it
        if args.command in ['convert', 'analyze']:
            if not self._validate_environment():
                return 1
        
        # Route to appropriate handler
        try:
            if args.command == "convert":
                return self.handle_convert_command(args)
            elif args.command == "analyze":
                return self.handle_analyze_command(args)
            elif args.command == "validate":
                return self.handle_validate_command(args)
            else:
                print(f"Unknown command: {args.command}")
                return 1
                
        except KeyboardInterrupt:
            print("\n\nOperation interrupted by user.")
            return 130
        except Exception as e:
            print(f"\nUnexpected error: {str(e)}")
            if getattr(args, 'debug', False):
                import traceback
                traceback.print_exc()
            return 1


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI."""
    cli = PHPCLI()
    return cli.run(argv)


if __name__ == "__main__":
    sys.exit(main())