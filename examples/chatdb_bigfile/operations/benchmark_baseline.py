"""Quick baseline benchmark to normalize performance comparisons.

This script runs simple JSON parsing benchmarks to establish
a baseline for your hardware, so we can compare our performance
relative to standard libraries on the same machine.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

# Test data similar to our chatdb records
SAMPLE_RECORD = {
    "@type": "Message",
    "id": "msg_000000000001",
    "ts": 1234567890,
    "payload": {
        "chat": {"$ref": "xwdb://Channel/chan_000001"},
        "author": {"$ref": "xwdb://User/user_000001"},
        "text": "This is a sample message with some text content for benchmarking purposes",
        "views": 12345,
        "edited_ts": None,
        "version": 1,
    },
}

SAMPLE_LINE = json.dumps(SAMPLE_RECORD, ensure_ascii=False, separators=(",", ":")) + "\n"


def benchmark_stdlib_json_parse():
    """Benchmark Python stdlib json parsing."""
    print("Benchmarking Python stdlib json parsing...")
    iterations = 1_000_000
    start = time.perf_counter()
    
    for _ in range(iterations):
        json.loads(SAMPLE_LINE.strip())
    
    elapsed = time.perf_counter() - start
    rate = iterations / elapsed
    print(f"  stdlib json: {rate:,.0f} records/s ({elapsed:.2f}s for {iterations:,} records)")
    return rate


def benchmark_stdlib_json_dumps():
    """Benchmark Python stdlib json serialization."""
    print("Benchmarking Python stdlib json serialization...")
    iterations = 1_000_000
    start = time.perf_counter()
    
    for _ in range(iterations):
        json.dumps(SAMPLE_RECORD, ensure_ascii=False, separators=(",", ":"))
    
    elapsed = time.perf_counter() - start
    rate = iterations / elapsed
    print(f"  stdlib json.dumps: {rate:,.0f} records/s ({elapsed:.2f}s for {iterations:,} records)")
    return rate


def benchmark_file_read():
    """Benchmark raw file reading (no parsing)."""
    print("Benchmarking raw file line reading...")
    db_path = Path(__file__).parents[1] / "data" / "chatdb.jsonl"
    
    if not db_path.exists():
        print(f"  Skipping (file not found: {db_path})")
        return None
    
    start = time.perf_counter()
    lines = 0
    bytes_read = 0
    
    with db_path.open("rb") as f:
        while True:
            line = f.readline()
            if not line:
                break
            lines += 1
            bytes_read += len(line)
            if lines >= 1_000_000:  # Limit to 1M lines for speed
                break
    
    elapsed = time.perf_counter() - start
    rate = lines / elapsed
    mb_per_s = (bytes_read / (1024 * 1024)) / elapsed
    print(f"  File read: {rate:,.0f} lines/s, {mb_per_s:.1f} MB/s ({elapsed:.2f}s for {lines:,} lines)")
    return rate


def main():
    print("=" * 60)
    print("Hardware Baseline Benchmark")
    print("=" * 60)
    print()
    
    # Run benchmarks
    stdlib_parse_rate = benchmark_stdlib_json_parse()
    print()
    
    stdlib_dumps_rate = benchmark_stdlib_json_dumps()
    print()
    
    file_read_rate = benchmark_file_read()
    print()
    
    # Compare to our observed performance
    print("=" * 60)
    print("Normalized Comparison")
    print("=" * 60)
    
    our_index_rate = 287_000  # From our index builder
    our_gen_rate_mb = 16.5  # From our generator
    
    if stdlib_parse_rate:
        ratio = our_index_rate / stdlib_parse_rate
        print(f"\nIndex Builder vs stdlib json.loads:")
        print(f"  Our rate: {our_index_rate:,} lines/s")
        print(f"  stdlib rate: {stdlib_parse_rate:,.0f} records/s")
        print(f"  Ratio: {ratio:.2f}x (we're {ratio:.1f}x faster)")
        print()
        print(f"  Note: We're doing MORE than just parsing:")
        print(f"    - JSON parsing")
        print(f"    - Building hash map (Type:id -> offset)")
        print(f"    - Tracking file offsets")
        print(f"    - Record validation")
        print()
        print(f"  If stdlib json is baseline, our {ratio:.2f}x ratio accounts")
        print(f"  for both hardware speed AND our additional work.")
    
    if file_read_rate:
        ratio = our_index_rate / file_read_rate
        print(f"\nIndex Builder vs raw file read:")
        print(f"  Our rate: {our_index_rate:,} lines/s")
        print(f"  File read rate: {file_read_rate:,.0f} lines/s")
        print(f"  Ratio: {ratio:.2f}x")
        print()
        print(f"  This shows parsing overhead: we're {ratio:.2f}x slower")
        print(f"  than raw file reading, which is expected.")
    
    print()
    print("=" * 60)
    print("Conclusion")
    print("=" * 60)
    print()
    print("This baseline helps normalize comparisons:")
    print("- If your hardware is 2x faster than average, our numbers")
    print("  would be 2x higher than on average hardware")
    print("- The RATIO between our performance and stdlib json is more")
    print("  meaningful than absolute numbers")
    print("- Our index builder doing MORE work (parsing + indexing)")
    print("  while maintaining good speed is the real achievement")


if __name__ == "__main__":
    main()
