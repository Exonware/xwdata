"""Benchmark XWJSON Index Caching Performance
Tests the new index/meta caching implementation to measure performance improvements.
Measures:
- First read (cold - loads index from disk)
- Second read (warm - index from cache)
- read_header_and_index() performance (cold vs warm)
- _load_index_file() performance (cold vs warm)
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
"""

from __future__ import annotations
import sys
import time
from pathlib import Path
from typing import Any
# Add xwjson to path
try:
    from exonware.xwjson import XWJSONSerializer
    from exonware.xwjson.formats.binary.xwjson.encoder import XWJSONDecoder
    XWJSON_AVAILABLE = True
except ImportError:
    XWJSON_AVAILABLE = False
    print("ERROR: xwjson not available. Install with: pip install exonware-xwjson")
    sys.exit(1)


def _here() -> Path:
    return Path(__file__).resolve()


def default_xwjson_path() -> Path:
    return _here().parents[1] / "data" / "chatdb.xwjson"


def format_time(seconds: float) -> str:
    """Format time in appropriate units."""
    if seconds < 0.001:
        return f"{seconds * 1000000:.2f} µs"
    elif seconds < 1.0:
        return f"{seconds * 1000:.2f} ms"
    else:
        return f"{seconds:.3f} s"


def benchmark_load_file(serializer: XWJSONSerializer, file_path: Path, label: str) -> dict[str, Any]:
    """Benchmark load_file() method."""
    print(f"\n{label}")
    print("-" * 70)
    start_time = time.perf_counter()
    data = serializer.load_file(file_path)
    elapsed = time.perf_counter() - start_time
    file_size = file_path.stat().st_size
    records_count = len(data.get("records", [])) if isinstance(data, dict) else 0
    mb_per_s = (file_size / (1024 * 1024)) / elapsed if elapsed > 0 else 0
    print(f"  Time: {format_time(elapsed)}")
    print(f"  File Size: {file_size / (1024 * 1024):.2f} MB")
    print(f"  Speed: {mb_per_s:.2f} MB/s")
    if records_count > 0:
        print(f"  Records: {records_count:,}")
    return {
        "time": elapsed,
        "file_size": file_size,
        "mb_per_s": mb_per_s,
        "records": records_count
    }


def benchmark_read_header_and_index(decoder: XWJSONDecoder, file_path: Path, label: str) -> dict[str, Any]:
    """Benchmark read_header_and_index() method."""
    print(f"\n{label}")
    print("-" * 70)
    # Check if this is dual-file format (has .data.xwjson)
    # For dual-file format, read_header_and_index may not work on .data.xwjson (pure MessagePack)
    # So we'll test with the main .xwjson file if it has a header, or skip if dual-file
    data_file_path = file_path.parent / f"{file_path.stem}.data.xwjson"
    is_dual_file = data_file_path.exists()
    actual_file_path = file_path
    start_time = time.perf_counter()
    try:
        header_info, index = decoder.read_header_and_index(actual_file_path)
        elapsed = time.perf_counter() - start_time
    except Exception as e:
        # If it fails, might be dual-file format - try loading index from meta file instead
        if is_dual_file:
            print(f"  [INFO] Dual-file format detected - using _load_index_file() instead")
            # Use _load_index_file for dual-file format
            start_time = time.perf_counter()
            index = decoder._load_index_file(data_file_path)
            elapsed = time.perf_counter() - start_time
            # Create a mock header_info for display
            header_info = {'flags': 0x22, 'format': 'dual_file'} if index else {}
        else:
            raise
    index_size = 0
    if index:
        import sys
        index_size = sys.getsizeof(str(index))
    print(f"  Time: {format_time(elapsed)}")
    print(f"  Header flags: {header_info.get('flags', 0):#x}")
    print(f"  Has index: {index is not None}")
    if index:
        print(f"  Index size: {index_size / 1024:.2f} KB (estimated)")
    return {
        "time": elapsed,
        "has_index": index is not None,
        "index_size": index_size
    }


def benchmark_load_index_file(decoder: XWJSONDecoder, file_path: Path, label: str) -> dict[str, Any]:
    """Benchmark _load_index_file() method."""
    print(f"\n{label}")
    print("-" * 70)
    # Handle dual-file format - check for .data.xwjson first
    actual_file_path = file_path
    if file_path.suffix == '.xwjson' and not file_path.name.endswith('.data.xwjson'):
        data_file_path = file_path.parent / f"{file_path.stem}.data.xwjson"
        if data_file_path.exists():
            # Dual-file format - use .data.xwjson file for _load_index_file
            actual_file_path = data_file_path
    start_time = time.perf_counter()
    index = decoder._load_index_file(actual_file_path)
    elapsed = time.perf_counter() - start_time
    index_size = 0
    if index:
        import sys
        index_size = sys.getsizeof(str(index))
    print(f"  Time: {format_time(elapsed)}")
    print(f"  Index loaded: {index is not None}")
    if index:
        print(f"  Index size: {index_size / 1024:.2f} KB (estimated)")
    return {
        "time": elapsed,
        "index_loaded": index is not None,
        "index_size": index_size
    }


def main() -> int:
    """Run index caching benchmarks."""
    import argparse
    parser = argparse.ArgumentParser(description="Benchmark XWJSON index caching performance")
    parser.add_argument(
        "--file",
        type=str,
        help="Path to XWJSON file to benchmark (default: data/chatdb.xwjson)"
    )
    args = parser.parse_args()
    if args.file:
        xwjson_path = Path(args.file).resolve()
    else:
        xwjson_path = default_xwjson_path()
    if not xwjson_path.exists():
        print(f"ERROR: XWJSON file not found: {xwjson_path}")
        print("Run convert_to_xwjson.py or generate_5gb_xwjson.py to create an XWJSON file.")
        return 1
    file_size_mb = xwjson_path.stat().st_size / (1024 * 1024)
    print("=" * 70)
    print("XWJSON Index Caching Performance Benchmark")
    print("=" * 70)
    print(f"File: {xwjson_path}")
    print(f"Size: {file_size_mb:.2f} MB")
    print()
    serializer = XWJSONSerializer(enable_cache=True)
    decoder = XWJSONDecoder()
    results = {}
    # ========================================================================
    # 1. LOAD_FILE BENCHMARKS (Cold vs Warm)
    # ========================================================================
    print("\n" + "=" * 70)
    print("1. LOAD_FILE() BENCHMARKS")
    print("=" * 70)
    # Cold read (first time - loads index from disk)
    results["load_cold"] = benchmark_load_file(serializer, xwjson_path, "Cold Read (First Load)")
    # Warm read (second time - index should be cached)
    results["load_warm"] = benchmark_load_file(serializer, xwjson_path, "Warm Read (Second Load - Index Cached)")
    # Calculate improvement
    if results["load_cold"]["time"] > 0:
        speedup = results["load_cold"]["time"] / results["load_warm"]["time"]
        improvement_pct = ((results["load_cold"]["time"] - results["load_warm"]["time"]) / results["load_cold"]["time"]) * 100
        print(f"\n  Load File Improvement: {speedup:.2f}x faster ({improvement_pct:.1f}% reduction)")
    # ========================================================================
    # 2. READ_HEADER_AND_INDEX BENCHMARKS (Cold vs Warm)
    # ========================================================================
    print("\n" + "=" * 70)
    print("2. READ_HEADER_AND_INDEX() BENCHMARKS")
    print("=" * 70)
    # Clear cache to test cold performance
    # (We can't easily clear the cache, but first call will be cold)
    # Actually, let's create a new decoder instance to ensure cold
    decoder_cold = XWJSONDecoder()
    results["read_header_cold"] = benchmark_read_header_and_index(
        decoder_cold, xwjson_path, "Cold read_header_and_index() (First Call)"
    )
    # Warm read (second call - should use cache)
    results["read_header_warm"] = benchmark_read_header_and_index(
        decoder, xwjson_path, "Warm read_header_and_index() (Second Call - Cached)"
    )
    # Calculate improvement
    if results["read_header_cold"]["time"] > 0:
        speedup = results["read_header_cold"]["time"] / results["read_header_warm"]["time"]
        improvement_pct = ((results["read_header_cold"]["time"] - results["read_header_warm"]["time"]) / results["read_header_cold"]["time"]) * 100
        print(f"\n  read_header_and_index() Improvement: {speedup:.2f}x faster ({improvement_pct:.1f}% reduction)")
        if speedup > 10:
            print(f"  [OK] Excellent! Index caching is working!")
        elif speedup > 2:
            print(f"  [OK] Good improvement from caching!")
        else:
            print(f"  [WARN] Minimal improvement - cache may not be working as expected")
    # ========================================================================
    # 3. _LOAD_INDEX_FILE BENCHMARKS (Cold vs Warm)
    # ========================================================================
    print("\n" + "=" * 70)
    print("3. _LOAD_INDEX_FILE() BENCHMARKS")
    print("=" * 70)
    # Check if dual-file format exists
    meta_file_path = xwjson_path.parent / f"{xwjson_path.stem}.meta.xwjson"
    if not meta_file_path.exists():
        idx_file_path = xwjson_path.parent / f"{xwjson_path.stem}.idx.xwjson"
        if idx_file_path.exists():
            meta_file_path = idx_file_path
    if meta_file_path.exists():
        # Cold read (first time - loads from disk)
        decoder_cold2 = XWJSONDecoder()
        results["load_index_cold"] = benchmark_load_index_file(
            decoder_cold2, xwjson_path, "Cold _load_index_file() (First Call)"
        )
        # Warm read (second time - should use cache)
        results["load_index_warm"] = benchmark_load_index_file(
            decoder, xwjson_path, "Warm _load_index_file() (Second Call - Cached)"
        )
        # Calculate improvement
        if results["load_index_cold"]["time"] > 0:
            speedup = results["load_index_cold"]["time"] / results["load_index_warm"]["time"]
            improvement_pct = ((results["load_index_cold"]["time"] - results["load_index_warm"]["time"]) / results["load_index_cold"]["time"]) * 100
            print(f"\n  _load_index_file() Improvement: {speedup:.2f}x faster ({improvement_pct:.1f}% reduction)")
            if speedup > 10:
                print(f"  [OK] Excellent! Index caching is working!")
            elif speedup > 2:
                print(f"  [OK] Good improvement from caching!")
            else:
                print(f"  [WARN] Minimal improvement - cache may not be working as expected")
    else:
        print("  [INFO] No dual-file format detected (.meta.xwjson or .idx.xwjson not found)")
        print("  Skipping _load_index_file() benchmark")
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print("Index Caching Performance Improvements:")
    print()
    if "load_cold" in results and "load_warm" in results:
        load_speedup = results["load_cold"]["time"] / results["load_warm"]["time"] if results["load_warm"]["time"] > 0 else 0
        print(f"  load_file():           {load_speedup:.2f}x faster")
    if "read_header_cold" in results and "read_header_warm" in results:
        header_speedup = results["read_header_cold"]["time"] / results["read_header_warm"]["time"] if results["read_header_warm"]["time"] > 0 else 0
        print(f"  read_header_and_index(): {header_speedup:.2f}x faster")
    if "load_index_cold" in results and "load_index_warm" in results:
        index_speedup = results["load_index_cold"]["time"] / results["load_index_warm"]["time"] if results["load_index_warm"]["time"] > 0 else 0
        print(f"  _load_index_file():    {index_speedup:.2f}x faster")
    print()
    print("Expected Results:")
    print("  - First read: Same as baseline (loads index from disk)")
    print("  - Second read: 10-50x faster (index from cache)")
    print("  - read_header_and_index(): 100-1000x faster after first call")
    print("  - _load_index_file(): 100-1000x faster after first call")
    print()
    return 0
if __name__ == "__main__":
    sys.exit(main())
