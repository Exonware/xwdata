"""Repository-local examples package for the xwdata project.

Note:
- This lives under the repo's `xwdata/examples/` folder (not the installed wheel).
- It exists to support running examples with:

    python -m xwdata.examples.<example_module>

When running from the monorepo, ensure your environment can import
`exonware.xwdata` (e.g. editable install or PYTHONPATH pointing at `xwdata/src`).
"""

from __future__ import annotations

# Make repo-root example execution work without requiring editable installs.
# This only affects the local `xwdata/examples` package (not the distributed wheel).
import sys
from pathlib import Path

_xwdata_root = Path(__file__).resolve().parents[1]
_xwdata_src = _xwdata_root / "src"
if _xwdata_src.exists() and str(_xwdata_src) not in sys.path:
    sys.path.insert(0, str(_xwdata_src))
