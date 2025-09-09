"""
File utilities for PHP to FastAPI converter.
Handles file operations, backups, and safe file management.
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
import json
import zipfile
import hashlib


class FileOperationError(Exception):
    """Exception raised for file operation errors."""
    pass


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure directory exists, create if it doesn't.
    
    Args:
        path: Directory path to ensure
        
    Returns:
        Path object of the directory
        
    Raises:
        FileOperationError: If directory cannot be created
    """
    try:
        path_obj = Path(path)
        path_obj.mkdir(parents=True, exist_ok=True)
        return path_obj
    except Exception as e:
        raise FileOperationError(f"Failed to create directory {path}: {str(e)}")


def create_backup(source_path: Union[str, Path], backup_dir: Optional[Union[str, Path]] = None) -> Path:
    """
    Create a backup of a file or directory.
    
    Args:
        source_path: Path to backup
        backup_dir: Directory to store backup (default: ./backups)
        
    Returns:
        Path to the created backup
        
    Raises:
        FileOperationError: If backup creation fails
    """
    try:
        source_path = Path(source_path)
        
        if not source_path.exists():
            raise FileOperationError(f"Source path {source_path} does not exist")
        
        # Set default backup directory
        if backup_dir is None:
            backup_dir = Path("./backups")
        else:
            backup_dir = Path(backup_dir)
        
        ensure_directory(backup_dir)
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{source_path.name}_{timestamp}"
        
        if source_path.is_file():
            backup_path = backup_dir / f"{backup_name}{source_path.suffix}"
            shutil.copy2(source_path, backup_path)
        else:
            # For directories, create a zip archive
            backup_path = backup_dir / f"{backup_name}.zip"
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(source_path):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(source_path)
                        zipf.write(file_path, arcname)
        
        return backup_path
        
    except Exception as e:
        raise FileOperationError(f"Failed to create backup: {str(e)}")


def copy_file_safe(source: Union[str, Path], destination: Union[str, Path], 
                  backup_existing: bool = True) -> bool:
    """
    Safely copy a file with optional backup of existing destination.
    
    Args:
        source: Source file path
        destination: Destination file path
        backup_existing: Whether to backup existing destination file
        
    Returns:
        True if successful, False otherwise
        
    Raises:
        FileOperationError: If copy operation fails
    """
    try:
        source_path = Path(source)
        dest_path = Path(destination)
        
        if not source_path.exists():
            raise FileOperationError(f"Source file {source_path} does not exist")
        
        if not source_path.is_file():
            raise FileOperationError(f"Source {source_path} is not a file")
        
        # Create destination directory if it doesn't exist
        ensure_directory(dest_path.parent)
        
        # Backup existing file if requested
        if backup_existing and dest_path.exists():
            backup_path = dest_path.with_suffix(dest_path.suffix + '.bak')
            shutil.copy2(dest_path, backup_path)
        
        # Copy the file
        shutil.copy2(source_path, dest_path)
        return True
        
    except Exception as e:
        raise FileOperationError(f"Failed to copy file: {str(e)}")


def write_file_safe(file_path: Union[str, Path], content: str, 
                   encoding: str = 'utf-8', backup_existing: bool = True) -> bool:
    """
    Safely write content to a file with optional backup.
    
    Args:
        file_path: Path to write to
        content: Content to write
        encoding: File encoding
        backup_existing: Whether to backup existing file
        
    Returns:
        True if successful, False otherwise
        
    Raises:
        FileOperationError: If write operation fails
    """
    try:
        file_path = Path(file_path)
        
        # Create directory if it doesn't exist
        ensure_directory(file_path.parent)
        
        # Backup existing file if requested
        if backup_existing and file_path.exists():
            backup_path = file_path.with_suffix(file_path.suffix + '.bak')
            shutil.copy2(file_path, backup_path)
        
        # Write to temporary file first, then move (atomic operation)
        with tempfile.NamedTemporaryFile(mode='w', encoding=encoding, 
                                       dir=file_path.parent, delete=False) as tmp_file:
            tmp_file.write(content)
            tmp_path = Path(tmp_file.name)
        
        # Move temporary file to final location
        shutil.move(tmp_path, file_path)
        return True
        
    except Exception as e:
        # Clean up temporary file if it exists
        if 'tmp_path' in locals() and tmp_path.exists():
            tmp_path.unlink()
        raise FileOperationError(f"Failed to write file {file_path}: {str(e)}")


def read_file_safe(file_path: Union[str, Path], encoding: str = 'utf-8') -> str:
    """
    Safely read content from a file.
    
    Args:
        file_path: Path to read from
        encoding: File encoding
        
    Returns:
        File content as string
        
    Raises:
        FileOperationError: If read operation fails
    """
    try:
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileOperationError(f"File {file_path} does not exist")
        
        if not file_path.is_file():
            raise FileOperationError(f"Path {file_path} is not a file")
        
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
            
    except Exception as e:
        raise FileOperationError(f"Failed to read file {file_path}: {str(e)}")


def get_file_hash(file_path: Union[str, Path], algorithm: str = 'md5') -> str:
    """
    Calculate hash of a file.
    
    Args:
        file_path: Path to file
        algorithm: Hash algorithm (md5, sha1, sha256)
        
    Returns:
        Hex digest of file hash
        
    Raises:
        FileOperationError: If hash calculation fails
    """
    try:
        file_path = Path(file_path)
        
        if not file_path.exists() or not file_path.is_file():
            raise FileOperationError(f"File {file_path} does not exist or is not a file")
        
        hash_obj = hashlib.new(algorithm)
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
        
    except Exception as e:
        raise FileOperationError(f"Failed to calculate hash for {file_path}: {str(e)}")


def find_files(directory: Union[str, Path], pattern: str = "*", 
               recursive: bool = True) -> List[Path]:
    """
    Find files matching a pattern in a directory.
    
    Args:
        directory: Directory to search in
        pattern: File pattern to match (e.g., "*.py", "test_*")
        recursive: Whether to search recursively
        
    Returns:
        List of matching file paths
        
    Raises:
        FileOperationError: If search fails
    """
    try:
        directory = Path(directory)
        
        if not directory.exists() or not directory.is_dir():
            raise FileOperationError(f"Directory {directory} does not exist or is not a directory")
        
        if recursive:
            return list(directory.rglob(pattern))
        else:
            return list(directory.glob(pattern))
            
    except Exception as e:
        raise FileOperationError(f"Failed to find files in {directory}: {str(e)}")


class FileManager:
    """
    File manager class for handling project-wide file operations.
    """
    
    def __init__(self, base_path: Union[str, Path], backup_enabled: bool = True):
        """
        Initialize file manager.
        
        Args:
            base_path: Base directory for operations
            backup_enabled: Whether to enable automatic backups
        """
        self.base_path = Path(base_path)
        self.backup_enabled = backup_enabled
        self.backup_dir = self.base_path / "backups"
        self.operations_log: List[Dict[str, Any]] = []
        
        # Ensure base directory exists
        ensure_directory(self.base_path)
        
        if self.backup_enabled:
            ensure_directory(self.backup_dir)
    
    def write_file(self, relative_path: Union[str, Path], content: str, 
                   encoding: str = 'utf-8') -> bool:
        """
        Write a file relative to base path.
        
        Args:
            relative_path: Path relative to base directory
            content: Content to write
            encoding: File encoding
            
        Returns:
            True if successful
        """
        try:
            full_path = self.base_path / relative_path
            success = write_file_safe(full_path, content, encoding, self.backup_enabled)
            
            # Log operation
            self.operations_log.append({
                'operation': 'write',
                'path': str(relative_path),
                'timestamp': datetime.now().isoformat(),
                'success': success
            })
            
            return success
            
        except Exception as e:
            self.operations_log.append({
                'operation': 'write',
                'path': str(relative_path),
                'timestamp': datetime.now().isoformat(),
                'success': False,
                'error': str(e)
            })
            raise
    
    def read_file(self, relative_path: Union[str, Path], encoding: str = 'utf-8') -> str:
        """
        Read a file relative to base path.
        
        Args:
            relative_path: Path relative to base directory
            encoding: File encoding
            
        Returns:
            File content
        """
        full_path = self.base_path / relative_path
        return read_file_safe(full_path, encoding)
    
    def copy_file(self, source_relative: Union[str, Path], 
                  dest_relative: Union[str, Path]) -> bool:
        """
        Copy a file within the managed directory.
        
        Args:
            source_relative: Source path relative to base
            dest_relative: Destination path relative to base
            
        Returns:
            True if successful
        """
        try:
            source_full = self.base_path / source_relative
            dest_full = self.base_path / dest_relative
            
            success = copy_file_safe(source_full, dest_full, self.backup_enabled)
            
            # Log operation
            self.operations_log.append({
                'operation': 'copy',
                'source': str(source_relative),
                'destination': str(dest_relative),
                'timestamp': datetime.now().isoformat(),
                'success': success
            })
            
            return success
            
        except Exception as e:
            self.operations_log.append({
                'operation': 'copy',
                'source': str(source_relative),
                'destination': str(dest_relative),
                'timestamp': datetime.now().isoformat(),
                'success': False,
                'error': str(e)
            })
            raise
    
    def create_directory(self, relative_path: Union[str, Path]) -> Path:
        """
        Create a directory relative to base path.
        
        Args:
            relative_path: Directory path relative to base
            
        Returns:
            Full path to created directory
        """
        full_path = self.base_path / relative_path
        ensure_directory(full_path)
        
        # Log operation
        self.operations_log.append({
            'operation': 'mkdir',
            'path': str(relative_path),
            'timestamp': datetime.now().isoformat(),
            'success': True
        })
        
        return full_path
    
    def backup_file(self, relative_path: Union[str, Path]) -> Optional[Path]:
        """
        Create backup of a specific file.
        
        Args:
            relative_path: File path relative to base
            
        Returns:
            Path to backup file, None if backup disabled
        """
        if not self.backup_enabled:
            return None
        
        full_path = self.base_path / relative_path
        return create_backup(full_path, self.backup_dir)
    
    def get_operations_log(self) -> List[Dict[str, Any]]:
        """
        Get log of all file operations.
        
        Returns:
            List of operation records
        """
        return self.operations_log.copy()
    
    def save_operations_log(self, log_file: str = "file_operations.json") -> bool:
        """
        Save operations log to a file.
        
        Args:
            log_file: Name of log file
            
        Returns:
            True if successful
        """
        try:
            log_path = self.base_path / log_file
            with open(log_path, 'w', encoding='utf-8') as f:
                json.dump(self.operations_log, f, indent=2)
            return True
        except Exception:
            return False