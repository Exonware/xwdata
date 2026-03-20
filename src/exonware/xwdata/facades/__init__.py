#!/usr/bin/env python3
"""
#exonware/xwdata/src/exonware/xwdata/facades/__init__.py
XWData Facades Module
Provides specialized facades for different use cases.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.6
Generation Date: 26-Jan-2025
"""

try:
    from .baas import XWDataBaaSFacade
    BaaS_AVAILABLE = True
except ImportError:
    BaaS_AVAILABLE = False
    XWDataBaaSFacade = None
__all__ = []
if BaaS_AVAILABLE:
    __all__.append('XWDataBaaSFacade')
