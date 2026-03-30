#!/usr/bin/env python3
"""
#exonware/xwdata/src/exonware/xwdata/integrations/schema/mapper.py
Schema Format Mapper (Optional BaaS Feature)
Maps xwdata formats to schema formats.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.11
Generation Date: 26-Jan-2025
"""

from typing import Any
from exonware.xwsystem import get_logger
from .contracts import ISchemaMapper
from ...defs import DataFormat
logger = get_logger(__name__)


class SchemaMapper(ISchemaMapper):
    """
    Format-to-schema mapping.
    Maps xwdata formats to schema formats.
    This is an optional BaaS feature.
    """

    def __init__(self):
        """Initialize schema mapper."""
        # Format to schema type mapping
        self._format_to_schema = {
            'json': 'json_schema',
            'json5': 'json_schema',
            'yaml': 'json_schema',  # YAML can use JSON Schema
            'xml': 'xml_schema',
            'toml': 'json_schema',  # TOML can use JSON Schema
            'avro': 'avro_schema',
            'protobuf': 'protobuf_schema',
        }

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
        format_name = self._normalize_format(data_format)
        # Get default schema type for format
        default_schema = self._format_to_schema.get(format_name, 'json_schema')
        # Use provided schema_type if it matches format, otherwise use default
        if schema_type in ['json_schema', 'openapi'] and format_name in ['json', 'yaml', 'json5']:
            return schema_type
        return default_schema

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
        # This would inspect the schema object to determine format
        # Placeholder implementation
        if hasattr(schema, 'format'):
            return schema.format
        if hasattr(schema, 'schema_type'):
            return schema.schema_type
        return None

    def _normalize_format(self, format: str | DataFormat) -> str:
        """Normalize format name to lowercase string."""
        if isinstance(format, DataFormat):
            return format.name.lower()
        return str(format).lower()
__all__ = ['SchemaMapper']
