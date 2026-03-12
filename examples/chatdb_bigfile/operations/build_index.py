"""Build a persistent Type:id -> byte_offset index for chatdb.jsonl.
Run (from repo root):
  python xwdata/examples/chatdb_bigfile/operations/build_index.py
The index is written under operations/.cache/ and validated against file mtime/size.
"""

from __future__ import annotations
import argparse
import json
import os
import random
import time
import sys
from pathlib import Path
from typing import Any
_OPS_DIR = Path(__file__).resolve().parent
if str(_OPS_DIR) not in sys.path:
    sys.path.insert(0, str(_OPS_DIR))
# Add xwsystem to path for parser access
_xwsystem_src = Path(__file__).resolve().parents[4] / "xwsystem" / "src"
if str(_xwsystem_src) not in sys.path:
    sys.path.insert(0, str(_xwsystem_src))
# Import optimized parser
try:
    from exonware.xwsystem.io.serialization.parsers.registry import get_best_available_parser
    _parser = get_best_available_parser()
    USE_OPTIMIZED_PARSER = True
except ImportError:
    USE_OPTIMIZED_PARSER = False
    _parser = None


def _here() -> Path:
    return Path(__file__).resolve()


def default_db_path() -> Path:
    return _here().parents[1] / "data" / "chatdb.jsonl"


def default_index_path() -> Path:
    return _here().parent / ".cache" / "chatdb.idx.json"


def _file_meta(path: Path) -> dict[str, Any]:
    st = path.stat()
    return {
        "path": str(path),
        "size_bytes": st.st_size,
        "mtime": int(st.st_mtime),
    }


def load_index(index_path: Path) -> dict[str, Any]:
    return json.loads(index_path.read_text(encoding="utf-8"))


def index_is_valid(index_doc: dict[str, Any], db_path: Path) -> bool:
    meta = index_doc.get("meta", {})
    if not meta:
        return False
    try:
        return (
            meta.get("path") == str(db_path)
            and int(meta.get("size_bytes")) == db_path.stat().st_size
            and int(meta.get("mtime")) == int(db_path.stat().st_mtime)
            and meta.get("version") == 1
        )
    except Exception:
        return False


def build_index(
    db_path: Path,
    use_parallel: bool | None = None,
    num_workers: int | None = None,
) -> dict[str, Any]:
    """
    Build index for JSONL file.
    Args:
        db_path: Path to JSONL file
        use_parallel: If True, use parallel processing; if None, auto-detect based on file size
        num_workers: Number of worker processes (only used if use_parallel=True)
    Returns:
        Index document
    """
    if not db_path.exists():
        raise FileNotFoundError(f"DB file not found: {db_path}")
    # Auto-detect: use parallel for files >500MB
    if use_parallel is None:
        file_size_mb = db_path.stat().st_size / (1024 * 1024)
        use_parallel = file_size_mb > 500
    # Use parallel if requested and available
    if use_parallel:
        try:
            from build_index_parallel import build_index_parallel
            return build_index_parallel(db_path, num_workers=num_workers, fallback_on_error=True)
        except ImportError:
            # Fall back to single-threaded if parallel module not available
            pass
        except Exception as e:
            print(f"Parallel index building failed, falling back to single-threaded: {e}")
            # Fall through to single-threaded
    # Single-threaded implementation (original)
    by_key: dict[str, int] = {}
    started = time.perf_counter()
    seen = 0
    with db_path.open("rb") as f:
        offset = 0
        while True:
            line = f.readline()
            if not line:
                break
            raw = line.strip()
            if not raw:
                offset += len(line)
                continue
            try:
                # Use optimized parser if available
                if USE_OPTIMIZED_PARSER:
                    rec = _parser.loads(raw)
                else:
                    rec = json.loads(raw)
            except Exception:
                # Skip invalid lines (shouldn't happen in our generator)
                offset += len(line)
                continue
            if isinstance(rec, dict):
                t = rec.get("@type")
                rid = rec.get("id")
                if t and rid:
                    by_key[f"{t}:{rid}"] = offset
            seen += 1
            offset += len(line)
            if seen % 1_000_000 == 0:
                elapsed = max(time.perf_counter() - started, 1e-9)
                rate = seen / elapsed
                print(f"... scanned {seen:,} lines ({rate:,.0f} lines/s), keys={len(by_key):,}")
    doc = {
        "meta": {
            **_file_meta(db_path),
            "version": 1,
            "created": int(time.time()),
            "parallel": False,
        },
        "by_key": by_key,
    }
    return doc


def spot_check(db_path: Path, index_doc: dict[str, Any], samples: int) -> None:
    import db_io
    keys = list(index_doc.get("by_key", {}).keys())
    if not keys:
        print("Index is empty; skipping spot-check")
        return
    rng = random.Random(123)
    for _ in range(min(samples, len(keys))):
        key = rng.choice(keys)
        offset = index_doc["by_key"][key]
        rec = db_io.read_record_by_offset(db_path, offset)
        if not isinstance(rec, dict):
            raise RuntimeError(f"Spot-check failed for {key}: not a dict")
        t, rid = key.split(":", 1)
        if rec.get("@type") != t or rec.get("id") != rid:
            raise RuntimeError(f"Spot-check mismatch for {key}: got {rec.get('@type')}:{rec.get('id')}")


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build a byte-offset index for chatdb.jsonl")
    p.add_argument("--db", type=str, default=str(default_db_path()))
    p.add_argument("--out", type=str, default=str(default_index_path()))
    p.add_argument("--force", action="store_true", help="Rebuild index even if valid")
    p.add_argument("--spot-check", type=int, default=10, help="Random reads to validate offsets")
    p.add_argument("--parallel", action="store_true", help="Use parallel processing (auto-enabled for large files)")
    p.add_argument("--no-parallel", action="store_true", help="Force single-threaded processing")
    p.add_argument("--workers", type=int, default=None, help="Number of worker processes (default: CPU count)")
    return p.parse_args()


def main() -> int:
    args = _parse_args()
    db_path = Path(args.db)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists() and not args.force:
        try:
            existing = load_index(out_path)
            if index_is_valid(existing, db_path):
                print(f"Index already valid: {out_path}")
                if args.spot_check:
                    spot_check(db_path, existing, args.spot_check)
                    print("Spot-check OK")
                return 0
        except Exception:
            # proceed with rebuild
            pass
    print(f"Building index for: {db_path}")
    # Determine parallel mode
    use_parallel = None
    if args.parallel:
        use_parallel = True
    elif args.no_parallel:
        use_parallel = False
    # else: auto-detect based on file size
    started = time.perf_counter()
    doc = build_index(db_path, use_parallel=use_parallel, num_workers=args.workers)
    elapsed = max(time.perf_counter() - started, 1e-9)
    # Write compact (can be large)
    out_path.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    size = os.path.getsize(out_path)
    print(
        f"Wrote index: {out_path} ({size:,} bytes) in {elapsed:.2f}s; "
        f"keys={len(doc.get('by_key', {})):,}"
    )
    if args.spot_check:
        spot_check(db_path, doc, args.spot_check)
        print("Spot-check OK")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
