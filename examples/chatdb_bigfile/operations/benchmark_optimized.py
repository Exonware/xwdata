"""Benchmark optimized serializers vs original.
Compares performance with and without orjson optimization.
"""

from __future__ import annotations
import json
import time
from pathlib import Path
from typing import Any
# Import optimized serializers
import sys
_OPS_DIR = Path(__file__).resolve().parent
if str(_OPS_DIR) not in sys.path:
    sys.path.insert(0, str(_OPS_DIR))
# Add xwsystem to path
_xwsystem_src = Path(__file__).resolve().parents[4] / "xwsystem" / "src"
if str(_xwsystem_src) not in sys.path:
    sys.path.insert(0, str(_xwsystem_src))
from exonware.xwsystem.io.serialization.formats.text.jsonlines import JsonLinesSerializer
from exonware.xwsystem.io.serialization.parsers.registry import get_parser, get_best_available_parser


def benchmark_parser_comparison():
    """Compare different parsers."""
    print("=" * 70)
    print("PARSER COMPARISON")
    print("=" * 70)
    print()
    # Sample record
    sample_record = {
        "@type": "Message",
        "id": "msg_000000000001",
        "ts": 1234567890,
        "payload": {
            "chat": {"$ref": "xwdb://Channel/chan_000001"},
            "author": {"$ref": "xwdb://User/user_000001"},
            "text": "This is a sample message with some text content for benchmarking purposes " * 3,
            "views": 12345,
            "edited_ts": None,
            "version": 1,
        },
    }
    sample_line = json.dumps(sample_record, ensure_ascii=False, separators=(",", ":")) + "\n"
    iterations = 1_000_000
    # Test stdlib json
    print("1. Standard library json.loads()...")
    start = time.perf_counter()
    for _ in range(iterations):
        json.loads(sample_line.strip())
    elapsed = time.perf_counter() - start
    stdlib_rate = iterations / elapsed
    print(f"   stdlib json: {stdlib_rate:,.0f} records/s ({elapsed:.2f}s)")
    print()
    # Test standard parser
    print("2. Standard parser (via registry)...")
    standard_parser = get_parser("standard")
    start = time.perf_counter()
    for _ in range(iterations):
        standard_parser.loads(sample_line.strip())
    elapsed = time.perf_counter() - start
    standard_rate = iterations / elapsed
    print(f"   Standard parser: {standard_rate:,.0f} records/s ({elapsed:.2f}s)")
    print()
    # Test orjson parser (if available)
    print("3. Orjson parser (if available)...")
    orjson_parser = get_parser("orjson")
    if orjson_parser.is_available:
        start = time.perf_counter()
        for _ in range(iterations):
            orjson_parser.loads(sample_line.strip())
        elapsed = time.perf_counter() - start
        orjson_rate = iterations / elapsed
        print(f"   Orjson parser: {orjson_rate:,.0f} records/s ({elapsed:.2f}s)")
        print(f"   Improvement: {orjson_rate/stdlib_rate:.2f}x faster than stdlib")
    else:
        print("   Orjson not available (install with: pip install orjson)")
        orjson_rate = None
    print()
    # Test best available parser
    print("4. Best available parser (auto-detect)...")
    best_parser = get_best_available_parser()
    start = time.perf_counter()
    for _ in range(iterations):
        best_parser.loads(sample_line.strip())
    elapsed = time.perf_counter() - start
    best_rate = iterations / elapsed
    print(f"   Best parser ({best_parser.parser_name}): {best_rate:,.0f} records/s ({elapsed:.2f}s)")
    if best_parser.parser_name == "orjson":
        print(f"   Improvement: {best_rate/stdlib_rate:.2f}x faster than stdlib")
    print()
    return {
        "stdlib": stdlib_rate,
        "standard": standard_rate,
        "orjson": orjson_rate,
        "best": best_rate,
        "best_parser": best_parser.parser_name,
    }


def benchmark_jsonlines_serializer():
    """Compare JsonLinesSerializer with different parsers."""
    print("=" * 70)
    print("JSONLINES SERIALIZER COMPARISON")
    print("=" * 70)
    print()
    db_path = Path(__file__).parents[1] / "data" / "chatdb.jsonl"
    if not db_path.exists():
        print(f"  Skipping (file not found: {db_path})")
        return None, None
    file_size_mb = db_path.stat().st_size / (1024 * 1024)
    print(f"File: {db_path.name} ({file_size_mb:.2f} MB)")
    print()
    # Test with standard parser
    print("1. JsonLinesSerializer with standard parser...")
    serializer_std = JsonLinesSerializer(parser_name="standard")
    start = time.perf_counter()
    page = serializer_std.get_record_page(db_path, page_number=1, page_size=1000)
    elapsed = time.perf_counter() - start
    std_rate = len(page) / elapsed if elapsed > 0 else 0
    print(f"   Standard: {std_rate:,.0f} records/s ({elapsed:.4f}s for {len(page)} records)")
    print()
    # Test with orjson parser (if available)
    print("2. JsonLinesSerializer with orjson parser (if available)...")
    serializer_orjson = JsonLinesSerializer(parser_name="orjson")
    if serializer_orjson._parser.is_available:
        start = time.perf_counter()
        page = serializer_orjson.get_record_page(db_path, page_number=1, page_size=1000)
        elapsed = time.perf_counter() - start
        orjson_rate = len(page) / elapsed if elapsed > 0 else 0
        print(f"   Orjson: {orjson_rate:,.0f} records/s ({elapsed:.4f}s for {len(page)} records)")
        print(f"   Improvement: {orjson_rate/std_rate:.2f}x faster than standard")
    else:
        print("   Orjson not available")
        orjson_rate = None
    print()
    # Test with auto-detect (best available)
    print("3. JsonLinesSerializer with auto-detect (best available)...")
    serializer_best = JsonLinesSerializer()  # Auto-detect
    start = time.perf_counter()
    page = serializer_best.get_record_page(db_path, page_number=1, page_size=1000)
    elapsed = time.perf_counter() - start
    best_rate = len(page) / elapsed if elapsed > 0 else 0
    print(f"   Best ({serializer_best._parser.parser_name}): {best_rate:,.0f} records/s ({elapsed:.4f}s for {len(page)} records)")
    if serializer_best._parser.parser_name == "orjson":
        print(f"   Improvement: {best_rate/std_rate:.2f}x faster than standard")
    print()
    return {
        "standard": std_rate,
        "orjson": orjson_rate,
        "best": best_rate,
        "best_parser": serializer_best._parser.parser_name,
    }


def benchmark_index_building():
    """Compare index building performance."""
    print("=" * 70)
    print("INDEX BUILDING COMPARISON")
    print("=" * 70)
    print()
    db_path = Path(__file__).parents[1] / "data" / "chatdb.jsonl"
    if not db_path.exists():
        print(f"  Skipping (file not found: {db_path})")
        return None
    import build_index
    # Test with standard parser (via build_index using stdlib)
    print("1. Index building with standard parser...")
    # We'll need to modify build_index to use the parser, but for now
    # we'll just time the existing implementation
    start = time.perf_counter()
    result = build_index.build_index(db_path)
    elapsed = time.perf_counter() - start
    total_keys = len(result.get("by_key", {}))
    std_rate = total_keys / elapsed if elapsed > 0 else 0
    print(f"   Standard: {std_rate:,.0f} keys/s ({elapsed:.2f}s for {total_keys:,} keys)")
    print()
    # Note: To test with orjson, we'd need to update build_index.py
    # to use the parser abstraction. For now, we'll just show the standard result.
    return {
        "standard": std_rate,
        "total_keys": total_keys,
        "time": elapsed,
    }


def main():
    print()
    print("=" * 70)
    print("OPTIMIZED SERIALIZER BENCHMARK")
    print("=" * 70)
    print()
    print("Comparing optimized serializers (with orjson) vs original (stdlib)")
    print()
    # Run benchmarks
    parser_results = benchmark_parser_comparison()
    print()
    serializer_results = benchmark_jsonlines_serializer()
    print()
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    if parser_results:
        print("Parser Performance:")
        print(f"  stdlib json: {parser_results['stdlib']:,.0f} records/s")
        print(f"  standard parser: {parser_results['standard']:,.0f} records/s")
        if parser_results['orjson']:
            print(f"  orjson parser: {parser_results['orjson']:,.0f} records/s")
            print(f"  orjson improvement: {parser_results['orjson']/parser_results['stdlib']:.2f}x")
        print(f"  best parser ({parser_results['best_parser']}): {parser_results['best']:,.0f} records/s")
        print()
    if serializer_results:
        print("JsonLinesSerializer Performance:")
        print(f"  standard parser: {serializer_results['standard']:,.0f} records/s")
        if serializer_results['orjson']:
            print(f"  orjson parser: {serializer_results['orjson']:,.0f} records/s")
            print(f"  orjson improvement: {serializer_results['orjson']/serializer_results['standard']:.2f}x")
        print(f"  best parser ({serializer_results['best_parser']}): {serializer_results['best']:,.0f} records/s")
        print()
    print("=" * 70)
    print("CONCLUSION")
    print("=" * 70)
    print()
    if parser_results and parser_results.get('orjson'):
        improvement = parser_results['orjson'] / parser_results['stdlib']
        print(f"[OK] orjson provides {improvement:.2f}x improvement over stdlib json")
        print("[OK] Auto-detection works: best parser is automatically selected")
    else:
        print("[WARN] orjson not available. Install with: pip install orjson")
        print("[OK] System falls back gracefully to stdlib json")
    print()
if __name__ == "__main__":
    main()
