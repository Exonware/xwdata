#!/usr/bin/env python3
"""
#exonware/xwdata/src/exonware/xwdata/integrations/storage/mapper.py
Storage Format Mapper (Optional BaaS Feature)
Maps xwdata formats to storage backend formats.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.1
Generation Date: 26-Jan-2025
"""

from typing import Optional
from exonware.xwsystem import get_logger
from .contracts import IStorageMapper
from ...defs import DataFormat
logger = get_logger(__name__)


class StorageFormatMapper(IStorageMapper):
    """
    Format-to-storage mapping.
    Maps xwdata formats to storage backend formats.
    This is an optional BaaS feature.
    """

    def __init__(self):
        """Initialize format mapper."""
        # Format mapping: xwdata format -> storage backend format
        self._format_mappings = {
            # Text formats
            'json': {'postgresql': 'jsonb', 'mongodb': 'bson', 'redis': 'json'},
            'yaml': {'postgresql': 'text', 'mongodb': 'bson', 'redis': 'string'},
            'xml': {'postgresql': 'xml', 'mongodb': 'bson', 'redis': 'string'},
            'toml': {'postgresql': 'text', 'mongodb': 'bson', 'redis': 'string'},
            'csv': {'postgresql': 'text', 'mongodb': 'bson', 'redis': 'string'},
            # Binary formats
            'bson': {'postgresql': 'bytea', 'mongodb': 'bson', 'redis': 'binary'},
            'msgpack': {'postgresql': 'bytea', 'mongodb': 'bson', 'redis': 'binary'},
            'cbor': {'postgresql': 'bytea', 'mongodb': 'bson', 'redis': 'binary'},
            'ubjson': {'postgresql': 'bytea', 'mongodb': 'bson', 'redis': 'binary'},
        }

    def map_format(
        self,
        data_format: str | DataFormat,
        backend: str
    ) -> str:
        """
        Map xwdata format to storage backend format.
        Args:
            data_format: xwdata format
            backend: Storage backend identifier
        Returns:
            Storage backend format identifier
        """
        format_name = self._normalize_format(data_format)
        backend_lower = backend.lower()
        # Get mapping for format
        format_map = self._format_mappings.get(format_name, {})
        # Get backend-specific format
        storage_format = format_map.get(backend_lower)
        if storage_format:
            return storage_format
        # Default mapping based on format type
        if format_name in ['json', 'yaml', 'xml', 'toml', 'csv']:
            # Text formats
            if backend_lower == 'postgresql':
                return 'text'
            elif backend_lower == 'mongodb':
                return 'bson'
            elif backend_lower == 'redis':
                return 'string'
        else:
            # Binary formats
            if backend_lower == 'postgresql':
                return 'bytea'
            elif backend_lower == 'mongodb':
                return 'bson'
            elif backend_lower == 'redis':
                return 'binary'
        # Ultimate fallback
        return format_name

    def get_storage_format(
        self,
        backend: str,
        location: str
    ) -> Optional[str]:
        """
        Get storage format from backend and location.
        Args:
            backend: Storage backend identifier
            location: Storage location/path
        Returns:
            Format identifier or None
        """
        # This would query the storage backend for format information
        # Placeholder implementation
        logger.debug(f"Getting storage format for {backend}:{location}")
        return None

    def _normalize_format(self, format: str | DataFormat) -> str:
        """Normalize format name to lowercase string."""
        if isinstance(format, DataFormat):
            return format.name.lower()
        return str(format).lower()
__all__ = ['StorageFormatMapper']
