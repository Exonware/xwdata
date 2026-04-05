#!/usr/bin/env python3
"""
#exonware/xwdata/src/exonware/xwdata/integrations/schema/__init__.py
Schema Integration Module (Optional BaaS Feature)
Provides integration interfaces for xwschema validation.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.13
Generation Date: 26-Jan-2025
"""
# Optional imports - these will be None if xwschema is not available

try:
    from .contracts import ISchemaValidator, ISchemaMapper
    from .validator import SchemaValidator
    from .mapper import SchemaMapper
    SCHEMA_INTEGRATION_AVAILABLE = True
except ImportError:
    SCHEMA_INTEGRATION_AVAILABLE = False
    ISchemaValidator = None
    ISchemaMapper = None
    SchemaValidator = None
    SchemaMapper = None
__all__ = []
if SCHEMA_INTEGRATION_AVAILABLE:
    __all__.extend([
        'ISchemaValidator',
        'ISchemaMapper',
        'SchemaValidator',
        'SchemaMapper',
    ])
