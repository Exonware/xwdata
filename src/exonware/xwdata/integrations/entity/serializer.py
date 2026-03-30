#!/usr/bin/env python3
"""
#exonware/xwdata/src/exonware/xwdata/integrations/entity/serializer.py
Entity Serializer/Deserializer Implementation (Optional BaaS Feature)
Provides entity serialization/deserialization for xwentity integration.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.8
Generation Date: 26-Jan-2025
"""

from typing import Any
from pathlib import Path
from exonware.xwsystem import get_logger
from .contracts import IEntitySerializer, IEntityDeserializer
from ...contracts import IData
from ...defs import DataFormat
from ...errors import XWDataError
logger = get_logger(__name__)
# Optional xwentity dependency
try:
    # xwentity integration would go here
    # For now, this is a placeholder interface
    XWENTITY_AVAILABLE = False
except ImportError:
    XWENTITY_AVAILABLE = False


class EntitySerializer(IEntitySerializer):
    """
    Entity serializer for xwentity integration.
    Serializes entities to various formats.
    This is an optional BaaS feature - xwentity is an optional dependency.
    """

    def __init__(self):
        """Initialize entity serializer."""
        if not XWENTITY_AVAILABLE:
            logger.warning(
                "EntitySerializer requires xwentity library. "
                "Install with: pip install exonware-xwentity"
            )

    async def serialize(
        self,
        entity: Any,  # xwentity entity object
        format: str | DataFormat = 'json',
        **opts
    ) -> IData:
        """
        Serialize entity to IData in specified format.
        Args:
            entity: Entity object from xwentity
            format: Target format
            **opts: Additional serialization options
        Returns:
            IData instance with serialized entity
        """
        if not XWENTITY_AVAILABLE:
            raise XWDataError(
                "EntitySerializer requires xwentity library. "
                "Install with: pip install exonware-xwentity"
            )
        # Convert entity to dict (would use xwentity's to_dict method)
        if hasattr(entity, 'to_dict'):
            entity_dict = entity.to_dict()
        elif hasattr(entity, '__dict__'):
            entity_dict = entity.__dict__
        else:
            entity_dict = dict(entity)
        # Create IData from dict
        from ...facade import XWData
        data = XWData(entity_dict)
        # Serialize to format if needed
        if format and format != 'native':
            await data.save(f"temp.{self._normalize_format(format)}", format=format, **opts)
            data = await XWData.load(f"temp.{self._normalize_format(format)}", format_hint=format, **opts)
        return data

    async def serialize_to_file(
        self,
        entity: Any,  # xwentity entity object
        path: str | Path,
        format: str | DataFormat | None = None,
        **opts
    ) -> IData:
        """
        Serialize entity to file.
        Args:
            entity: Entity object from xwentity
            path: File path
            format: Optional format (auto-detected from path if not provided)
            **opts: Additional options
        Returns:
            IData instance
        """
        data = await self.serialize(entity, format or 'json', **opts)
        await data.save(path, format=format, **opts)
        return data

    def _normalize_format(self, format: str | DataFormat) -> str:
        """Normalize format name to lowercase string."""
        if isinstance(format, DataFormat):
            return format.name.lower()
        return str(format).lower()


class EntityDeserializer(IEntityDeserializer):
    """
    Entity deserializer for xwentity integration.
    Deserializes formats to entities.
    This is an optional BaaS feature.
    """

    def __init__(self):
        """Initialize entity deserializer."""
        if not XWENTITY_AVAILABLE:
            logger.warning(
                "EntityDeserializer requires xwentity library. "
                "Install with: pip install exonware-xwentity"
            )

    async def deserialize(
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
            **opts: Additional deserialization options
        Returns:
            Entity object
        """
        if not XWENTITY_AVAILABLE:
            raise XWDataError(
                "EntityDeserializer requires xwentity library. "
                "Install with: pip install exonware-xwentity"
            )
        # Get native data from IData
        native_data = data.to_native()
        # Convert to entity (would use xwentity's from_dict method)
        if hasattr(entity_type, 'from_dict'):
            return entity_type.from_dict(native_data, **opts)
        elif hasattr(entity_type, '__init__'):
            return entity_type(**native_data, **opts)
        else:
            raise XWDataError(f"Entity type {entity_type} does not support deserialization")

    async def deserialize_from_file(
        self,
        path: str | Path,
        entity_type: type,
        format: str | DataFormat | None = None,
        **opts
    ) -> Any:
        """
        Deserialize file to entity.
        Args:
            path: File path
            entity_type: Entity type class
            format: Optional format hint
            **opts: Additional options
        Returns:
            Entity object
        """
        from ...facade import XWData
        data = await XWData.load(path, format_hint=format, **opts)
        return await self.deserialize(data, entity_type, **opts)
__all__ = ['EntitySerializer', 'EntityDeserializer']
