#!/usr/bin/env python3
"""
#exonware/xwdata/src/exonware/xwdata/integrations/storage/batch.py
Storage Batch Operations (Optional BaaS Feature)
Provides batch operations for storage backends.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.12
Generation Date: 26-Jan-2025
"""

from collections.abc import AsyncIterator
from typing import Any
from pathlib import Path
from exonware.xwsystem import get_logger
from .adapter import StorageAdapter
from ...contracts import IData
from ...defs import DataFormat
logger = get_logger(__name__)


class StorageBatchOperations:
    """
    Batch operations for storage backends.
    Provides efficient batch operations for storage integration.
    This is an optional BaaS feature.
    """

    def __init__(self, adapter: StorageAdapter | None = None):
        """
        Initialize batch operations.
        Args:
            adapter: Optional storage adapter (creates default if not provided)
        """
        self._adapter = adapter or StorageAdapter()

    async def batch_store(
        self,
        items: list[tuple[IData, str, str]],  # (data, backend, location)
        format_hint: str | DataFormat | None = None,
        **opts
    ) -> list[bool]:
        """
        Batch store multiple data items.
        Args:
            items: List of (data, backend, location) tuples
            format_hint: Optional format hint for all items
            **opts: Additional options
        Returns:
            List of success flags for each item
        """
        results = []
        for data, backend, location in items:
            try:
                await self._adapter.store(data, backend, location, format_hint, **opts)
                results.append(True)
            except Exception as e:
                logger.error(f"Batch store failed for {backend}:{location}: {e}")
                results.append(False)
        return results

    async def batch_load(
        self,
        items: list[tuple[str, str]],  # (backend, location)
        format_hint: str | DataFormat | None = None,
        **opts
    ) -> list[IData | None]:
        """
        Batch load multiple data items.
        Args:
            items: List of (backend, location) tuples
            format_hint: Optional format hint for all items
            **opts: Additional options
        Returns:
            List of loaded data items (None for failed loads)
        """
        results = []
        for backend, location in items:
            try:
                data = await self._adapter.load(backend, location, format_hint, **opts)
                results.append(data)
            except Exception as e:
                logger.error(f"Batch load failed for {backend}:{location}: {e}")
                results.append(None)
        return results

    async def batch_delete(
        self,
        items: list[tuple[str, str]],  # (backend, location)
        **opts
    ) -> list[bool]:
        """
        Batch delete multiple data items.
        Args:
            items: List of (backend, location) tuples
            **opts: Additional options
        Returns:
            List of success flags for each item
        """
        results = []
        for backend, location in items:
            try:
                result = await self._adapter.delete(backend, location, **opts)
                results.append(result)
            except Exception as e:
                logger.error(f"Batch delete failed for {backend}:{location}: {e}")
                results.append(False)
        return results
__all__ = ['StorageBatchOperations']
