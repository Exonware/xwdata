"""Test example code parallel performance to verify 11.73s benchmark."""

from __future__ import annotations

import sys
import time
from pathlib import Path

# Add paths for local imports
_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from build_index_parallel import build_index_parallel


def test_example_parallel():
    """Test example code parallel performance."""
    db_path = _THIS_DIR.parent / "data" / "chatdb.jsonl"
    db_path = db_path.resolve()
    
    if not db_path.exists():
        print(f"ERROR: Database file not found: {db_path}")
        return
    
    file_size_mb = db_path.stat().st_size / 1_048_576
    print("=" * 70)
    print("TESTING EXAMPLE CODE PARALLEL PERFORMANCE")
    print("=" * 70)
    print(f"File: {db_path.name} ({file_size_mb:.2f} MB)")
    print(f"Target: 11.73s, 1,503,168 lines/s")
    print()
    
    # Run 3 times to check consistency
    times = []
    for run in range(1, 4):
        print(f"Run {run}/3...", end=" ", flush=True)
        started = time.perf_counter()
        doc = build_index_parallel(
            db_path,
            num_workers=32,
            chunk_size_mb=100,
            fallback_on_error=True,
        )
        elapsed = time.perf_counter() - started
        times.append(elapsed)
        
        keys_count = len(doc.get("by_key", {}))
        rate = keys_count / elapsed if elapsed > 0 else 0
        print(f"Time: {elapsed:.2f}s | Rate: {rate:,.0f} keys/s")
    
    print()
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"Times: {[f'{t:.2f}s' for t in times]}")
    print(f"Average: {avg_time:.2f}s")
    print(f"Min: {min_time:.2f}s")
    print(f"Max: {max_time:.2f}s")
    print(f"Range: {max_time - min_time:.2f}s")
    print()
    
    # Compare to target
    target_time = 11.73
    print(f"Target: {target_time:.2f}s")
    if avg_time <= target_time:
        print(f"[OK] Average is {((target_time - avg_time) / target_time * 100):.1f}% faster than target")
    else:
        print(f"[SLOW] Average is {((avg_time - target_time) / target_time * 100):.1f}% slower than target")
    
    # Check if consistent
    if max_time - min_time < 0.5:
        print("[CONSISTENT] Times are consistent (range < 0.5s)")
    else:
        print("[VARIABLE] Times vary significantly (range >= 0.5s)")


if __name__ == "__main__":
    test_example_parallel()
