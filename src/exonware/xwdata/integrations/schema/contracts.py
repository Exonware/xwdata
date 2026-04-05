#!/usr/bin/env python3
"""
#exonware/xwdata/src/exonware/xwdata/integrations/schema/contracts.py
Schema Integration Contracts (Optional BaaS Feature)
Defines interfaces for xwschema validation integration.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.13
Generation Date: 26-Jan-2025
"""


from typing import Any, Protocol, runtime_checkable
from ...contracts import IData
from ...defs import DataFormat
@runtime_checkable

class ISchemaValidator(Protocol):
    """
    Interface for schema validation using xwschema.
    Provides schema-driven validation for xwdata.
    This is an optional BaaS feature - xwschema is an optional dependency.
    """

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
        ...

    async def validate_file(
        self,
        data_path: str | Any,  # Path or IData
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
        ...
@runtime_checkable

class ISchemaMapper(Protocol):
    """
    Interface for format-to-schema mapping.
    Maps xwdata formats to schema formats.
    This is an optional BaaS feature.
    """

    def map_format_to_schema(
        self,
        data_format: str | DataFormat,
        schema_type: str = 'json_schema'
    ) -> str:
        """
        Map xwdata format to schema format.
        Args:
            data_format: xwdata format
            schema_type: Schema type (json_schema, openapi, avro, etc.)
        Returns:
            Schema format identifier
        """
        ...

    def get_schema_format(
        self,
        schema: Any  # xwschema schema object
    ) -> str | None:
        """
        Get schema format from schema object.
        Args:
            schema: Schema object from xwschema
        Returns:
            Schema format identifier or None
        """
        ...
__all__ = ['ISchemaValidator', 'ISchemaMapper']
