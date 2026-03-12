"""chatdb_bigfile example.
A single-file JSONL "chat database" used to demonstrate:
- xwsystem JsonLinesSerializer (record paging + atomic updates)
- xwdata lazy file-backed nodes + paging
- xwschema validation
- xwnode navigation
- xwquery querying over paged subsets
"""

from __future__ import annotations
