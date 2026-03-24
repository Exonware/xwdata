#!/usr/bin/env python3
"""
#exonware/xwdata/src/exonware/xwdata/data/references/__init__.py
Reference Resolution System
Detection and resolution of cross-references in data.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.7
Generation Date: 26-Oct-2025
"""

from .detector import ReferenceDetector
from .resolver import ReferenceResolver
from .patterns import ReferencePatterns
__all__ = [
    'ReferenceDetector',
    'ReferenceResolver',
    'ReferencePatterns',
]
