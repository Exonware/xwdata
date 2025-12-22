"""Complete Performance Benchmark

Runs BOTH apple-to-apple AND full-featured benchmarks
to show performance with and without additional features.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

# Import our index builder
import sys
_OPS_DIR = Path(__file__).resolve().parent
if str(_OPS_DIR) not in sys.path:
    sys.path.insert(0, str(_OPS_DIR))

import build_index


def benchmark_apple_to_apple_parse():
    """Apple-to-Apple: Pure JSON parsing (no indexing)."""
    print("=" * 70)
    print("APPLE-TO-APPLE: Pure JSON Parsing (No Indexing)")
    print("=" * 70)
    print()
    
    # Create sample line
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
    print("Benchmarking stdlib json.loads()...")
    start = time.perf_counter()
    for _ in range(iterations):
        json.loads(sample_line.strip())
    elapsed = time.perf_counter() - start
    stdlib_rate = iterations / elapsed
    print(f"  stdlib json.loads: {stdlib_rate:,.0f} records/s ({elapsed:.2f}s)")
    print()
    
    # Test our approach: read file line-by-line and parse (no indexing)
    print("Benchmarking our approach (file read + parse, NO indexing)...")
    db_path = Path(__file__).parents[1] / "data" / "chatdb.jsonl"
    
    if not db_path.exists():
        print(f"  Skipping (file not found: {db_path})")
        return stdlib_rate, None
    
    start = time.perf_counter()
    parsed = 0
    with db_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            json.loads(line)  # Just parse, no indexing
            parsed += 1
            if parsed >= iterations:
                break
    elapsed = time.perf_counter() - start
    our_rate = parsed / elapsed
    print(f"  Our approach (read + parse): {our_rate:,.0f} records/s ({elapsed:.2f}s)")
    print()
    
    ratio = our_rate / stdlib_rate if stdlib_rate > 0 else 0
    print(f"Comparison: {ratio*100:.1f}% of stdlib ({'Good' if ratio > 0.9 else 'Slower'})")
    print()
    
    return stdlib_rate, our_rate


def benchmark_full_featured_indexing():
    """Full-Featured: JSON parsing + index building + hash map."""
    print("=" * 70)
    print("FULL-FEATURED: Index Building (Parsing + Indexing + Hash Map)")
    print("=" * 70)
    print()
    
    db_path = Path(__file__).parents[1] / "data" / "chatdb.jsonl"
    
    if not db_path.exists():
        print(f"  Skipping (file not found: {db_path})")
        return None, None
    
    file_size_mb = db_path.stat().st_size / (1024 * 1024)
    print(f"File: {db_path.name} ({file_size_mb:.2f} MB)")
    print()
    print("Benchmarking full-featured index builder...")
    print("  Features: JSON parsing + hash map building + offset tracking + validation")
    print()
    
    started = time.perf_counter()
    result = build_index.build_index(db_path)
    elapsed = time.perf_counter() - started
    
    total_keys = len(result.get("by_key", {}))
    total_records = result.get("meta", {}).get("total_records", 0)
    
    records_per_sec = total_records / elapsed if elapsed > 0 else 0
    keys_per_sec = total_keys / elapsed if elapsed > 0 else 0
    
    print(f"Results:")
    print(f"  Time: {elapsed:.2f}s")
    print(f"  Records processed: {total_records:,}")
    print(f"  Keys indexed: {total_keys:,}")
    print(f"  Records/s: {records_per_sec:,.0f}")
    print(f"  Keys/s: {keys_per_sec:,.0f}")
    print()
    
    return records_per_sec, total_records


def benchmark_apple_to_apple_write():
    """Apple-to-Apple: Pure JSON serialization (no file I/O overhead)."""
    print("=" * 70)
    print("APPLE-TO-APPLE: Pure JSON Serialization")
    print("=" * 70)
    print()
    
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
    iterations = 1_000_000
    
    # Test stdlib json.dumps
    print("Benchmarking stdlib json.dumps()...")
    start = time.perf_counter()
    total_bytes = 0
    for _ in range(iterations):
        line = json.dumps(sample_record, ensure_ascii=False, separators=(",", ":"))
        total_bytes += len(line.encode("utf-8"))
    elapsed = time.perf_counter() - start
    stdlib_rate = iterations / elapsed
    stdlib_mb_s = (total_bytes / (1024 * 1024)) / elapsed
    print(f"  stdlib json.dumps: {stdlib_rate:,.0f} records/s, {stdlib_mb_s:.1f} MB/s ({elapsed:.2f}s)")
    print()
    
    # Test our approach: write to file (buffered)
    print("Benchmarking our approach (write to file, buffered)...")
    import tempfile
    
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False) as f:
        temp_path = Path(f.name)
        start = time.perf_counter()
        total_bytes = 0
        for _ in range(iterations):
            line = json.dumps(sample_record, ensure_ascii=False, separators=(",", ":")) + "\n"
            f.write(line)
            total_bytes += len(line.encode("utf-8"))
        f.flush()
        elapsed = time.perf_counter() - start
        our_rate = iterations / elapsed
        our_mb_s = (total_bytes / (1024 * 1024)) / elapsed
        print(f"  Our approach (buffered write): {our_rate:,.0f} records/s, {our_mb_s:.1f} MB/s ({elapsed:.2f}s)")
    
    temp_path.unlink()
    print()
    
    ratio = our_rate / stdlib_rate if stdlib_rate > 0 else 0
    print(f"Comparison: {ratio*100:.1f}% of stdlib ({'Good' if ratio > 0.9 else 'Slower'})")
    print()
    
    return stdlib_rate, our_rate, stdlib_mb_s, our_mb_s


def main():
    print()
    print("=" * 70)
    print("COMPLETE Performance Benchmark")
    print("=" * 70)
    print()
    print("This benchmark runs BOTH:")
    print("  1. Apple-to-Apple: Pure features (no indexing)")
    print("  2. Full-Featured: Complete implementation (with indexing)")
    print()
    
    # Run all benchmarks
    stdlib_parse, our_parse_aa = benchmark_apple_to_apple_parse()
    print()
    
    our_parse_ff, total_records = benchmark_full_featured_indexing()
    print()
    
    stdlib_write, our_write, stdlib_mb_s, our_mb_s = benchmark_apple_to_apple_write()
    print()
    
    # Summary comparison
    print("=" * 70)
    print("COMPARISON SUMMARY")
    print("=" * 70)
    print()
    
    print("JSON Parsing:")
    print(f"  stdlib json (baseline):     {stdlib_parse:,.0f} records/s")
    if our_parse_aa:
        ratio_aa = our_parse_aa / stdlib_parse if stdlib_parse > 0 else 0
        print(f"  Our (apple-to-apple):       {our_parse_aa:,.0f} records/s ({ratio_aa*100:.1f}% of stdlib)")
    if our_parse_ff:
        ratio_ff = our_parse_ff / stdlib_parse if stdlib_parse > 0 else 0
        print(f"  Our (full-featured):        {our_parse_ff:,.0f} records/s ({ratio_ff*100:.1f}% of stdlib)")
        if our_parse_aa:
            overhead = (our_parse_aa - our_parse_ff) / our_parse_aa * 100 if our_parse_aa > 0 else 0
            print(f"  Feature overhead:          {overhead:.1f}% slower (indexing + hash map)")
    print()
    
    print("JSON Writing:")
    print(f"  stdlib json (baseline):     {stdlib_write:,.0f} records/s, {stdlib_mb_s:.1f} MB/s")
    if our_write:
        ratio_write = our_write / stdlib_write if stdlib_write > 0 else 0
        print(f"  Our (apple-to-apple):       {our_write:,.0f} records/s, {our_mb_s:.1f} MB/s ({ratio_write*100:.1f}% of stdlib)")
    print()
    
    print("=" * 70)
    print("KEY INSIGHTS")
    print("=" * 70)
    print()
    print("1. Apple-to-Apple shows pure JSON performance (I/O overhead)")
    print("2. Full-Featured shows complete implementation (with indexing)")
    print("3. The difference shows the cost of additional features")
    print()
    if our_parse_aa and our_parse_ff:
        overhead_pct = (our_parse_aa - our_parse_ff) / our_parse_aa * 100
        print(f"4. Indexing overhead: ~{overhead_pct:.1f}% (acceptable for the features gained)")


if __name__ == "__main__":
    main()
