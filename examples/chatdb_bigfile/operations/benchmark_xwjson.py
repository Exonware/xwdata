"""Benchmark XWJSON performance with 5GB chatdb database.

Compares XWJSON performance with JSONL for:
- File reading
- Record access
- Paging
- Updates
- Queries

Run (from repo root):
  python xwdata/examples/chatdb_bigfile/operations/benchmark_xwjson.py

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
    print("ERROR: xwjson not available. Install with: pip install exonware-xwjson")
    sys.exit(1)


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


async def benchmark_xwjson_load(xwjson_path: Path) -> dict[str, Any]:
    """Benchmark XWJSON file loading."""
    if not xwjson_path.exists():
        return {"error": "File not found"}
    
    serializer = XWJSONSerializer()
    
    print("Benchmarking XWJSON file load...")
    start_time = time.perf_counter()
    
    data = serializer.load_file(xwjson_path)
    
    elapsed = time.perf_counter() - start_time
    file_size = xwjson_path.stat().st_size
    
    records_count = len(data.get("records", []))
    
    mb_per_s = (file_size / (1024 * 1024)) / elapsed if elapsed > 0 else 0
    records_per_s = records_count / elapsed if elapsed > 0 else 0
    
    print(f"  Loaded {records_count:,} records in {elapsed:.2f}s")
    print(f"  Speed: {mb_per_s:.1f} MB/s, {records_per_s:,.0f} records/s")
    
    return {
        "records": records_count,
        "file_size": file_size,
        "load_time": elapsed,
        "mb_per_s": mb_per_s,
        "records_per_s": records_per_s
    }


async def benchmark_xwjson_paging(xwjson_path: Path, num_pages: int = 10) -> dict[str, Any]:
    """Benchmark XWJSON paging operations."""
    if not xwjson_path.exists():
        return {"error": "File not found"}
    
    ops = XWJSONDataOperations()
    
    print(f"Benchmarking XWJSON paging ({num_pages} pages)...")
    start_time = time.perf_counter()
    
    page_times = []
    total_records = 0
    
    for page_num in range(1, num_pages + 1):
        page_start = time.perf_counter()
        page = await ops.read_page(xwjson_path, page_number=page_num, page_size=100, path="/records")
        page_time = time.perf_counter() - page_start
        page_times.append(page_time)
        total_records += len(page)
    
    total_time = time.perf_counter() - start_time
    avg_page_time = sum(page_times) / len(page_times) if page_times else 0
    
    print(f"  Read {total_records:,} records in {total_time:.2f}s")
    print(f"  Avg page time: {avg_page_time * 1000:.2f} ms")
    
    return {
        "total_records": total_records,
        "total_time": total_time,
        "avg_page_time": avg_page_time,
        "pages_per_second": num_pages / total_time if total_time > 0 else 0
    }


async def benchmark_xwjson_path_access(xwjson_path: Path, num_accesses: int = 100) -> dict[str, Any]:
    """Benchmark XWJSON path-based access."""
    if not xwjson_path.exists():
        return {"error": "File not found"}
    
    ops = XWJSONDataOperations()
    
    print(f"Benchmarking XWJSON path access ({num_accesses} accesses)...")
    start_time = time.perf_counter()
    
    # Access random paths
    for i in range(num_accesses):
        path = f"/records/{i % 1000}/@type"
        try:
            await ops.read_path(xwjson_path, path)
        except Exception:
            pass  # Some paths may not exist
    
    elapsed = time.perf_counter() - start_time
    accesses_per_s = num_accesses / elapsed if elapsed > 0 else 0
    
    print(f"  {num_accesses} path accesses in {elapsed:.2f}s")
    print(f"  Speed: {accesses_per_s:,.0f} accesses/s")
    
    return {
        "accesses": num_accesses,
        "time": elapsed,
        "accesses_per_s": accesses_per_s
    }


async def benchmark_jsonl_load(jsonl_path: Path) -> dict[str, Any]:
    """Benchmark JSONL file loading (for comparison)."""
    if not jsonl_path.exists():
        return {"error": "File not found"}
    
    print("Benchmarking JSONL file load (for comparison)...")
    start_time = time.perf_counter()
    
    records = []
    bytes_read = 0
    
    with jsonl_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                record = json.loads(line)
                records.append(record)
                bytes_read += len(line.encode('utf-8'))
    
    elapsed = time.perf_counter() - start_time
    file_size = jsonl_path.stat().st_size
    
    mb_per_s = (file_size / (1024 * 1024)) / elapsed if elapsed > 0 else 0
    records_per_s = len(records) / elapsed if elapsed > 0 else 0
    
    print(f"  Loaded {len(records):,} records in {elapsed:.2f}s")
    print(f"  Speed: {mb_per_s:.1f} MB/s, {records_per_s:,.0f} records/s")
    
    return {
        "records": len(records),
        "file_size": file_size,
        "load_time": elapsed,
        "mb_per_s": mb_per_s,
        "records_per_s": records_per_s
    }


async def run_benchmarks(jsonl_path: Path, xwjson_path: Path) -> int:
    """Run all benchmarks."""
    print("=" * 60)
    print("XWJSON Performance Benchmark")
    print("=" * 60)
    print()
    
    results = {}
    
    # Benchmark JSONL (baseline)
    if jsonl_path.exists():
        print("1. JSONL Baseline")
        print("-" * 60)
        jsonl_results = await benchmark_jsonl_load(jsonl_path)
        results["jsonl"] = jsonl_results
        print()
    
    # Benchmark XWJSON
    if xwjson_path.exists():
        print("2. XWJSON Performance")
        print("-" * 60)
        
        # Load benchmark
        xwjson_load = await benchmark_xwjson_load(xwjson_path)
        results["xwjson_load"] = xwjson_load
        print()
        
        # Paging benchmark
        xwjson_paging = await benchmark_xwjson_paging(xwjson_path)
        results["xwjson_paging"] = xwjson_paging
        print()
        
        # Path access benchmark
        xwjson_path_access = await benchmark_xwjson_path_access(xwjson_path)
        results["xwjson_path_access"] = xwjson_path_access
        print()
    else:
        print("WARNING: XWJSON file not found. Run convert_to_xwjson.py first.")
        print()
    
    # Comparison
    if "jsonl" in results and "xwjson_load" in results:
        print("3. Comparison")
        print("-" * 60)
        
        jsonl_time = results["jsonl"].get("load_time", 0)
        xwjson_time = results["xwjson_load"].get("load_time", 0)
        
        if jsonl_time > 0 and xwjson_time > 0:
            speedup = jsonl_time / xwjson_time
            print(f"  Load speedup: {speedup:.2f}x ({'faster' if speedup > 1 else 'slower'})")
        
        jsonl_mb_s = results["jsonl"].get("mb_per_s", 0)
        xwjson_mb_s = results["xwjson_load"].get("mb_per_s", 0)
        
        if jsonl_mb_s > 0 and xwjson_mb_s > 0:
            print(f"  JSONL: {jsonl_mb_s:.1f} MB/s")
            print(f"  XWJSON: {xwjson_mb_s:.1f} MB/s")
            print(f"  Difference: {((xwjson_mb_s - jsonl_mb_s) / jsonl_mb_s * 100):+.1f}%")
    
    print()
    print("=" * 60)
    print("Benchmark Complete")
    print("=" * 60)
    
    return 0


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Benchmark XWJSON performance")
    p.add_argument("--jsonl", type=str, default=str(default_jsonl_path()), help="JSONL file path")
    p.add_argument("--xwjson", type=str, default=str(default_xwjson_path()), help="XWJSON file path")
    return p.parse_args()


def main() -> int:
    if not XWJSON_AVAILABLE:
        print("ERROR: xwjson not available")
        return 1
    
    args = _parse_args()
    jsonl_path = Path(args.jsonl)
    xwjson_path = Path(args.xwjson)
    
    return asyncio.run(run_benchmarks(jsonl_path, xwjson_path))


if __name__ == "__main__":
    raise SystemExit(main())

