#!/usr/bin/env python3
"""
#exonware/xwdata/src/exonware/xwdata/integrations/schema/validator.py
Schema Validator Implementation (BaaS Feature)
Provides schema validation using xwschema. Integration is via ISchemaValidator:
xwschema requires xwdata as its base engine; xwdata uses xwschema only in this
module when validating data. Circular dependency is avoided: xwschema imports
xwdata at module level; xwdata imports xwschema only here when this validator
is used (xwdata is already loaded).
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.18
Generation Date: 26-Jan-2025
"""

from typing import Any
from pathlib import Path
from exonware.xwsystem import get_logger
from .contracts import ISchemaValidator
from ...contracts import IData
from ...defs import DataFormat
from ...errors import XWDataError
logger = get_logger(__name__)
# Optional xwschema dependency
try:
    from exonware.xwschema import XWSchema
    XWSCHEMA_AVAILABLE = True
except ImportError:
    XWSCHEMA_AVAILABLE = False
    XWSchema = None


class SchemaValidator(ISchemaValidator):
    """
    Schema validator using xwschema.
    Provides schema-driven validation for xwdata.
    This is an optional BaaS feature - xwschema is an optional dependency.
    """

    def __init__(self):
        """Initialize schema validator."""
        if not XWSCHEMA_AVAILABLE:
            logger.warning(
                "SchemaValidator requires xwschema library. "
                "Install with: pip install exonware-xwschema"
            )

    async def validate(
        self,
        data: IData,
        schema: Any,  # xwschema schema object
        format: str | DataFormat | None = None,
        **opts
    ) -> dict[str, Any]:
        """
        Validate data against schema.
        Args:
            data: Data to validate
            schema: Schema object from xwschema
            format: Optional format hint
            **opts: Additional validation options
        Returns:
            Validation result dictionary with 'valid' (bool) and 'errors' (list)
        """
        if not XWSCHEMA_AVAILABLE:
            raise XWDataError(
                "SchemaValidator requires xwschema library. "
                "Install with: pip install exonware-xwschema"
            )
        try:
            # Pass IData (XWData) when possible so xwschema can use path-based validation
            payload = data if hasattr(data, 'to_native') and hasattr(data, '__getitem__') else data.to_native()
            # Use xwschema for validation (schema.validate accepts dict, list, or XWData)
            if isinstance(schema, XWSchema):
                validation_result = await schema.validate(payload, **opts)
            else:
                xw_schema = XWSchema(schema)
                validation_result = await xw_schema.validate(payload, **opts)
            # xwschema.validate returns (bool, list[str]); xwdata expects dict with valid/errors
            if isinstance(validation_result, tuple):
                is_valid, errors = validation_result
                validation_result = {'valid': is_valid, 'errors': errors or []}
            data_format = None
            if hasattr(data, 'get_format') and callable(data.get_format):
                data_format = data.get_format()
            if data_format is None and hasattr(data, 'get_active_format') and callable(data.get_active_format):
                data_format = data.get_active_format()
            return {
                'valid': validation_result.get('valid', False),
                'errors': validation_result.get('errors', []),
                'format': format or data_format
            }
        except Exception as e:
            logger.error(f"Schema validation failed: {e}")
            return {
                'valid': False,
                'errors': [str(e)],
                'format': format or data.get_format()
            }

    async def validate_file(
        self,
        data_path: str | Path | IData,
        schema: Any,  # xwschema schema object
        format: str | DataFormat | None = None,
        **opts
    ) -> dict[str, Any]:
        """
        Validate file against schema.
        Args:
            data_path: File path or IData instance
            schema: Schema object from xwschema
            format: Optional format hint
            **opts: Additional validation options
        Returns:
            Validation result dictionary
        """
        if not XWSCHEMA_AVAILABLE:
            raise XWDataError(
                "SchemaValidator requires xwschema library. "
                "Install with: pip install exonware-xwschema"
            )
        # Handle IData instance
        if isinstance(data_path, IData):
            return await self.validate(data_path, schema, format, **opts)
        # Load from file
        from ...facade import XWData
        data = await XWData.load(data_path, format_hint=format, **opts)
        return await self.validate(data, schema, format, **opts)
__all__ = ['SchemaValidator']
