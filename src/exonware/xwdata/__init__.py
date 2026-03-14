#!/usr/bin/env python3
"""
#exonware/xwdata/src/exonware/xwdata/__init__.py
xwdata: Advanced Data Manipulation with XWNode Integration
The xwdata library provides universal data manipulation with:
- Format-agnostic operations (load from any format, save to any)
- XWNode integration for powerful navigation and queries
- Copy-on-write semantics for safe concurrent access
- Universal metadata for perfect roundtrips
- Reference resolution with circular detection
- Performance caching and optimization
- Async operations by design
- Engine-driven orchestration
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.3
Generation Date: 26-Oct-2025
Main Classes:
    XWData: Primary facade for data operations
    XWDataEngine: Core orchestration engine
    XWDataNode: Data node with COW semantics
    XWDataConfig: Configuration system
Example:
    >>> from exonware.xwdata import XWData
    >>> 
    >>> # Load from any format
    >>> data = await XWData.load('config.json')
    >>> 
    >>> # Navigate and modify (COW)
    >>> data = await data.set('api.timeout', 30)
    >>> 
    >>> # Save to different format
    >>> await data.save('config.yaml')  # JSON → YAML!
    >>> 
    >>> # Or synchronously from native data
    >>> data = XWData({'name': 'Alice', 'age': 30})
    >>> name = await data.get('name')  # 'Alice'
"""
# =============================================================================
# XWLAZY INTEGRATION - Auto-install missing dependencies silently (EARLY)
# =============================================================================
# Activate xwlazy BEFORE other imports to enable auto-installation of missing dependencies
# This enables silent auto-installation of missing libraries when they are imported

try:
    from exonware.xwlazy import auto_enable_lazy
    auto_enable_lazy(__package__ or "exonware.xwdata", mode="smart")
except ImportError:
    # xwlazy not installed - lazy mode simply stays disabled (normal behavior)
    pass
# =============================================================================
# CORE IMPORTS
# =============================================================================
# Facade and main classes
from .facade import XWData, load, from_native, parse
# Builder pattern
from .builder import XWDataBuilder
# Shortcuts API
from .shortcuts import (
    quick_load, quick_save, quick_convert,
    to_json, to_yaml, to_xml, to_toml, to_csv,
    from_json, from_yaml, from_xml, from_toml, from_csv,
    quick_get, quick_set, quick_delete,
    quick_merge, quick_diff, quick_patch, quick_validate
)
# Operations (xwsystem integration)
from .operations import (
    MergeStrategy, DiffMode, PatchOperation, DiffResult, PatchResult,
    DataMerger, DataDiffer, DataPatcher, BatchOperations,
    merge_data, diff_data, patch_data,
    batch_convert, batch_validate, batch_transform
)
# Format conversion (BaaS features - uses xwjson)
try:
    from .operations.format_conversion import FormatConverter, convert_format
    from .operations.conversion_pipeline import ConversionPipeline
    from .operations.format_validator import FormatValidator
    FORMAT_CONVERSION_AVAILABLE = True
except ImportError:
    FORMAT_CONVERSION_AVAILABLE = False
    FormatConverter = None
    convert_format = None
    ConversionPipeline = None
    FormatValidator = None
# BaaS facade (optional features)
try:
    from .facades.baas import XWDataBaaSFacade
    BAAS_FACADE_AVAILABLE = True
except ImportError:
    BAAS_FACADE_AVAILABLE = False
    XWDataBaaSFacade = None
# Configuration
from .config import (
    XWDataConfig,
    SecurityConfig,
    PerformanceConfig,
    ReferenceConfig,
    MetadataConfig,
    COWConfig
)
# Enums and definitions
from .defs import (
    DataFormat,
    EngineMode,
    CacheStrategy,
    ReferenceResolutionMode,
    MergeStrategy,
    SerializationMode,
    COWMode,
    MetadataMode,
    ValidationMode,
    PerformanceTrait,
    SecurityTrait
)
# Errors
from .errors import (
    XWDataError,
    XWDataSecurityError,
    XWDataParseError,
    XWDataSerializeError,
    XWDataIOError,
    XWDataEngineError,
    XWDataMetadataError,
    XWDataReferenceError,
    XWDataCircularReferenceError,
    XWDataCacheError,
    XWDataNodeError,
    XWDataPathError,
    XWDataTypeError,
    XWDataValidationError,
    XWDataConfigError
)
# Engine and components (for advanced usage)
from .data.engine import XWDataEngine
from .data.node import XWDataNode
from .data.factory import NodeFactory
# Strategies (for extensibility)
from .data.strategies.registry import FormatStrategyRegistry
# Version info
from .version import (
    __version__,
    __author__,
    __email__,
    __company__,
    __description__,
    get_version,
    get_version_info
)
# =============================================================================
# PUBLIC API
# =============================================================================
__all__ = [
    # Main classes
    'XWData',
    'XWDataBuilder',
    # Convenience functions
    'load',
    'from_native',
    'parse',
    # Shortcuts API
    'quick_load', 'quick_save', 'quick_convert',
    'to_json', 'to_yaml', 'to_xml', 'to_toml', 'to_csv',
    'from_json', 'from_yaml', 'from_xml', 'from_toml', 'from_csv',
    'quick_get', 'quick_set', 'quick_delete',
    'quick_merge', 'quick_diff', 'quick_patch', 'quick_validate',
    # Operations (xwsystem integration)
    'MergeStrategy', 'DiffMode', 'PatchOperation', 'DiffResult', 'PatchResult',
    'DataMerger', 'DataDiffer', 'DataPatcher', 'BatchOperations',
    'merge_data', 'diff_data', 'patch_data',
    'batch_convert', 'batch_validate', 'batch_transform',
    # Format conversion (BaaS features - uses xwjson)
    # FormatConverter, convert_format, ConversionPipeline, FormatValidator
    # (added conditionally if available)
    # BaaS facade (optional features)
    # XWDataBaaSFacade (added conditionally if available)
    # Configuration
    'XWDataConfig',
    'SecurityConfig',
    'PerformanceConfig',
    'ReferenceConfig',
    'MetadataConfig',
    'COWConfig',
    # Enums
    'DataFormat',
    'EngineMode',
    'CacheStrategy',
    'ReferenceResolutionMode',
    'MergeStrategy',
    'SerializationMode',
    'COWMode',
    'MetadataMode',
    'ValidationMode',
    'PerformanceTrait',
    'SecurityTrait',
    # Errors
    'XWDataError',
    'XWDataSecurityError',
    'XWDataParseError',
    'XWDataSerializeError',
    'XWDataIOError',
    'XWDataEngineError',
    'XWDataMetadataError',
    'XWDataReferenceError',
    'XWDataCircularReferenceError',
    'XWDataCacheError',
    'XWDataNodeError',
    'XWDataPathError',
    'XWDataTypeError',
    'XWDataValidationError',
    'XWDataConfigError',
    # Advanced (for extensions)
    'XWDataEngine',
    'XWDataNode',
    'NodeFactory',
    'FormatStrategyRegistry',
    # Version
    '__version__',
    '__author__',
    '__email__',
    '__company__',
    '__description__',
    'get_version',
    'get_version_info',
]
# =============================================================================
# LIBRARY INFORMATION
# =============================================================================


def get_info() -> dict:
    """
    Get comprehensive library information.
    Returns:
        Dictionary with library details
    """
    return {
        'version': __version__,
        'description': __description__,
        'author': __author__,
        'company': __company__,
        'email': __email__
    }
__all__.append('get_info')
# Add format conversion exports if available
if FORMAT_CONVERSION_AVAILABLE:
    __all__.extend([
        'FormatConverter',
        'convert_format',
        'ConversionPipeline',
        'FormatValidator',
    ])
# Add BaaS facade if available
if BAAS_FACADE_AVAILABLE:
    __all__.append('XWDataBaaSFacade')
