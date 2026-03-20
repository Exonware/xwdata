#!/usr/bin/env python3
"""
#exonware/xwdata/src/exonware/xwdata/facades/baas.py
BaaS Facade for XWData (Optional BaaS Features)
Provides convenience methods for BaaS multi-format storage operations.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.6
Generation Date: 26-Jan-2025
"""

from typing import Any
from pathlib import Path
from exonware.xwsystem import get_logger
from ..contracts import IData
from ..defs import DataFormat
from ..facade import XWData
from ..operations.format_conversion import FormatConverter, convert_format
from ..operations.conversion_pipeline import ConversionPipeline
from ..operations.format_validator import FormatValidator
logger = get_logger(__name__)
# Optional integration imports
try:
    from ..integrations.storage import StorageAdapter, StorageFormatMapper, StorageBatchOperations
    STORAGE_AVAILABLE = True
except ImportError:
    STORAGE_AVAILABLE = False
    StorageAdapter = None
    StorageFormatMapper = None
    StorageBatchOperations = None
try:
    from ..integrations.schema import SchemaValidator, SchemaMapper
    SCHEMA_AVAILABLE = True
except ImportError:
    SCHEMA_AVAILABLE = False
    SchemaValidator = None
    SchemaMapper = None
try:
    from ..integrations.entity import EntitySerializer, EntityDeserializer
    ENTITY_AVAILABLE = True
except ImportError:
    ENTITY_AVAILABLE = False
    EntitySerializer = None
    EntityDeserializer = None


class XWDataBaaSFacade:
    """
    BaaS facade for xwdata BaaS platform capabilities.
    Provides convenience methods for:
    - Format conversion (using xwjson XWJSONConverter)
    - Storage integration (optional - requires xwstorage)
    - Schema validation (optional - requires xwschema)
    - Entity operations (optional - requires xwentity)
    - Batch operations
    All features are optional and can be used independently.
    Required dependencies: xwsystem, xwnode, xwquery, xwjson
    """

    def __init__(self):
        """Initialize BaaS facade."""
        # Format conversion (always available - uses xwjson)
        self._converter = FormatConverter()
        self._pipeline = ConversionPipeline(self._converter)
        self._validator = FormatValidator()
        # Optional integrations (lazy initialization)
        self._storage_adapter: StorageAdapter | None = None
        self._storage_mapper: StorageFormatMapper | None = None
        self._storage_batch: StorageBatchOperations | None = None
        self._schema_validator: SchemaValidator | None = None
        self._schema_mapper: SchemaMapper | None = None
        self._entity_serializer: EntitySerializer | None = None
        self._entity_deserializer: EntityDeserializer | None = None
    # ============================================================================
    # FORMAT CONVERSION (Always Available - Uses xwjson)
    # ============================================================================

    async def convert_format(
        self,
        data: IData | Any,
        source_format: str | DataFormat,
        target_format: str | DataFormat,
        **opts
    ) -> IData:
        """
        Convert data from source format to target format.
        Uses xwjson XWJSONConverter for lossless, metadata-preserving conversion.
        Args:
            data: Data to convert (IData instance or native data)
            source_format: Source format
            target_format: Target format
            **opts: Additional conversion options
        Returns:
            Converted data as IData instance
        """
        # Convert to IData if needed
        if not isinstance(data, IData):
            data = XWData(data)
        # Serialize source format
        source_serialized = await data.serialize(source_format, **opts)
        # Convert using xwjson converter
        target_serialized = await self._converter.convert(
            source_serialized,
            source_format,
            target_format,
            **opts
        )
        # Create IData from converted data
        return await XWData.parse(target_serialized, format=target_format, **opts)

    async def convert_file(
        self,
        source_path: str | Path,
        target_path: str | Path,
        target_format: str | DataFormat | None = None,
        **opts
    ) -> IData:
        """
        Convert file from source format to target format.
        Args:
            source_path: Source file path
            target_path: Target file path
            target_format: Optional target format (auto-detected if not provided)
            **opts: Additional options
        Returns:
            Converted data as IData instance
        """
        await self._converter.convert_file(source_path, target_path, target_format, **opts)
        return await XWData.load(target_path, format_hint=target_format, **opts)

    async def convert_pipeline(
        self,
        data: IData | Any,
        steps: list[tuple[str | DataFormat, dict[str, Any]]],
        **opts
    ) -> IData:
        """
        Execute multi-step conversion pipeline.
        Args:
            data: Initial data
            steps: List of (format, options) tuples for each step
            **opts: Global pipeline options
        Returns:
            Final converted data as IData instance
        """
        # Convert to IData if needed
        if not isinstance(data, IData):
            data = XWData(data)
        # Serialize initial data
        initial_format = steps[0][0] if steps else 'json'
        serialized = await data.serialize(initial_format, **opts)
        # Execute pipeline
        result = await self._pipeline.execute(serialized, steps, **opts)
        # Create IData from result
        final_format = steps[-1][0] if steps else 'json'
        return await XWData.parse(result, format=final_format, **opts)

    async def validate_format(
        self,
        data: IData | Any,
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
            Validation result dictionary
        """
        if not isinstance(data, IData):
            data = XWData(data)
        return await self._validator.validate(data.to_native(), format, **opts)
    # ============================================================================
    # STORAGE INTEGRATION (Optional - Requires xwstorage)
    # ============================================================================

    def get_storage_adapter(self) -> StorageAdapter | None:
        """Get storage adapter (optional - requires xwstorage)."""
        if not STORAGE_AVAILABLE:
            logger.warning("Storage integration requires xwstorage library")
            return None
        if self._storage_adapter is None:
            self._storage_adapter = StorageAdapter()
        return self._storage_adapter

    async def store_to_backend(
        self,
        data: IData,
        backend: str,
        location: str,
        format_hint: str | DataFormat | None = None,
        **opts
    ) -> None:
        """
        Store data to storage backend.
        Args:
            data: Data to store
            backend: Storage backend identifier
            location: Storage location/path
            format_hint: Optional format hint
            **opts: Additional options
        """
        adapter = self.get_storage_adapter()
        if adapter:
            await adapter.store(data, backend, location, format_hint, **opts)
        else:
            raise RuntimeError("Storage integration not available (xwstorage required)")

    async def load_from_backend(
        self,
        backend: str,
        location: str,
        format_hint: str | DataFormat | None = None,
        **opts
    ) -> IData:
        """
        Load data from storage backend.
        Args:
            backend: Storage backend identifier
            location: Storage location/path
            format_hint: Optional format hint
            **opts: Additional options
        Returns:
            Loaded data as IData instance
        """
        adapter = self.get_storage_adapter()
        if adapter:
            return await adapter.load(backend, location, format_hint, **opts)
        else:
            raise RuntimeError("Storage integration not available (xwstorage required)")
    # ============================================================================
    # SCHEMA INTEGRATION (Optional - Requires xwschema)
    # ============================================================================

    def get_schema_validator(self) -> SchemaValidator | None:
        """Get schema validator (optional - requires xwschema)."""
        if not SCHEMA_AVAILABLE:
            logger.warning("Schema integration requires xwschema library")
            return None
        if self._schema_validator is None:
            self._schema_validator = SchemaValidator()
        return self._schema_validator

    async def validate_with_schema(
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
            **opts: Additional options
        Returns:
            Validation result dictionary
        """
        validator = self.get_schema_validator()
        if validator:
            return await validator.validate(data, schema, format, **opts)
        else:
            raise RuntimeError("Schema integration not available (xwschema required)")
    # ============================================================================
    # ENTITY INTEGRATION (Optional - Requires xwentity)
    # ============================================================================

    def get_entity_serializer(self) -> EntitySerializer | None:
        """Get entity serializer (optional - requires xwentity)."""
        if not ENTITY_AVAILABLE:
            logger.warning("Entity integration requires xwentity library")
            return None
        if self._entity_serializer is None:
            self._entity_serializer = EntitySerializer()
        return self._entity_serializer

    def get_entity_deserializer(self) -> EntityDeserializer | None:
        """Get entity deserializer (optional - requires xwentity)."""
        if not ENTITY_AVAILABLE:
            logger.warning("Entity integration requires xwentity library")
            return None
        if self._entity_deserializer is None:
            self._entity_deserializer = EntityDeserializer()
        return self._entity_deserializer

    async def serialize_entity(
        self,
        entity: Any,  # xwentity entity object
        format: str | DataFormat = 'json',
        **opts
    ) -> IData:
        """
        Serialize entity to IData.
        Args:
            entity: Entity object from xwentity
            format: Target format
            **opts: Additional options
        Returns:
            IData instance with serialized entity
        """
        serializer = self.get_entity_serializer()
        if serializer:
            return await serializer.serialize(entity, format, **opts)
        else:
            raise RuntimeError("Entity integration not available (xwentity required)")

    async def deserialize_entity(
        self,
        data: IData,
        entity_type: type,
        **opts
    ) -> Any:
        """
        Deserialize IData to entity.
        Args:
            data: IData instance
            entity_type: Entity type class
            **opts: Additional options
        Returns:
            Entity object
        """
        deserializer = self.get_entity_deserializer()
        if deserializer:
            return await deserializer.deserialize(data, entity_type, **opts)
        else:
            raise RuntimeError("Entity integration not available (xwentity required)")
    # ============================================================================
    # BATCH OPERATIONS
    # ============================================================================

    async def batch_convert(
        self,
        items: list[tuple[Any, str | DataFormat, str | DataFormat]],  # (data, source, target)
        **opts
    ) -> list[IData]:
        """
        Batch convert multiple data items.
        Args:
            items: List of (data, source_format, target_format) tuples
            **opts: Additional options
        Returns:
            List of converted IData instances
        """
        results = []
        for data, source_fmt, target_fmt in items:
            try:
                converted = await self.convert_format(data, source_fmt, target_fmt, **opts)
                results.append(converted)
            except Exception as e:
                logger.error(f"Batch convert failed: {e}")
                results.append(None)
        return results
__all__ = ['XWDataBaaSFacade']
