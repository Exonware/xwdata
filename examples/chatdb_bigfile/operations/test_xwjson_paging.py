"""Test XWJSON paging to verify bug fix.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
"""

from exonware.xwjson import XWJSONSerializer
from pathlib import Path


def test_paging():
    serializer = XWJSONSerializer()
    file_path = Path(__file__).parents[1] / "data" / "chatdb.xwjson"
    print("Testing XWJSON paging...")
    print(f"File: {file_path}")
    print()
    total_records = 0
    num_pages = 10
    page_size = 100
    for i in range(1, num_pages + 1):
        page = serializer.get_record_page(file_path, page_number=i, page_size=page_size)
        total_records += len(page)
        print(f"Page {i}: {len(page)} records")
    print()
    print(f"Total records: {total_records}")
    print(f"Expected: {num_pages * page_size} records")
    if total_records == num_pages * page_size:
        print("[PASS] Paging bug is fixed!")
    else:
        print(f"[FAIL] Expected {num_pages * page_size}, got {total_records}")
if __name__ == "__main__":
    test_paging()
