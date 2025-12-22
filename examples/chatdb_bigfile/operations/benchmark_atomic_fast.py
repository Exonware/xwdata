"""Fast atomic update benchmark (uses smaller test file or fewer updates)."""

from __future__ import annotations

import sys
import time
from pathlib import Path

# Add paths for local imports
_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import db_io


def benchmark_atomic_updates_fast(n_updates: int = 5):
    """Benchmark atomic updates with fewer iterations."""
    print("=" * 70)
    print("ATOMIC UPDATE BENCHMARK (Fast - Limited Updates)")
    print("=" * 70)
    print()
    
    db_path = db_io.default_db_path()
    file_size_mb = db_path.stat().st_size / (1024 * 1024)
    print(f"File: {db_path.name} ({file_size_mb:.2f} MB)")
    print(f"Updates: {n_updates}")
    print()
    
    def updater(rec: dict) -> dict:
        rec = rec.copy()
        rec["views"] = rec.get("views", 0) + 1
        return rec
    
    # Full rewrite
    print("1. Full rewrite (baseline)...")
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
    print(f"   Time: {elapsed_full:.2f}s")
    print(f"   Updates: {total_full}")
    print(f"   Rate: {total_full/elapsed_full:,.0f} updates/s")
    if file_size_mb > 0:
        effective_mbps = (file_size_mb * total_full) / elapsed_full
        print(f"   Effective: {effective_mbps:.2f} MB/s")
    print()
    
    # Append-only log
    print("2. Append-only log...")
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
    print(f"   Time: {elapsed_append:.2f}s")
    print(f"   Updates: {total_append}")
    print(f"   Rate: {total_append/elapsed_append:,.0f} updates/s")
    print()
    
    # Comparison
    if elapsed_append > 0 and elapsed_full > 0:
        speedup = elapsed_full / elapsed_append
        print("=" * 70)
        print("COMPARISON")
        print("=" * 70)
        print(f"Full rewrite:    {elapsed_full:.2f}s ({total_full/elapsed_full:,.0f} updates/s)")
        print(f"Append-only log: {elapsed_append:.2f}s ({total_append/elapsed_append:,.0f} updates/s)")
        print(f"Speedup:         {speedup:.2f}x {'faster' if speedup > 1 else 'slower'}")
        print()
        
        return {
            "full_rewrite": {"time": elapsed_full, "updates": total_full, "updates_per_sec": total_full/elapsed_full},
            "append_log": {"time": elapsed_append, "updates": total_append, "updates_per_sec": total_append/elapsed_append},
            "speedup": speedup,
        }
    
    return None


if __name__ == "__main__":
    result = benchmark_atomic_updates_fast(n_updates=3)  # Just 3 updates for speed
    if result:
        print("Summary:")
        print(f"  Full rewrite: {result['full_rewrite']['time']:.2f}s")
        print(f"  Append log:   {result['append_log']['time']:.2f}s")
        print(f"  Speedup:      {result['speedup']:.2f}x")
