"""Demo: record-level paging over chatdb.jsonl + schema validation."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from exonware.xwschema import XWSchema

_OPS_DIR = Path(__file__).resolve().parent
if str(_OPS_DIR) not in sys.path:
    sys.path.insert(0, str(_OPS_DIR))

import db_io


def _schemas_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "schemas"


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Demo JSONL paging + schema validation")
    p.add_argument("--db", type=str, default=None)
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--page-size", type=int, default=25)
    p.add_argument("--validate", action="store_true", help="Validate envelope + payload schema")
    return p.parse_args()


async def _run(db_path: Path, page: int, page_size: int, validate: bool) -> int:
    records = db_io.get_record_page(db_path, page_number=page, page_size=page_size)
    print(f"Loaded page {page} (size={len(records)})")

    if not records:
        return 0

    if validate:
        sdir = _schemas_dir()
        record_schema = await XWSchema.load(sdir / "record.schema.json")
        payload_schemas = {
            "User": await XWSchema.load(sdir / "user.schema.json"),
            "Channel": await XWSchema.load(sdir / "channel.schema.json"),
            "Group": await XWSchema.load(sdir / "group.schema.json"),
            "Message": await XWSchema.load(sdir / "message.schema.json"),
            "Reaction": await XWSchema.load(sdir / "reaction.schema.json"),
        }

        bad = 0
        for i, rec in enumerate(records[: min(len(records), 50)]):
            ok_env, env_errors = await record_schema.validate(rec)
            if not ok_env:
                bad += 1
                print(f"Envelope invalid at i={i}: {env_errors}")
                continue

            t = rec.get("@type")
            payload = rec.get("payload")
            schema = payload_schemas.get(t)
            if schema is None:
                continue
            ok_pl, pl_errors = await schema.validate(payload)
            if not ok_pl:
                bad += 1
                print(f"Payload invalid ({t}) at i={i}: {pl_errors}")

        print(f"Validation complete (sampled={min(len(records), 50)}, bad={bad})")

    # Show a preview
    head = records[0]
    print(f"First: @type={head.get('@type')} id={head.get('id')}")
    return 0


def main() -> int:
    args = _parse_args()
    db_path = Path(args.db) if args.db else db_io.default_db_path()
    return asyncio.run(_run(db_path, args.page, args.page_size, args.validate))


if __name__ == "__main__":
    raise SystemExit(main())
