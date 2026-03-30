#!/usr/bin/env python3
"""
#exonware/xwdata/src/exonware/xwdata/integrations/storage/__init__.py
Storage Integration Module (Optional BaaS Feature)
Provides integration interfaces for xwstorage multi-backend storage.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.12
Generation Date: 26-Jan-2025
"""
# Optional imports - these will be None if xwstorage is not available

try:
    from .contracts import IStorageAdapter, IStorageMapper
    from .adapter import StorageAdapter
    from .mapper import StorageFormatMapper
    from .batch import StorageBatchOperations
    STORAGE_INTEGRATION_AVAILABLE = True
except ImportError:
    STORAGE_INTEGRATION_AVAILABLE = False
    IStorageAdapter = None
    IStorageMapper = None
    StorageAdapter = None
    StorageFormatMapper = None
    StorageBatchOperations = None
__all__ = []
if STORAGE_INTEGRATION_AVAILABLE:
    __all__.extend([
        'IStorageAdapter',
        'IStorageMapper',
        'StorageAdapter',
        'StorageFormatMapper',
        'StorageBatchOperations',
    ])
