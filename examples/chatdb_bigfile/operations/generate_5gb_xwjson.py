"""Generate a 5GB XWJSON file for performance testing.
Generates a large XWJSON file with synthetic data for testing index caching performance.
Run (from repo root):
  python xwdata/examples/chatdb_bigfile/operations/generate_5gb_xwjson.py --output ../data/chatdb_5gb.xwjson --size-gb 5.0
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
"""

from __future__ import annotations
import argparse
import sys
import time
from pathlib import Path
from typing import Any
# Add xwjson to path
try:
    from exonware.xwjson import XWJSONSerializer
    XWJSON_AVAILABLE = True
except ImportError:
    XWJSON_AVAILABLE = False
    print("ERROR: xwjson not available. Install with: pip install exonware-xwjson")
    sys.exit(1)
    # Import progress indicator
try:
    from progress_indicator import ProgressIndicator
    HAS_PROGRESS = True
except ImportError:
    # Fallback progress indicator
    class ProgressIndicator:
        def __init__(self, message: str, total: int):
            self.message = message
            self.total = total
            self.current = 0
            self.start_time = None
        def start(self):
            self.start_time = time.time()
            print(f"{self.message}...")
        def update(self, n: int = 1):
            self.current += n
            if self.current % 10000 == 0 or self.current >= self.total:
                pct = (self.current / self.total * 100) if self.total > 0 else 0
                elapsed = time.time() - self.start_time if self.start_time else 0
                rate = self.current / elapsed if elapsed > 0 else 0
                print(f"  {self.current:,}/{self.total:,} ({pct:.1f}%) - {rate:.0f} records/s", end='\r')
        def stop(self):
            elapsed = time.time() - self.start_time if self.start_time else 0
            rate = self.current / elapsed if elapsed > 0 else 0
            print(f"\n  Completed: {self.current:,} records in {elapsed:.2f}s ({rate:.0f} records/s)")
    HAS_PROGRESS = False


def _here() -> Path:
    return Path(__file__).resolve()


def default_output_path() -> Path:
    return _here().parents[1] / "data" / "chatdb_5gb.xwjson"


def _human_bytes(n: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(n)
    for u in units:
        if size < 1024.0 or u == units[-1]:
            return f"{size:.2f}{u}"
        size /= 1024.0
    return f"{n}B"


def generate_large_dataset(target_size_gb: float) -> dict[str, Any]:
    """
    Generate a large dataset targeting approximately target_size_gb GB.
    Args:
        target_size_gb: Target size in GB
    Returns:
        Dictionary with "records" key containing list of records
    """
    target_size_bytes = int(target_size_gb * 1024 * 1024 * 1024)
    # Each record is approximately 300-350 bytes (JSON representation)
    # So we need approximately: target_size_gb * 1024 * 1024 / 300 records
    estimated_records_per_mb = 1024 * 1024 // 300  # ~3500 records per MB
    target_records = int(target_size_gb * 1024 * estimated_records_per_mb)
    # For testing, we'll generate records in batches to monitor progress
    records = []
    current_size_estimate = 0
    print(f"Generating ~{target_size_gb:.1f} GB dataset...")
    print(f"Target records: ~{target_records:,}")
    print()
    progress = ProgressIndicator("Generating records", total=target_records)
    progress.start()
    # Generate records
    for i in range(target_records):
        record = {
            "@type": "Message",
            "id": f"msg_{i:010d}",
            "ts": 1000000000 + i,
            "payload": {
                "text": f"Message {i} with some content to make it larger. This is message number {i} in a large dataset. " * 3,
                "user_id": f"user_{i % 10000:08d}",
                "channel_id": f"chan_{i % 1000:06d}",
                "views": i * 10,
                "reactions": [
                    {"emoji": "👍", "count": i % 100}
                    for _ in range(min(10, i % 20))
                ],
                "metadata": {
                    "created": f"2025-01-{(i % 28) + 1:02d}",
                    "updated": f"2025-01-{(i % 28) + 1:02d}",
                    "tags": [f"tag{j}" for j in range(i % 5)]
                }
            }
        }
        records.append(record)
        current_size_estimate += 300  # Rough estimate
        progress.update(1)
        # Check actual size periodically and stop if we've reached target
        if i > 0 and i % 100000 == 0:
            # Quick size check (sample)
            sample_size = len(str(records[-1000:]).encode('utf-8'))
            avg_record_size = sample_size / 1000
            current_size_estimate = len(records) * avg_record_size
            if current_size_estimate >= target_size_bytes * 0.95:  # Stop at 95% to account for encoding
                print(f"\n  Reached target size estimate, stopping at {i:,} records")
                break
    progress.stop()
    return {
        "records": records,
        "metadata": {
            "total_records": len(records),
            "target_size_gb": target_size_gb,
            "generation_time": time.time()
        }
    }


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate a 5GB XWJSON file for performance testing")
    parser.add_argument(
        "--output",
        type=str,
        default=str(default_output_path()),
        help="Output XWJSON file path (default: data/chatdb_5gb.xwjson)"
    )
    parser.add_argument(
        "--size-gb",
        type=float,
        default=5.0,
        help="Target file size in GB (default: 5.0)"
    )
    parser.add_argument(
        "--create-index-file",
        action="store_true",
        help="Create dual-file format with separate .meta.xwjson file"
    )
    args = parser.parse_args()
    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    print("=" * 70)
    print("Generate 5GB XWJSON File for Performance Testing")
    print("=" * 70)
    print(f"Output: {output_path}")
    print(f"Target size: {args.size_gb:.1f} GB")
    print(f"Dual-file format: {args.create_index_file}")
    print()
    # Generate dataset
    start_time = time.time()
    data = generate_large_dataset(args.size_gb)
    generation_time = time.time() - start_time
    print()
    print(f"Dataset generated: {len(data['records']):,} records in {generation_time:.2f}s")
    print()
    # Save to XWJSON
    print("Saving to XWJSON format...")
    serializer = XWJSONSerializer()
    save_start = time.time()
    serializer.save_file(
        data,
        output_path,
        create_index_file=args.create_index_file
    )
    save_time = time.time() - save_start
    # Get file size
    file_size = output_path.stat().st_size
    file_size_gb = file_size / (1024 * 1024 * 1024)
    print()
    print("=" * 70)
    print("Generation Complete")
    print("=" * 70)
    print(f"Output file: {output_path}")
    print(f"File size: {_human_bytes(file_size)} ({file_size_gb:.2f} GB)")
    print(f"Records: {len(data['records']):,}")
    print(f"Generation time: {generation_time:.2f}s")
    print(f"Save time: {save_time:.2f}s")
    print(f"Total time: {generation_time + save_time:.2f}s")
    print(f"Save speed: {file_size_gb / save_time:.2f} GB/s" if save_time > 0 else "N/A")
    print()
    # Check for dual-file format
    if args.create_index_file or file_size > 10 * 1024 * 1024:  # > 10MB
        meta_file = output_path.parent / f"{output_path.stem}.meta.xwjson"
        if meta_file.exists():
            meta_size = meta_file.stat().st_size
            print(f"Meta file: {meta_file}")
            print(f"Meta file size: {_human_bytes(meta_size)}")
            print()
    return 0
if __name__ == "__main__":
    sys.exit(main())
