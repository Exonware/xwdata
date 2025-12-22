"""Benchmark atomic updates: append-only log vs full rewrite."""

from __future__ import annotations

import sys
import time
from pathlib import Path

# Ensure we can import local operations modules directly
_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

# Now we can import db_io as a local module
import db_io


def _bench(mode: str, use_append_log: bool | None, n_updates: int = 10) -> None:
    db_path = db_io.default_db_path()
    print(f"Mode={mode}, use_append_log={use_append_log}, file={db_path}")

    def _updater(rec: dict) -> dict:
        v = rec.get("views", 0)
        rec["views"] = v + 1
        return rec

    started = time.perf_counter()
    total = 0
    for i in range(n_updates):
        # Just re-update the same id; we care about throughput, not semantics
        updated = db_io.atomic_update_record_by_key(
            db_path,
            "Message",
            "msg_0",
            updater=_updater,
            use_append_log=use_append_log,
        )
        total += updated
    elapsed = max(time.perf_counter() - started, 1e-9)
    print(f"  Updates={total}, time={elapsed:.2f}s, updates/s={total/elapsed:,.0f}")


def main() -> int:
    print("=" * 70)
    print("ATOMIC UPDATE BENCHMARK (append-only log vs full rewrite)")
    print("=" * 70)
    print()

    # Warm-up
    _bench("warmup-append", use_append_log=True, n_updates=1)
    _bench("warmup-full", use_append_log=False, n_updates=1)

    print()
    print("Running main benchmark (10 updates each)...")

    _bench("append-only", use_append_log=True, n_updates=10)
    _bench("full-rewrite", use_append_log=False, n_updates=10)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
