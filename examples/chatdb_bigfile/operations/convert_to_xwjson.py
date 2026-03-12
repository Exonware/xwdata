"""Convert chatdb.jsonl to XWJSON format.
Converts the JSONL database to XWJSON binary format for performance comparison.
XWJSON is a binary format that should be faster than JSONL for read/write operations.
Run (from repo root):
  python xwdata/examples/chatdb_bigfile/operations/convert_to_xwjson.py --input ../data/chatdb.jsonl --output ../data/chatdb.xwjson
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
"""

from __future__ import annotations
import argparse
import asyncio
import json
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
from progress_indicator import ProgressIndicator


def _here() -> Path:
    return Path(__file__).resolve()


def default_input_path() -> Path:
    return _here().parents[1] / "data" / "chatdb.jsonl"


def default_output_path() -> Path:
    return _here().parents[1] / "data" / "chatdb.xwjson"


def _human_bytes(n: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(n)
    for u in units:
        if size < 1024.0 or u == units[-1]:
            return f"{size:.2f}{u}"
        size /= 1024.0
    return f"{n}B"
async def convert_jsonl_to_xwjson(input_path: Path, output_path: Path) -> dict[str, Any]:
    """
    Convert JSONL file to XWJSON format.
    Args:
        input_path: Path to input JSONL file
        output_path: Path to output XWJSON file
    Returns:
        Statistics dictionary
    """
    serializer = XWJSONSerializer()
    print(f"Converting {input_path} to {output_path}")
    print(f"Input size: {_human_bytes(input_path.stat().st_size)}")
    print()
    # Read all records from JSONL
    records = []
    bytes_read = 0
    start_time = time.perf_counter()
    # Count total lines first for progress
    print("Counting records...")
    total_lines = sum(1 for _ in input_path.open("r", encoding="utf-8"))
    print(f"Total records: {total_lines:,}")
    print()
    # Read records with progress indicator
    progress = ProgressIndicator("Reading JSONL records", total=total_lines)
    progress.start()
    try:
        with input_path.open("r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    record = json.loads(line)
                    records.append(record)
                    bytes_read += len(line.encode('utf-8'))
                # Update progress every 100 lines for smoother updates
                if line_num % 100 == 0:
                    progress.update(line_num)
        # Final update
        progress.update(total_lines)
    finally:
        progress.stop()
    read_time = time.perf_counter() - start_time
    print(f"\nRead {len(records):,} records in {read_time:.2f}s")
    # Convert to XWJSON
    print("Encoding to XWJSON...")
    start_time = time.perf_counter()
    # Encode all records as a list with progress
    data = {"records": records}
    progress = ProgressIndicator("Converting JSON file to XWJSON", total=len(records))
    progress.start()
    # Set progress callback on encoder for real-time updates during encoding
    encoder = serializer._encoder
    original_encode = encoder._encode_record_level
    def encode_with_progress(records_list, data_wrapper, metadata, format_code, flags):
        # Create wrapper that calls original with progress updates
        total = len(records_list)
        # Store progress callback
        def progress_callback(current):
            progress.update(current)
        # Temporarily set progress callback
        encoder._progress_callback = progress_callback
        try:
            # Call original encode
            result = original_encode(records_list, data_wrapper, metadata, format_code, flags)
            # Final update
            progress.update(total)
            return result
        finally:
            # Clean up
            if hasattr(encoder, '_progress_callback'):
                del encoder._progress_callback
    # Temporarily replace method to add progress
    encoder._encode_record_level = encode_with_progress
    try:
        # Use dual-file format for maximum performance (148.8 MB/s)
        encoded = serializer.encode(data, options={
            'file_path': output_path,
            'create_index_file': True  # Create data.idx.xwjson for paging
        })
    finally:
        # Restore original method
        encoder._encode_record_level = original_encode
        progress.stop()
    encode_time = time.perf_counter() - start_time
    encoded_size = len(encoded)
    print(f"\nEncoded {len(records):,} records in {encode_time:.2f}s")
    print(f"Encoded size: {_human_bytes(encoded_size)}")
    print(f"Encoding speed: {encoded_size / (1024 * 1024) / encode_time if encode_time > 0 else 0:.1f} MB/s")
    # Write to file
    print(f"\nWriting to {output_path}...")
    start_time = time.perf_counter()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Writing is fast, no need for progress indicator
    serializer.save_file(data, output_path)
    write_time = time.perf_counter() - start_time
    # Verify file was written
    actual_size = output_path.stat().st_size
    print(f"\nWritten {_human_bytes(actual_size)} in {write_time:.2f}s")
    print(f"Write speed: {actual_size / (1024 * 1024) / write_time if write_time > 0 else 0:.1f} MB/s")
    # Compression ratio
    input_size = input_path.stat().st_size
    compression_ratio = input_size / actual_size if actual_size > 0 else 1.0
    print(f"Size ratio (JSONL/XWJSON): {compression_ratio:.2f}x")
    return {
        "input_path": str(input_path),
        "output_path": str(output_path),
        "records": len(records),
        "input_size": input_size,
        "output_size": actual_size,
        "read_time": read_time,
        "encode_time": encode_time,
        "write_time": write_time,
        "total_time": read_time + encode_time + write_time,
        "compression_ratio": compression_ratio
    }


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Convert JSONL database to XWJSON format")
    p.add_argument("--input", type=str, default=str(default_input_path()), help="Input JSONL file path")
    p.add_argument("--output", type=str, default=str(default_output_path()), help="Output XWJSON file path")
    return p.parse_args()


def main() -> int:
    if not XWJSON_AVAILABLE:
        print("ERROR: xwjson not available")
        return 1
    args = _parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}")
        return 1
    print("=" * 60)
    print("JSONL to XWJSON Conversion")
    print("=" * 60)
    print()
    stats = asyncio.run(convert_jsonl_to_xwjson(input_path, output_path))
    print()
    print("=" * 60)
    print("Conversion Complete")
    print("=" * 60)
    print(f"Records: {stats['records']:,}")
    print(f"Input size: {_human_bytes(stats['input_size'])}")
    print(f"Output size: {_human_bytes(stats['output_size'])}")
    print(f"Total time: {stats['total_time']:.2f}s")
    print(f"Compression ratio: {stats['compression_ratio']:.2f}x")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
