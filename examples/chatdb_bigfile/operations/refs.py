"""Internal-only $ref resolver for xwdb://Type/id references.
This example does NOT rely on external files for references.
Instead it resolves references inside the single JSONL database file using the index.
Reference format:
    {"$ref": "xwdb://User/user_000001"}
"""

from __future__ import annotations
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse
_OPS_DIR = Path(__file__).resolve().parent
if str(_OPS_DIR) not in sys.path:
    sys.path.insert(0, str(_OPS_DIR))
from cache import LRUCache
from db_io import ChatDBIndex, read_record_by_key
@dataclass(frozen=True)


class RefTarget:
    type_name: str
    id_value: str


def parse_xwdb_ref(ref: str) -> RefTarget:
    """Parse xwdb://Type/id into components."""
    u = urlparse(ref)
    if u.scheme != "xwdb":
        raise ValueError(f"Unsupported ref scheme: {u.scheme}")
    type_name = u.netloc
    id_value = u.path.lstrip("/")
    if not type_name or not id_value:
        raise ValueError(f"Invalid xwdb ref: {ref!r}")
    return RefTarget(type_name=type_name, id_value=id_value)


def is_ref_obj(obj: Any) -> bool:
    return isinstance(obj, dict) and "$ref" in obj and isinstance(obj.get("$ref"), str)


class InternalRefResolver:

    def __init__(
        self,
        db_path,
        index: ChatDBIndex,
        *,
        cache_capacity: int = 10_000,
    ):
        from pathlib import Path
        self.db_path = Path(db_path)
        self.index = index
        self.cache: LRUCache[str, dict[str, Any]] = LRUCache(capacity=cache_capacity)

    def get_one(self, type_name: str, id_value: str) -> dict[str, Any]:
        key = f"{type_name}:{id_value}"
        cached = self.cache.get(key)
        if cached is not None:
            return cached
        rec = read_record_by_key(self.db_path, self.index, type_name, id_value)
        self.cache.put(key, rec)
        return rec

    def resolve(
        self,
        obj: Any,
        *,
        max_depth: int = 3,
        _depth: int = 0,
        _seen: Optional[set[str]] = None,
    ) -> Any:
        """Recursively resolve internal $ref objects up to max_depth."""
        if _seen is None:
            _seen = set()
        if _depth > max_depth:
            return obj
        if is_ref_obj(obj):
            ref_str = obj["$ref"]
            target = parse_xwdb_ref(ref_str)
            key = f"{target.type_name}:{target.id_value}"
            if key in _seen:
                return obj  # break cycles
            _seen.add(key)
            resolved = self.get_one(target.type_name, target.id_value)
            return self.resolve(resolved, max_depth=max_depth, _depth=_depth + 1, _seen=_seen)
        if isinstance(obj, dict):
            return {
                k: self.resolve(v, max_depth=max_depth, _depth=_depth, _seen=_seen)
                for k, v in obj.items()
            }
        if isinstance(obj, list):
            return [self.resolve(v, max_depth=max_depth, _depth=_depth, _seen=_seen) for v in obj]
        return obj
