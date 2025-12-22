"""Comprehensive benchmark showing all performance improvements."""

from __future__ import annotations

import sys
import time
from pathlib import Path

# Add paths for local imports
_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import build_index
import db_io


def _human_time(seconds: float) -> str:
    """Format time as human-readable string."""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        mins = int(seconds // 60)
        secs = seconds % 60
        return f"{mins}m {secs:.1f}s"


def benchmark_index_building():
    """Benchmark index building: single-threaded vs parallel."""
    print("=" * 70)
    print("INDEX BUILDING: Single-Threaded vs Parallel")
    print("=" * 70)
    print()
    
    db_path = build_index.default_db_path()
    file_size_mb = db_path.stat().st_size / (1024 * 1024)
    print(f"File: {db_path.name} ({file_size_mb:.2f} MB)")
    print()
    
    # Single-threaded
    print("1. Single-threaded (baseline)...")
    started = time.perf_counter()
    doc_single = build_index.build_index(db_path, use_parallel=False)
    elapsed_single = time.perf_counter() - started
    keys_single = len(doc_single.get("by_key", {}))
    print(f"   Time: {_human_time(elapsed_single)}")
    print(f"   Keys: {keys_single:,}")
    print(f"   Rate: {keys_single/elapsed_single:,.0f} keys/s")
    print()
    
    # Parallel (optimized)
    print("2. Parallel (32 workers, 100MB chunks)...")
    started = time.perf_counter()
    doc_parallel = build_index.build_index(db_path, use_parallel=True, num_workers=32)
    elapsed_parallel = time.perf_counter() - started
    keys_parallel = len(doc_parallel.get("by_key", {}))
    print(f"   Time: {_human_time(elapsed_parallel)}")
    print(f"   Keys: {keys_parallel:,}")
    print(f"   Rate: {keys_parallel/elapsed_parallel:,.0f} keys/s")
    print()
    
    # Comparison
    speedup = elapsed_single / elapsed_parallel if elapsed_parallel > 0 else 0
    print("=" * 70)
    print("COMPARISON")
    print("=" * 70)
    print(f"Single-threaded: {_human_time(elapsed_single)}")
    print(f"Parallel:        {_human_time(elapsed_parallel)}")
    print(f"Speedup:         {speedup:.2f}x faster")
    print()
    
    return {
        "single": {"time": elapsed_single, "keys": keys_single},
        "parallel": {"time": elapsed_parallel, "keys": keys_parallel},
        "speedup": speedup,
    }


def benchmark_atomic_updates():
    """Benchmark atomic updates: full rewrite vs append-only log."""
    print("=" * 70)
    print("ATOMIC UPDATES: Full Rewrite vs Append-Only Log")
    print("=" * 70)
    print()
    
    db_path = db_io.default_db_path()
    file_size_mb = db_path.stat().st_size / (1024 * 1024)
    print(f"File: {db_path.name} ({file_size_mb:.2f} MB)")
    print()
    
    def updater(rec: dict) -> dict:
        rec = rec.copy()
        rec["views"] = rec.get("views", 0) + 1
        return rec
    
    n_updates = 20
    
    # Full rewrite
    print(f"1. Full rewrite (baseline, {n_updates} updates)...")
    started = time.perf_counter()
    total_full = 0
    for i in range(n_updates):
        updated = db_io.atomic_update_record_by_key(
            db_path,
            "Message",
            "msg_0",
            updater=updater,
            use_append_log=False,
        )
        total_full += updated
    elapsed_full = time.perf_counter() - started
    print(f"   Time: {_human_time(elapsed_full)}")
    print(f"   Updates: {total_full}")
    print(f"   Rate: {total_full/elapsed_full:,.0f} updates/s")
    if file_size_mb > 0:
        effective_mbps = (file_size_mb * total_full) / elapsed_full
        print(f"   Effective: {effective_mbps:.2f} MB/s")
    print()
    
    # Append-only log
    print(f"2. Append-only log ({n_updates} updates)...")
    # Clear any existing log first
    log_path = db_path.with_suffix(db_path.suffix + '.log')
    if log_path.exists():
        log_path.unlink()
    
    started = time.perf_counter()
    total_append = 0
    for i in range(n_updates):
        updated = db_io.atomic_update_record_by_key(
            db_path,
            "Message",
            "msg_0",
            updater=updater,
            use_append_log=True,
        )
        total_append += updated
    elapsed_append = time.perf_counter() - started
    print(f"   Time: {_human_time(elapsed_append)}")
    print(f"   Updates: {total_append}")
    print(f"   Rate: {total_append/elapsed_append:,.0f} updates/s")
    print()
    
    # Comparison
    speedup = elapsed_full / elapsed_append if elapsed_append > 0 else 0
    print("=" * 70)
    print("COMPARISON")
    print("=" * 70)
    print(f"Full rewrite:    {_human_time(elapsed_full)} ({total_full/elapsed_full:,.0f} updates/s)")
    print(f"Append-only log: {_human_time(elapsed_append)} ({total_append/elapsed_append:,.0f} updates/s)")
    print(f"Speedup:         {speedup:.2f}x faster")
    print()
    
    return {
        "full_rewrite": {"time": elapsed_full, "updates": total_full},
        "append_log": {"time": elapsed_append, "updates": total_append},
        "speedup": speedup,
    }


def main() -> int:
    """Run all benchmarks."""
    print()
    print("=" * 70)
    print("COMPREHENSIVE PERFORMANCE BENCHMARK")
    print("=" * 70)
    print()
    print("This benchmark shows performance improvements from:")
    print("  1. Parallel index building (multi-core)")
    print("  2. Append-only log for atomic updates")
    print()
    
    results = {}
    
    try:
        # Index building
        results["index"] = benchmark_index_building()
        
        # Atomic updates
        results["atomic"] = benchmark_atomic_updates()
        
        # Final summary
        print()
        print("=" * 70)
        print("FINAL SUMMARY")
        print("=" * 70)
        print()
        print("Index Building:")
        print(f"  Single-threaded: {_human_time(results['index']['single']['time'])}")
        print(f"  Parallel:        {_human_time(results['index']['parallel']['time'])}")
        print(f"  Improvement:     {results['index']['speedup']:.2f}x faster")
        print()
        print("Atomic Updates:")
        print(f"  Full rewrite:    {_human_time(results['atomic']['full_rewrite']['time'])}")
        print(f"  Append-only log: {_human_time(results['atomic']['append_log']['time'])}")
        print(f"  Improvement:     {results['atomic']['speedup']:.2f}x faster")
        print()
        
        return 0
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
