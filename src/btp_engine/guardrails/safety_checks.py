"""Safety checks for BTP Engine operations."""

import os
from pathlib import Path
from typing import Dict, List, Optional
from .exceptions import SafetyViolationError


class SafetyChecker:
    """Validates safety constraints before operations."""
    
    FORBIDDEN_EXTENSIONS = {".exe", ".dll", ".so", ".dylib", ".bat", ".sh", ".cmd"}
    MAX_FILE_SIZE_MB = 100
    
    def __init__(self):
        self.violations: List[str] = []
    
    def check_file_safety(self, filepath: str) -> bool:
        """Check if file is safe to process."""
        path = Path(filepath)
        
        if not path.exists():
            self.violations.append(f"File does not exist: {filepath}")
            return False
        
        if not path.is_file():
            self.violations.append(f"Not a file: {filepath}")
            return False
        
        if path.suffix.lower() in self.FORBIDDEN_EXTENSIONS:
            self.violations.append(f"Forbidden extension: {path.suffix}")
            return False
        
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > self.MAX_FILE_SIZE_MB:
            self.violations.append(f"File too large: {size_mb:.1f}MB > {self.MAX_FILE_SIZE_MB}MB")
            return False
        
        return True
    
    def check_directory_safety(self, dirpath: str) -> bool:
        """Check if directory is safe to process."""
        path = Path(dirpath)
        
        if not path.exists():
            self.violations.append(f"Directory does not exist: {dirpath}")
            return False
        
        if not path.is_dir():
            self.violations.append(f"Not a directory: {dirpath}")
            return False
        
        return True
    
    def enforce(self) -> None:
        """Raise exception if violations exist."""
        if self.violations:
            raise SafetyViolationError("; ".join(self.violations))
    
    def reset(self) -> None:
        """Clear violations."""
        self.violations.clear()