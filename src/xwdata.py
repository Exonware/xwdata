#!/usr/bin/env python3
"""
#exonware/xwdata/src/xwdata.py
Convenience module for importing xwdata.
This allows users to import the library in two ways:
1. from exonware.xwdata import XWData
2. import xwdata  # This convenience import
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.9
Generation Date: 26-Oct-2025
"""
# Import everything from the main package

from exonware.xwdata import *  # noqa: F401, F403
# Re-export version from source of truth (version.py via exonware.xwdata)
__version__ = __version__  # noqa: F405
