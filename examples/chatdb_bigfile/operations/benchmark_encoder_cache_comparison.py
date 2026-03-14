"""Compare encoder_1.py: Simple read_header_and_index vs Updated with caching.
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


def read_header_and_index_simple(self, file_path, HEADER_SIZE, FLAG_HAS_INDEX, XWJSONHybridParser, SerializationError, Path):
    """Simple version without caching helpers (for comparison)."""
    path = Path(file_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"{path}")
    # Check for external index first
    ext_index = self._load_external_index(path)
    with open(path, 'rb') as f:
        # Read minimal header
        header_bytes = f.read(HEADER_SIZE)
        if len(header_bytes) < HEADER_SIZE:
            raise SerializationError("File too short for header")
        header_info = self._parse_header(header_bytes)
        if ext_index:
            return header_info, ext_index
        # Read embedded index
        if header_info['flags'] & FLAG_HAS_INDEX:
            # Calculate offset
            seek_pos = HEADER_SIZE + header_info['data_length'] + header_info['metadata_length']
            f.seek(seek_pos)
            index_bytes = f.read(header_info['index_length'])
            return header_info, XWJSONHybridParser.msgpack_decode(index_bytes)
    return header_info, None


def benchmark_comparison(decoder, file_path: Path, num_iterations: int = 1000) -> dict[str, Any]:
    """Compare simple vs updated version."""
    import exonware.xwjson.formats.binary.xwjson.encoder_1 as encoder_1_module
    print(f"  Testing {num_iterations:,} iterations...")
    print()
    # Clear cache
    try:
        from exonware.xwjson.formats.binary.xwjson.serializer import XWJSONSerializer
        if XWJSONSerializer._cache_initialized:
            with XWJSONSerializer._cache_lock:
                XWJSONSerializer._index_cache.clear() if hasattr(XWJSONSerializer._index_cache, 'clear') else None
                XWJSONSerializer._mtime_cache.clear()
                XWJSONSerializer._index_mtime_cache.clear()
    except Exception:
        pass
    # Test SIMPLE version (without caching helpers)
    print("  SIMPLE VERSION (no caching helpers):")
    simple_start = time.perf_counter()
    for i in range(num_iterations):
        # Clear cache before each call to simulate no caching
        try:
            from exonware.xwjson.formats.binary.xwjson.serializer import XWJSONSerializer
            if XWJSONSerializer._cache_initialized:
                with XWJSONSerializer._cache_lock:
                    # Remove this file's cache entry
                    cache_key = f"header_index:{str(file_path.resolve())}"
                    try:
                        XWJSONSerializer._index_cache.pop(cache_key)
                    except KeyError:
                        pass
                    XWJSONSerializer._mtime_cache.pop(str(file_path.resolve()), None)
        except Exception:
            pass
        # Use the simple version (bypass cache)
        ext_index = decoder._load_external_index(file_path)
        with open(file_path, 'rb') as f:
            header_bytes = f.read(encoder_1_module.HEADER_SIZE)
            header_info = decoder._parse_header(header_bytes)
            if ext_index:
                result = header_info, ext_index
            elif header_info['flags'] & encoder_1_module.FLAG_HAS_INDEX:
                seek_pos = encoder_1_module.HEADER_SIZE + header_info['data_length'] + header_info['metadata_length']
                f.seek(seek_pos)
                index_bytes = f.read(header_info['index_length'])
                result = header_info, encoder_1_module.XWJSONHybridParser.msgpack_decode(index_bytes)
            else:
                result = header_info, None
    simple_time = time.perf_counter() - simple_start
    simple_avg = simple_time / num_iterations
    print(f"    Total time: {simple_time * 1000:.3f} ms")
    print(f"    Average: {simple_avg * 1000:.3f} ms/call")
    print(f"    Throughput: {num_iterations / simple_time:,.0f} calls/s")
    print()
    # Clear cache again
    try:
        from exonware.xwjson.formats.binary.xwjson.serializer import XWJSONSerializer
        if XWJSONSerializer._cache_initialized:
            with XWJSONSerializer._cache_lock:
                XWJSONSerializer._index_cache.clear() if hasattr(XWJSONSerializer._index_cache, 'clear') else None
                XWJSONSerializer._mtime_cache.clear()
                XWJSONSerializer._index_mtime_cache.clear()
    except Exception:
        pass
    # Test UPDATED version (with caching helpers)
    print("  UPDATED VERSION (with caching helpers):")
    # Cold read (first call)
    cold_start = time.perf_counter()
    cold_result = decoder.read_header_and_index(file_path)
    cold_time = time.perf_counter() - cold_start
    # Warm reads (should hit cache)
    warm_start = time.perf_counter()
    for i in range(num_iterations - 1):
        warm_result = decoder.read_header_and_index(file_path)
    warm_total = time.perf_counter() - warm_start
    warm_avg = warm_total / (num_iterations - 1) if num_iterations > 1 else 0
    total_updated_time = cold_time + warm_total
    total_avg = total_updated_time / num_iterations
    print(f"    Cold read (first call): {cold_time * 1000:.3f} ms")
    print(f"    Warm reads (avg): {warm_avg * 1000:.3f} ms/call")
    print(f"    Total time: {total_updated_time * 1000:.3f} ms")
    print(f"    Average (including cold): {total_avg * 1000:.3f} ms/call")
    print(f"    Warm throughput: {(num_iterations - 1) / warm_total:,.0f} calls/s" if warm_total > 0 else "    Warm throughput: N/A")
    print()
    # Comparison
    print("  COMPARISON:")
    improvement = simple_time / total_updated_time if total_updated_time > 0 else 0
    warm_improvement = simple_avg / warm_avg if warm_avg > 0 else 0
    print(f"    Overall speedup: {improvement:.2f}x ({'faster' if improvement > 1 else 'slower'})")
    print(f"    Warm cache speedup: {warm_improvement:.2f}x ({'faster' if warm_improvement > 1 else 'slower'})")
    print(f"    Simple avg: {simple_avg * 1000:.3f} ms/call")
    print(f"    Updated avg (total): {total_avg * 1000:.3f} ms/call")
    print(f"    Updated avg (warm): {warm_avg * 1000:.3f} ms/call")
    return {
        "simple_time": simple_time,
        "simple_avg": simple_avg,
        "cold_time": cold_time,
        "warm_total": warm_total,
        "warm_avg": warm_avg,
        "total_updated_time": total_updated_time,
        "total_avg": total_avg,
        "improvement": improvement,
        "warm_improvement": warm_improvement
    }


def main() -> int:
    """Main entry point."""
    print("=" * 70)
    print("Encoder Cache Comparison: Simple vs Updated read_header_and_index")
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
    print("=" * 70)
    print("PERFORMANCE TEST")
    print("=" * 70)
    print()
    result = benchmark_comparison(decoder, test_file, num_iterations=500)
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    if result['improvement'] > 1.1:
        print(f"[OK] Updated version is {result['improvement']:.2f}x faster overall!")
    elif result['improvement'] < 0.9:
        print(f"[WARN] Updated version is {1/result['improvement']:.2f}x slower overall")
    else:
        print("[INFO] Performance is similar")
    if result['warm_improvement'] > 5:
        print(f"[OK] Caching is working well! Warm reads are {result['warm_improvement']:.2f}x faster")
    elif result['warm_improvement'] > 2:
        print(f"[INFO] Caching helps! Warm reads are {result['warm_improvement']:.2f}x faster")
    else:
        print(f"[WARN] Caching benefit is minimal ({result['warm_improvement']:.2f}x)")
    print()
    print(f"Simple version: {result['simple_avg'] * 1000:.3f} ms/call")
    print(f"Updated version (cold): {result['cold_time'] * 1000:.3f} ms")
    print(f"Updated version (warm): {result['warm_avg'] * 1000:.3f} ms/call")
    return 0
if __name__ == "__main__":
    sys.exit(main())
