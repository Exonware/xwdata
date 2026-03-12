"""Compare encoder_1.py vs encoder.py performance.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
"""

from __future__ import annotations
import sys
import time
import tempfile
from pathlib import Path
from typing import Any
# Add paths
_OPS_DIR = Path(__file__).resolve().parent
if str(_OPS_DIR) not in sys.path:
    sys.path.insert(0, str(_OPS_DIR))
_xwsystem_src = Path(__file__).resolve().parents[4] / "xwsystem" / "src"
if str(_xwsystem_src) not in sys.path:
    sys.path.insert(0, str(_xwsystem_src))
_xwjson_src = Path(__file__).resolve().parents[4] / "xwjson" / "src"
if str(_xwjson_src) not in sys.path:
    sys.path.insert(0, str(_xwjson_src))


def create_test_data(num_records: int = 1000) -> dict[str, Any]:
    """Create test data structure."""
    records = []
    for i in range(num_records):
        records.append({
            "@type": "Message",
            "id": f"msg_{i:08d}",
            "ts": 1000000000 + i,
            "payload": {
                "text": f"Message {i} with some content",
                "user_id": f"user_{i % 100:06d}",
                "views": i * 10
            }
        })
    return {"records": records}


def benchmark_encode(data: dict[str, Any], encoder, num_iterations: int = 100) -> dict[str, Any]:
    """Benchmark encoding performance."""
    print(f"  Encoding {num_iterations:,} times...")
    start_time = time.perf_counter()
    for i in range(num_iterations):
        encoded = encoder.encode(
            data=data["records"],
            metadata=None,
            format_code=0x00,
            flags=0,
            index=None,
            file_path=None,
            create_index_file=False
        )
    elapsed = time.perf_counter() - start_time
    ops_per_sec = num_iterations / elapsed if elapsed > 0 else 0
    # Calculate data rate (approximate)
    if num_iterations > 0:
        sample_size = len(encoded)
        total_bytes = sample_size * num_iterations
        mb_per_sec = (total_bytes / (1024 * 1024)) / elapsed if elapsed > 0 else 0
    else:
        mb_per_sec = 0
    print(f"    Time: {elapsed:.3f}s")
    print(f"    Throughput: {ops_per_sec:,.0f} encodes/s")
    print(f"    Data rate: {mb_per_sec:.2f} MB/s")
    return {
        "time": elapsed,
        "ops_per_sec": ops_per_sec,
        "mb_per_sec": mb_per_sec,
        "encoded_size": len(encoded)
    }


def benchmark_encode_with_file(data: dict[str, Any], encoder, num_iterations: int = 50) -> dict[str, Any]:
    """Benchmark encoding with file path (dual-file format)."""
    print(f"  Encoding with file path {num_iterations:,} times...")
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        start_time = time.perf_counter()
        total_bytes = 0
        for i in range(num_iterations):
            file_path = temp_path / f"test_{i}.xwjson"
            encoded = encoder.encode(
                data=data["records"],
                metadata=None,
                format_code=0x00,
                flags=0,
                index=None,
                file_path=file_path,
                create_index_file=True  # Force dual-file format
            )
            # Check actual file sizes
            data_file = temp_path / f"test_{i}.data.xwjson"
            if data_file.exists():
                total_bytes += data_file.stat().st_size
        elapsed = time.perf_counter() - start_time
        ops_per_sec = num_iterations / elapsed if elapsed > 0 else 0
        mb_per_sec = (total_bytes / (1024 * 1024)) / elapsed if elapsed > 0 else 0
        print(f"    Time: {elapsed:.3f}s")
        print(f"    Throughput: {ops_per_sec:,.0f} encodes/s")
        print(f"    Data rate: {mb_per_sec:.2f} MB/s")
        return {
            "time": elapsed,
            "ops_per_sec": ops_per_sec,
            "mb_per_sec": mb_per_sec
        }


def main() -> int:
    """Main entry point."""
    print("=" * 70)
    print("Encoder Performance Comparison: encoder.py vs encoder_1.py")
    print("=" * 70)
    print()
    # Create test data
    print("Creating test data...")
    test_data = create_test_data(num_records=1000)
    print(f"  Records: {len(test_data['records']):,}")
    print()
    # Import both encoders
    try:
        # Backup original encoder
        import exonware.xwjson.formats.binary.xwjson.encoder as encoder_module
        from exonware.xwjson.formats.binary.xwjson.encoder import XWJSONEncoder
        # Try to import encoder_1
        import importlib.util
        encoder_1_path = Path(__file__).resolve().parents[4] / "xwjson" / "src" / "exonware" / "xwjson" / "formats" / "binary" / "xwjson" / "encoder_1.py"
        if not encoder_1_path.exists():
            print(f"ERROR: encoder_1.py not found at {encoder_1_path}")
            return 1
        spec = importlib.util.spec_from_file_location("encoder_1", encoder_1_path)
        encoder_1_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(encoder_1_module)
        XWJSONEncoder1 = encoder_1_module.XWJSONEncoder
    except Exception as e:
        print(f"ERROR: Failed to import encoders: {e}")
        import traceback
        traceback.print_exc()
        return 1
    # Create encoder instances
    encoder_original = XWJSONEncoder()
    encoder_new = XWJSONEncoder1()
    print("=" * 70)
    print("1. ENCODING PERFORMANCE (No file path, single-file format)")
    print("=" * 70)
    print("\nOriginal encoder.py:")
    result_original = benchmark_encode(test_data, encoder_original, num_iterations=100)
    print("\nNew encoder_1.py:")
    result_new = benchmark_encode(test_data, encoder_new, num_iterations=100)
    improvement = result_new["ops_per_sec"] / result_original["ops_per_sec"] if result_original["ops_per_sec"] > 0 else 0
    print(f"\nImprovement: {improvement:.2f}x ({'faster' if improvement > 1 else 'slower'})")
    print("\n" + "=" * 70)
    print("2. ENCODING PERFORMANCE (With file path, dual-file format)")
    print("=" * 70)
    print("\nOriginal encoder.py:")
    result_original_file = benchmark_encode_with_file(test_data, encoder_original, num_iterations=50)
    print("\nNew encoder_1.py:")
    result_new_file = benchmark_encode_with_file(test_data, encoder_new, num_iterations=50)
    improvement_file = result_new_file["ops_per_sec"] / result_original_file["ops_per_sec"] if result_original_file["ops_per_sec"] > 0 else 0
    print(f"\nImprovement: {improvement_file:.2f}x ({'faster' if improvement_file > 1 else 'slower'})")
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Single-file encoding: {improvement:.2f}x {'faster' if improvement > 1 else 'slower'}")
    print(f"Dual-file encoding: {improvement_file:.2f}x {'faster' if improvement_file > 1 else 'slower'}")
    if improvement > 1.05 or improvement_file > 1.05:
        print("\n[OK] New encoder_1.py is faster!")
    elif improvement < 0.95 or improvement_file < 0.95:
        print("\n[WARN] New encoder_1.py is slower - may need optimization")
    else:
        print("\n[INFO] Performance is similar")
    return 0
if __name__ == "__main__":
    sys.exit(main())
