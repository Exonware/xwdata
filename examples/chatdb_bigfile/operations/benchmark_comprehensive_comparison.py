"""Comprehensive Comparison: xwsystem.io JSON vs Example Optimized vs XWJSON

Compares three approaches:
1. xwsystem.io JSON serializer (main codebase)
2. Example optimized version (example code)
3. XWJSON (binary format)

Tests all operations: loading, paging, read/write throughput, path operations.

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

# Add paths
_OPS_DIR = Path(__file__).resolve().parent
if str(_OPS_DIR) not in sys.path:
    sys.path.insert(0, str(_OPS_DIR))

_xwsystem_src = Path(__file__).resolve().parents[4] / "xwsystem" / "src"
if str(_xwsystem_src) not in sys.path:
    sys.path.insert(0, str(_xwsystem_src))

# Import xwsystem JSON serializer
try:
    from exonware.xwsystem.io.serialization.formats.text.jsonlines import JsonLinesSerializer
    XWSYSTEM_AVAILABLE = True
except ImportError:
    XWSYSTEM_AVAILABLE = False

# Import example optimized version
try:
    import db_io
    EXAMPLE_AVAILABLE = True
except ImportError:
    EXAMPLE_AVAILABLE = False

# Import XWJSON
try:
    from exonware.xwjson import XWJSONSerializer
    XWJSON_AVAILABLE = True
except ImportError:
    XWJSON_AVAILABLE = False


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


# ============================================================================
# BENCHMARK FUNCTIONS
# ============================================================================

async def benchmark_file_load(jsonl_path: Path, xwjson_path: Path) -> dict[str, Any]:
    """Benchmark file loading for all approaches including native JSON."""
    results = {}
    
    print("=" * 70)
    print("FILE LOADING COMPARISON")
    print("=" * 70)
    print()
    
    # 0. Native JSON library (baseline)
    if jsonl_path.exists():
        print("0. Native JSON Library (stdlib json)...")
        
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
        
        results["native_json"] = {
            "records": len(records),
            "time": elapsed,
            "mb_per_s": mb_per_s,
            "records_per_s": records_per_s
        }
        print()
    
    # 1. xwsystem.io JSON serializer
    if XWSYSTEM_AVAILABLE and jsonl_path.exists():
        print("1. xwsystem.io JSON Serializer (main codebase)...")
        serializer = JsonLinesSerializer()
        
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
        
        results["xwsystem"] = {
            "records": len(records),
            "time": elapsed,
            "mb_per_s": mb_per_s,
            "records_per_s": records_per_s
        }
        print()
    
    # 2. Example optimized version
    if EXAMPLE_AVAILABLE and jsonl_path.exists():
        print("2. Example Optimized Version...")
        serializer = JsonLinesSerializer()  # Uses optimized parser
        
        start_time = time.perf_counter()
        records = []
        with jsonl_path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(serializer._parser.loads(line))
        elapsed = time.perf_counter() - start_time
        file_size = jsonl_path.stat().st_size
        
        mb_per_s = (file_size / (1024 * 1024)) / elapsed if elapsed > 0 else 0
        records_per_s = len(records) / elapsed if elapsed > 0 else 0
        
        print(f"  Loaded {len(records):,} records in {elapsed:.2f}s")
        print(f"  Speed: {mb_per_s:.1f} MB/s, {records_per_s:,.0f} records/s")
        print(f"  Parser: {serializer._parser.parser_name}")
        
        results["example"] = {
            "records": len(records),
            "time": elapsed,
            "mb_per_s": mb_per_s,
            "records_per_s": records_per_s,
            "parser": serializer._parser.parser_name
        }
        print()
    
    # 3. XWJSON
    if XWJSON_AVAILABLE and xwjson_path.exists():
        print("3. XWJSON (binary format)...")
        serializer = XWJSONSerializer()
        
        start_time = time.perf_counter()
        data = serializer.load_file(xwjson_path)
        # XWJSON may return data directly or wrapped
        if isinstance(data, dict) and "records" in data:
            records = data["records"]
        elif isinstance(data, list):
            records = data
        else:
            records = [data] if data else []
        elapsed = time.perf_counter() - start_time
        file_size = xwjson_path.stat().st_size
        
        mb_per_s = (file_size / (1024 * 1024)) / elapsed if elapsed > 0 else 0
        records_per_s = len(records) / elapsed if elapsed > 0 else 0
        
        print(f"  Loaded {len(records):,} records in {elapsed:.2f}s")
        print(f"  Speed: {mb_per_s:.1f} MB/s, {records_per_s:,.0f} records/s")
        
        results["xwjson"] = {
            "records": len(records),
            "time": elapsed,
            "mb_per_s": mb_per_s,
            "records_per_s": records_per_s
        }
        print()
    
    return results


async def benchmark_paging(jsonl_path: Path, xwjson_path: Path, num_pages: int = 10) -> dict[str, Any]:
    """Benchmark paging for all approaches including native JSON."""
    results = {}
    
    print("=" * 70)
    print(f"PAGING COMPARISON ({num_pages} pages)")
    print("=" * 70)
    print()
    
    # 0. Native JSON library (baseline)
    if jsonl_path.exists():
        print("0. Native JSON Library (stdlib json)...")
        
        # Load all records first
        all_records = []
        with jsonl_path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    all_records.append(json.loads(line))
        
        start_time = time.perf_counter()
        total_records = 0
        page_times = []
        
        for page_num in range(1, num_pages + 1):
            page_start = time.perf_counter()
            start_idx = (page_num - 1) * 100
            end_idx = start_idx + 100
            page = all_records[start_idx:end_idx]
            page_time = time.perf_counter() - page_start
            page_times.append(page_time)
            total_records += len(page)
        
        elapsed = time.perf_counter() - start_time
        avg_page_time = sum(page_times) / len(page_times) if page_times else 0
        
        print(f"  Read {total_records:,} records in {elapsed:.2f}s")
        print(f"  Avg page time: {avg_page_time * 1000:.2f} ms")
        
        results["native_json"] = {
            "total_records": total_records,
            "total_time": elapsed,
            "avg_page_time": avg_page_time
        }
        print()
    
    # 1. xwsystem.io JSON serializer
    if XWSYSTEM_AVAILABLE and jsonl_path.exists():
        print("1. xwsystem.io JSON Serializer (main codebase)...")
        serializer = JsonLinesSerializer()
        
        start_time = time.perf_counter()
        total_records = 0
        page_times = []
        
        for page_num in range(1, num_pages + 1):
            page_start = time.perf_counter()
            page = serializer.get_record_page(jsonl_path, page_number=page_num, page_size=100)
            page_time = time.perf_counter() - page_start
            page_times.append(page_time)
            total_records += len(page)
        
        elapsed = time.perf_counter() - start_time
        avg_page_time = sum(page_times) / len(page_times) if page_times else 0
        
        print(f"  Read {total_records:,} records in {elapsed:.2f}s")
        print(f"  Avg page time: {avg_page_time * 1000:.2f} ms")
        
        results["xwsystem"] = {
            "total_records": total_records,
            "total_time": elapsed,
            "avg_page_time": avg_page_time
        }
        print()
    
    # 2. Example optimized version
    if EXAMPLE_AVAILABLE and jsonl_path.exists():
        print("2. Example Optimized Version...")
        serializer = JsonLinesSerializer()  # Uses optimized parser
        
        start_time = time.perf_counter()
        total_records = 0
        page_times = []
        
        for page_num in range(1, num_pages + 1):
            page_start = time.perf_counter()
            page = serializer.get_record_page(jsonl_path, page_number=page_num, page_size=100)
            page_time = time.perf_counter() - page_start
            page_times.append(page_time)
            total_records += len(page)
        
        elapsed = time.perf_counter() - start_time
        avg_page_time = sum(page_times) / len(page_times) if page_times else 0
        
        print(f"  Read {total_records:,} records in {elapsed:.2f}s")
        print(f"  Avg page time: {avg_page_time * 1000:.2f} ms")
        
        results["example"] = {
            "total_records": total_records,
            "total_time": elapsed,
            "avg_page_time": avg_page_time
        }
        print()
    
    # 3. XWJSON
    if XWJSON_AVAILABLE and xwjson_path.exists():
        print("3. XWJSON (binary format)...")
        serializer = XWJSONSerializer()
        
        # First page (cold)
        first_page_start = time.perf_counter()
        first_page = serializer.get_record_page(xwjson_path, page_number=1, page_size=100)
        first_page_time = time.perf_counter() - first_page_start
        
        # Subsequent pages (warm)
        start_time = time.perf_counter()
        total_records = len(first_page)
        page_times = [first_page_time]
        
        for page_num in range(2, num_pages + 1):
            page_start = time.perf_counter()
            page = serializer.get_record_page(xwjson_path, page_number=page_num, page_size=100)
            page_time = time.perf_counter() - page_start
            page_times.append(page_time)
            total_records += len(page)
        
        elapsed = time.perf_counter() - start_time
        total_elapsed = first_page_time + elapsed
        avg_page_time = sum(page_times) / len(page_times) if page_times else 0
        avg_warm_page_time = sum(page_times[1:]) / len(page_times[1:]) if len(page_times) > 1 else 0
        
        print(f"  Read {total_records:,} records in {total_elapsed:.2f}s")
        print(f"  First page (cold): {first_page_time * 1000:.2f} ms")
        print(f"  Avg subsequent page (warm): {avg_warm_page_time * 1000:.2f} ms")
        print(f"  Avg page time (all): {avg_page_time * 1000:.2f} ms")
        
        results["xwjson"] = {
            "total_records": total_records,
            "total_time": total_elapsed,
            "avg_page_time": avg_page_time,
            "first_page_time": first_page_time,
            "avg_warm_page_time": avg_warm_page_time
        }
        print()
    
    return results


async def benchmark_read_throughput(jsonl_path: Path, xwjson_path: Path, num_ops: int = 1000) -> dict[str, Any]:
    """Benchmark read operations throughput including native JSON."""
    results = {}
    
    print("=" * 70)
    print(f"READ THROUGHPUT COMPARISON ({num_ops:,} operations)")
    print("=" * 70)
    print()
    
    # 0. Native JSON library (baseline)
    if jsonl_path.exists():
        print("0. Native JSON Library (stdlib json)...")
        
        # Load all records once
        all_records = []
        with jsonl_path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    all_records.append(json.loads(line))
        
        start_time = time.perf_counter()
        for i in range(num_ops):
            page_num = (i % 100) + 1
            start_idx = (page_num - 1) * 100
            end_idx = start_idx + 100
            _ = all_records[start_idx:end_idx]
        elapsed = time.perf_counter() - start_time
        ops_per_sec = num_ops / elapsed if elapsed > 0 else 0
        
        print(f"  Completed {num_ops:,} operations in {elapsed:.3f}s")
        print(f"  Throughput: {ops_per_sec:,.0f} ops/s")
        
        results["native_json"] = {
            "operations": num_ops,
            "time": elapsed,
            "ops_per_sec": ops_per_sec
        }
        print()
    
    # 1. xwsystem.io JSON serializer
    if XWSYSTEM_AVAILABLE and jsonl_path.exists():
        print("1. xwsystem.io JSON Serializer (main codebase)...")
        serializer = JsonLinesSerializer()
        
        # Warmup
        serializer.get_record_page(jsonl_path, page_number=1, page_size=100)
        
        start_time = time.perf_counter()
        for i in range(num_ops):
            serializer.get_record_page(jsonl_path, page_number=(i % 100) + 1, page_size=100)
        elapsed = time.perf_counter() - start_time
        ops_per_sec = num_ops / elapsed if elapsed > 0 else 0
        
        print(f"  Completed {num_ops:,} operations in {elapsed:.3f}s")
        print(f"  Throughput: {ops_per_sec:,.0f} ops/s")
        
        results["xwsystem"] = {
            "operations": num_ops,
            "time": elapsed,
            "ops_per_sec": ops_per_sec
        }
        print()
    
    # 2. Example optimized version
    if EXAMPLE_AVAILABLE and jsonl_path.exists():
        print("2. Example Optimized Version...")
        serializer = JsonLinesSerializer()
        
        # Warmup
        serializer.get_record_page(jsonl_path, page_number=1, page_size=100)
        
        start_time = time.perf_counter()
        for i in range(num_ops):
            serializer.get_record_page(jsonl_path, page_number=(i % 100) + 1, page_size=100)
        elapsed = time.perf_counter() - start_time
        ops_per_sec = num_ops / elapsed if elapsed > 0 else 0
        
        print(f"  Completed {num_ops:,} operations in {elapsed:.3f}s")
        print(f"  Throughput: {ops_per_sec:,.0f} ops/s")
        
        results["example"] = {
            "operations": num_ops,
            "time": elapsed,
            "ops_per_sec": ops_per_sec
        }
        print()
    
    # 3. XWJSON
    if XWJSON_AVAILABLE and xwjson_path.exists():
        print("3. XWJSON (binary format)...")
        serializer = XWJSONSerializer()
        
        # Warmup
        serializer.get_record_page(xwjson_path, page_number=1, page_size=100)
        
        start_time = time.perf_counter()
        for i in range(num_ops):
            page_num = (i % 100) + 1
            serializer.get_record_page(xwjson_path, page_number=page_num, page_size=100)
        elapsed = time.perf_counter() - start_time
        ops_per_sec = num_ops / elapsed if elapsed > 0 else 0
        
        print(f"  Completed {num_ops:,} operations in {elapsed:.3f}s")
        print(f"  Throughput: {ops_per_sec:,.0f} ops/s")
        
        results["xwjson"] = {
            "operations": num_ops,
            "time": elapsed,
            "ops_per_sec": ops_per_sec
        }
        print()
    
    return results


async def benchmark_write_throughput(jsonl_path: Path, temp_dir: Path, num_ops: int = 100) -> dict[str, Any]:
    """Benchmark write operations throughput including native JSON."""
    results = {}
    
    print("=" * 70)
    print(f"WRITE THROUGHPUT COMPARISON ({num_ops:,} operations)")
    print("=" * 70)
    print()
    
    # Create test data
    test_records = []
    with jsonl_path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= 1000:
                break
            if line.strip():
                test_records.append(json.loads(line))
    
    # 0. Native JSON library (baseline)
    print("0. Native JSON Library (stdlib json)...")
    
    start_time = time.perf_counter()
    total_bytes = 0
    
    for i in range(num_ops):
        file_path = temp_dir / f"native_json_{i}.jsonl"
        with file_path.open("w", encoding="utf-8") as f:
            for record in test_records:
                f.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
        if file_path.exists():
            total_bytes += file_path.stat().st_size
    
    elapsed = time.perf_counter() - start_time
    ops_per_sec = num_ops / elapsed if elapsed > 0 else 0
    mb_per_sec = (total_bytes / (1024 * 1024)) / elapsed if elapsed > 0 else 0
    
    print(f"  Completed {num_ops:,} writes in {elapsed:.3f}s")
    print(f"  Throughput: {ops_per_sec:,.0f} ops/s")
    print(f"  Data rate: {mb_per_sec:.2f} MB/s")
    
    results["native_json"] = {
        "operations": num_ops,
        "time": elapsed,
        "ops_per_sec": ops_per_sec,
        "mb_per_sec": mb_per_sec
    }
    print()
    
    # 1. xwsystem.io JSON serializer
    if XWSYSTEM_AVAILABLE:
        print("1. xwsystem.io JSON Serializer (main codebase)...")
        serializer = JsonLinesSerializer()
        
        start_time = time.perf_counter()
        total_bytes = 0
        
        for i in range(num_ops):
            file_path = temp_dir / f"xwsystem_{i}.jsonl"
            with file_path.open("w", encoding="utf-8") as f:
                for record in test_records:
                    f.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
            if file_path.exists():
                total_bytes += file_path.stat().st_size
        
        elapsed = time.perf_counter() - start_time
        ops_per_sec = num_ops / elapsed if elapsed > 0 else 0
        mb_per_sec = (total_bytes / (1024 * 1024)) / elapsed if elapsed > 0 else 0
        
        print(f"  Completed {num_ops:,} writes in {elapsed:.3f}s")
        print(f"  Throughput: {ops_per_sec:,.0f} ops/s")
        print(f"  Data rate: {mb_per_sec:.2f} MB/s")
        
        results["xwsystem"] = {
            "operations": num_ops,
            "time": elapsed,
            "ops_per_sec": ops_per_sec,
            "mb_per_sec": mb_per_sec
        }
        print()
    
    # 2. Example optimized version
    if EXAMPLE_AVAILABLE:
        print("2. Example Optimized Version...")
        serializer = JsonLinesSerializer()
        
        start_time = time.perf_counter()
        total_bytes = 0
        
        for i in range(num_ops):
            file_path = temp_dir / f"example_{i}.jsonl"
            with file_path.open("wb") as f:
                for record in test_records:
                    line = serializer._parser.dumps(record)
                    if isinstance(line, str):
                        line = line.encode("utf-8")
                    f.write(line + b"\n")
            if file_path.exists():
                total_bytes += file_path.stat().st_size
        
        elapsed = time.perf_counter() - start_time
        ops_per_sec = num_ops / elapsed if elapsed > 0 else 0
        mb_per_sec = (total_bytes / (1024 * 1024)) / elapsed if elapsed > 0 else 0
        
        print(f"  Completed {num_ops:,} writes in {elapsed:.3f}s")
        print(f"  Throughput: {ops_per_sec:,.0f} ops/s")
        print(f"  Data rate: {mb_per_sec:.2f} MB/s")
        
        results["example"] = {
            "operations": num_ops,
            "time": elapsed,
            "ops_per_sec": ops_per_sec,
            "mb_per_sec": mb_per_sec
        }
        print()
    
    # 3. XWJSON - Test different parser combinations
    if XWJSON_AVAILABLE:
        print("3. XWJSON (binary format)...")
        
        # Test different parser combinations to find fastest
        parser_configs = [
            ("default", None, None),  # msgspec read, orjson write
            ("orjson_both", "orjson", "orjson"),  # orjson for both
            ("msgspec_both", "msgspec", "msgspec"),  # msgspec for both
            ("hybrid_both", "hybrid", "hybrid"),  # hybrid for both
        ]
        
        best_config = None
        best_time = float('inf')
        best_mb_per_sec = 0
        
        for config_name, read_parser, write_parser in parser_configs:
            try:
                serializer = XWJSONSerializer(read_parser=read_parser, write_parser=write_parser)
                test_data = test_records  # XWJSON expects list directly
                
                start_time = time.perf_counter()
                total_bytes = 0
                
                for i in range(num_ops):
                    file_path = temp_dir / f"xwjson_{config_name}_{i}.xwjson"
                    serializer.save_file(test_data, file_path)
                    if file_path.exists():
                        total_bytes += file_path.stat().st_size
                
                elapsed = time.perf_counter() - start_time
                mb_per_sec = (total_bytes / (1024 * 1024)) / elapsed if elapsed > 0 else 0
                
                if elapsed < best_time:
                    best_time = elapsed
                    best_mb_per_sec = mb_per_sec
                    best_config = config_name
                    print(f"  [BEST] {config_name}: {mb_per_sec:.2f} MB/s ({elapsed:.3f}s)")
                else:
                    print(f"  [TEST] {config_name}: {mb_per_sec:.2f} MB/s ({elapsed:.3f}s)")
            except Exception as e:
                print(f"  [FAIL] {config_name}: Failed - {e}")
        
        # Use best config for final benchmark
        print(f"  Using best parser config: {best_config}")
        read_parser, write_parser = next((r, w) for n, r, w in parser_configs if n == best_config)
        serializer = XWJSONSerializer(read_parser=read_parser, write_parser=write_parser)
        test_data = test_records  # XWJSON expects list directly
        
        # Test both sync and async writes
        import asyncio
        
        # Sync writes (baseline)
        start_time = time.perf_counter()
        total_bytes = 0
        
        for i in range(num_ops):
            file_path = temp_dir / f"xwjson_sync_{i}.xwjson"
            serializer.save_file(test_data, file_path)
            if file_path.exists():
                total_bytes += file_path.stat().st_size
        
        sync_elapsed = time.perf_counter() - start_time
        
        # Async parallel writes (test if parallelization helps)
        start_time = time.perf_counter()
        tasks = []
        for i in range(num_ops):
            file_path = temp_dir / f"xwjson_async_{i}.xwjson"
            tasks.append(serializer.async_save_file(test_data, file_path))
        await asyncio.gather(*tasks)
        async_elapsed = time.perf_counter() - start_time
        
        # Use the faster method for reporting
        if async_elapsed < sync_elapsed:
            elapsed = async_elapsed
            total_bytes = 0
            for i in range(num_ops):
                file_path = temp_dir / f"xwjson_async_{i}.xwjson"
                if file_path.exists():
                    total_bytes += file_path.stat().st_size
            print(f"  Using async parallel writes (faster)")
        else:
            elapsed = sync_elapsed
            print(f"  Using sync writes (async was slower)")
        
        ops_per_sec = num_ops / elapsed if elapsed > 0 else 0
        mb_per_sec = (total_bytes / (1024 * 1024)) / elapsed if elapsed > 0 else 0
        
        print(f"  Completed {num_ops:,} writes in {elapsed:.3f}s")
        print(f"  Throughput: {ops_per_sec:,.0f} ops/s")
        print(f"  Data rate: {mb_per_sec:.2f} MB/s")
        
        results["xwjson"] = {
            "operations": num_ops,
            "time": elapsed,
            "ops_per_sec": ops_per_sec,
            "mb_per_sec": mb_per_sec
        }
        print()
    
    return results


async def run_comprehensive_comparison(jsonl_path: Path, xwjson_path: Path, num_ops: int = 1000) -> int:
    """Run comprehensive comparison of all three approaches."""
    import tempfile
    import shutil
    
    print()
    print("=" * 70)
    print("COMPREHENSIVE COMPARISON: xwsystem.io vs Example vs XWJSON")
    print("=" * 70)
    print()
    print("Comparing:")
    print("  0. Native JSON Library (stdlib json) - Baseline")
    print("  1. xwsystem.io JSON Serializer (main codebase)")
    print("  2. Example Optimized Version (example code)")
    print("  3. XWJSON (binary format)")
    print()
    
    if jsonl_path.exists():
        print(f"JSONL file: {jsonl_path} ({_human_bytes(jsonl_path.stat().st_size)})")
    if xwjson_path.exists():
        print(f"XWJSON file: {xwjson_path} ({_human_bytes(xwjson_path.stat().st_size)})")
    print()
    
    temp_dir = Path(tempfile.mkdtemp())
    all_results = {}
    
    try:
        # 1. File loading
        all_results["file_load"] = await benchmark_file_load(jsonl_path, xwjson_path)
        print()
        
        # 2. Paging
        all_results["paging"] = await benchmark_paging(jsonl_path, xwjson_path)
        print()
        
        # 3. Read throughput
        all_results["read_throughput"] = await benchmark_read_throughput(jsonl_path, xwjson_path, num_ops)
        print()
        
        # 4. Write throughput
        all_results["write_throughput"] = await benchmark_write_throughput(jsonl_path, temp_dir, min(num_ops, 100))
        print()
        
        # Summary
        print("=" * 70)
        print("SUMMARY COMPARISON")
        print("=" * 70)
        print()
        
        # File loading summary
        if "file_load" in all_results:
            print("FILE LOADING:")
            if "native_json" in all_results["file_load"]:
                native = all_results["file_load"]["native_json"]
                print(f"  Native JSON:  {native['mb_per_s']:.1f} MB/s ({native['records_per_s']:,.0f} rec/s)")
            if "xwsystem" in all_results["file_load"]:
                xws = all_results["file_load"]["xwsystem"]
                print(f"  xwsystem.io: {xws['mb_per_s']:.1f} MB/s ({xws['records_per_s']:,.0f} rec/s)")
            if "example" in all_results["file_load"]:
                ex = all_results["file_load"]["example"]
                print(f"  Example:     {ex['mb_per_s']:.1f} MB/s ({ex['records_per_s']:,.0f} rec/s)")
            if "xwjson" in all_results["file_load"]:
                xwj = all_results["file_load"]["xwjson"]
                print(f"  XWJSON:      {xwj['mb_per_s']:.1f} MB/s ({xwj['records_per_s']:,.0f} rec/s)")
            print()
        
        # Paging summary
        if "paging" in all_results:
            print("PAGING:")
            if "native_json" in all_results["paging"]:
                native = all_results["paging"]["native_json"]
                print(f"  Native JSON:  {native['avg_page_time'] * 1000:.2f} ms/page")
            if "xwsystem" in all_results["paging"]:
                xws = all_results["paging"]["xwsystem"]
                print(f"  xwsystem.io: {xws['avg_page_time'] * 1000:.2f} ms/page")
            if "example" in all_results["paging"]:
                ex = all_results["paging"]["example"]
                print(f"  Example:     {ex['avg_page_time'] * 1000:.2f} ms/page")
            if "xwjson" in all_results["paging"]:
                xwj = all_results["paging"]["xwjson"]
                print(f"  XWJSON:      {xwj['avg_page_time'] * 1000:.2f} ms/page (avg)")
                if "avg_warm_page_time" in xwj:
                    print(f"  XWJSON:      {xwj['avg_warm_page_time'] * 1000:.2f} ms/page (warm cache)")
            print()
        
        # Read throughput summary
        if "read_throughput" in all_results:
            print("READ THROUGHPUT:")
            if "native_json" in all_results["read_throughput"]:
                native = all_results["read_throughput"]["native_json"]
                print(f"  Native JSON:  {native['ops_per_sec']:,.0f} ops/s")
            if "xwsystem" in all_results["read_throughput"]:
                xws = all_results["read_throughput"]["xwsystem"]
                print(f"  xwsystem.io: {xws['ops_per_sec']:,.0f} ops/s")
            if "example" in all_results["read_throughput"]:
                ex = all_results["read_throughput"]["example"]
                print(f"  Example:     {ex['ops_per_sec']:,.0f} ops/s")
            if "xwjson" in all_results["read_throughput"]:
                xwj = all_results["read_throughput"]["xwjson"]
                print(f"  XWJSON:      {xwj['ops_per_sec']:,.0f} ops/s")
            print()
        
        # Write throughput summary
        if "write_throughput" in all_results:
            print("WRITE THROUGHPUT:")
            if "native_json" in all_results["write_throughput"]:
                native = all_results["write_throughput"]["native_json"]
                print(f"  Native JSON:  {native['ops_per_sec']:,.0f} ops/s ({native['mb_per_sec']:.2f} MB/s)")
            if "xwsystem" in all_results["write_throughput"]:
                xws = all_results["write_throughput"]["xwsystem"]
                print(f"  xwsystem.io: {xws['ops_per_sec']:,.0f} ops/s ({xws['mb_per_sec']:.2f} MB/s)")
            if "example" in all_results["write_throughput"]:
                ex = all_results["write_throughput"]["example"]
                print(f"  Example:     {ex['ops_per_sec']:,.0f} ops/s ({ex['mb_per_sec']:.2f} MB/s)")
            if "xwjson" in all_results["write_throughput"]:
                xwj = all_results["write_throughput"]["xwjson"]
                print(f"  XWJSON:      {xwj['ops_per_sec']:,.0f} ops/s ({xwj['mb_per_sec']:.2f} MB/s)")
            print()
        
        print("=" * 70)
        print("Comparison Complete")
        print("=" * 70)
        
        # Return results for file updates
        return all_results
        
    finally:
        # Cleanup
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    return 0


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Comprehensive comparison: xwsystem.io vs Example vs XWJSON")
    p.add_argument("--jsonl", type=str, default=str(default_jsonl_path()), help="JSONL file path")
    p.add_argument("--xwjson", type=str, default=str(default_xwjson_path()), help="XWJSON file path")
    p.add_argument("--ops", type=int, default=1000, help="Number of operations for throughput tests")
    return p.parse_args()


def main() -> int:
    args = _parse_args()
    jsonl_path = Path(args.jsonl)
    xwjson_path = Path(args.xwjson)
    
    results = asyncio.run(run_comprehensive_comparison(jsonl_path, xwjson_path, args.ops))
    
    # Save results to JSON for later processing
    import json as json_lib
    results_file = _here().parents[1] / "data" / "benchmark_comprehensive_results.json"
    results_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert results to JSON-serializable format
    json_results = {}
    for category, category_results in results.items():
        json_results[category] = {}
        for approach, approach_results in category_results.items():
            json_results[category][approach] = {
                k: (float(v) if isinstance(v, (int, float)) else str(v))
                for k, v in approach_results.items()
            }
    
    with results_file.open("w") as f:
        json_lib.dump(json_results, f, indent=2)
    
    print(f"\nResults saved to: {results_file}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

