"""Demo: run xwquery over a paged subset of chatdb.jsonl.
Important: This demo queries a *paged subset* (in-memory) rather than the full file.
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
import db_io


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Demo xwquery on a JSONL page")
    p.add_argument("--db", type=str, default=None)
    p.add_argument("--page", type=int, default=200, help="Starting page (messages start ~page 100+)")
    p.add_argument("--page-size", type=int, default=500)
    p.add_argument("--min-views", type=int, default=1000)
    p.add_argument("--max-seek-pages", type=int, default=500, help="Scan forward to find Message records")
    return p.parse_args()
async def _run(db_path: Path, page: int, page_size: int, min_views: int, max_seek_pages: int) -> int:
    # Use db_io directly for reliable record-level paging
    current_page = page
    page_records = db_io.get_record_page(db_path, current_page, page_size)
    messages = [r for r in page_records if r.get("@type") == "Message"]
    # If the starting page doesn't contain messages (e.g., header blocks), scan forward.
    attempts = 0
    while not messages and attempts < max_seek_pages:
        attempts += 1
        current_page += 1
        page_records = db_io.get_record_page(db_path, current_page, page_size)
        messages = [r for r in page_records if r.get("@type") == "Message"]
        if attempts % 50 == 0:
            print(f"... scanned to page {current_page}, messages={len(messages)}")
    print(f"Loaded page {current_page}: items={len(page_records)}, messages={len(messages)}")
    # Prepare a queryable in-memory view
    view = XWData.from_native({"messages": messages})
    sql = f"SELECT * FROM messages WHERE payload.views > {min_views}"
    res = await view.query(sql, format="sql")
    if hasattr(res, "success"):
        print(f"SQL success={res.success} action={res.action_type} error={res.error!r}")
        data = res.data
    else:
        # Some older paths may return raw data
        data = res
    # Show results
    try:
        if isinstance(data, list):
            n = len(data)
            print(f"Result rows: {n}")
            if n > 0:
                # Show first result as preview
                first = data[0]
                msg_id = first.get("id", "?")
                views = first.get("payload", {}).get("views", "?")
                text_preview = first.get("payload", {}).get("text", "")[:60]
                print(f"  First result: id={msg_id}, views={views}, text='{text_preview}...'")
        else:
            print(f"Result (non-list): {type(data).__name__}")
    except Exception as e:
        print(f"Error inspecting results: {e}")
    return 0


def main() -> int:
    args = _parse_args()
    db_path = Path(args.db) if args.db else db_io.default_db_path()
    return asyncio.run(_run(db_path, args.page, args.page_size, args.min_views, args.max_seek_pages))
if __name__ == "__main__":
    raise SystemExit(main())
