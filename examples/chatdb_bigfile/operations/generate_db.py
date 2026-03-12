"""Generate a large single-file JSONL chat database.
Creates `../data/chatdb.jsonl` with Telegram-like entities:
- Users
- Channels
- Groups
- Messages
- Reactions
Records are written as JSONL lines with an envelope:
  {"@type": "User|Channel|Group|Message|Reaction", "id": "...", "ts": 0, "payload": {...}}
Run (from repo root):
  python xwdata/examples/chatdb_bigfile/operations/generate_db.py --target-gb 5
Use --quick for fast local iteration.
"""

from __future__ import annotations
import argparse
import os
import random
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
@dataclass(frozen=True)


class GenConfig:
    target_bytes: int
    seed: int
    users: int
    channels: int
    groups: int
    messages_per_channel: int
    reactions_per_message: int
    max_text_len: int
    progress_every_mb: int


def _here() -> Path:
    return Path(__file__).resolve()


def default_db_path() -> Path:
    # .../xwdata/examples/chatdb_bigfile/operations/generate_db.py
    # -> .../xwdata/examples/chatdb_bigfile/data/chatdb.jsonl
    return _here().parents[1] / "data" / "chatdb.jsonl"


def _human_bytes(n: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(n)
    for u in units:
        if size < 1024.0 or u == units[-1]:
            return f"{size:.2f}{u}"
        size /= 1024.0
    return f"{n}B"


def _ref(type_name: str, id_value: str) -> dict[str, str]:
    return {"$ref": f"xwdb://{type_name}/{id_value}"}


def _record(type_name: str, id_value: str, ts: int, payload: dict[str, Any]) -> dict[str, Any]:
    return {"@type": type_name, "id": id_value, "ts": ts, "payload": payload}


def _rand_text(rng: random.Random, max_len: int) -> str:
    # Simple deterministic "chatty" text
    words = [
        "hello",
        "world",
        "chat",
        "data",
        "stream",
        "paging",
        "index",
        "schema",
        "query",
        "node",
        "atomic",
        "update",
        "ref",
        "lazy",
    ]
    target = rng.randint(max(1, max_len // 4), max_len)
    out: list[str] = []
    while sum(len(w) + 1 for w in out) < target:
        out.append(rng.choice(words))
    return " ".join(out)[:max_len]


def _write_jsonl_line(f, obj: dict[str, Any]) -> int:
    # Write compact JSON (no spaces) for size efficiency.
    # Use UTF-8 and track exact bytes written.
    import json
    line = (json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
    f.write(line)
    return len(line)


def generate(db_path: Path, cfg: GenConfig) -> dict[str, Any]:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    rng = random.Random(cfg.seed)
    ts0 = int(time.time())
    # Deterministic IDs
    user_ids = [f"user_{i:06d}" for i in range(1, cfg.users + 1)]
    channel_ids = [f"chan_{i:06d}" for i in range(1, cfg.channels + 1)]
    group_ids = [f"grp_{i:06d}" for i in range(1, cfg.groups + 1)]
    bytes_written = 0
    records_written = 0
    next_progress = cfg.progress_every_mb * 1024 * 1024
    msg_seq = 0
    rct_seq = 0
    started = time.perf_counter()
    spinner_chars = ["/", "-", "\\", "|"]
    spinner_idx = 0
    with db_path.open("wb") as f:
        # --- Header blocks: Users / Channels / Groups ---
        for i, uid in enumerate(user_ids, 1):
            payload = {
                "username": f"user{i}",
                "display_name": f"User {i}",
                "settings": {"theme": rng.choice(["dark", "light"]), "lang": rng.choice(["en", "ar"])},
                "followers": [],
                "following": [],
            }
            bytes_written += _write_jsonl_line(f, _record("User", uid, ts0 + i, payload))
            records_written += 1
        for i, cid in enumerate(channel_ids, 1):
            owner = rng.choice(user_ids)
            admins = rng.sample(user_ids, k=min(3, len(user_ids)))
            payload = {
                "name": f"Channel {i}",
                "owner": _ref("User", owner),
                "admins": [_ref("User", a) for a in admins],
                "member_count": rng.randint(10, 1000000),
                "permissions": {"can_post": True, "can_comment": rng.choice([True, False])},
            }
            bytes_written += _write_jsonl_line(f, _record("Channel", cid, ts0 + 10_000 + i, payload))
            records_written += 1
        for i, gid in enumerate(group_ids, 1):
            members = rng.sample(user_ids, k=min(max(5, len(user_ids) // 3), len(user_ids)))
            admins = rng.sample(members, k=min(3, len(members)))
            payload = {
                "title": f"Group {i}",
                "members": [_ref("User", m) for m in members],
                "admins": [_ref("User", a) for a in admins],
                "permissions": {"can_invite": True, "can_pin": True},
            }
            bytes_written += _write_jsonl_line(f, _record("Group", gid, ts0 + 20_000 + i, payload))
            records_written += 1
        # --- Main blocks: per channel message blocks + reaction blocks ---
        # This makes file-order paging meaningful.
        #
        # IMPORTANT: keep generating *epochs* of channel blocks until target size is reached.
        while bytes_written < cfg.target_bytes:
            for cid in channel_ids:
                # message block (contiguous per channel)
                channel_message_ids: list[str] = []
                for _ in range(cfg.messages_per_channel):
                    msg_seq += 1
                    mid = f"msg_{msg_seq:012d}"
                    channel_message_ids.append(mid)
                    author = rng.choice(user_ids)
                    reply_to = None
                    if channel_message_ids and rng.random() < 0.10:
                        reply_to = _ref("Message", rng.choice(channel_message_ids))
                    payload = {
                        "chat": _ref("Channel", cid),
                        "author": _ref("User", author),
                        "text": _rand_text(rng, cfg.max_text_len),
                        "reply_to": reply_to,
                        "views": rng.randint(0, 5_000_000),
                        "edited_ts": None,
                        "version": 1,
                    }
                    bytes_written += _write_jsonl_line(
                        f, _record("Message", mid, ts0 + 30_000 + msg_seq, payload)
                    )
                    records_written += 1
                    if bytes_written >= cfg.target_bytes:
                        break
                    if bytes_written >= next_progress:
                        elapsed = max(time.perf_counter() - started, 1e-9)
                        percent = min(100.0, (bytes_written / cfg.target_bytes) * 100.0)
                        spinner = spinner_chars[spinner_idx % len(spinner_chars)]
                        spinner_idx += 1
                        mb = bytes_written / (1024 * 1024)
                        rate = mb / elapsed
                        sys.stdout.write(
                            f"\r{percent:.2f}% {spinner} | {_human_bytes(bytes_written)} / {_human_bytes(cfg.target_bytes)} | {rate:.1f} MB/s | {records_written:,} records"
                        )
                        sys.stdout.flush()
                        next_progress += cfg.progress_every_mb * 1024 * 1024
                if bytes_written >= cfg.target_bytes:
                    break
                # reaction block (contiguous, optional)
                for mid in channel_message_ids:
                    for _ in range(cfg.reactions_per_message):
                        if rng.random() < 0.6:
                            # sparse-ish reactions
                            continue
                        rct_seq += 1
                        rid = f"rct_{rct_seq:012d}"
                        payload = {
                            "message": _ref("Message", mid),
                            "user": _ref("User", rng.choice(user_ids)),
                            "emoji": rng.choice(["👍", "❤️", "😂", "🔥", "🙏", "🎉"]),
                        }
                        bytes_written += _write_jsonl_line(
                            f, _record("Reaction", rid, ts0 + 40_000 + rct_seq, payload)
                        )
                        records_written += 1
                        if bytes_written >= next_progress:
                            elapsed = max(time.perf_counter() - started, 1e-9)
                            percent = min(100.0, (bytes_written / cfg.target_bytes) * 100.0)
                            spinner = spinner_chars[spinner_idx % len(spinner_chars)]
                            spinner_idx += 1
                            mb = bytes_written / (1024 * 1024)
                            rate = mb / elapsed
                            sys.stdout.write(
                                f"\r{percent:.2f}% {spinner} | {_human_bytes(bytes_written)} / {_human_bytes(cfg.target_bytes)} | {rate:.1f} MB/s | {records_written:,} records"
                            )
                            sys.stdout.flush()
                            next_progress += cfg.progress_every_mb * 1024 * 1024
                        if bytes_written >= cfg.target_bytes:
                            break
                    if bytes_written >= cfg.target_bytes:
                        break
            if not channel_ids:
                break
    # Final progress update to 100%
    percent = min(100.0, (bytes_written / cfg.target_bytes) * 100.0)
    spinner = spinner_chars[spinner_idx % len(spinner_chars)]
    elapsed = max(time.perf_counter() - started, 1e-9)
    mb = bytes_written / (1024 * 1024)
    rate = mb / elapsed
    sys.stdout.write(
        f"\r{percent:.2f}% {spinner} | {_human_bytes(bytes_written)} / {_human_bytes(cfg.target_bytes)} | {rate:.1f} MB/s | {records_written:,} records\n"
    )
    sys.stdout.flush()
    return {
        "path": str(db_path),
        "bytes": bytes_written,
        "records": records_written,
        "seed": cfg.seed,
        "users": cfg.users,
        "channels": cfg.channels,
        "groups": cfg.groups,
        "messages_per_channel": cfg.messages_per_channel,
        "reactions_per_message": cfg.reactions_per_message,
    }


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate a large chatdb.jsonl dataset")
    p.add_argument("--output", type=str, default=str(default_db_path()), help="Output JSONL path")
    p.add_argument("--target-gb", type=float, default=5.0, help="Target size in GB")
    p.add_argument("--target-mb", type=int, default=None, help="Target size in MB (overrides --target-gb)")
    p.add_argument("--quick", action="store_true", help="Fast mode (~25MB) for development")
    p.add_argument("--seed", type=int, default=1337, help="Deterministic RNG seed")
    p.add_argument("--users", type=int, default=50_000)
    p.add_argument("--channels", type=int, default=1_000)
    p.add_argument("--groups", type=int, default=250)
    p.add_argument("--messages-per-channel", type=int, default=5_000)
    p.add_argument("--reactions-per-message", type=int, default=2)
    p.add_argument("--max-text-len", type=int, default=240)
    p.add_argument("--progress-every-mb", type=int, default=100)
    return p.parse_args()


def main() -> int:
    args = _parse_args()
    if args.quick:
        target_bytes = 25 * 1024 * 1024
        # smaller/faster defaults
        users = min(args.users, 5_000)
        channels = min(args.channels, 50)
        groups = min(args.groups, 10)
        messages_per_channel = min(args.messages_per_channel, 500)
        reactions_per_message = min(args.reactions_per_message, 1)
        progress_every_mb = 5
    else:
        if args.target_mb is not None:
            target_bytes = int(args.target_mb) * 1024 * 1024
        else:
            target_bytes = int(args.target_gb * 1024 * 1024 * 1024)
        users = args.users
        channels = args.channels
        groups = args.groups
        messages_per_channel = args.messages_per_channel
        reactions_per_message = args.reactions_per_message
        progress_every_mb = args.progress_every_mb
    out = Path(args.output)
    cfg = GenConfig(
        target_bytes=target_bytes,
        seed=args.seed,
        users=users,
        channels=channels,
        groups=groups,
        messages_per_channel=messages_per_channel,
        reactions_per_message=reactions_per_message,
        max_text_len=args.max_text_len,
        progress_every_mb=progress_every_mb,
    )
    print(f"Generating chatdb JSONL -> {out}")
    print(f"Target size: {_human_bytes(cfg.target_bytes)} (quick={args.quick})")
    started = time.perf_counter()
    stats = generate(out, cfg)
    elapsed = max(time.perf_counter() - started, 1e-9)
    actual = os.path.getsize(out)
    print(
        "Done. "
        f"Wrote {_human_bytes(actual)} in {elapsed:.2f}s "
        f"({_human_bytes(int(actual / elapsed))}/s), records={stats['records']:,}"
    )
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
