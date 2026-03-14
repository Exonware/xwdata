#!/usr/bin/env python3
"""
#exonware/xwdata/src/exonware/xwdata/integrations/entity/contracts.py
Entity Integration Contracts (Optional BaaS Feature)
Defines interfaces for xwentity integration.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.5
Generation Date: 26-Jan-2025
"""


from typing import Any, Protocol, runtime_checkable
from ...contracts import IData
from ...defs import DataFormat
@runtime_checkable

class IEntitySerializer(Protocol):
    """
    Interface for entity serialization.
    Serializes entities to various formats.
    This is an optional BaaS feature - xwentity is an optional dependency.
    """

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
        ...

    async def serialize_to_file(
        self,
        entity: Any,  # xwentity entity object
        path: str | Any,  # Path
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
        ...
@runtime_checkable

class IEntityDeserializer(Protocol):
    """
    Interface for entity deserialization.
    Deserializes formats to entities.
    This is an optional BaaS feature.
    """

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
        ...

    async def deserialize_from_file(
        self,
        path: str | Any,  # Path
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
        ...
__all__ = ['IEntitySerializer', 'IEntityDeserializer']
