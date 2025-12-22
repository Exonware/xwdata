"""Comprehensive benchmark comparing all JSON parsers (apple-to-apple + full-featured)."""

import sys
import time
import json
from pathlib import Path

# Add paths for local imports
_xwsystem_src = Path(__file__).resolve().parents[4] / "xwsystem" / "src"
_xwdata_src = Path(__file__).resolve().parents[4] / "xwdata" / "src"
if str(_xwsystem_src) not in sys.path:
    sys.path.insert(0, str(_xwsystem_src))
if str(_xwdata_src) not in sys.path:
    sys.path.insert(0, str(_xwdata_src))

from exonware.xwsystem.io.serialization.parsers.registry import get_parser, register_parser
from exonware.xwsystem.io.serialization.parsers.orjson_direct_parser import OrjsonDirectParser

# Register direct orjson parser
register_parser("orjson_direct", OrjsonDirectParser)

# Test data file
DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "chatdb.jsonl"


def _human_bytes(n: int) -> str:
    """Format bytes as human-readable string."""
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024.0:
            return f"{n:.2f} {unit}"
        n /= 1024.0
    return f"{n:.2f} TB"


def _load_test_data(num_records: int = 10000) -> list:
    """Load test data from file."""
    records = []
    with open(DATA_FILE, "rb") as f:
        for i, line in enumerate(f):
            if i >= num_records:
                break
            records.append(line.strip())
    return records


def benchmark_apple_to_apple(parser_name: str, records: list) -> dict:
    """Apple-to-apple benchmark: pure JSON parsing."""
    try:
        parser = get_parser(parser_name)
        if not parser.is_available:
            return {"available": False, "error": "Parser not available"}
    except Exception as e:
        return {"available": False, "error": str(e)}
    
    # Warmup
    for rec in records[:100]:
        try:
            parser.loads(rec)
        except:
            pass
    
    # Benchmark
    start = time.perf_counter()
    parsed = 0
    for rec in records:
        try:
            parser.loads(rec)
            parsed += 1
        except Exception as e:
            pass
    
    elapsed = time.perf_counter() - start
    rate = parsed / elapsed if elapsed > 0 else 0
    
    return {
        "available": True,
        "parser": parser_name,
        "records": parsed,
        "time": elapsed,
        "rate": rate,
        "rate_str": f"{rate:,.0f} records/s",
    }


def benchmark_full_featured(parser_name: str) -> dict:
    """Full-featured benchmark: index building with parser."""
    try:
        parser = get_parser(parser_name)
        if not parser.is_available:
            return {"available": False, "error": "Parser not available"}
    except Exception as e:
        return {"available": False, "error": str(e)}
    
    # Build index using the parser
    index = {}
    keys_indexed = 0
    lines_scanned = 0
    
    start = time.perf_counter()
    
    with open(DATA_FILE, "rb") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                rec = parser.loads(line)
                if isinstance(rec, dict):
                    rec_type = rec.get("type")
                    rec_id = rec.get("id")
                    if rec_type and rec_id:
                        key = f"{rec_type}:{rec_id}"
                        index[key] = f.tell() - len(line) - 1
                        keys_indexed += 1
                lines_scanned += 1
                
                # Progress update every 1M lines
                if lines_scanned % 1_000_000 == 0:
                    elapsed = time.perf_counter() - start
                    rate = lines_scanned / elapsed if elapsed > 0 else 0
                    print(f"  ... scanned {lines_scanned:,} lines ({rate:,.0f} lines/s), keys={keys_indexed:,}")
            except Exception:
                pass
    
    elapsed = time.perf_counter() - start
    rate = keys_indexed / elapsed if elapsed > 0 else 0
    
    return {
        "available": True,
        "parser": parser_name,
        "keys_indexed": keys_indexed,
        "lines_scanned": lines_scanned,
        "time": elapsed,
        "rate": rate,
        "rate_str": f"{rate:,.0f} keys/s",
    }


def main():
    """Run comprehensive benchmarks."""
    print("=" * 70)
    print("COMPREHENSIVE PARSER BENCHMARK")
    print("=" * 70)
    print()
    
    if not DATA_FILE.exists():
        print(f"[ERROR] Data file not found: {DATA_FILE}")
        return
    
    file_size = DATA_FILE.stat().st_size
    print(f"Data file: {DATA_FILE.name} ({_human_bytes(file_size)})")
    print()
    
    # Parser list to test
    parsers_to_test = [
        "hybrid",  # NEW: msgspec for reading, orjson for writing
        "standard",
        "orjson",
        "msgspec",
    ]
    
    # Load test data for apple-to-apple
    print("Loading test data for apple-to-apple benchmark...")
    test_records = _load_test_data(10000)
    print(f"Loaded {len(test_records):,} records")
    print()
    
    # Apple-to-apple benchmarks
    print("=" * 70)
    print("APPLE-TO-APPLE: Pure JSON Parsing (10,000 records)")
    print("=" * 70)
    print()
    
    apple_results = {}
    for parser_name in parsers_to_test:
        print(f"Testing {parser_name}...")
        result = benchmark_apple_to_apple(parser_name, test_records)
        apple_results[parser_name] = result
        
        if result.get("available"):
            print(f"  Rate: {result['rate_str']}")
        else:
            print(f"  [SKIP] {result.get('error', 'Not available')}")
        print()
    
    # Full-featured benchmarks
    print("=" * 70)
    print("FULL-FEATURED: Index Building (all records)")
    print("=" * 70)
    print()
    
    full_results = {}
    for parser_name in parsers_to_test:
        print(f"Testing {parser_name}...")
        result = benchmark_full_featured(parser_name)
        full_results[parser_name] = result
        
        if result.get("available"):
            print(f"  Rate: {result['rate_str']}")
            print(f"  Time: {result['time']:.2f}s")
            print(f"  Keys: {result['keys_indexed']:,}")
        else:
            print(f"  [SKIP] {result.get('error', 'Not available')}")
        print()
    
    # Summary
    print("=" * 70)
    print("SUMMARY: Apple-to-Apple")
    print("=" * 70)
    print()
    
    # Sort by rate
    available_apple = [(k, v) for k, v in apple_results.items() if v.get("available")]
    available_apple.sort(key=lambda x: x[1]["rate"], reverse=True)
    
    if available_apple:
        baseline_rate = available_apple[-1][1]["rate"]  # Standard (slowest)
        
        print(f"{'Parser':<20} {'Rate (records/s)':<20} {'vs stdlib':<15}")
        print("-" * 55)
        for parser_name, result in available_apple:
            vs_stdlib = result["rate"] / baseline_rate if baseline_rate > 0 else 0
            print(f"{parser_name:<20} {result['rate_str']:<20} {vs_stdlib:.2f}x")
        print()
    
    print("=" * 70)
    print("SUMMARY: Full-Featured")
    print("=" * 70)
    print()
    
    # Sort by rate
    available_full = [(k, v) for k, v in full_results.items() if v.get("available")]
    available_full.sort(key=lambda x: x[1]["rate"], reverse=True)
    
    if available_full:
        baseline_rate = available_full[-1][1]["rate"]  # Standard (slowest)
        
        print(f"{'Parser':<20} {'Rate (keys/s)':<20} {'Time (s)':<12} {'vs stdlib':<15}")
        print("-" * 67)
        for parser_name, result in available_full:
            vs_stdlib = result["rate"] / baseline_rate if baseline_rate > 0 else 0
            print(f"{parser_name:<20} {result['rate_str']:<20} {result['time']:<12.2f} {vs_stdlib:.2f}x")
        print()
    
    # Comparison: orjson vs orjson_direct
    print("=" * 70)
    print("DIRECT vs AUTO-DETECT: orjson_direct vs orjson")
    print("=" * 70)
    print()
    
    if "orjson" in apple_results and "orjson_direct" in apple_results:
        orjson_result = apple_results["orjson"]
        direct_result = apple_results["orjson_direct"]
        
        if orjson_result.get("available") and direct_result.get("available"):
            improvement = direct_result["rate"] / orjson_result["rate"] if orjson_result["rate"] > 0 else 0
            print(f"orjson (auto-detect): {orjson_result['rate_str']}")
            print(f"orjson_direct (no try/catch): {direct_result['rate_str']}")
            print(f"Improvement: {improvement:.4f}x")
            print()
    
    print("=" * 70)
    print("TOP 3 RECOMMENDATIONS")
    print("=" * 70)
    print()
    
    # Top 3 by full-featured performance
    if available_full:
        top3 = available_full[:3]
        print("Based on full-featured (index building) performance:")
        for i, (parser_name, result) in enumerate(top3, 1):
            print(f"{i}. {parser_name}: {result['rate_str']} ({result['time']:.2f}s)")
        print()


if __name__ == "__main__":
    main()
