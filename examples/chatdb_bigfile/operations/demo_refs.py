"""Demo: resolve internal-only $ref references via index."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_OPS_DIR = Path(__file__).resolve().parent
if str(_OPS_DIR) not in sys.path:
    sys.path.insert(0, str(_OPS_DIR))

import build_index
import db_io
from refs import InternalRefResolver


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Demo internal reference resolution")
    p.add_argument("--db", type=str, default=None)
    p.add_argument("--index", type=str, default=str(build_index.default_index_path()))
    p.add_argument("--max-depth", type=int, default=2)
    p.add_argument("--message-id", type=str, default=None)
    return p.parse_args()


def main() -> int:
    args = _parse_args()
    db_path = Path(args.db) if args.db else db_io.default_db_path()
    index = db_io.load_index(Path(args.index))

    # choose a message
    msg_id = args.message_id
    if msg_id is None:
        for k in index.by_key.keys():
            if k.startswith("Message:"):
                msg_id = k.split(":", 1)[1]
                break
    if msg_id is None:
        raise SystemExit("No Message records found in index")

    msg = db_io.read_record_by_key(db_path, index, "Message", msg_id)
    resolver = InternalRefResolver(db_path, index)

    resolved = resolver.resolve(msg, max_depth=args.max_depth)

    print(f"Resolved message id={msg_id} (depth={args.max_depth})")
    payload = resolved.get("payload", {})
    author = payload.get("author")
    chat = payload.get("chat")
    print(f"- author.type={author.get('@type') if isinstance(author, dict) else type(author)}")
    print(f"- chat.type={chat.get('@type') if isinstance(chat, dict) else type(chat)}")
    print(f"- text.preview={(payload.get('text') or '')[:80]!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
