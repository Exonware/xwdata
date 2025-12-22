"""Demo: atomic record update in chatdb.jsonl."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

_OPS_DIR = Path(__file__).resolve().parent
if str(_OPS_DIR) not in sys.path:
    sys.path.insert(0, str(_OPS_DIR))

import build_index
from db_io import ChatDBIndex, atomic_update_record_by_key, read_record_by_key


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Demo atomic record update")
    p.add_argument("--db", type=str, default=None)
    p.add_argument("--index", type=str, default=str(build_index.default_index_path()))
    p.add_argument("--backup", action="store_true", help="Keep .bak during atomic rewrite")
    p.add_argument("--message-id", type=str, default=None, help="Message id to update (defaults to first found)")
    return p.parse_args()


def _ensure_index(db_path: Path, index_path: Path) -> ChatDBIndex:
    if index_path.exists():
        doc = build_index.load_index(index_path)
        if build_index.index_is_valid(doc, db_path):
            return ChatDBIndex(meta=doc["meta"], by_key={k: int(v) for k, v in doc["by_key"].items()})

    built = build_index.build_index(db_path)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(__import__("json").dumps(built, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return ChatDBIndex(meta=built["meta"], by_key={k: int(v) for k, v in built["by_key"].items()})


def main() -> int:
    args = _parse_args()
    import db_io

    db_path = Path(args.db) if args.db else db_io.default_db_path()
    index_path = Path(args.index)

    index = _ensure_index(db_path, index_path)

    # Pick a message id
    msg_id = args.message_id
    if msg_id is None:
        for k in index.by_key.keys():
            if k.startswith("Message:"):
                msg_id = k.split(":", 1)[1]
                break
    if msg_id is None:
        raise SystemExit("No Message records found in index")

    before = read_record_by_key(db_path, index, "Message", msg_id)

    def updater(rec: dict):
        rec = dict(rec)
        payload = dict(rec.get("payload") or {})
        payload["text"] = (payload.get("text") or "") + f" [atomic_updated@{int(time.time())}]"
        payload["edited_ts"] = int(time.time())
        payload["version"] = int(payload.get("version") or 1) + 1
        rec["payload"] = payload
        return rec

    updated = atomic_update_record_by_key(db_path, "Message", msg_id, updater=updater, backup=args.backup)
    print(f"Updated records: {updated}")

    # Rebuild/refresh index (offsets may change after rewrite)
    rebuilt = build_index.build_index(db_path)
    index_path.write_text(__import__("json").dumps(rebuilt, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    index = ChatDBIndex(meta=rebuilt["meta"], by_key={k: int(v) for k, v in rebuilt["by_key"].items()})

    after = read_record_by_key(db_path, index, "Message", msg_id)

    print(f"Message id={msg_id}")
    print(f"- before.version={before.get('payload', {}).get('version')} after.version={after.get('payload', {}).get('version')}")
    print(f"- after.edited_ts={after.get('payload', {}).get('edited_ts')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
