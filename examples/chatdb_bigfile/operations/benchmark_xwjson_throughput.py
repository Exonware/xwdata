"""XWJSON Throughput Benchmark: Read/Write Operations per Second
Measures how many read and write operations XWJSON can perform per second.
This shows the throughput capacity of XWJSON for high-frequency operations.
Run (from repo root):
  python xwdata/examples/chatdb_bigfile/operations/benchmark_xwjson_throughput.py
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
import time
import tempfile
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


def default_xwjson_path() -> Path:
    return _here().parents[1] / "data" / "chatdb.xwjson"


def create_test_data(num_records: int = 1000) -> dict[str, Any]:
    """Create test data structure."""
    records = []
    for i in range(num_records):
        records.append({
            "@type": "Message",
            "id": f"msg_{i:08d}",
            "ts": 1000000000 + i,
            "payload": {
                "text": f"Message {i} with some content",
                "user_id": f"user_{i % 100:06d}",
                "views": i * 10
            }
        })
    return {"records": records}
async def benchmark_read_throughput(
    ops: XWJSONDataOperations,
    file_path: Path,
    num_operations: int = 1000,
    use_cache: bool = True
) -> dict[str, Any]:
    """Benchmark read operations per second."""
    print(f"Benchmarking read throughput ({num_operations:,} operations)...")
    # Warmup: read once to populate cache
    await ops.atomic_read(file_path, use_cache=use_cache)
    # Benchmark reads
    start_time = time.perf_counter()
    for i in range(num_operations):
        await ops.atomic_read(file_path, use_cache=use_cache)
    elapsed = time.perf_counter() - start_time
    ops_per_sec = num_operations / elapsed if elapsed > 0 else 0
    print(f"  Completed {num_operations:,} reads in {elapsed:.3f}s")
    print(f"  Throughput: {ops_per_sec:,.0f} reads/s")
    return {
        "operations": num_operations,
        "time": elapsed,
        "ops_per_sec": ops_per_sec
    }
async def benchmark_write_throughput(
    ops: XWJSONDataOperations,
    temp_dir: Path,
    num_operations: int = 100,
    data_size: int = 1000
) -> dict[str, Any]:
    """Benchmark write operations per second."""
    print(f"Benchmarking write throughput ({num_operations:,} operations, {data_size:,} records each)...")
    test_data = create_test_data(data_size)
    # Benchmark writes
    start_time = time.perf_counter()
    total_bytes = 0
    for i in range(num_operations):
        file_path = temp_dir / f"test_{i}.xwjson"
        await ops.atomic_write(file_path, test_data)
        if file_path.exists():
            total_bytes += file_path.stat().st_size
    elapsed = time.perf_counter() - start_time
    ops_per_sec = num_operations / elapsed if elapsed > 0 else 0
    mb_per_sec = (total_bytes / (1024 * 1024)) / elapsed if elapsed > 0 else 0
    print(f"  Completed {num_operations:,} writes in {elapsed:.3f}s")
    print(f"  Throughput: {ops_per_sec:,.0f} writes/s")
    print(f"  Data rate: {mb_per_sec:.2f} MB/s")
    return {
        "operations": num_operations,
        "time": elapsed,
        "ops_per_sec": ops_per_sec,
        "mb_per_sec": mb_per_sec,
        "total_bytes": total_bytes
    }
async def benchmark_path_read_throughput(
    ops: XWJSONDataOperations,
    file_path: Path,
    num_operations: int = 1000
) -> dict[str, Any]:
    """Benchmark path read operations per second."""
    print(f"Benchmarking path read throughput ({num_operations:,} operations)...")
    # Warmup: read once to populate cache (data is a list, not dict with records key)
    await ops.read_path(file_path, "/0/@type")
    # Benchmark path reads
    start_time = time.perf_counter()
    for i in range(num_operations):
        path = f"/{i % 100}/@type"
        await ops.read_path(file_path, path)
    elapsed = time.perf_counter() - start_time
    ops_per_sec = num_operations / elapsed if elapsed > 0 else 0
    print(f"  Completed {num_operations:,} path reads in {elapsed:.3f}s")
    print(f"  Throughput: {ops_per_sec:,.0f} path reads/s")
    return {
        "operations": num_operations,
        "time": elapsed,
        "ops_per_sec": ops_per_sec
    }
async def benchmark_paging_throughput(
    ops: XWJSONDataOperations,
    file_path: Path,
    num_operations: int = 1000,
    page_size: int = 100
) -> dict[str, Any]:
    """Benchmark paging operations per second."""
    print(f"Benchmarking paging throughput ({num_operations:,} operations, page_size={page_size})...")
    # Warmup: read first page to populate cache (data is a list, so path is None)
    await ops.read_page(file_path, page_number=1, page_size=page_size, path=None)
    # Benchmark paging
    start_time = time.perf_counter()
    total_records = 0
    for i in range(num_operations):
        page_num = (i % 100) + 1  # Cycle through first 100 pages
        page = await ops.read_page(file_path, page_number=page_num, page_size=page_size, path=None)
        total_records += len(page)
    elapsed = time.perf_counter() - start_time
    ops_per_sec = num_operations / elapsed if elapsed > 0 else 0
    records_per_sec = total_records / elapsed if elapsed > 0 else 0
    print(f"  Completed {num_operations:,} page reads in {elapsed:.3f}s")
    print(f"  Read {total_records:,} total records")
    print(f"  Throughput: {ops_per_sec:,.0f} pages/s")
    print(f"  Records throughput: {records_per_sec:,.0f} records/s")
    return {
        "operations": num_operations,
        "time": elapsed,
        "ops_per_sec": ops_per_sec,
        "records_per_sec": records_per_sec,
        "total_records": total_records
    }
async def benchmark_mixed_operations(
    ops: XWJSONDataOperations,
    file_path: Path,
    temp_dir: Path,
    num_operations: int = 500
) -> dict[str, Any]:
    """Benchmark mixed read/write operations per second."""
    print(f"Benchmarking mixed operations ({num_operations:,} operations)...")
    test_data = create_test_data(100)
    # Warmup
    await ops.atomic_read(file_path)
    # Benchmark mixed operations
    start_time = time.perf_counter()
    reads = 0
    writes = 0
    path_reads = 0
    for i in range(num_operations):
        op_type = i % 3
        if op_type == 0:
            # Read operation
            await ops.atomic_read(file_path)
            reads += 1
        elif op_type == 1:
            # Write operation
            write_path = temp_dir / f"mixed_{i}.xwjson"
            await ops.atomic_write(write_path, test_data)
            writes += 1
        else:
            # Path read operation (data is a list, not dict with records key)
            path = f"/{i % 100}/@type"
            await ops.read_path(file_path, path)
            path_reads += 1
    elapsed = time.perf_counter() - start_time
    ops_per_sec = num_operations / elapsed if elapsed > 0 else 0
    print(f"  Completed {num_operations:,} operations in {elapsed:.3f}s")
    print(f"    Reads: {reads:,}")
    print(f"    Writes: {writes:,}")
    print(f"    Path reads: {path_reads:,}")
    print(f"  Throughput: {ops_per_sec:,.0f} ops/s")
    return {
        "operations": num_operations,
        "time": elapsed,
        "ops_per_sec": ops_per_sec,
        "reads": reads,
        "writes": writes,
        "path_reads": path_reads
    }
async def run_benchmarks(xwjson_path: Path, num_ops: int = 1000) -> int:
    """Run all throughput benchmarks."""
    if not xwjson_path.exists():
        print(f"ERROR: XWJSON file not found: {xwjson_path}")
        print("Run convert_to_xwjson.py first to create the XWJSON file.")
        return 1
    print("=" * 70)
    print("XWJSON Throughput Benchmark")
    print("=" * 70)
    print(f"File: {xwjson_path}")
    print(f"Size: {xwjson_path.stat().st_size / (1024 * 1024):.2f} MB")
    print(f"Operations per test: {num_ops:,}")
    print()
    ops = XWJSONDataOperations()
    temp_dir = Path(tempfile.mkdtemp())
    results = {}
    try:
        # 1. Read throughput
        print("1. READ OPERATIONS THROUGHPUT")
        print("-" * 70)
        results["read"] = await benchmark_read_throughput(ops, xwjson_path, num_ops)
        print()
        # 2. Write throughput
        print("2. WRITE OPERATIONS THROUGHPUT")
        print("-" * 70)
        results["write"] = await benchmark_write_throughput(ops, temp_dir, min(num_ops, 100), 1000)
        print()
        # 3. Path read throughput
        print("3. PATH READ OPERATIONS THROUGHPUT")
        print("-" * 70)
        results["path_read"] = await benchmark_path_read_throughput(ops, xwjson_path, num_ops)
        print()
        # 4. Paging throughput
        print("4. PAGING OPERATIONS THROUGHPUT")
        print("-" * 70)
        results["paging"] = await benchmark_paging_throughput(ops, xwjson_path, num_ops)
        print()
        # 5. Mixed operations throughput
        print("5. MIXED OPERATIONS THROUGHPUT")
        print("-" * 70)
        results["mixed"] = await benchmark_mixed_operations(ops, xwjson_path, temp_dir, min(num_ops, 500))
        print()
        # Summary
        print("=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print()
        if "read" in results:
            print(f"Read operations:     {results['read']['ops_per_sec']:>12,.0f} ops/s")
        if "write" in results:
            print(f"Write operations:    {results['write']['ops_per_sec']:>12,.0f} ops/s ({results['write']['mb_per_sec']:.2f} MB/s)")
        if "path_read" in results:
            print(f"Path read operations: {results['path_read']['ops_per_sec']:>11,.0f} ops/s")
        if "paging" in results:
            print(f"Paging operations:   {results['paging']['ops_per_sec']:>12,.0f} ops/s ({results['paging']['records_per_sec']:,.0f} records/s)")
        if "mixed" in results:
            print(f"Mixed operations:    {results['mixed']['ops_per_sec']:>12,.0f} ops/s")
        print()
        print("=" * 70)
        print("Benchmark Complete")
        print("=" * 70)
    finally:
        # Cleanup temp files
        import shutil
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
    return 0


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Benchmark XWJSON throughput (ops/s)")
    p.add_argument("--xwjson", type=str, default=str(default_xwjson_path()), help="XWJSON file path")
    p.add_argument("--ops", type=int, default=1000, help="Number of operations per test")
    return p.parse_args()


def main() -> int:
    if not XWJSON_AVAILABLE:
        print("ERROR: xwjson not available")
        return 1
    args = _parse_args()
    xwjson_path = Path(args.xwjson)
    return asyncio.run(run_benchmarks(xwjson_path, args.ops))
if __name__ == "__main__":
    raise SystemExit(main())
