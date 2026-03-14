#!/usr/bin/env python3
"""
#exonware/xwdata/src/exonware/xwdata/operations/format_validator.py
Format Validator (Optional BaaS Feature)
Provides format-specific validation beyond basic type checking.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.3
Generation Date: 26-Jan-2025
"""

from typing import Any
from pathlib import Path
from exonware.xwsystem import get_logger
from ..contracts import IFormatValidator
from ..defs import DataFormat
from ..errors import XWDataError
logger = get_logger(__name__)


class FormatValidator(IFormatValidator):
    """
    Format-specific validator.
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
        format_name = self._normalize_format(format)
        errors = []
        try:
            # Get serializer from xwsystem AutoSerializer (same as xwdata uses)
            # Format name must be uppercase for AutoSerializer
            from exonware.xwsystem.io.serialization.auto_serializer import AutoSerializer
            auto_serializer = AutoSerializer()
            format_upper = format_name.upper()
            serializer = auto_serializer._get_serializer(format_upper)
            if not serializer:
                errors.append(f"Serializer not found for format: {format_name}")
                return {'valid': False, 'errors': errors}
            # Try to serialize/deserialize to validate format
            if isinstance(data, (dict, list)):
                # Native data - try serialization
                try:
                    serialized = serializer.dumps(data, **opts)
                    # Try to deserialize back to validate
                    deserialized = serializer.loads(serialized, **opts)
                    # Basic validation passed
                except Exception as e:
                    errors.append(f"Serialization validation failed: {e}")
            else:
                # Serialized data - try deserialization
                try:
                    deserialized = serializer.loads(data, **opts)
                    # Basic validation passed
                except Exception as e:
                    errors.append(f"Deserialization validation failed: {e}")
            # Format-specific validation
            format_errors = await self._validate_format_specific(data, format_name, **opts)
            errors.extend(format_errors)
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'format': format_name
            }
        except Exception as e:
            logger.error(f"Validation error: {e}")
            errors.append(f"Validation error: {e}")
            return {'valid': False, 'errors': errors}

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
        path_obj = Path(path)
        if not path_obj.exists():
            return {
                'valid': False,
                'errors': [f"File not found: {path_obj}"]
            }
        # Detect format if not provided
        if format:
            format_name = self._normalize_format(format)
        else:
            format_name = path_obj.suffix.lstrip('.').lower()
        # Read file
        try:
            if path_obj.suffix.lower() in ['.json', '.yaml', '.yml', '.toml', '.xml', '.csv']:
                data = path_obj.read_text(encoding='utf-8')
            else:
                data = path_obj.read_bytes()
        except Exception as e:
            return {
                'valid': False,
                'errors': [f"Failed to read file: {e}"]
            }
        # Validate
        return await self.validate(data, format_name, **opts)

    async def _validate_format_specific(
        self,
        data: Any,
        format_name: str,
        **opts
    ) -> list[str]:
        """
        Perform format-specific validation.
        Args:
            data: Data to validate
            format_name: Format name
            **opts: Validation options
        Returns:
            List of validation errors
        """
        errors = []
        # JSON-specific validation
        if format_name == 'json':
            if isinstance(data, str):
                from exonware.xwsystem.io.serialization import JsonSerializer, SerializationError
                try:
                    JsonSerializer().decode(data)
                except SerializationError as e:
                    errors.append(f"Invalid JSON: {e}")
        # YAML-specific validation
        elif format_name in ['yaml', 'yml']:
            if isinstance(data, str):
                try:
                    from exonware.xwsystem.io.serialization import YamlSerializer, SerializationError
                    YamlSerializer().decode(data)
                except SerializationError as e:
                    errors.append(f"Invalid YAML: {e}")
                except ImportError:
                    pass  # YAML library not available
        # XML-specific validation
        elif format_name == 'xml':
            if isinstance(data, str):
                try:
                    from exonware.xwsystem.io.serialization import XmlSerializer, SerializationError
                    XmlSerializer().decode(data)
                except SerializationError as e:
                    errors.append(f"Invalid XML: {e}")
        # Add more format-specific validations as needed
        return errors

    def _normalize_format(self, format: str | DataFormat) -> str:
        """Normalize format name to lowercase string."""
        if isinstance(format, DataFormat):
            return format.name.lower()
        return str(format).lower()
__all__ = ['FormatValidator']
