"""
Utilities package for PHP to FastAPI converter.
"""

from .file_utils import (
    ensure_directory,
    create_backup,
    copy_file_safe,
    write_file_safe,
    read_file_safe,
    FileManager
)

from .validation import (
    PythonValidator,
    FastAPIValidator,
    ProjectValidator,
    ValidationResult,
    ValidationError
)

from .report_generator import (
    ConversionReport,
    ReportGenerator,
    ReportSection
)

__all__ = [
    # File utilities
    "ensure_directory",
    "create_backup", 
    "copy_file_safe",
    "write_file_safe",
    "read_file_safe",
    "FileManager",
    
    # Validation utilities
    "PythonValidator",
    "FastAPIValidator", 
    "ProjectValidator",
    "ValidationResult",
    "ValidationError",
    
    # Report generation
    "ConversionReport",
    "ReportGenerator",
    "ReportSection"
]