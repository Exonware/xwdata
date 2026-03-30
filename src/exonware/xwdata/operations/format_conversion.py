#!/usr/bin/env python3
"""
#exonware/xwdata/src/exonware/xwdata/operations/format_conversion.py
Format Conversion Operations (Optional BaaS Feature)
Provides optimized format-to-format conversion with caching and validation.
REUSES xwjson's XWJSONConverter for format conversion (single version of truth).
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.9
Generation Date: 26-Jan-2025
"""

import hashlib
from typing import Any
from pathlib import Path
from exonware.xwsystem import get_logger
from exonware.xwsystem.io.errors import SerializationError
from exonware.xwsystem.io.serialization.auto_serializer import AutoSerializer
from exonware.xwsystem.io.serialization.formats.text.json import JsonSerializer
from exonware.xwjson.formats.binary.xwjson.converter import XWJSONConverter
from ..contracts import IFormatConverter
from ..defs import DataFormat
from ..errors import XWDataError, XWDataParseError, XWDataStrategyError
from ..core.validators import get_format_validator, get_input_sanitizer
from ..core.file_security import get_file_security
logger = get_logger(__name__)
# xwjson is a required dependency for xwdata


class FormatConverter(IFormatConverter):
    """
    Format converter with optimization and caching.
    REUSES xwjson's XWJSONConverter for format conversion (single version of truth).
    Falls back to direct serializer conversion if xwjson is not available.
    Features:
    - Uses xwjson as universal intermediate format (lossless, metadata-preserving)
    - Conversion caching to avoid redundant conversions
    - Validation at each conversion step
    - Error recovery and partial conversion support
    This is an optional BaaS feature for multi-format storage capabilities.
    """

    def __init__(self, enable_caching: bool = True, cache_size: int = 1000):
        """
        Initialize format converter.
        Uses xwjson's XWJSONConverter as the single version of truth for format conversion.
        xwjson is a required dependency for xwdata.
        Args:
            enable_caching: Enable conversion result caching
            cache_size: Maximum cache size
        """
        self._enable_caching = enable_caching
        self._cache: dict[str, Any] = {}
        self._cache_size = cache_size
        # xwjson is required - always use XWJSONConverter
        self._xwjson_converter = XWJSONConverter()
        self._json_text = JsonSerializer()
        logger.debug("xwdata: Using xwjson XWJSONConverter for format conversion")

    def _get_cache_key(
        self,
        data: Any,
        source_format: str,
        target_format: str
    ) -> str:
        """Generate cache key for conversion."""
        # Use hash of data + formats for cache key
        data_str = str(data)[:100]  # Limit length for hashing
        key_str = f"{source_format}:{target_format}:{data_str}"
        return hashlib.md5(key_str.encode()).hexdigest()

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
        # Security: Validate format names
        format_validator = get_format_validator()
        if isinstance(source_format, DataFormat):
            source_fmt = source_format.name.lower()
        else:
            source_fmt = format_validator.validate_format_name(source_format)
        if isinstance(target_format, DataFormat):
            target_fmt = target_format.name.lower()
        else:
            target_fmt = format_validator.validate_format_name(target_format)
        if not self.supports_conversion(source_fmt, target_fmt):
            raise XWDataStrategyError(
                f"Unsupported conversion strategy: {source_fmt} -> {target_fmt}",
                strategy=f"{source_fmt}->{target_fmt}"
            )
        # For explicit JSON input, enforce JSON syntax validation (non-empty only).
        if source_fmt == "json" and isinstance(data, str) and data.strip():
            try:
                self._json_text.loads(data)
            except SerializationError as e:
                raise XWDataParseError(
                    f"Invalid JSON input for conversion: {e}",
                    format="json"
                ) from e
        # Security: Sanitize string inputs if applicable
        # Keep conversion lossless by default for structured formats.
        # Callers can still opt in via sanitize_input=True.
        if isinstance(data, str) and opts.get('sanitize_input', False):
            sanitizer = get_input_sanitizer()
            try:
                data = sanitizer.sanitize_string(data, allow_html=False)
            except XWDataError:
                # If sanitization fails, log but continue (may be false positive)
                logger.warning(f"Input sanitization warning for format conversion: {source_fmt} → {target_fmt}")
        # Check cache
        if self._enable_caching:
            cache_key = self._get_cache_key(data, source_fmt, target_fmt)
            if cache_key in self._cache:
                logger.debug(f"Format conversion cache hit: {source_fmt} → {target_fmt}")
                return self._cache[cache_key]
        # Same format - no conversion needed
        if source_fmt == target_fmt:
            return data
        try:
            # Always use xwjson converter (required dependency)
            result = await self._xwjson_converter.convert(
                source_data=data,
                source_format=source_fmt,
                target_format=target_fmt
            )
            # Ensure text formats return text payloads for API consistency.
            _text_targets = {"json", "yaml", "yml", "xml", "toml", "csv", "ini"}
            if target_fmt in _text_targets:
                serializer = AutoSerializer()
                if not isinstance(result, str):
                    result = serializer.detect_and_serialize(result, format_hint=target_fmt)
                else:
                    if not result.strip():
                        parsed = serializer.detect_and_deserialize(
                            data, format_hint=source_fmt
                        )
                        result = serializer.detect_and_serialize(
                            parsed, format_hint=target_fmt
                        )
                    elif target_fmt == "json":
                        try:
                            self._json_text.loads(result)
                        except SerializationError:
                            parsed = serializer.detect_and_deserialize(
                                data, format_hint=source_fmt
                            )
                            result = serializer.detect_and_serialize(
                                parsed, format_hint="json"
                            )
                    elif target_fmt == "toml" and source_fmt == "json":
                        try:
                            serializer.detect_and_deserialize(
                                result, format_hint="toml"
                            )
                        except Exception:
                            parsed = serializer.detect_and_deserialize(
                                data, format_hint=source_fmt
                            )
                            result = serializer.detect_and_serialize(
                                parsed, format_hint="toml"
                            )
            # Cache result
            if self._enable_caching:
                cache_key = self._get_cache_key(data, source_fmt, target_fmt)
                if len(self._cache) >= self._cache_size:
                    # Simple cache eviction (remove first item)
                    self._cache.pop(next(iter(self._cache)))
                self._cache[cache_key] = result
            return result
        except Exception as e:
            logger.error(f"Format conversion failed: {source_fmt} → {target_fmt}: {e}")
            raise XWDataError(f"Format conversion failed: {source_fmt} → {target_fmt}") from e

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
        # Security: Validate file paths
        file_security = get_file_security()
        source_path_obj = file_security.validate_file_path(source_path, operation="convert_file", check_exists=True)
        target_path_obj = file_security.validate_file_path(target_path, operation="convert_file")
        # Security: Check file size
        file_security.check_file_size(source_path_obj)
        # Detect source format from extension
        source_format = source_path_obj.suffix.lstrip('.').lower()
        # Detect or use provided target format
        if target_format:
            target_fmt = self._normalize_format(target_format)
        else:
            target_fmt = target_path_obj.suffix.lstrip('.').lower()
        # Read source file
        if source_path_obj.suffix.lower() in ['.json', '.yaml', '.yml', '.toml', '.xml', '.csv']:
            # Text format
            data = source_path_obj.read_text(encoding='utf-8')
        else:
            # Binary format
            data = source_path_obj.read_bytes()
        # Convert
        converted_data = await self.convert(data, source_format, target_fmt, **opts)
        # Write target file
        if isinstance(converted_data, bytes):
            target_path_obj.write_bytes(converted_data)
        else:
            target_path_obj.write_text(converted_data, encoding='utf-8')
        logger.debug(f"File converted: {source_path_obj} → {target_path_obj}")
        return target_path_obj

    def get_conversion_path(
        self,
        source_format: str | DataFormat,
        target_format: str | DataFormat
    ) -> list[str]:
        """
        Get optimal conversion path (direct or via intermediate formats).
        If xwjson is available, uses XWJSON as universal intermediate format.
        Otherwise, falls back to JSON as intermediate.
        Args:
            source_format: Source format
            target_format: Target format
        Returns:
            List of format names in conversion path
        """
        source_fmt = self._normalize_format(source_format)
        target_fmt = self._normalize_format(target_format)
        # Same format - no conversion
        if source_fmt == target_fmt:
            return [source_fmt]
        # Always use xwjson as universal intermediate (required dependency)
        return [source_fmt, 'xwjson', target_fmt]

    def supports_conversion(
        self,
        source_format: str | DataFormat,
        target_format: str | DataFormat
    ) -> bool:
        """
        Check if conversion is supported.
        Uses xwjson converter which supports all formats registered in xwsystem.
        Args:
            source_format: Source format
            target_format: Target format
        Returns:
            True if conversion is supported (xwjson supports all registered formats)
        """
        try:
            from exonware.xwsystem.io.serialization.registry import get_serialization_registry
            registry = get_serialization_registry()
            source_fmt = self._normalize_format(source_format)
            target_fmt = self._normalize_format(target_format)
            # xwjson converter can convert between any formats registered in xwsystem
            source_serializer = registry.get_by_format(source_fmt)
            target_serializer = registry.get_by_format(target_fmt)
            return source_serializer is not None and target_serializer is not None
        except Exception:
            return False

    def _normalize_format(self, format: str | DataFormat) -> str:
        """Normalize format name to lowercase string."""
        if isinstance(format, DataFormat):
            return format.name.lower()
        return str(format).lower()
# Convenience function
async def convert_format(
    data: Any,
    source_format: str | DataFormat,
    target_format: str | DataFormat,
    **opts
) -> Any:
    """
    Convenience function for format conversion.
    Args:
        data: Data to convert
        source_format: Source format
        target_format: Target format
        **opts: Additional options
    Returns:
        Converted data
    """
    converter = FormatConverter()
    return await converter.convert(data, source_format, target_format, **opts)
__all__ = ['FormatConverter', 'convert_format']
