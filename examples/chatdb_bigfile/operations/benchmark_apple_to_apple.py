"""Apple-to-apple comparison: Both codebases with same settings (with/without line_offsets)."""

from __future__ import annotations

import sys
import time
from pathlib import Path

# Add paths for imports
_THIS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _THIS_DIR.parents[3]
if str(_REPO_ROOT / "xwsystem" / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "xwsystem" / "src"))

if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from exonware.xwsystem.io.data_operations import NDJSONDataOperations
from build_index_parallel import build_index_parallel


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


def benchmark_apple_to_apple():
    """Compare both codebases with identical settings."""
    print("=" * 80)
    print("APPLE-TO-APPLE COMPARISON")
    print("=" * 80)
    print()
    
    # Get database path
    db_path = _THIS_DIR.parent / "data" / "chatdb.jsonl"
    db_path = db_path.resolve()
    if not db_path.exists():
        print(f"ERROR: Database file not found: {db_path}")
        return None
    
    file_size_mb = db_path.stat().st_size / 1_048_576
    print(f"File: {db_path.name} ({file_size_mb:.2f} MB)")
    print()
    
    ops = NDJSONDataOperations()
    
    # Test configurations
    configs = [
        (False, "Without line_offsets (id_index only)"),
        (True, "With line_offsets (full index)"),
    ]
    
    results = []
    
    for build_offsets, description in configs:
        print(f"Testing: {description}")
        print("-" * 80)
        
        # Example code
        print("  Example code...", end=" ", flush=True)
        try:
            started = time.perf_counter()
            doc_example = build_index_parallel(
                db_path,
                num_workers=32,
                chunk_size_mb=100,
                build_line_offsets=build_offsets,
            )
            elapsed_example = time.perf_counter() - started
            keys_example = len(doc_example.get("by_key", {}))
            rate_example = keys_example / elapsed_example if elapsed_example > 0 else 0
            print(f"Time: {_human_time(elapsed_example)} | Rate: {rate_example:,.0f} keys/s")
        except Exception as e:
            print(f"FAILED: {e}")
            elapsed_example = None
            rate_example = 0
        
        # Main codebase
        print("  Main codebase...", end=" ", flush=True)
        try:
            started = time.perf_counter()
            index_main = ops.build_index(
                db_path,
                id_field="id",
                use_parallel=True,
                num_workers=32,
                chunk_size_mb=100,
                build_line_offsets=build_offsets,
            )
            elapsed_main = time.perf_counter() - started
            keys_main = len(index_main.id_index) if index_main.id_index else len(index_main.line_offsets) if index_main.line_offsets else 0
            rate_main = keys_main / elapsed_main if elapsed_main > 0 else 0
            print(f"Time: {_human_time(elapsed_main)} | Rate: {rate_main:,.0f} keys/s")
        except Exception as e:
            print(f"FAILED: {e}")
            elapsed_main = None
            rate_main = 0
        
        if elapsed_example and elapsed_main:
            diff_time = elapsed_main - elapsed_example
            diff_pct = (diff_time / elapsed_example) * 100
            diff_rate = rate_main - rate_example
            diff_rate_pct = (diff_rate / rate_example) * 100
            
            print(f"  Difference: {diff_time:+.2f}s ({diff_pct:+.1f}%) | Rate: {diff_rate:+,.0f} ({diff_rate_pct:+.1f}%)")
            
            results.append({
                "config": description,
                "example_time": elapsed_example,
                "main_time": elapsed_main,
                "example_rate": rate_example,
                "main_rate": rate_main,
                "diff_time": diff_time,
                "diff_pct": diff_pct,
            })
        
        print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print(f"{'Config':<50} {'Example':<15} {'Main':<15} {'Difference':<15}")
    print("-" * 80)
    
    for r in results:
        example_str = _human_time(r["example_time"])
        main_str = _human_time(r["main_time"])
        diff_str = f"{r['diff_time']:+.2f}s ({r['diff_pct']:+.1f}%)"
        print(f"{r['config']:<50} {example_str:<15} {main_str:<15} {diff_str:<15}")
    
    return results


if __name__ == "__main__":
    benchmark_apple_to_apple()
