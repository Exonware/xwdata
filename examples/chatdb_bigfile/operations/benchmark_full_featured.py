"""Full-Featured Performance Benchmark
Tests our complete implementation WITH all features:
- JSON parsing + index building (Type:id → byte_offset)
- Hash map construction
- Record validation
- File offset tracking
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


def benchmark_full_featured_indexing():
    """Test: Full-featured index building (parsing + indexing + hash map)."""
    print("=" * 70)
    print("FULL-FEATURED TEST: Index Building (Parsing + Indexing)")
    print("=" * 70)
    print()
    db_path = Path(__file__).parents[1] / "data" / "chatdb.jsonl"
    if not db_path.exists():
        print(f"  Skipping (file not found: {db_path})")
        return None, None
    file_size_mb = db_path.stat().st_size / (1024 * 1024)
    print(f"File: {db_path.name} ({file_size_mb:.2f} MB)")
    print()
    # Test our full-featured index builder
    print("Benchmarking full-featured index builder...")
    print("  (JSON parsing + hash map building + offset tracking + validation)")
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


def benchmark_full_featured_parsing_with_index():
    """Test: Parse records while building index (simulating our approach)."""
    print("=" * 70)
    print("FULL-FEATURED TEST: Parsing with Index Building")
    print("=" * 70)
    print()
    db_path = Path(__file__).parents[1] / "data" / "chatdb.jsonl"
    if not db_path.exists():
        print(f"  Skipping (file not found: {db_path})")
        return None, None
    print("Benchmarking: Parse records + build hash map (Type:id → offset)")
    print()
    by_key: dict[str, int] = {}
    started = time.perf_counter()
    parsed = 0
    with db_path.open("rb") as f:
        offset = 0
        while True:
            line = f.readline()
            if not line:
                break
            raw = line.strip()
            if not raw:
                offset += len(line)
                continue
            try:
                rec = json.loads(raw)
                parsed += 1
                # Full-featured: build index
                if isinstance(rec, dict):
                    t = rec.get("@type")
                    rid = rec.get("id")
                    if t and rid:
                        by_key[f"{t}:{rid}"] = offset
            except Exception:
                offset += len(line)
                continue
            offset += len(line)
            # Progress indicator
            if parsed % 1_000_000 == 0:
                elapsed = time.perf_counter() - started
                rate = parsed / elapsed if elapsed > 0 else 0
                print(f"  ... {parsed:,} records ({rate:,.0f} records/s)")
    elapsed = time.perf_counter() - started
    records_per_sec = parsed / elapsed if elapsed > 0 else 0
    print()
    print(f"Results:")
    print(f"  Time: {elapsed:.2f}s")
    print(f"  Records parsed: {parsed:,}")
    print(f"  Keys indexed: {len(by_key):,}")
    print(f"  Records/s: {records_per_sec:,.0f}")
    print()
    return records_per_sec, parsed


def main():
    print()
    print("=" * 70)
    print("Full-Featured Performance Benchmark")
    print("=" * 70)
    print()
    print("This benchmark tests our COMPLETE implementation with all features:")
    print("  - JSON parsing")
    print("  - Hash map building (Type:id -> byte_offset)")
    print("  - File offset tracking")
    print("  - Record validation")
    print()
    # Run full-featured tests
    index_rate, index_records = benchmark_full_featured_indexing()
    print()
    parse_rate, parse_records = benchmark_full_featured_parsing_with_index()
    print()
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    if index_rate:
        print(f"Full-Featured Index Building:")
        print(f"  Records/s: {index_rate:,.0f}")
        print(f"  Total records: {index_records:,}")
        print()
    if parse_rate:
        print(f"Full-Featured Parsing with Index:")
        print(f"  Records/s: {parse_rate:,.0f}")
        print(f"  Total records: {parse_records:,}")
        print()
    print("=" * 70)
    print("NOTE")
    print("=" * 70)
    print()
    print("Compare these numbers to the apple-to-apple benchmark:")
    print("  - Apple-to-apple: Pure JSON parsing (no indexing)")
    print("  - Full-featured: JSON parsing + indexing + hash map building")
    print()
    print("The difference shows the overhead of our additional features.")
if __name__ == "__main__":
    main()
