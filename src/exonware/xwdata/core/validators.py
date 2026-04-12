#!/usr/bin/env python3
"""
#exonware/xwdata/src/exonware/xwdata/core/validators.py
Input Validation and Sanitization for xwdata.
REUSES xwsystem security features:
- Path validation via xwsystem.security.PathValidator
- Input sanitization via xwsystem.security.SecurityValidator
- Format validation (xwdata-specific)
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.17
Generation Date: 26-Jan-2025
"""

import re
from urllib.parse import unquote
from pathlib import Path
from typing import Any
from exonware.xwsystem.security import PathValidator as XWSystemPathValidator, PathSecurityError
from exonware.xwsystem.security.validator import SecurityValidator as XWSystemSecurityValidator
from exonware.xwdata.errors import (
    XWDataPathSecurityError,
    XWDataSecurityError,
    XWDataValidationError
)


class PathValidator:
    """
    Path validator wrapper that REUSES xwsystem.security.PathValidator.
    Provides xwdata-specific error types while leveraging xwsystem's
    production-grade path validation with caching and comprehensive checks.
    """

    def __init__(self, allowed_directories: list[str] | None = None):
        """
        Initialize path validator using xwsystem.
        Args:
            allowed_directories: List of allowed base directories (if None, all relative paths allowed)
        """
        # REUSE xwsystem PathValidator - single version of truth!
        base_path = Path(allowed_directories[0]).resolve() if allowed_directories else None
        self._xwsystem_validator = XWSystemPathValidator(
            base_path=base_path,
            allow_absolute=True,  # Allow absolute paths so load(path, format=...) works from any dir
            check_existence=False,  # Existence is operation-specific; do not block safe path validation.
            enable_cache=True  # Use xwsystem's LRU cache for performance
        )
        self._allowed_directories = allowed_directories

    def validate_path(self, path: str | Path, operation: str = "access") -> Path:
        """
        Validate and sanitize a file path using xwsystem.
        Args:
            path: Path to validate
            operation: Operation being performed (for error messages)
        Returns:
            Validated Path object
        Raises:
            XWDataPathSecurityError: If path is invalid or contains traversal patterns
        """
        try:
            path_str = str(path)
            decoded_path = unquote(path_str)
            normalized = decoded_path.replace("\\", "/").lower()
            # Block common traversal/protected-path probes before filesystem checks.
            if ".." in normalized or normalized.startswith("/etc/") or normalized.startswith("c:/windows"):
                raise XWDataPathSecurityError(
                    "Potential path traversal or protected path access detected",
                    path=path_str,
                    context={"operation": operation}
                )
            # REUSE xwsystem's comprehensive path validation
            validated = self._xwsystem_validator.validate_path(
                path,
                for_writing=(operation == "save"),
                create_dirs=False
            )
            # Additional check for multiple allowed directories (if specified)
            if self._allowed_directories and len(self._allowed_directories) > 1:
                is_allowed = False
                for allowed_dir in self._allowed_directories:
                    allowed_path = Path(allowed_dir).resolve()
                    try:
                        validated.relative_to(allowed_path)
                        is_allowed = True
                        break
                    except ValueError:
                        continue
                if not is_allowed:
                    raise XWDataPathSecurityError(
                        f"Path is outside allowed directories",
                        path=str(path),
                        context={
                            'operation': operation,
                            'allowed_directories': self._allowed_directories
                        }
                    )
            return validated
        except PathSecurityError as e:
            # Convert xwsystem error to xwdata error
            raise XWDataPathSecurityError(
                str(e),
                path=str(path),
                context={'operation': operation}
            ) from e
        except (PermissionError, FileNotFoundError, OSError, ValueError) as e:
            raise XWDataPathSecurityError(
                str(e),
                path=str(path),
                context={'operation': operation}
            ) from e

    def sanitize_path(self, path: str | Path) -> str:
        """
        Sanitize a path using xwsystem's safe filename check.
        Args:
            path: Path to sanitize
        Returns:
            Sanitized path string
        """
        # REUSE xwsystem's is_safe_filename check
        path_obj = Path(path)
        if self._xwsystem_validator.is_safe_filename(path_obj.name):
            return str(path_obj)
        else:
            # If filename is unsafe, use xwsystem's get_safe_path
            base = path_obj.parent if path_obj.parent != Path('.') else None
            if base:
                safe_path = self._xwsystem_validator.get_safe_path(base, path_obj.name)
                return str(safe_path)
            else:
                # Fallback: just return the path and let validation catch it
                return str(path)


class FormatValidator:
    """Validates format strings and format names."""
    # Valid format names (extensible)
    VALID_FORMATS: set[str] = {
        'json', 'yaml', 'xml', 'toml', 'csv', 'ini', 'properties',
        'xwjson', 'native', 'pickle', 'msgpack', 'parquet', 'avro',
        'protobuf', 'bson', 'ubjson', 'cbor', 'hdf5', 'feather'
    }
    # Format name pattern (alphanumeric + underscore, dash)
    FORMAT_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')

    def validate_format_name(self, format_name: str) -> str:
        """
        Validate format name.
        Args:
            format_name: Format name to validate
        Returns:
            Normalized format name (lowercase)
        Raises:
            XWDataValidationError: If format name is invalid
        """
        if not format_name:
            raise XWDataValidationError(
                "Format name cannot be empty",
                field='format'
            )
        # Normalize to lowercase
        format_name = format_name.lower().strip()
        # Check pattern
        if not self.FORMAT_PATTERN.match(format_name):
            raise XWDataValidationError(
                f"Invalid format name: {format_name}. Must contain only alphanumeric characters, underscores, and dashes",
                field='format'
            )
        return format_name

    def is_valid_format(self, format_name: str) -> bool:
        """
        Check if format name is valid.
        Args:
            format_name: Format name to check
        Returns:
            True if format is valid
        """
        try:
            self.validate_format_name(format_name)
            return True
        except XWDataValidationError:
            return False


class InputSanitizer:
    """
    Input sanitizer wrapper that REUSES xwsystem.security.SecurityValidator.
    Provides xwdata-specific error types while leveraging xwsystem's
    production-grade input sanitization and injection detection.
    """

    def __init__(self, strict_mode: bool = False):
        """
        Initialize input sanitizer using xwsystem.
        Args:
            strict_mode: If True, use stricter validation (detect more patterns)
        """
        # REUSE xwsystem SecurityValidator - single version of truth!
        from exonware.xwsystem.security.defs import SecurityLevel
        security_level = SecurityLevel.HIGH if strict_mode else SecurityLevel.MEDIUM
        self._xwsystem_validator = XWSystemSecurityValidator(security_level=security_level)
        self._strict_mode = strict_mode

    def sanitize_string(self, value: str, allow_html: bool = False) -> str:
        """
        Sanitize a string input using xwsystem.
        Args:
            value: String to sanitize
            allow_html: If True, allow HTML (but still sanitize scripts)
        Returns:
            Sanitized string
        Raises:
            XWDataSecurityError: If injection attacks are detected
        """
        if not isinstance(value, str):
            return value
        # REUSE xwsystem's injection detection
        if self._xwsystem_validator.detect_sql_injection(value):
            raise XWDataSecurityError(
                "Potential SQL injection detected in input",
                context={'input_preview': value[:50]}
            )
        if self._strict_mode:
            suspicious_shell = (';', '|', '&', '`', '$(')
            if any(token in value for token in suspicious_shell):
                raise XWDataSecurityError(
                    "Potential command injection detected in input",
                    context={'input_preview': value[:50]}
                )
        if not allow_html and self._xwsystem_validator.detect_xss(value):
            raise XWDataSecurityError(
                "Potential XSS attack detected in input",
                context={'input_preview': value[:50]}
            )
        # REUSE xwsystem's sanitize_input method
        sanitized = self._xwsystem_validator.sanitize_input(value)
        return sanitized

    def sanitize_dict(self, data: dict, recursive: bool = True) -> dict:
        """
        Sanitize dictionary values.
        Args:
            data: Dictionary to sanitize
            recursive: If True, recursively sanitize nested structures
        Returns:
            Sanitized dictionary
        """
        sanitized = {}
        for key, value in data.items():
            # Sanitize key
            sanitized_key = self.sanitize_string(str(key)) if isinstance(key, str) else key
            # Sanitize value
            if isinstance(value, str):
                sanitized_value = self.sanitize_string(value)
            elif isinstance(value, dict) and recursive:
                sanitized_value = self.sanitize_dict(value, recursive=True)
            elif isinstance(value, list) and recursive:
                sanitized_value = self.sanitize_list(value, recursive=True)
            else:
                sanitized_value = value
            sanitized[sanitized_key] = sanitized_value
        return sanitized

    def sanitize_list(self, data: list, recursive: bool = True) -> list:
        """
        Sanitize list values.
        Args:
            data: List to sanitize
            recursive: If True, recursively sanitize nested structures
        Returns:
            Sanitized list
        """
        sanitized = []
        for item in data:
            if isinstance(item, str):
                sanitized.append(self.sanitize_string(item))
            elif isinstance(item, dict) and recursive:
                sanitized.append(self.sanitize_dict(item, recursive=True))
            elif isinstance(item, list) and recursive:
                sanitized.append(self.sanitize_list(item, recursive=True))
            else:
                sanitized.append(item)
        return sanitized


class DataValidator:
    """Validates data structure integrity."""

    def __init__(self, max_depth: int = 100, max_size: int = 100 * 1024 * 1024):
        """
        Initialize data validator.
        Args:
            max_depth: Maximum nesting depth
            max_size: Maximum data size in bytes (100MB default)
        """
        self._max_depth = max_depth
        self._max_size = max_size

    def validate_structure(self, data: Any, depth: int = 0) -> None:
        """
        Validate data structure.
        Args:
            data: Data to validate
            depth: Current nesting depth
        Raises:
            XWDataValidationError: If structure is invalid
        """
        # Check depth
        if depth > self._max_depth:
            raise XWDataValidationError(
                f"Data structure exceeds maximum depth: {self._max_depth}",
                context={'depth': depth, 'max_depth': self._max_depth}
            )
        # Check size (approximate)
        size = self._estimate_size(data)
        if size > self._max_size:
            raise XWDataValidationError(
                f"Data structure exceeds maximum size: {self._max_size} bytes",
                context={'size': size, 'max_size': self._max_size}
            )
        # Recursively validate nested structures
        if isinstance(data, dict):
            for key, value in data.items():
                self.validate_structure(key, depth + 1)
                self.validate_structure(value, depth + 1)
        elif isinstance(data, (list, tuple)):
            for item in data:
                self.validate_structure(item, depth + 1)

    def _estimate_size(self, data: Any) -> int:
        """Estimate size of data structure in bytes."""
        import sys
        return sys.getsizeof(data)
# Global validators
_path_validator: PathValidator | None = None
_format_validator: FormatValidator | None = None
_input_sanitizer: InputSanitizer | None = None
_data_validator: DataValidator | None = None


def get_path_validator() -> PathValidator:
    """Get global path validator instance."""
    global _path_validator
    if _path_validator is None:
        _path_validator = PathValidator()
    return _path_validator


def get_format_validator() -> FormatValidator:
    """Get global format validator instance."""
    global _format_validator
    if _format_validator is None:
        _format_validator = FormatValidator()
    return _format_validator


def get_input_sanitizer() -> InputSanitizer:
    """Get global input sanitizer instance."""
    global _input_sanitizer
    if _input_sanitizer is None:
        _input_sanitizer = InputSanitizer()
    return _input_sanitizer


def get_data_validator() -> DataValidator:
    """Get global data validator instance."""
    global _data_validator
    if _data_validator is None:
        _data_validator = DataValidator()
    return _data_validator
