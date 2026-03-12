"""Demo: XWJSON operations on chatdb database.
Demonstrates XWJSON operations:
- Loading XWJSON file
- Paging through records
- Path-based access
- Queries
- Updates
Run (from repo root):
  python xwdata/examples/chatdb_bigfile/operations/demo_xwjson.py
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
"""

from __future__ import annotations
import argparse
import asyncio
import sys
from pathlib import Path
# Add xwjson to path
try:
    from exonware.xwjson import XWJSONSerializer
    from exonware.xwjson.operations.xwjson_ops import XWJSONDataOperations
    XWJSON_AVAILABLE = True
except ImportError:
    XWJSON_AVAILABLE = False
    print("ERROR: xwjson not available. Install with: pip install exonware-xwjson")
    sys.exit(1)


def _here() -> Path:
    return Path(__file__).resolve()


def default_xwjson_path() -> Path:
    return _here().parents[1] / "data" / "chatdb.xwjson"
async def demo_load(xwjson_path: Path) -> None:
    """Demo: Load XWJSON file."""
    print("=" * 60)
    print("Demo: Load XWJSON File")
    print("=" * 60)
    serializer = XWJSONSerializer()
    print(f"Loading {xwjson_path}...")
    data = serializer.load_file(xwjson_path)
    records = data.get("records", [])
    print(f"Loaded {len(records):,} records")
    if records:
        print(f"\nFirst record:")
        print(f"  Type: {records[0].get('@type')}")
        print(f"  ID: {records[0].get('id')}")
        print(f"  Payload keys: {list(records[0].get('payload', {}).keys())}")
    print()
async def demo_paging(xwjson_path: Path, page: int = 1, page_size: int = 25) -> None:
    """Demo: Paging through records."""
    print("=" * 60)
    print(f"Demo: Paging (page {page}, size {page_size})")
    print("=" * 60)
    ops = XWJSONDataOperations()
    print(f"Reading page {page}...")
    page_records = await ops.read_page(xwjson_path, page_number=page, page_size=page_size, path="/records")
    print(f"Retrieved {len(page_records)} records")
    if page_records:
        print(f"\nFirst record in page:")
        first = page_records[0]
        print(f"  Type: {first.get('@type')}")
        print(f"  ID: {first.get('id')}")
        if first.get('@type') == 'Message':
            payload = first.get('payload', {})
            text = payload.get('text', '')[:50]
            print(f"  Text preview: {text}...")
    print()
async def demo_path_access(xwjson_path: Path) -> None:
    """Demo: Path-based access."""
    print("=" * 60)
    print("Demo: Path-Based Access")
    print("=" * 60)
    ops = XWJSONDataOperations()
    # Access various paths
    paths = [
        "/records/0/@type",
        "/records/0/id",
        "/records/0/payload/text",
    ]
    for path in paths:
        try:
            value = await ops.read_path(xwjson_path, path)
            print(f"  {path}: {str(value)[:50]}")
        except Exception as e:
            print(f"  {path}: Error - {e}")
    print()
async def demo_query(xwjson_path: Path) -> None:
    """Demo: Query operations."""
    print("=" * 60)
    print("Demo: Query Operations")
    print("=" * 60)
    ops = XWJSONDataOperations()
    # Try JSONPath query
    try:
        print("Query: $.records[*].@type (get all record types)")
        results = await ops.query(xwjson_path, "$.records[*].@type")
        if isinstance(results, list):
            # Count types
            from collections import Counter
            type_counts = Counter(results)
            print(f"Found {len(results)} records")
            print("Type distribution:")
            for record_type, count in type_counts.most_common():
                print(f"  {record_type}: {count:,}")
        else:
            print(f"Results: {results}")
    except Exception as e:
        print(f"Query failed: {e}")
        print("(Query support may require xwquery)")
    print()
async def demo_update(xwjson_path: Path) -> None:
    """Demo: Update operations."""
    print("=" * 60)
    print("Demo: Update Operations")
    print("=" * 60)
    ops = XWJSONDataOperations()
    # Read first record
    try:
        first_type = await ops.read_path(xwjson_path, "/records/0/@type")
        print(f"First record type: {first_type}")
        # Update a path (if it's a Message)
        if first_type == "Message":
            # Read current text
            current_text = await ops.read_path(xwjson_path, "/records/0/payload/text")
            print(f"Current text: {str(current_text)[:50]}...")
            # Update text
            new_text = "Updated via XWJSON demo"
            await ops.write_path(xwjson_path, "/records/0/payload/text", new_text)
            # Verify update
            updated_text = await ops.read_path(xwjson_path, "/records/0/payload/text")
            print(f"Updated text: {updated_text}")
            print("✓ Update successful")
    except Exception as e:
        print(f"Update demo failed: {e}")
    print()
async def run_demos(xwjson_path: Path) -> int:
    """Run all demos."""
    if not xwjson_path.exists():
        print(f"ERROR: XWJSON file not found: {xwjson_path}")
        print("Run convert_to_xwjson.py first to create the XWJSON file.")
        return 1
    print()
    print("=" * 60)
    print("XWJSON Operations Demo")
    print("=" * 60)
    print(f"File: {xwjson_path}")
    print(f"Size: {xwjson_path.stat().st_size / (1024 * 1024 * 1024):.2f} GB")
    print()
    await demo_load(xwjson_path)
    await demo_paging(xwjson_path, page=1, page_size=25)
    await demo_path_access(xwjson_path)
    await demo_query(xwjson_path)
    await demo_update(xwjson_path)
    print("=" * 60)
    print("Demo Complete")
    print("=" * 60)
    return 0


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Demo XWJSON operations on chatdb")
    p.add_argument("--xwjson", type=str, default=str(default_xwjson_path()), help="XWJSON file path")
    p.add_argument("--page", type=int, default=1, help="Page number for paging demo")
    p.add_argument("--page-size", type=int, default=25, help="Page size for paging demo")
    return p.parse_args()


def main() -> int:
    if not XWJSON_AVAILABLE:
        print("ERROR: xwjson not available")
        return 1
    args = _parse_args()
    xwjson_path = Path(args.xwjson)
    return asyncio.run(run_demos(xwjson_path))
if __name__ == "__main__":
    raise SystemExit(main())
