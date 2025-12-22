"""Demo: show file-backed lazy node behavior for huge JSONL.

This is intentionally small and safe to run in quick mode.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from exonware.xwdata import XWData
from exonware.xwdata.config import XWDataConfig

_OPS_DIR = Path(__file__).resolve().parent
if str(_OPS_DIR) not in sys.path:
    sys.path.insert(0, str(_OPS_DIR))


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Demo xwdata lazy load for JSONL")
    p.add_argument("--db", type=str, default=None, help="Path to chatdb.jsonl")
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--page-size", type=int, default=5)
    return p.parse_args()


async def _run(db_path: Path, page: int, page_size: int) -> int:
    cfg = XWDataConfig.default()
    # Allow large file usage explicitly (example/demo only)
    cfg.security.max_file_size_mb = 10_000
    cfg.security.enable_path_validation = False
    cfg.lazy.defer_file_io = True

    data = await XWData.load(db_path, config=cfg)

    print("Loaded XWData")
    print(f"- detected_format: {data.get_detected_format()}")
    print(f"- lazy_mode: {data._metadata.get('lazy_mode')}")
    print(f"- load_strategy: {data._metadata.get('load_strategy')}")
    print(f"- size_bytes: {data._metadata.get('size_bytes')}")

    # This should NOT materialize the whole file.
    items = await data.get_page(page_number=page, page_size=page_size)
    print(f"Page {page} size={len(items)}")
    if items:
        print(f"First record @type={items[0].to_native().get('@type')} id={items[0].to_native().get('id')}")

    return 0


def main() -> int:
    args = _parse_args()

    if args.db:
        db_path = Path(args.db)
    else:
        import db_io

        db_path = db_io.default_db_path()

    return asyncio.run(_run(db_path, args.page, args.page_size))


if __name__ == "__main__":
    raise SystemExit(main())
