"""Compare encoder_1.py caching performance: simple vs updated version.
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
# Add paths
_OPS_DIR = Path(__file__).resolve().parent
if str(_OPS_DIR) not in sys.path:
    sys.path.insert(0, str(_OPS_DIR))
_xwsystem_src = Path(__file__).resolve().parents[4] / "xwsystem" / "src"
if str(_xwsystem_src) not in sys.path:
    sys.path.insert(0, str(_xwsystem_src))
_xwjson_src = Path(__file__).resolve().parents[4] / "xwjson" / "src"
if str(_xwjson_src) not in sys.path:
    sys.path.insert(0, str(_xwjson_src))


def benchmark_read_header_and_index(decoder, file_path: Path, num_iterations: int = 1000) -> dict[str, Any]:
    """Benchmark read_header_and_index performance (cold and warm cache)."""
    print(f"  Testing read_header_and_index() {num_iterations:,} times...")
    # Cold read (first call - loads from disk)
    print("    Cold read (first call)...")
    cold_start = time.perf_counter()
    header_info_cold, index_cold = decoder.read_header_and_index(file_path)
    cold_time = time.perf_counter() - cold_start
    print(f"      Time: {cold_time * 1000:.3f} ms")
    # Warm reads (subsequent calls - from cache)
    print(f"    Warm reads ({num_iterations} calls)...")
    warm_start = time.perf_counter()
    for i in range(num_iterations):
        header_info, index = decoder.read_header_and_index(file_path)
    warm_total = time.perf_counter() - warm_start
    warm_avg = warm_total / num_iterations if num_iterations > 0 else 0
    print(f"      Total time: {warm_total * 1000:.3f} ms")
    print(f"      Average per call: {warm_avg * 1000:.3f} ms")
    print(f"      Throughput: {num_iterations / warm_total:,.0f} calls/s" if warm_total > 0 else "      Throughput: N/A")
    return {
        "cold_time": cold_time,
        "warm_total": warm_total,
        "warm_avg": warm_avg,
        "warm_throughput": num_iterations / warm_total if warm_total > 0 else 0,
        "num_iterations": num_iterations
    }


def main() -> int:
    """Main entry point."""
    print("=" * 70)
    print("Encoder Cache Performance Comparison: Simple vs Updated Version")
    print("=" * 70)
    print()
    # Use existing test file
    test_file = Path("xwdata/examples/chatdb_bigfile/data/chatdb.xwjson")
    if not test_file.exists():
        print(f"ERROR: Test file not found: {test_file}")
        return 1
    file_size_mb = test_file.stat().st_size / (1024 * 1024)
    print(f"Test file: {test_file}")
    print(f"File size: {file_size_mb:.2f} MB")
    print()
    # Import encoder_1.py
    try:
        import importlib.util
        encoder_1_path = Path(__file__).resolve().parents[4] / "xwjson" / "src" / "exonware" / "xwjson" / "formats" / "binary" / "xwjson" / "encoder_1.py"
        if not encoder_1_path.exists():
            print(f"ERROR: encoder_1.py not found at {encoder_1_path}")
            return 1
        spec = importlib.util.spec_from_file_location("encoder_1", encoder_1_path)
        encoder_1_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(encoder_1_module)
        XWJSONDecoder1 = encoder_1_module.XWJSONDecoder
    except Exception as e:
        print(f"ERROR: Failed to import encoder_1.py: {e}")
        import traceback
        traceback.print_exc()
        return 1
    # Create decoder instance
    decoder = XWJSONDecoder1()
    # Clear cache before test (if possible)
    try:
        from exonware.xwjson.formats.binary.xwjson.serializer import XWJSONSerializer
        if XWJSONSerializer._cache_initialized:
            with XWJSONSerializer._cache_lock:
                # Clear caches
                XWJSONSerializer._index_cache.clear() if hasattr(XWJSONSerializer._index_cache, 'clear') else None
                XWJSONSerializer._mtime_cache.clear()
                XWJSONSerializer._index_mtime_cache.clear()
            print("Cache cleared before test")
    except Exception:
        pass
    print("=" * 70)
    print("READ_HEADER_AND_INDEX PERFORMANCE TEST")
    print("=" * 70)
    print()
    result = benchmark_read_header_and_index(decoder, test_file, num_iterations=1000)
    print()
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Cold read (first call): {result['cold_time'] * 1000:.3f} ms")
    print(f"Warm read (avg): {result['warm_avg'] * 1000:.3f} ms")
    print(f"Warm read throughput: {result['warm_throughput']:,.0f} calls/s")
    if result['cold_time'] > 0:
        speedup = result['cold_time'] / result['warm_avg'] if result['warm_avg'] > 0 else 0
        print(f"Cache speedup: {speedup:.2f}x faster ({((speedup - 1) / speedup * 100):.1f}% reduction)")
    print()
    print("Expected for good caching:")
    print("  - Cold read: ~1-5ms (loads from disk)")
    print("  - Warm read: ~0.1-1ms (from cache)")
    print("  - Speedup: 5-50x faster")
    # Check if cache is working
    if result['warm_avg'] < result['cold_time'] / 5:
        print("\n[OK] Caching is working well!")
    elif result['warm_avg'] < result['cold_time']:
        print("\n[INFO] Caching is working, but could be better")
    else:
        print("\n[WARN] Caching may not be working optimally")
    return 0
if __name__ == "__main__":
    sys.exit(main())
