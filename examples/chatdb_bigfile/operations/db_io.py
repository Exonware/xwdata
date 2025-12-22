"""Low-level DB I/O helpers for chatdb.jsonl.

Includes:
- Read record by byte offset
- Read record by Type:id using an index
- Record paging (delegates to xwsystem JsonLinesSerializer)
- Atomic record updates (stream rewrite, temp+replace)

These helpers are intentionally simple and file-oriented.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional

from exonware.xwsystem.io.serialization.formats.text.jsonlines import JsonLinesSerializer


class ChatDBIOError(RuntimeError):
    pass


@dataclass(frozen=True)
class ChatDBIndex:
    """In-memory representation of the persisted index."""

    meta: dict[str, Any]
    by_key: dict[str, int]

    def is_valid_for(self, db_path: Path) -> bool:
        try:
            st = db_path.stat()
            return (
                self.meta.get("version") == 1
                and self.meta.get("path") == str(db_path)
                and int(self.meta.get("size_bytes")) == st.st_size
                and int(self.meta.get("mtime")) == int(st.st_mtime)
            )
        except Exception:
            return False


def default_db_path() -> Path:
    # .../xwdata/examples/chatdb_bigfile/operations/db_io.py
    # -> .../xwdata/examples/chatdb_bigfile/data/chatdb.jsonl
    return Path(__file__).resolve().parents[1] / "data" / "chatdb.jsonl"


def default_index_path() -> Path:
    return Path(__file__).resolve().parent / ".cache" / "chatdb.idx.json"


def load_index(index_path: Path) -> ChatDBIndex:
    doc = json.loads(index_path.read_text(encoding="utf-8"))
    meta = doc.get("meta") or {}
    by_key = doc.get("by_key") or {}
    # Normalize offsets to int
    by_key_int = {k: int(v) for k, v in by_key.items()}
    return ChatDBIndex(meta=meta, by_key=by_key_int)


def read_record_by_offset(db_path: Path, offset: int) -> dict[str, Any]:
    """Seek to a byte offset and read one JSONL line."""
    try:
        with db_path.open("rb") as f:
            f.seek(int(offset))
            line = f.readline()
        raw = line.strip()
        if not raw:
            raise ChatDBIOError(f"Empty line at offset {offset}")
        obj = json.loads(raw)
        if not isinstance(obj, dict):
            raise ChatDBIOError("Record is not a JSON object")
        return obj
    except Exception as e:
        raise ChatDBIOError(f"Failed to read record at offset {offset}: {e}") from e


def make_key(type_name: str, id_value: str) -> str:
    return f"{type_name}:{id_value}"


def read_record_by_key(db_path: Path, index: ChatDBIndex, type_name: str, id_value: str) -> dict[str, Any]:
    key = make_key(type_name, id_value)
    if key not in index.by_key:
        raise KeyError(key)
    return read_record_by_offset(db_path, index.by_key[key])


def get_record_page(db_path: Path, page_number: int, page_size: int) -> list[dict[str, Any]]:
    """File-order paging using xwsystem's JsonLinesSerializer."""
    serializer = JsonLinesSerializer()
    records = serializer.get_record_page(db_path, page_number=page_number, page_size=page_size)
    # JsonLinesSerializer returns list[Any]
    return [r for r in records if isinstance(r, dict)]


def stream_update_record(
    db_path: Path,
    match: Callable[[dict[str, Any]], bool],
    updater: Callable[[dict[str, Any]], dict[str, Any]],
    *,
    atomic: bool = True,
    backup: bool = True,
    ensure_ascii: bool = False,
) -> int:
    serializer = JsonLinesSerializer()

    def _match_any(obj: Any) -> bool:
        return isinstance(obj, dict) and match(obj)

    def _updater_any(obj: Any) -> Any:
        if not isinstance(obj, dict):
            return obj
        return updater(obj)

    return serializer.stream_update_record(
        db_path,
        _match_any,
        _updater_any,
        atomic=atomic,
        backup=backup,
        ensure_ascii=ensure_ascii,
    )


def atomic_update_record_by_key(
    db_path: Path,
    type_name: str,
    id_value: str,
    *,
    updater: Callable[[dict[str, Any]], dict[str, Any]],
    backup: bool = True,
    use_append_log: bool | None = None,
) -> int:
    """
    Atomic update using append-only log with fallback to full rewrite.
    
    Args:
        db_path: Path to JSONL file
        type_name: Record type
        id_value: Record ID
        updater: Function to update the record
        backup: Whether to create backup (ignored for append-only log)
        use_append_log: If True, use append-only log; if None, auto-detect based on file size
    
    Returns:
        Number of records updated
    """
    # Try append-only log first (with fallback)
    try:
        from atomic_update_append_log import atomic_update_record_by_key_append_log
        return atomic_update_record_by_key_append_log(
            db_path,
            type_name,
            id_value,
            updater=updater,
            backup=backup,
            use_append_log=use_append_log,
        )
    except ImportError:
        # Fall back to original implementation if append-only log not available
        pass
    except Exception as e:
        # Fall back on any error
        print(f"Append-only log update failed, using full rewrite: {e}")
    
    # Original implementation (full rewrite)
    def _match(rec: dict[str, Any]) -> bool:
        return rec.get("@type") == type_name and rec.get("id") == id_value

    return stream_update_record(db_path, _match, updater, atomic=True, backup=backup)


def try_get_record_by_id_linear(db_path: Path, id_value: str, id_field: str = "id") -> Optional[dict[str, Any]]:
    """Slow fallback: linear scan by id field."""
    serializer = JsonLinesSerializer()
    try:
        rec = serializer.get_record_by_id(db_path, id_value, id_field=id_field)
        return rec if isinstance(rec, dict) else None
    except Exception:
        return None
