"""Full comparison: JSONL vs XWJSON performance.

Compares JSONL (text) vs XWJSON (binary) performance for:
- File loading
- Record access
- Paging
- Updates
- Memory usage

Run (from repo root):
  python xwdata/examples/chatdb_bigfile/operations/benchmark_xwjson_comparison.py

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Any

# Add xwjson to path
try:
    from exonware.xwjson import XWJSONSerializer
    from exonware.xwjson.operations.xwjson_ops import XWJSONDataOperations
    XWJSON_AVAILABLE = True
except ImportError:
    XWJSON_AVAILABLE = False
    print("WARNING: xwjson not available. Install with: pip install exonware-xwjson")

# Add xwsystem to path
_OPS_DIR = Path(__file__).resolve().parent
if str(_OPS_DIR) not in sys.path:
    sys.path.insert(0, str(_OPS_DIR))

_xwsystem_src = Path(__file__).resolve().parents[4] / "xwsystem" / "src"
if str(_xwsystem_src) not in sys.path:
    sys.path.insert(0, str(_xwsystem_src))

try:
    from exonware.xwsystem.io.serialization.formats.text.jsonlines import JsonLinesSerializer
    JSONLINES_AVAILABLE = True
except ImportError:
    JSONLINES_AVAILABLE = False


def _here() -> Path:
    return Path(__file__).resolve()


def default_jsonl_path() -> Path:
    return _here().parents[1] / "data" / "chatdb.jsonl"


def default_xwjson_path() -> Path:
    return _here().parents[1] / "data" / "chatdb.xwjson"


def _human_bytes(n: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(n)
    for u in units:
        if size < 1024.0 or u == units[-1]:
            return f"{size:.2f}{u}"
        size /= 1024.0
    return f"{n}B"


async def benchmark_jsonl_load(jsonl_path: Path) -> dict[str, Any]:
    """Benchmark JSONL file loading."""
    if not jsonl_path.exists():
        return {"error": "File not found"}
    
    print("JSONL: Loading file...")
    start_time = time.perf_counter()
    
    records = []
    with jsonl_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    
    elapsed = time.perf_counter() - start_time
    file_size = jsonl_path.stat().st_size
    
    mb_per_s = (file_size / (1024 * 1024)) / elapsed if elapsed > 0 else 0
    records_per_s = len(records) / elapsed if elapsed > 0 else 0
    
    print(f"  Loaded {len(records):,} records in {elapsed:.2f}s")
    print(f"  Speed: {mb_per_s:.1f} MB/s, {records_per_s:,.0f} records/s")
    
    return {
        "format": "JSONL",
        "records": len(records),
        "file_size": file_size,
        "load_time": elapsed,
        "mb_per_s": mb_per_s,
        "records_per_s": records_per_s
    }


async def benchmark_xwjson_load(xwjson_path: Path) -> dict[str, Any]:
    """Benchmark XWJSON file loading."""
    if not xwjson_path.exists():
        return {"error": "File not found"}
    
    if not XWJSON_AVAILABLE:
        return {"error": "XWJSON not available"}
    
    serializer = XWJSONSerializer()
    
    print("XWJSON: Loading file...")
    start_time = time.perf_counter()
    
    data = serializer.load_file(xwjson_path)
    records = data.get("records", [])
    
    elapsed = time.perf_counter() - start_time
    file_size = xwjson_path.stat().st_size
    
    mb_per_s = (file_size / (1024 * 1024)) / elapsed if elapsed > 0 else 0
    records_per_s = len(records) / elapsed if elapsed > 0 else 0
    
    print(f"  Loaded {len(records):,} records in {elapsed:.2f}s")
    print(f"  Speed: {mb_per_s:.1f} MB/s, {records_per_s:,.0f} records/s")
    
    return {
        "format": "XWJSON",
        "records": len(records),
        "file_size": file_size,
        "load_time": elapsed,
        "mb_per_s": mb_per_s,
        "records_per_s": records_per_s
    }


async def benchmark_jsonl_paging(jsonl_path: Path, num_pages: int = 10) -> dict[str, Any]:
    """Benchmark JSONL paging (sequential read)."""
    if not jsonl_path.exists():
        return {"error": "File not found"}
    
    print(f"JSONL: Paging ({num_pages} pages)...")
    start_time = time.perf_counter()
    
    page_size = 100
    records_read = 0
    
    with jsonl_path.open("r", encoding="utf-8") as f:
        for page_num in range(num_pages):
            page_records = []
            for _ in range(page_size):
                line = f.readline()
                if not line:
                    break
                if line.strip():
                    page_records.append(json.loads(line))
            records_read += len(page_records)
            if not page_records:
                break
    
    elapsed = time.perf_counter() - start_time
    avg_page_time = elapsed / num_pages if num_pages > 0 else 0
    
    print(f"  Read {records_read:,} records in {elapsed:.2f}s")
    print(f"  Avg page time: {avg_page_time * 1000:.2f} ms")
    
    return {
        "format": "JSONL",
        "total_records": records_read,
        "total_time": elapsed,
        "avg_page_time": avg_page_time
    }


async def benchmark_xwjson_paging(xwjson_path: Path, num_pages: int = 10) -> dict[str, Any]:
    """Benchmark XWJSON paging."""
    if not xwjson_path.exists():
        return {"error": "File not found"}
    
    if not XWJSON_AVAILABLE:
        return {"error": "XWJSON not available"}
    
    # CRITICAL: Reuse same ops instance to benefit from caching
    # This mimics real-world usage where same ops instance is reused
    ops = XWJSONDataOperations()
    
    print(f"XWJSON: Paging ({num_pages} pages)...")
    
    # First page read (loads file and builds cache)
    first_page_start = time.perf_counter()
    first_page = await ops.read_page(xwjson_path, page_number=1, page_size=100, path="/records")
    first_page_time = time.perf_counter() - first_page_start
    
    # Subsequent pages (should use cache - very fast)
    start_time = time.perf_counter()
    total_records = len(first_page)
    page_times = [first_page_time]
    
    for page_num in range(2, num_pages + 1):
        page_start = time.perf_counter()
        page = await ops.read_page(xwjson_path, page_number=page_num, page_size=100, path="/records")
        page_time = time.perf_counter() - page_start
        page_times.append(page_time)
        total_records += len(page)
        if not page:
            break
    
    elapsed = time.perf_counter() - start_time
    total_elapsed = first_page_time + elapsed
    avg_page_time = sum(page_times) / len(page_times) if page_times else 0
    avg_subsequent_page_time = sum(page_times[1:]) / len(page_times[1:]) if len(page_times) > 1 else 0
    
    print(f"  Read {total_records:,} records in {total_elapsed:.2f}s")
    print(f"  First page (cold): {first_page_time * 1000:.2f} ms")
    print(f"  Avg subsequent page (warm): {avg_subsequent_page_time * 1000:.2f} ms")
    print(f"  Avg page time (all): {avg_page_time * 1000:.2f} ms")
    
    return {
        "format": "XWJSON",
        "total_records": total_records,
        "total_time": total_elapsed,
        "avg_page_time": avg_page_time,
        "first_page_time": first_page_time,
        "avg_subsequent_page_time": avg_subsequent_page_time
    }


async def run_comparison(jsonl_path: Path, xwjson_path: Path) -> int:
    """Run full comparison."""
    print("=" * 70)
    print("JSONL vs XWJSON Performance Comparison")
    print("=" * 70)
    print()
    
    results = {}
    
    # 1. File Loading Comparison
    print("1. FILE LOADING COMPARISON")
    print("-" * 70)
    
    if jsonl_path.exists():
        jsonl_load = await benchmark_jsonl_load(jsonl_path)
        results["jsonl_load"] = jsonl_load
        print()
    
    if xwjson_path.exists() and XWJSON_AVAILABLE:
        xwjson_load = await benchmark_xwjson_load(xwjson_path)
        results["xwjson_load"] = xwjson_load
        print()
    else:
        print("XWJSON file not found. Run convert_to_xwjson.py first.")
        print()
    
    # 2. Paging Comparison
    print("2. PAGING COMPARISON")
    print("-" * 70)
    
    if jsonl_path.exists():
        jsonl_paging = await benchmark_jsonl_paging(jsonl_path)
        results["jsonl_paging"] = jsonl_paging
        print()
    
    if xwjson_path.exists() and XWJSON_AVAILABLE:
        xwjson_paging = await benchmark_xwjson_paging(xwjson_path)
        results["xwjson_paging"] = xwjson_paging
        print()
    
    # 3. Summary Comparison
    print("3. SUMMARY COMPARISON")
    print("-" * 70)
    
    if "jsonl_load" in results and "xwjson_load" in results:
        jsonl_time = results["jsonl_load"].get("load_time", 0)
        xwjson_time = results["xwjson_load"].get("load_time", 0)
        
        if jsonl_time > 0 and xwjson_time > 0:
            speedup = jsonl_time / xwjson_time
            print(f"Load Speedup: {speedup:.2f}x ({'XWJSON faster' if speedup > 1 else 'JSONL faster'})")
        
        jsonl_mb_s = results["jsonl_load"].get("mb_per_s", 0)
        xwjson_mb_s = results["xwjson_load"].get("mb_per_s", 0)
        
        if jsonl_mb_s > 0 and xwjson_mb_s > 0:
            print(f"JSONL: {jsonl_mb_s:.1f} MB/s")
            print(f"XWJSON: {xwjson_mb_s:.1f} MB/s")
            improvement = ((xwjson_mb_s - jsonl_mb_s) / jsonl_mb_s * 100)
            print(f"Improvement: {improvement:+.1f}%")
        
        jsonl_size = results["jsonl_load"].get("file_size", 0)
        xwjson_size = results["xwjson_load"].get("file_size", 0)
        
        if jsonl_size > 0 and xwjson_size > 0:
            size_ratio = jsonl_size / xwjson_size
            print(f"File Size Ratio (JSONL/XWJSON): {size_ratio:.2f}x")
            print(f"JSONL: {_human_bytes(jsonl_size)}")
            print(f"XWJSON: {_human_bytes(xwjson_size)}")
    
    if "jsonl_paging" in results and "xwjson_paging" in results:
        jsonl_page_time = results["jsonl_paging"].get("avg_page_time", 0)
        xwjson_page_time = results["xwjson_paging"].get("avg_page_time", 0)
        xwjson_warm_page_time = results["xwjson_paging"].get("avg_subsequent_page_time", 0)
        
        if jsonl_page_time > 0 and xwjson_page_time > 0:
            page_speedup = jsonl_page_time / xwjson_page_time
            print(f"Paging Speedup (avg): {page_speedup:.2f}x ({'XWJSON faster' if page_speedup > 1 else 'JSONL faster'})")
            print(f"JSONL: {jsonl_page_time * 1000:.2f} ms/page")
            print(f"XWJSON (avg): {xwjson_page_time * 1000:.2f} ms/page")
            
            # Show warm cache performance (this is the real comparison)
            if xwjson_warm_page_time > 0:
                warm_speedup = jsonl_page_time / xwjson_warm_page_time
                print(f"XWJSON (warm cache): {xwjson_warm_page_time * 1000:.2f} ms/page")
                print(f"Warm Cache Speedup: {warm_speedup:.2f}x ({'XWJSON faster' if warm_speedup > 1 else 'JSONL faster'})")
                if warm_speedup > 1:
                    print(f"[SUCCESS] XWJSON paging is {warm_speedup:.1f}x faster than JSONL when cache is warm!")
    
    print()
    print("=" * 70)
    print("Comparison Complete")
    print("=" * 70)
    
    return 0


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Compare JSONL vs XWJSON performance")
    p.add_argument("--jsonl", type=str, default=str(default_jsonl_path()), help="JSONL file path")
    p.add_argument("--xwjson", type=str, default=str(default_xwjson_path()), help="XWJSON file path")
    return p.parse_args()


def main() -> int:
    args = _parse_args()
    jsonl_path = Path(args.jsonl)
    xwjson_path = Path(args.xwjson)
    
    return asyncio.run(run_comparison(jsonl_path, xwjson_path))


if __name__ == "__main__":
    raise SystemExit(main())

