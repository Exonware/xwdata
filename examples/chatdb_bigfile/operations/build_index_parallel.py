"""Parallel index building with fallback to single-threaded.
This module provides parallel index building using multiple CPU cores,
with automatic fallback to single-threaded if parallel processing fails.
"""

from __future__ import annotations
import multiprocessing as mp
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any
# Import the original single-threaded implementation as fallback
from build_index import build_index as build_index_single_threaded
# Add xwsystem to path for parser access
_xwsystem_src = Path(__file__).resolve().parents[4] / "xwsystem" / "src"
if str(_xwsystem_src) not in sys.path:
    sys.path.insert(0, str(_xwsystem_src))
try:
    from exonware.xwsystem.io.serialization.parsers.registry import get_best_available_parser
    _parser = get_best_available_parser()
    USE_OPTIMIZED_PARSER = True
except ImportError:
    USE_OPTIMIZED_PARSER = False
    _parser = None


def _process_chunk(
    db_path: str,
    start_offset: int,
    end_offset: int,
    chunk_id: int,
    build_line_offsets: bool = False,
) -> tuple[int, dict[str, int], list[int] | None, int]:
    """
    Process a chunk of the file and build index for that chunk.
    Args:
        build_line_offsets: If True, also build line_offsets list
    Returns:
        (chunk_id, index_dict, line_offsets_or_none, lines_processed)
    """
    index_chunk: dict[str, int] = {}
    line_offsets: list[int] | None = [] if build_line_offsets else None
    lines_processed = 0
    current_offset = start_offset
    try:
        with open(db_path, "rb") as f:
            # Seek to start of chunk
            f.seek(start_offset)
            # Process until end of chunk
            while current_offset < end_offset:
                line_start = current_offset
                line = f.readline()
                if not line:
                    break
                current_offset = f.tell()
                # Skip if we've gone past the end
                if line_start >= end_offset:
                    break
                # Track line offset if requested
                if build_line_offsets:
                    line_offsets.append(line_start)
                raw = line.strip()
                if not raw:
                    continue
                try:
                    # Use optimized parser if available
                    if USE_OPTIMIZED_PARSER:
                        rec = _parser.loads(raw)
                    else:
                        import json
                        rec = json.loads(raw)
                except Exception:
                    continue
                if isinstance(rec, dict):
                    t = rec.get("@type")
                    rid = rec.get("id")
                    if t and rid:
                        index_chunk[f"{t}:{rid}"] = line_start
                lines_processed += 1
    except Exception as e:
        # Return partial results even on error
        print(f"Warning: Chunk {chunk_id} encountered error: {e}")
    return (chunk_id, index_chunk, line_offsets, lines_processed)


def build_index_parallel(
    db_path: Path,
    num_workers: int | None = None,
    chunk_size_mb: int = 100,
    fallback_on_error: bool = True,
    build_line_offsets: bool = False,
) -> dict[str, Any]:
    """
    Build index using parallel processing.
    Args:
        db_path: Path to the JSONL file
        num_workers: Number of worker processes (default: CPU count)
        chunk_size_mb: Size of each chunk in MB (default: 100MB)
        fallback_on_error: If True, fall back to single-threaded on error
        build_line_offsets: If True, also build line_offsets list (slower)
    Returns:
        Index document (same format as build_index_single_threaded)
    """
    if not db_path.exists():
        raise FileNotFoundError(f"DB file not found: {db_path}")
    # Determine number of workers
    if num_workers is None:
        num_workers = max(1, mp.cpu_count())
    # Get file size
    file_size = db_path.stat().st_size
    chunk_size_bytes = chunk_size_mb * 1024 * 1024
    # If file is small, use single-threaded
    if file_size < chunk_size_bytes * 2:
        if fallback_on_error:
            return build_index_single_threaded(db_path)
        else:
            raise ValueError(f"File too small for parallel processing: {file_size} bytes")
    # Split file into chunks
    chunks = []
    current_offset = 0
    chunk_id = 0
    while current_offset < file_size:
        chunk_end = min(current_offset + chunk_size_bytes, file_size)
        chunks.append((chunk_id, current_offset, chunk_end))
        current_offset = chunk_end
        chunk_id += 1
    # Limit number of chunks to num_workers
    if len(chunks) > num_workers * 2:
        # Merge small chunks
        merged_chunks = []
        for i in range(0, len(chunks), max(1, len(chunks) // num_workers)):
            chunk_group = chunks[i:i + max(1, len(chunks) // num_workers)]
            if chunk_group:
                merged_chunks.append((
                    chunk_group[0][0],
                    chunk_group[0][1],
                    chunk_group[-1][2]
                ))
        chunks = merged_chunks
    print(f"Processing {len(chunks)} chunks with {num_workers} workers...")
    started = time.perf_counter()
    merged_index: dict[str, int] = {}
    merged_line_offsets: list[int] | None = [] if build_line_offsets else None
    total_lines = 0
    try:
        # Process chunks in parallel
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            futures = {
                executor.submit(
                    _process_chunk,
                    str(db_path),
                    start,
                    end,
                    cid,
                    build_line_offsets,
                ): cid
                for cid, start, end in chunks
            }
            completed = 0
            chunk_results: list[tuple[int, dict[str, int], list[int] | None]] = []
            for future in as_completed(futures):
                chunk_id = futures[future]
                try:
                    cid, index_chunk, chunk_line_offsets, lines = future.result()
                    chunk_results.append((cid, index_chunk, chunk_line_offsets))
                    total_lines += lines
                    completed += 1
                    if completed % max(1, len(chunks) // 10) == 0:
                        elapsed = time.perf_counter() - started
                        rate = total_lines / elapsed if elapsed > 0 else 0
                        print(f"... processed {completed}/{len(chunks)} chunks ({rate:,.0f} lines/s), keys={len(merged_index):,}")
                except Exception as e:
                    print(f"Error processing chunk {chunk_id}: {e}")
                    if not fallback_on_error:
                        raise
                    # Fall back to single-threaded
                    print("Falling back to single-threaded index building...")
                    return build_index_single_threaded(db_path)
            # Merge results in order
            chunk_results.sort(key=lambda x: x[0])
            for _, index_chunk, chunk_line_offsets in chunk_results:
                merged_index.update(index_chunk)
                if build_line_offsets and chunk_line_offsets:
                    merged_line_offsets.extend(chunk_line_offsets)
    except Exception as e:
        print(f"Parallel processing failed: {e}")
        if fallback_on_error:
            print("Falling back to single-threaded index building...")
            return build_index_single_threaded(db_path)
        else:
            raise
    # Build final document (same format as single-threaded)
    from build_index import _file_meta
    import time as time_module
    doc = {
        "meta": {
            **_file_meta(db_path),
            "version": 1,
            "created": int(time_module.time()),
            "parallel": True,
            "num_workers": num_workers,
            "chunks": len(chunks),
        },
        "by_key": merged_index,
    }
    # Add line_offsets if built
    if build_line_offsets and merged_line_offsets:
        doc["line_offsets"] = merged_line_offsets
    elapsed = time.perf_counter() - started
    print(f"Parallel index building completed in {elapsed:.2f}s ({total_lines:,} lines, {len(merged_index):,} keys)")
    return doc
