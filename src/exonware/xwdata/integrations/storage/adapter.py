#!/usr/bin/env python3
"""
#exonware/xwdata/src/exonware/xwdata/integrations/storage/adapter.py
Storage Adapter Implementation (Optional BaaS Feature)
Provides storage backend integration interface for xwstorage.
This is an optional feature - xwstorage integration is optional.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.2
Generation Date: 26-Jan-2025
"""

from typing import Any
from pathlib import Path
from exonware.xwsystem import get_logger
from .contracts import IStorageAdapter
from ...contracts import IData
from ...defs import DataFormat
from ...errors import XWDataError
logger = get_logger(__name__)
# Optional xwstorage dependency
try:
    # xwstorage integration would go here
    # For now, this is a placeholder interface
    XWSTORAGE_AVAILABLE = False
except ImportError:
    XWSTORAGE_AVAILABLE = False


class StorageAdapter(IStorageAdapter):
    """
    Storage adapter for xwstorage backend integration.
    Provides abstraction layer for xwstorage multi-backend storage.
    This is an optional BaaS feature - xwstorage is an optional dependency.
    """

    def __init__(self):
        """Initialize storage adapter."""
        if not XWSTORAGE_AVAILABLE:
            logger.warning(
                "StorageAdapter requires xwstorage library. "
                "Install with: pip install exonware-xwstorage"
            )
        self._backends: dict[str, Any] = {}

    async def store(
        self,
        data: IData,
        backend: str,
        location: str,
        format_hint: str | DataFormat | None = None,
        **opts
    ) -> None:
        """
        Store data in storage backend.
        Args:
            data: Data to store
            backend: Storage backend identifier
            location: Storage location/path
            format_hint: Optional format hint
            **opts: Additional storage options
        """
        if not XWSTORAGE_AVAILABLE:
            raise XWDataError(
                "StorageAdapter requires xwstorage library. "
                "Install with: pip install exonware-xwstorage"
            )
        # Get backend instance
        backend_instance = self._get_backend(backend)
        # Serialize data to format
        if format_hint:
            format_name = self._normalize_format(format_hint)
        else:
            format_name = data.get_format() or 'json'
        # Serialize data
        serialized = await data.serialize(format_name, **opts)
        # Store in backend
        await backend_instance.store(location, serialized, format=format_name, **opts)
        logger.debug(f"Stored data to {backend}:{location} in format {format_name}")

    async def load(
        self,
        backend: str,
        location: str,
        format_hint: str | DataFormat | None = None,
        **opts
    ) -> IData:
        """
        Load data from storage backend.
        Args:
            backend: Storage backend identifier
            location: Storage location/path
            format_hint: Optional format hint
            **opts: Additional load options
        Returns:
            Loaded data as IData instance
        """
        if not XWSTORAGE_AVAILABLE:
            raise XWDataError(
                "StorageAdapter requires xwstorage library. "
                "Install with: pip install exonware-xwstorage"
            )
        # Get backend instance
        backend_instance = self._get_backend(backend)
        # Load from backend
        serialized = await backend_instance.load(location, **opts)
        # Detect format if not provided
        if format_hint:
            format_name = self._normalize_format(format_hint)
        else:
            format_name = self._detect_format(serialized)
        # Deserialize and create IData instance
        from ...facade import XWData
        data = await XWData.parse(serialized, format=format_name, **opts)
        logger.debug(f"Loaded data from {backend}:{location} in format {format_name}")
        return data

    async def delete(
        self,
        backend: str,
        location: str,
        **opts
    ) -> bool:
        """
        Delete data from storage backend.
        Args:
            backend: Storage backend identifier
            location: Storage location/path
            **opts: Additional delete options
        Returns:
            True if deleted, False if not found
        """
        if not XWSTORAGE_AVAILABLE:
            raise XWDataError(
                "StorageAdapter requires xwstorage library. "
                "Install with: pip install exonware-xwstorage"
            )
        backend_instance = self._get_backend(backend)
        result = await backend_instance.delete(location, **opts)
        logger.debug(f"Deleted data from {backend}:{location}")
        return result

    async def exists(
        self,
        backend: str,
        location: str,
        **opts
    ) -> bool:
        """
        Check if data exists in storage backend.
        Args:
            backend: Storage backend identifier
            location: Storage location/path
            **opts: Additional options
        Returns:
            True if exists, False otherwise
        """
        if not XWSTORAGE_AVAILABLE:
            raise XWDataError(
                "StorageAdapter requires xwstorage library. "
                "Install with: pip install exonware-xwstorage"
            )
        backend_instance = self._get_backend(backend)
        return await backend_instance.exists(location, **opts)

    def _get_backend(self, backend: str) -> Any:
        """Get backend instance (placeholder - would integrate with xwstorage)."""
        if backend not in self._backends:
            # Placeholder - would create xwstorage backend instance here
            raise XWDataError(f"Backend '{backend}' not configured")
        return self._backends[backend]

    def _normalize_format(self, format: str | DataFormat) -> str:
        """Normalize format name to lowercase string."""
        if isinstance(format, DataFormat):
            return format.name.lower()
        return str(format).lower()

    def _detect_format(self, data: Any) -> str:
        """Detect format from data (placeholder)."""
        # Would use format detection from xwsystem
        return 'json'  # Default
__all__ = ['StorageAdapter']
