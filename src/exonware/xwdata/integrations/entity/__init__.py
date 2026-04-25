#!/usr/bin/env python3
"""
#exonware/xwdata/src/exonware/xwdata/integrations/entity/__init__.py
Entity Integration Module (Optional BaaS Feature)
Provides integration interfaces for xwentity operations.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.18
Generation Date: 26-Jan-2025
"""
# Optional imports - these will be None if xwentity is not available

try:
    from .contracts import IEntitySerializer, IEntityDeserializer
    from .serializer import EntitySerializer, EntityDeserializer
    ENTITY_INTEGRATION_AVAILABLE = True
except ImportError:
    ENTITY_INTEGRATION_AVAILABLE = False
    IEntitySerializer = None
    IEntityDeserializer = None
    EntitySerializer = None
    EntityDeserializer = None
__all__ = []
if ENTITY_INTEGRATION_AVAILABLE:
    __all__.extend([
        'IEntitySerializer',
        'IEntityDeserializer',
        'EntitySerializer',
        'EntityDeserializer',
    ])
