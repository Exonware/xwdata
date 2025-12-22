"""Benchmark using main codebase APIs (xwsystem.io.data_operations)."""

from __future__ import annotations

import sys
import time
from pathlib import Path

# Add paths for imports
_THIS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _THIS_DIR.parents[3]
if str(_REPO_ROOT / "xwsystem" / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "xwsystem" / "src"))

from exonware.xwsystem.io.data_operations import NDJSONDataOperations


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
    """Benchmark index building: single-threaded vs parallel using main codebase."""
    print("=" * 70)
    print("INDEX BUILDING: Main Codebase (xwsystem.io.data_operations)")
    print("=" * 70)
    print()
    
    # Get database path (same as build_index.py)
    # _THIS_DIR is operations/, so parents[1] is chatdb_bigfile/
    db_path = _THIS_DIR.parent / "data" / "chatdb.jsonl"
    db_path = db_path.resolve()
    if not db_path.exists():
        print(f"ERROR: Database file not found: {db_path}")
        return None
    
    file_size_mb = db_path.stat().st_size / (1024 * 1024)
    print(f"File: {db_path.name} ({file_size_mb:.2f} MB)")
    print()
    
    ops = NDJSONDataOperations()
    
    # Single-threaded
    print("1. Single-threaded (baseline)...")
    started = time.perf_counter()
    index_single = ops.build_index(
        db_path,
        id_field="id",  # Use "id" field for indexing
        use_parallel=False,
    )
    elapsed_single = time.perf_counter() - started
    total_lines_single = len(index_single.line_offsets)
    keys_single = len(index_single.id_index) if index_single.id_index else total_lines_single
    print(f"   Time: {_human_time(elapsed_single)}")
    print(f"   Total lines: {total_lines_single:,}")
    print(f"   Indexed keys: {keys_single:,}")
    print(f"   Rate: {total_lines_single/elapsed_single:,.0f} lines/s")
    print()
    
    # Parallel (optimized - auto workers based on file size)
    print("2. Parallel (auto workers, 100MB chunks)...")
    started = time.perf_counter()
    index_parallel = ops.build_index(
        db_path,
        id_field="id",  # Use "id" field, not "@type"
        use_parallel=True,
        # num_workers=None,  # Let it auto-calculate (1 worker per 10MB, max 128)
        chunk_size_mb=100,
    )
    elapsed_parallel = time.perf_counter() - started
    keys_parallel = len(index_parallel.id_index) if index_parallel.id_index else len(index_parallel.line_offsets)
    total_lines_parallel = len(index_parallel.line_offsets)
    print(f"   Time: {_human_time(elapsed_parallel)}")
    print(f"   Total lines: {total_lines_parallel:,}")
    print(f"   Indexed keys: {keys_parallel:,}")
    print(f"   Rate: {total_lines_parallel/elapsed_parallel:,.0f} lines/s")
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
    """Benchmark atomic updates using main codebase."""
    print("=" * 70)
    print("ATOMIC UPDATES: Main Codebase (JsonLinesSerializer)")
    print("=" * 70)
    print()
    
    from exonware.xwsystem.io.serialization.formats.text.jsonlines import JsonLinesSerializer
    
    # Get database path (same as build_index.py)
    # _THIS_DIR is operations/, so parent is chatdb_bigfile/
    db_path = _THIS_DIR.parent / "data" / "chatdb.jsonl"
    db_path = db_path.resolve()
    if not db_path.exists():
        print(f"ERROR: Database file not found: {db_path}")
        return None
    
    file_size_mb = db_path.stat().st_size / (1024 * 1024)
    print(f"File: {db_path.name} ({file_size_mb:.2f} MB)")
    print()
    
    serializer = JsonLinesSerializer()
    
    # Test match function (find first Message record)
    def match_msg(rec: dict) -> bool:
        return isinstance(rec, dict) and rec.get("@type") == "Message" and rec.get("id") == "msg_0"
    
    def updater(rec: dict) -> dict:
        rec = rec.copy()
        rec["views"] = rec.get("views", 0) + 1
        return rec
    
    # Full rewrite (baseline)
    print("1. Full rewrite (baseline, use_append_log=False)...")
    started = time.perf_counter()
    updated_full = serializer.stream_update_record(
        db_path,
        match=match_msg,
        updater=updater,
        atomic=True,
        use_append_log=False,
    )
    elapsed_full = time.perf_counter() - started
    print(f"   Time: {_human_time(elapsed_full)}")
    print(f"   Updated: {updated_full} records")
    print()
    
    # Append-only log (optimized)
    print("2. Append-only log (use_append_log=True)...")
    started = time.perf_counter()
    updated_append = serializer.stream_update_record(
        db_path,
        match=match_msg,
        updater=updater,
        atomic=True,
        use_append_log=True,
    )
    elapsed_append = time.perf_counter() - started
    print(f"   Time: {_human_time(elapsed_append)}")
    print(f"   Updated: {updated_append} records")
    print()
    
    # Comparison
    if elapsed_append > 0 and elapsed_full > 0:
        speedup = elapsed_full / elapsed_append
        print("=" * 70)
        print("COMPARISON")
        print("=" * 70)
        print(f"Full rewrite:    {_human_time(elapsed_full)}")
        print(f"Append-only log: {_human_time(elapsed_append)}")
        print(f"Speedup:         {speedup:.2f}x {'faster' if speedup > 1 else 'slower'}")
        print()
    
    return {
        "full_rewrite": {"time": elapsed_full, "updated": updated_full},
        "append_log": {"time": elapsed_append, "updated": updated_append},
    }


def main():
    """Run all benchmarks."""
    print("BENCHMARKING MAIN CODEBASE PERFORMANCE")
    print("=" * 70)
    print()
    
    # Index building
    index_results = benchmark_index_building()
    
    print()
    print()
    
    # Atomic updates
    atomic_results = benchmark_atomic_updates()
    
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    if index_results:
        print(f"Index Building Speedup: {index_results['speedup']:.2f}x")
    if atomic_results:
        if atomic_results['append_log']['time'] > 0:
            atomic_speedup = atomic_results['full_rewrite']['time'] / atomic_results['append_log']['time']
            print(f"Atomic Updates Speedup: {atomic_speedup:.2f}x")
    print()


if __name__ == "__main__":
    main()
