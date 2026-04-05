#!/usr/bin/env python3
"""
#exonware/xwdata/src/exonware/xwdata/contracts.py
XWData Interfaces and Contracts
This module defines all interfaces for the xwdata library following
GUIDELINES_DEV.md standards. All interfaces use 'I' prefix.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.13
Generation Date: 26-Oct-2025
"""

from __future__ import annotations
from collections.abc import AsyncIterator
from typing import Any, Protocol, runtime_checkable
from pathlib import Path
# Import enums from defs
from .defs import DataFormat, MergeStrategy, SerializationMode, COWMode
# ==============================================================================
# CORE DATA INTERFACE
# ==============================================================================
@runtime_checkable

class IData(Protocol):
    """
    Core interface for all XWData instances.
    This interface defines the fundamental operations that all XWData
    implementations must support. Follows GUIDELINES_DEV.md naming:
    IData (interface) → AData (abstract) → XWData (concrete).
    """

    async def get(self, path: str, default: Any = None) -> Any:
        """Get value at path with optional default."""
        ...

    async def set(self, path: str, value: Any) -> IData:
        """Set value at path (returns new instance with COW)."""
        ...

    async def delete(self, path: str) -> IData:
        """Delete value at path (returns new instance with COW)."""
        ...

    async def exists(self, path: str) -> bool:
        """Check if path exists."""
        ...

    def to_native(self) -> Any:
        """Get native Python object."""
        ...

    async def serialize(self, format: str | DataFormat, **opts) -> str | bytes:
        """Serialize to specified format."""
        ...

    def to_format(self, format: str | DataFormat, **opts) -> str | bytes:
        """Synchronously serialize to specified format."""
        ...

    async def save(self, path: str | Path, format: str | DataFormat | None = None, **opts) -> IData:
        """Save to file (returns self for chaining)."""
        ...

    def to_file(self, path: str | Path, format: str | DataFormat | None = None, **opts) -> IData:
        """Synchronously save to file (returns self for chaining)."""
        ...

    async def merge(self, other: IData, strategy: str | MergeStrategy = 'deep') -> IData:
        """Merge with another IData instance."""
        ...

    async def transform(self, transformer: callable) -> IData:
        """Transform data using function."""
        ...

    def get_metadata(self) -> dict[str, Any]:
        """Get metadata dictionary."""
        ...

    def get_format(self) -> str | None:
        """Get format information."""
        ...
# ==============================================================================
# DATA ENGINE INTERFACE
# ==============================================================================
@runtime_checkable

class IDataEngine(Protocol):
    """
    Interface for data processing engine.
    The engine orchestrates all data operations, composing:
    - XWSerializer (xwsystem) for format I/O
    - FormatStrategyRegistry for format-specific logic
    - MetadataProcessor for universal metadata
    - ReferenceResolver for reference handling
    - CacheManager for performance
    - NodeFactory for node creation
    """

    async def load(
        self,
        path: str | Path,
        format_hint: str | DataFormat | None = None,
        **opts
    ) -> IDataNode:
        """Load data from file."""
        ...

    async def save(
        self,
        node: IDataNode,
        path: str | Path,
        format: str | DataFormat | None = None,
        **opts
    ) -> None:
        """Save node to file."""
        ...

    async def parse(
        self,
        content: str | bytes,
        format: str | DataFormat,
        **opts
    ) -> IDataNode:
        """Parse content with specified format."""
        ...

    async def create_node_from_native(
        self,
        data: Any,
        metadata: dict | None = None,
        **opts
    ) -> IDataNode:
        """Create node from native Python data."""
        ...

    async def merge_nodes(
        self,
        nodes: list[IDataNode],
        strategy: str | MergeStrategy = 'deep'
    ) -> IDataNode:
        """Merge multiple nodes into one."""
        ...

    async def stream_load(
        self,
        path: str | Path,
        chunk_size: int = 8192,
        **opts
    ) -> AsyncIterator[IDataNode]:
        """Stream load large files."""
        ...
# ==============================================================================
# DATA NODE INTERFACE
# ==============================================================================
@runtime_checkable

class IDataNode(Protocol):
    """
    Interface for data nodes.
    Data nodes extend XWNode with:
    - Copy-on-write semantics
    - Format-specific metadata
    - Reference tracking
    - Structural hashing
    """

    def to_native(self) -> Any:
        """Convert node to native Python object."""
        ...

    def get_value_at_path(self, path: str, default: Any = None) -> Any:
        """Get value at path."""
        ...

    def set_value_at_path(self, path: str, value: Any) -> IDataNode:
        """Set value at path (returns new node with COW)."""
        ...

    def delete_at_path(self, path: str) -> IDataNode:
        """Delete value at path (returns new node with COW)."""
        ...

    def path_exists(self, path: str) -> bool:
        """Check if path exists."""
        ...

    def copy(self) -> IDataNode:
        """Create copy of node."""
        ...
    @property

    def is_frozen(self) -> bool:
        """Check if node is frozen (COW active)."""
        ...
    @property

    def metadata(self) -> dict[str, Any]:
        """Get metadata dictionary."""
        ...
    @property

    def format_info(self) -> dict[str, Any]:
        """Get format information."""
        ...
# ==============================================================================
# FORMAT STRATEGY INTERFACE
# ==============================================================================
@runtime_checkable

class IFormatStrategy(Protocol):
    """
    Interface for format-specific strategies.
    Format strategies provide format-specific logic:
    - Metadata extraction (format-specific semantics)
    - Reference detection (format-specific patterns)
    - Type mapping (format ↔ native ↔ universal)
    They do NOT handle serialization (that's xwsystem's job).
    """
    @property

    def name(self) -> str:
        """Strategy name (format identifier)."""
        ...
    @property

    def extensions(self) -> list[str]:
        """Supported file extensions."""
        ...

    async def extract_metadata(self, data: Any, **opts) -> dict[str, Any]:
        """Extract format-specific metadata."""
        ...

    async def detect_references(self, data: Any, **opts) -> list[dict[str, Any]]:
        """Detect format-specific references."""
        ...

    def get_reference_patterns(self) -> dict[str, Any]:
        """Get reference detection patterns for this format."""
        ...

    def get_type_mapping(self) -> dict[str, str]:
        """Get type mapping (format types → universal types)."""
        ...
# ==============================================================================
# METADATA PROCESSOR INTERFACE
# ==============================================================================
@runtime_checkable

class IMetadataProcessor(Protocol):
    """Interface for metadata processing."""

    async def extract(
        self,
        data: Any,
        strategy: IFormatStrategy,
        **opts
    ) -> dict[str, Any]:
        """Extract metadata using format strategy."""
        ...

    async def apply(
        self,
        data: Any,
        metadata: dict[str, Any],
        target_format: str,
        **opts
    ) -> Any:
        """Apply metadata for target format."""
        ...
# ==============================================================================
# REFERENCE RESOLVER INTERFACE
# ==============================================================================
@runtime_checkable

class IReferenceDetector(Protocol):
    """Interface for reference detection."""

    async def detect(
        self,
        data: Any,
        strategy: IFormatStrategy,
        **opts
    ) -> list[dict[str, Any]]:
        """Detect references in data."""
        ...
@runtime_checkable

class IReferenceResolver(Protocol):
    """Interface for reference resolution."""

    async def resolve(
        self,
        data: Any,
        strategy: IFormatStrategy,
        base_path: Path | None = None,
        **opts
    ) -> Any:
        """Resolve all references in data."""
        ...

    async def resolve_reference(
        self,
        reference: dict[str, Any],
        base_path: Path | None = None,
        **opts
    ) -> Any:
        """Resolve single reference."""
        ...
# ==============================================================================
# CACHE MANAGER INTERFACE
# ==============================================================================
@runtime_checkable

class ICacheManager(Protocol):
    """Interface for cache management."""

    async def get(self, key: str) -> Any | None:
        """Get cached value."""
        ...

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set cached value."""
        ...

    async def invalidate(self, key: str) -> None:
        """Invalidate cached value."""
        ...

    async def clear(self) -> None:
        """Clear all cached values."""
        ...

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        ...
# ==============================================================================
# NODE FACTORY INTERFACE
# ==============================================================================
@runtime_checkable

class INodeFactory(Protocol):
    """Interface for node creation."""

    async def create_node(
        self,
        data: Any,
        metadata: dict | None = None,
        format_info: dict | None = None,
        **opts
    ) -> IDataNode:
        """Create data node."""
        ...

    async def create_from_native(self, data: Any, **opts) -> IDataNode:
        """Create node from native Python data."""
        ...
# ==============================================================================
# SERIALIZER INTERFACE (EXTENDS XWSYSTEM)
# ==============================================================================
@runtime_checkable

class IXWDataSerializer(Protocol):
    """
    Interface for xwdata-specific serializers.
    Extends xwsystem's ISerialization with xwdata features.
    """
    @property

    def name(self) -> str:
        """Serializer name."""
        ...
    @property

    def extensions(self) -> list[str]:
        """Supported extensions."""
        ...

    async def serialize(self, data: Any, **opts) -> str | bytes:
        """Serialize data."""
        ...

    async def deserialize(self, content: str | bytes, **opts) -> Any:
        """Deserialize content."""
        ...

    def detect(self, content: str | bytes) -> float:
        """Detect if content matches this format (0.0-1.0 confidence)."""
        ...
# ==============================================================================
# FORMAT CONVERSION INTERFACES (Optional BaaS Features)
# ==============================================================================
@runtime_checkable

class IFormatConverter(Protocol):
    """
    Interface for format conversion operations.
    Provides optimized format-to-format conversion with caching and validation.
    This is an optional BaaS feature for multi-format storage capabilities.
    """

    async def convert(
        self,
        data: Any,
        source_format: str | DataFormat,
        target_format: str | DataFormat,
        **opts
    ) -> Any:
        """
        Convert data from source format to target format.
        Args:
            data: Data to convert
            source_format: Source format name or enum
            target_format: Target format name or enum
            **opts: Additional conversion options
        Returns:
            Converted data in target format
        """
        ...

    async def convert_file(
        self,
        source_path: str | Path,
        target_path: str | Path,
        target_format: str | DataFormat | None = None,
        **opts
    ) -> Path:
        """
        Convert file from source format to target format.
        Args:
            source_path: Source file path
            target_path: Target file path
            target_format: Optional target format (auto-detected if not provided)
            **opts: Additional conversion options
        Returns:
            Path to converted file
        """
        ...

    def get_conversion_path(
        self,
        source_format: str | DataFormat,
        target_format: str | DataFormat
    ) -> list[str]:
        """
        Get optimal conversion path (direct or via intermediate formats).
        Args:
            source_format: Source format
            target_format: Target format
        Returns:
            List of format names in conversion path
        """
        ...

    def supports_conversion(
        self,
        source_format: str | DataFormat,
        target_format: str | DataFormat
    ) -> bool:
        """
        Check if conversion is supported.
        Args:
            source_format: Source format
            target_format: Target format
        Returns:
            True if conversion is supported
        """
        ...
@runtime_checkable

class IConversionPipeline(Protocol):
    """
    Interface for multi-step conversion pipelines.
    Provides support for complex conversion workflows with multiple steps.
    This is an optional BaaS feature.
    """

    async def execute(
        self,
        data: Any,
        steps: list[tuple[str | DataFormat, dict[str, Any]]],
        **opts
    ) -> Any:
        """
        Execute multi-step conversion pipeline.
        Args:
            data: Initial data
            steps: List of (format, options) tuples for each step
            **opts: Global pipeline options
        Returns:
            Final converted data
        """
        ...

    async def execute_file(
        self,
        source_path: str | Path,
        steps: list[tuple[str | DataFormat, dict[str, Any]]],
        target_path: str | Path | None = None,
        **opts
    ) -> Path:
        """
        Execute multi-step conversion pipeline on file.
        Args:
            source_path: Source file path
            steps: List of (format, options) tuples for each step
            target_path: Optional target path (auto-generated if not provided)
            **opts: Global pipeline options
        Returns:
            Path to final converted file
        """
        ...
@runtime_checkable

class IFormatValidator(Protocol):
    """
    Interface for format-specific validation.
    Provides format-aware validation beyond basic type checking.
    This is an optional BaaS feature.
    """

    async def validate(
        self,
        data: Any,
        format: str | DataFormat,
        **opts
    ) -> dict[str, Any]:
        """
        Validate data against format-specific rules.
        Args:
            data: Data to validate
            format: Format to validate against
            **opts: Validation options
        Returns:
            Validation result dictionary with 'valid' (bool) and 'errors' (list)
        """
        ...

    async def validate_file(
        self,
        path: str | Path,
        format: str | DataFormat | None = None,
        **opts
    ) -> dict[str, Any]:
        """
        Validate file against format-specific rules.
        Args:
            path: File path to validate
            format: Optional format hint (auto-detected if not provided)
            **opts: Validation options
        Returns:
            Validation result dictionary with 'valid' (bool) and 'errors' (list)
        """
        ...
# ==============================================================================
# EXPORTS
# ==============================================================================
__all__ = [
    # Core interfaces
    'IData',
    'IDataEngine',
    'IDataNode',
    # Strategy interfaces
    'IFormatStrategy',
    # Service interfaces
    'IMetadataProcessor',
    'IReferenceDetector',
    'IReferenceResolver',
    'ICacheManager',
    'INodeFactory',
    # Serializer interface
    'IXWDataSerializer',
    # Format conversion interfaces (optional BaaS features)
    'IFormatConverter',
    'IConversionPipeline',
    'IFormatValidator',
]
