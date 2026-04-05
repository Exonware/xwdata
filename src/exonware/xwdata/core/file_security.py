#!/usr/bin/env python3
"""
#exonware/xwdata/src/exonware/xwdata/core/file_security.py
Secure File Operations for xwdata.
REUSES xwsystem.security.FileSecurity (moved from xwdata to xwsystem).
This module provides xwdata-specific error types that wrap xwsystem FileSecurity.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.13
Generation Date: 26-Jan-2025
"""

from pathlib import Path
from exonware.xwdata.errors import (
    XWDataPathSecurityError,
    XWDataSizeLimitError,
    XWDataIOError
)
# REUSE xwsystem FileSecurity (moved from xwdata to xwsystem)
from exonware.xwsystem.security.file_security import (
    FileSecurity as XWSystemFileSecurity,
    FileSecurityError,
    FileSizeLimitError,
    FileIOError
)
from exonware.xwsystem.security.path_validator import PathSecurityError


class FileSecurity:
    """
    Secure file operations wrapper for xwdata.
    REUSES xwsystem.security.FileSecurity and provides xwdata-specific error types.
    """

    def __init__(
        self,
        max_file_size: int = 100 * 1024 * 1024,  # 100MB default
        allowed_directories: list[str] | None = None,
        allow_absolute_paths: bool = False
    ):
        """
        Initialize file security using xwsystem.
        Args:
            max_file_size: Maximum file size in bytes
            allowed_directories: List of allowed base directories
            allow_absolute_paths: If True, allow absolute paths
        """
        # REUSE xwsystem FileSecurity
        self._xwsystem_file_security = XWSystemFileSecurity(
            max_file_size=max_file_size,
            allowed_directories=allowed_directories,
            allow_absolute_paths=allow_absolute_paths
        )
        self._max_file_size = max_file_size

    def validate_file_path(
        self,
        path: str | Path,
        operation: str = "access",
        check_exists: bool = False
    ) -> Path:
        """
        Validate file path for security.
        REUSES xwsystem FileSecurity.validate_file_path.
        Args:
            path: File path to validate
            operation: Operation being performed
            check_exists: If True, check if file exists
        Returns:
            Validated Path object
        Raises:
            XWDataPathSecurityError: If path is invalid
            XWDataIOError: If file doesn't exist (when check_exists=True)
        """
        try:
            # REUSE xwsystem FileSecurity
            return self._xwsystem_file_security.validate_file_path(path, operation, check_exists)
        except (FileSecurityError, PathSecurityError) as e:
            # Convert to xwdata-specific errors
            if isinstance(e, FileSizeLimitError):
                raise XWDataSizeLimitError(
                    str(e),
                    size=e.size,
                    limit=e.limit,
                    path=e.path
                )
            elif isinstance(e, FileIOError):
                raise XWDataIOError(
                    str(e),
                    path=e.path
                )
            else:
                raise XWDataPathSecurityError(
                    str(e),
                    path=getattr(e, "path", str(path)),
                    context=getattr(e, "context", {})
                )

    def check_file_size(self, path: str | Path) -> int:
        """
        Check file size and validate against limits.
        REUSES xwsystem FileSecurity.check_file_size.
        Args:
            path: File path
        Returns:
            File size in bytes
        Raises:
            XWDataSizeLimitError: If file exceeds size limit
            XWDataIOError: If file cannot be accessed
        """
        try:
            # REUSE xwsystem FileSecurity
            return self._xwsystem_file_security.check_file_size(path)
        except FileSizeLimitError as e:
            raise XWDataSizeLimitError(
                str(e),
                size=e.size,
                limit=e.limit,
                path=e.path
            )
        except FileIOError as e:
            raise XWDataIOError(
                str(e),
                path=e.path
            )

    def validate_file_permissions(
        self,
        path: str | Path,
        required_permission: str = "read"
    ) -> None:
        """
        Validate file permissions.
        REUSES xwsystem FileSecurity.validate_file_permissions.
        Args:
            path: File path
            required_permission: Required permission ('read', 'write', 'execute')
        Raises:
            XWDataIOError: If file doesn't have required permissions
        """
        try:
            # REUSE xwsystem FileSecurity
            self._xwsystem_file_security.validate_file_permissions(path, required_permission)
        except FileIOError as e:
            raise XWDataIOError(
                str(e),
                path=e.path
            )

    def secure_read_file(self, path: str | Path) -> bytes:
        """
        Securely read a file with validation.
        Args:
            path: File path
        Returns:
            File contents as bytes
        Raises:
            XWDataPathSecurityError: If path is invalid
            XWDataSizeLimitError: If file exceeds size limit
            XWDataIOError: If file cannot be read
        """
        # Validate path
        validated_path = self.validate_file_path(path, operation="read", check_exists=True)
        # Check file size
        self.check_file_size(validated_path)
        # Check permissions
        self.validate_file_permissions(validated_path, required_permission="read")
        # Read file
        try:
            with open(validated_path, 'rb') as f:
                return f.read()
        except OSError as e:
            raise XWDataIOError(
                f"Cannot read file: {e}",
                path=str(validated_path)
            )

    def secure_write_file(
        self,
        path: str | Path,
        data: bytes,
        check_size: bool = True
    ) -> None:
        """
        Securely write a file with validation.
        Args:
            path: File path
            data: Data to write
            check_size: If True, check data size against limit
        Raises:
            XWDataPathSecurityError: If path is invalid
            XWDataSizeLimitError: If data exceeds size limit
            XWDataIOError: If file cannot be written
        """
        # Validate path
        validated_path = self.validate_file_path(path, operation="write")
        # Check data size
        if check_size and len(data) > self._max_file_size:
            raise XWDataSizeLimitError(
                f"Data size {len(data)} exceeds limit {self._max_file_size}",
                size=len(data),
                limit=self._max_file_size,
                path=str(validated_path)
            )
        # Create parent directory if needed
        validated_path.parent.mkdir(parents=True, exist_ok=True)
        # Write file
        try:
            with open(validated_path, 'wb') as f:
                f.write(data)
        except OSError as e:
            raise XWDataIOError(
                f"Cannot write file: {e}",
                path=str(validated_path)
            )

    def is_safe_path(self, path: str | Path) -> bool:
        """
        Check if path is safe (doesn't raise exception).
        Args:
            path: Path to check
        Returns:
            True if path is safe
        """
        try:
            self.validate_file_path(path, operation="check")
            return True
        except (XWDataPathSecurityError, XWDataIOError):
            return False
# Global file security instance
_file_security: FileSecurity | None = None


def get_file_security() -> FileSecurity:
    """Get global file security instance."""
    global _file_security
    if _file_security is None:
        _file_security = FileSecurity()
    return _file_security


def set_file_security(security: FileSecurity) -> None:
    """Set global file security instance."""
    global _file_security
    _file_security = security
