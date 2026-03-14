"""
Convenience module for importing {LIBRARY_NAME}.
This allows users to import the library in two ways:
1. import exonware.{LIBRARY_NAME}
2. import {LIBRARY_NAME}  # This convenience import
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.2
Generation Date: {GENERATION_DATE}
"""
# Import everything from the main package

from exonware.xwdata import *  # noqa: F401, F403
# Re-export version from source of truth
from exonware.xwdata import __version__
