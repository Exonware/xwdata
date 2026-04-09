#!/usr/bin/env python3
"""
#exonware/xwdata/src/exonware/xwdata/integrations/storage/contracts.py
Storage Integration Contracts (Optional BaaS Feature)
Defines interfaces for xwstorage backend integration.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.15
Generation Date: 26-Jan-2025
"""


from typing import Any, Protocol, runtime_checkable
from pathlib import Path
from ...contracts import IData
from ...defs import DataFormat
@runtime_checkable

class IStorageAdapter(Protocol):
    """
    Interface for storage backend integration.
    Provides abstraction layer for xwstorage multi-backend storage.
    This is an optional BaaS feature.
    """

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
        ...

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
        ...

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
        ...

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
        ...
@runtime_checkable

class IStorageMapper(Protocol):
    """
    Interface for format-to-storage mapping.
    Maps xwdata formats to storage backend formats.
    This is an optional BaaS feature.
    """

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
        ...

    def get_storage_format(
        self,
        backend: str,
        location: str
    ) -> str | None:
        """
        Get storage format from backend and location.
        Args:
            backend: Storage backend identifier
            location: Storage location/path
        Returns:
            Format identifier or None
        """
        ...
__all__ = ['IStorageAdapter', 'IStorageMapper']
