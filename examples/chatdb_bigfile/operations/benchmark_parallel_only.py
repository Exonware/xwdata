"""Benchmark parallel index building with different configurations.
Focus: Find the optimal worker count and chunk size for maximum lines/second.
"""

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


def benchmark_parallel_configs():
    """Benchmark different parallel configurations to find optimal settings."""
    print("=" * 80)
    print("PARALLEL INDEX BUILDING: Configuration Optimization")
    print("=" * 80)
    print()
    # Get database path
    db_path = _THIS_DIR.parent / "data" / "chatdb.jsonl"
    db_path = db_path.resolve()
    if not db_path.exists():
        print(f"ERROR: Database file not found: {db_path}")
        return None
    file_size_mb = db_path.stat().st_size / 1_048_576  # 1024 * 1024
    print(f"File: {db_path.name} ({file_size_mb:.2f} MB)")
    print(f"Target: Beat example code (11.73s, 1,503,168 lines/s)")
    print()
    ops = NDJSONDataOperations()
    # Test configurations
    configs = [
        # (num_workers, chunk_size_mb, description)
        (16, 100, "16 workers, 100MB chunks"),
        (32, 100, "32 workers, 100MB chunks"),
        (32, 50, "32 workers, 50MB chunks"),
        (32, 200, "32 workers, 200MB chunks"),
        (48, 50, "48 workers, 50MB chunks"),
        (48, 100, "48 workers, 100MB chunks"),
        (61, 50, "61 workers (max), 50MB chunks"),
        (61, 100, "61 workers (max), 100MB chunks"),
        (61, 200, "61 workers (max), 200MB chunks"),
        # Auto-calculated (1 worker per 10MB)
        (None, 50, "Auto workers (~513), 50MB chunks"),
        (None, 100, "Auto workers (~513), 100MB chunks"),
    ]
    results = []
    for num_workers, chunk_size_mb, description in configs:
        print(f"Testing: {description}...")
        try:
            started = time.perf_counter()
            index = ops.build_index(
                db_path,
                id_field="id",
                use_parallel=True,
                num_workers=num_workers,
                chunk_size_mb=chunk_size_mb,
            )
            elapsed = time.perf_counter() - started
            total_lines = len(index.line_offsets)
            rate = total_lines / elapsed if elapsed > 0 else 0
            results.append({
                "config": description,
                "workers": num_workers or "auto",
                "chunk_mb": chunk_size_mb,
                "time": elapsed,
                "rate": rate,
            })
            status = "[OK]" if elapsed <= 11.73 else "[SLOW]"
            print(f"  {status} Time: {_human_time(elapsed)} | Rate: {rate:,.0f} lines/s")
            print()
        except Exception as e:
            print(f"  [FAILED] {e}")
            print()
    # Summary
    print("=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    print()
    # Sort by rate (highest first)
    results.sort(key=lambda x: x["rate"], reverse=True)
    print(f"{'Config':<40} {'Workers':<10} {'Chunk MB':<10} {'Time':<12} {'Rate (lines/s)':<15}")
    print("-" * 80)
    for r in results:
        workers_str = str(r["workers"])
        chunk_str = str(r["chunk_mb"])
        time_str = _human_time(r["time"])
        rate_str = f"{r['rate']:,.0f}"
        # Highlight best
        marker = "[BEST]" if r == results[0] else "       "
        print(f"{marker} {r['config']:<38} {workers_str:<10} {chunk_str:<10} {time_str:<12} {rate_str:<15}")
    print()
    print(f"Best config: {results[0]['config']}")
    print(f"Best time: {_human_time(results[0]['time'])}")
    print(f"Best rate: {results[0]['rate']:,.0f} lines/s")
    # Compare to target
    target_time = 11.73
    target_rate = 1_503_168
    best_time = results[0]['time']
    best_rate = results[0]['rate']
    print()
    print("=" * 80)
    print("VS TARGET (Example Code)")
    print("=" * 80)
    print(f"Target time:  {_human_time(target_time)}")
    print(f"Best time:    {_human_time(best_time)}")
    if best_time <= target_time:
        print(f"[BEAT] Faster by {((target_time - best_time) / target_time * 100):.1f}%")
    else:
        print(f"[SLOW] Slower by {((best_time - target_time) / target_time * 100):.1f}%")
    print()
    print(f"Target rate:  {target_rate:,.0f} lines/s")
    print(f"Best rate:    {best_rate:,.0f} lines/s")
    if best_rate >= target_rate:
        print(f"[BEAT] Faster by {((best_rate - target_rate) / target_rate * 100):.1f}%")
    else:
        print(f"[SLOW] Slower by {((target_rate - best_rate) / target_rate * 100):.1f}%")
    return results
if __name__ == "__main__":
    benchmark_parallel_configs()
