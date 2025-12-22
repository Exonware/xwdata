"""Benchmark parallel vs single-threaded index building with auto-tuning."""

from __future__ import annotations

import multiprocessing as mp
import sys
import time
from pathlib import Path

# Add paths for local imports
_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import build_index


def benchmark_index_building(
    db_path: Path,
    use_parallel: bool,
    num_workers: int | None = None,
    chunk_size_mb: int = 100,
) -> dict:
    """Benchmark index building and return results."""
    started = time.perf_counter()
    
    if use_parallel:
        from build_index_parallel import build_index_parallel
        doc = build_index_parallel(
            db_path,
            num_workers=num_workers,
            chunk_size_mb=chunk_size_mb,
            fallback_on_error=True,
        )
    else:
        doc = build_index.build_index(db_path, use_parallel=False)
    
    elapsed = time.perf_counter() - started
    keys_count = len(doc.get("by_key", {}))
    
    return {
        "parallel": use_parallel,
        "workers": num_workers,
        "chunk_size_mb": chunk_size_mb,
        "time": elapsed,
        "keys": keys_count,
        "keys_per_sec": keys_count / elapsed if elapsed > 0 else 0,
    }


def auto_tune_parallel(db_path: Path) -> dict:
    """Auto-tune parallel index building parameters."""
    print("=" * 70)
    print("AUTO-TUNING PARALLEL INDEX BUILDING")
    print("=" * 70)
    print()
    
    # Get file size
    file_size_mb = db_path.stat().st_size / (1024 * 1024)
    print(f"File size: {file_size_mb:.2f} MB")
    print(f"CPU cores: {mp.cpu_count()}")
    print()
    
    # Benchmark single-threaded first (baseline)
    print("1. Benchmarking single-threaded (baseline)...")
    baseline = benchmark_index_building(db_path, use_parallel=False)
    print(f"   Time: {baseline['time']:.2f}s, Keys: {baseline['keys']:,}, Rate: {baseline['keys_per_sec']:,.0f} keys/s")
    print()
    
    # Test different worker counts
    cpu_count = mp.cpu_count()
    worker_counts = [2, 4, 8, cpu_count // 2, cpu_count]
    worker_counts = [w for w in worker_counts if w <= cpu_count and w > 0]
    worker_counts = sorted(set(worker_counts))
    
    print("2. Testing different worker counts...")
    results = []
    
    for workers in worker_counts:
        print(f"   Testing {workers} workers...", end=" ", flush=True)
        result = benchmark_index_building(
            db_path,
            use_parallel=True,
            num_workers=workers,
            chunk_size_mb=100,
        )
        speedup = baseline['time'] / result['time'] if result['time'] > 0 else 0
        result['speedup'] = speedup
        results.append(result)
        print(f"Time: {result['time']:.2f}s ({speedup:.2f}x speedup)")
    
    print()
    
    # Find best configuration
    best = max(results, key=lambda r: r['speedup'])
    
    print("3. Best configuration:")
    print(f"   Workers: {best['workers']}")
    print(f"   Time: {best['time']:.2f}s")
    print(f"   Speedup: {best['speedup']:.2f}x faster than single-threaded")
    print(f"   Rate: {best['keys_per_sec']:,.0f} keys/s")
    print()
    
    # Test different chunk sizes with best worker count
    print("4. Testing different chunk sizes (with best worker count)...")
    chunk_sizes = [50, 100, 200, 500]
    chunk_results = []
    
    for chunk_mb in chunk_sizes:
        print(f"   Testing chunk size {chunk_mb}MB...", end=" ", flush=True)
        result = benchmark_index_building(
            db_path,
            use_parallel=True,
            num_workers=best['workers'],
            chunk_size_mb=chunk_mb,
        )
        speedup = baseline['time'] / result['time'] if result['time'] > 0 else 0
        result['speedup'] = speedup
        chunk_results.append(result)
        print(f"Time: {result['time']:.2f}s ({speedup:.2f}x speedup)")
    
    print()
    
    # Find best chunk size
    best_chunk = max(chunk_results, key=lambda r: r['speedup'])
    
    print("5. Optimal configuration:")
    print(f"   Workers: {best_chunk['workers']}")
    print(f"   Chunk size: {best_chunk['chunk_size_mb']}MB")
    print(f"   Time: {best_chunk['time']:.2f}s")
    print(f"   Speedup: {best_chunk['speedup']:.2f}x faster than single-threaded")
    print(f"   Rate: {best_chunk['keys_per_sec']:,.0f} keys/s")
    print()
    
    return {
        "baseline": baseline,
        "best": best_chunk,
        "all_results": results + chunk_results,
    }


def main() -> int:
    db_path = build_index.default_db_path()
    
    if not db_path.exists():
        print(f"Error: Database file not found: {db_path}")
        return 1
    
    try:
        results = auto_tune_parallel(db_path)
        
        print("=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print()
        print(f"Single-threaded: {results['baseline']['time']:.2f}s")
        print(f"Parallel (optimized): {results['best']['time']:.2f}s")
        print(f"Improvement: {results['best']['speedup']:.2f}x faster")
        print()
        print(f"Recommended settings:")
        print(f"  --parallel --workers {results['best']['workers']}")
        print(f"  (chunk_size_mb={results['best']['chunk_size_mb']} is hardcoded in build_index_parallel.py)")
        print()
        
        return 0
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
