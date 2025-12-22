"""Read/Write comparison: msgspec vs orjson."""

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

from exonware.xwsystem.io.serialization.parsers.registry import get_parser

# Test data file
DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "chatdb.jsonl"


def _load_test_data(num_records: int = 10000) -> list:
    """Load test data from file."""
    records = []
    with open(DATA_FILE, "rb") as f:
        for i, line in enumerate(f):
            if i >= num_records:
                break
            records.append(line.strip())
    return records


def _load_parsed_data(num_records: int = 10000) -> list:
    """Load and parse test data."""
    parsed = []
    with open(DATA_FILE, "rb") as f:
        for i, line in enumerate(f):
            if i >= num_records:
                break
            try:
                rec = json.loads(line)
                parsed.append(rec)
            except:
                pass
    return parsed


def benchmark_read(parser_name: str, records: list) -> dict:
    """Benchmark JSON reading/parsing."""
    parser = get_parser(parser_name)
    if not parser.is_available:
        return {"available": False, "error": "Parser not available"}
    
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
        except Exception:
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


def benchmark_write(parser_name: str, data: list) -> dict:
    """Benchmark JSON writing/serialization."""
    parser = get_parser(parser_name)
    if not parser.is_available:
        return {"available": False, "error": "Parser not available"}
    
    # Warmup
    for obj in data[:100]:
        try:
            parser.dumps(obj)
        except:
            pass
    
    # Benchmark
    start = time.perf_counter()
    serialized = 0
    total_bytes = 0
    for obj in data:
        try:
            result = parser.dumps(obj)
            serialized += 1
            if isinstance(result, bytes):
                total_bytes += len(result)
            elif isinstance(result, str):
                total_bytes += len(result.encode("utf-8"))
        except Exception:
            pass
    
    elapsed = time.perf_counter() - start
    rate = serialized / elapsed if elapsed > 0 else 0
    mbps = (total_bytes / elapsed / 1024 / 1024) if elapsed > 0 else 0
    
    return {
        "available": True,
        "parser": parser_name,
        "records": serialized,
        "time": elapsed,
        "rate": rate,
        "rate_str": f"{rate:,.0f} records/s",
        "mbps": mbps,
        "mbps_str": f"{mbps:.2f} MB/s",
        "total_bytes": total_bytes,
    }


def main():
    """Run read/write comparison."""
    print("=" * 70)
    print("READ/WRITE COMPARISON: msgspec vs orjson")
    print("=" * 70)
    print()
    
    if not DATA_FILE.exists():
        print(f"[ERROR] Data file not found: {DATA_FILE}")
        return
    
    # Load test data
    print("Loading test data...")
    test_records = _load_test_data(10000)
    print(f"Loaded {len(test_records):,} records for read benchmark")
    
    print("Loading and parsing test data for write benchmark...")
    test_data = _load_parsed_data(10000)
    print(f"Loaded {len(test_data):,} parsed records for write benchmark")
    print()
    
    # Read benchmarks
    print("=" * 70)
    print("READ PERFORMANCE (JSON Parsing)")
    print("=" * 70)
    print()
    
    hybrid_read = benchmark_read("hybrid", test_records)
    msgspec_read = benchmark_read("msgspec", test_records)
    orjson_read = benchmark_read("orjson", test_records)
    
    if hybrid_read.get("available"):
        print(f"hybrid:  {hybrid_read['rate_str']} (msgspec for reading)")
    if msgspec_read.get("available"):
        print(f"msgspec: {msgspec_read['rate_str']}")
    if orjson_read.get("available"):
        print(f"orjson:  {orjson_read['rate_str']}")
    
    if hybrid_read.get("available") and orjson_read.get("available") and orjson_read["rate"] > 0:
        improvement = hybrid_read["rate"] / orjson_read["rate"]
        print(f"hybrid is {improvement:.2f}x {'faster' if improvement > 1 else 'slower'} than orjson")
    print()
    
    # Write benchmarks
    print("=" * 70)
    print("WRITE PERFORMANCE (JSON Serialization)")
    print("=" * 70)
    print()
    
    hybrid_write = benchmark_write("hybrid", test_data)
    msgspec_write = benchmark_write("msgspec", test_data)
    orjson_write = benchmark_write("orjson", test_data)
    
    if hybrid_write.get("available"):
        print(f"hybrid:  {hybrid_write['rate_str']} ({hybrid_write['mbps_str']}) (orjson for writing)")
    if msgspec_write.get("available"):
        print(f"msgspec: {msgspec_write['rate_str']} ({msgspec_write['mbps_str']})")
    if orjson_write.get("available"):
        print(f"orjson:  {orjson_write['rate_str']} ({orjson_write['mbps_str']})")
    
    if hybrid_write.get("available") and msgspec_write.get("available") and msgspec_write["rate"] > 0:
        improvement = hybrid_write["rate"] / msgspec_write["rate"]
        print(f"hybrid is {improvement:.2f}x {'faster' if improvement > 1 else 'slower'} than msgspec (records/s)")
    
    if hybrid_write.get("available") and msgspec_write.get("available") and msgspec_write["mbps"] > 0:
        improvement_mbps = hybrid_write["mbps"] / msgspec_write["mbps"]
        print(f"hybrid is {improvement_mbps:.2f}x {'faster' if improvement_mbps > 1 else 'slower'} than msgspec (MB/s)")
    print()
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    
    print("READ (Parsing - using msgspec):")
    if hybrid_read.get("available"):
        print(f"  hybrid:  {hybrid_read['rate_str']} ({hybrid_read['time']:.3f}s)")
    if msgspec_read.get("available"):
        print(f"  msgspec: {msgspec_read['rate_str']} ({msgspec_read['time']:.3f}s)")
    if orjson_read.get("available"):
        print(f"  orjson:  {orjson_read['rate_str']} ({orjson_read['time']:.3f}s)")
    if hybrid_read.get("available") and orjson_read.get("available") and orjson_read["rate"] > 0:
        ratio = hybrid_read["rate"] / orjson_read["rate"]
        print(f"  hybrid vs orjson: {ratio:.2f}x")
    print()
    
    print("WRITE (Serialization - using orjson):")
    if hybrid_write.get("available"):
        print(f"  hybrid:  {hybrid_write['rate_str']} ({hybrid_write['mbps_str']})")
    if msgspec_write.get("available"):
        print(f"  msgspec: {msgspec_write['rate_str']} ({msgspec_write['mbps_str']})")
    if orjson_write.get("available"):
        print(f"  orjson:  {orjson_write['rate_str']} ({orjson_write['mbps_str']})")
    if hybrid_write.get("available") and msgspec_write.get("available") and msgspec_write["rate"] > 0:
        ratio = hybrid_write["rate"] / msgspec_write["rate"]
        print(f"  hybrid vs msgspec: {ratio:.2f}x")
    print()


if __name__ == "__main__":
    main()
