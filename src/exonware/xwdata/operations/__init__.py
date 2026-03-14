#!/usr/bin/env python3
"""
#exonware/xwdata/src/exonware/xwdata/operations/__init__.py
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.5
Generation Date: October 27, 2025
Data operations module integrating xwsystem.operations.
This module provides data-specific operations built on top of xwsystem's
universal operations library, adding XWData-aware functionality.
"""
# Import xwsystem operations infrastructure

from exonware.xwsystem.operations import (
    MergeStrategy,
    DiffMode,
    PatchOperation,
    DiffResult,
    PatchResult,
    OperationError,
    MergeError,
    DiffError,
    PatchError,
    deep_merge as sys_deep_merge,
    generate_diff as sys_generate_diff,
    apply_patch as sys_apply_patch
)
from .data_merge import DataMerger, merge_data
from .data_diff import DataDiffer, diff_data  
from .data_patch import DataPatcher, patch_data
from .batch_operations import BatchOperations, batch_convert, batch_validate, batch_transform
# Format conversion (optional BaaS features)
try:
    from .format_conversion import FormatConverter, convert_format
    from .conversion_pipeline import ConversionPipeline
    from .format_validator import FormatValidator
    FORMAT_CONVERSION_AVAILABLE = True
except ImportError:
    FORMAT_CONVERSION_AVAILABLE = False
    FormatConverter = None
    convert_format = None
    ConversionPipeline = None
    FormatValidator = None
__all__ = [
    # xwsystem operations (re-exported)
    "MergeStrategy",
    "DiffMode",
    "PatchOperation",
    "DiffResult",
    "PatchResult",
    "OperationError",
    "MergeError",
    "DiffError",
    "PatchError",
    # XWData-specific operations
    "DataMerger",
    "DataDiffer",
    "DataPatcher",
    "BatchOperations",
    # Convenience functions
    "merge_data",
    "diff_data",
    "patch_data",
    "batch_convert",
    "batch_validate",
    "batch_transform",
]
# Add format conversion exports if available
if FORMAT_CONVERSION_AVAILABLE:
    __all__.extend([
        "FormatConverter",
        "convert_format",
        "ConversionPipeline",
        "FormatValidator",
    ])
