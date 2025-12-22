"""Append-only log for fast atomic updates with fallback to full rewrite.

This module provides an append-only log system for atomic updates,
with automatic fallback to full file rewrite if append-only log is unavailable.
"""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from typing import Any, Callable

# Import original atomic update as fallback
from db_io import atomic_update_record_by_key as atomic_update_full_rewrite


class AppendOnlyLog:
    """Append-only log for fast atomic updates with in-memory index."""
    
    def __init__(self, db_path: Path, log_path: Path | None = None):
        self.db_path = db_path
        self.log_path = log_path or db_path.with_suffix(db_path.suffix + '.log')
        self._lock = threading.Lock()
        self._log_index: dict[str, int] = {}  # key -> byte offset in log file
        self._log_cache: dict[str, dict[str, Any]] = {}  # key -> latest log entry
        self._compaction_threshold_mb = 100
        self._load_log_index()
    
    def _load_log_index(self):
        """Load log index from file (build in-memory index for O(1) lookups)."""
        if not self.log_path.exists():
            return
        
        try:
            import json
            with open(self.log_path, 'rb') as f:
                offset = 0
                for line in f:
                    line_start = offset
                    line = line.strip()
                    if not line:
                        offset = f.tell()
                        continue
                    
                    try:
                        entry = json.loads(line)
                        key = f"{entry.get('type')}:{entry.get('id')}"
                        # Update index (latest entry wins)
                        self._log_index[key] = line_start
                        self._log_cache[key] = entry
                    except Exception:
                        pass
                    
                    offset = f.tell()
        except Exception:
            pass
    
    def update_record(
        self,
        type_name: str,
        id_value: str,
        updater: Callable[[dict[str, Any]], dict[str, Any]],
    ) -> int:
        """
        Update record by appending to log (O(1) operation).
        
        Returns:
            Number of records updated (always 1 for append-only log)
        """
        key = f"{type_name}:{id_value}"
        
        # Read base record from main file (if exists)
        base_record = None
        try:
            from db_io import read_record_by_key, load_index, default_index_path
            index = load_index(default_index_path())
            base_record = read_record_by_key(self.db_path, index, type_name, id_value)
        except Exception:
            # Record might not exist, or index not available
            pass
        
        # Apply updater to get updated record
        if base_record:
            updated_record = updater(base_record.copy())
        else:
            # Create new record
            updated_record = {'@type': type_name, 'id': id_value}
            updated_record = updater(updated_record)
        
        # Create log entry with full updated record
        log_entry = {
            'type': type_name,
            'id': id_value,
            'timestamp': time.time(),
            'record': updated_record,  # Store full updated record
        }
        
        with self._lock:
            # Append to log file (FAST - just append)
            try:
                with open(self.log_path, 'a', encoding='utf-8') as f:
                    entry_json = json.dumps(log_entry, ensure_ascii=False)
                    log_offset = f.tell()
                    f.write(entry_json + '\n')
                    f.flush()
                
                # Update in-memory index (O(1))
                self._log_index[key] = log_offset
                self._log_cache[key] = log_entry
                
            except Exception as e:
                raise RuntimeError(f"Failed to write to append-only log: {e}") from e
            
            # Check if compaction is needed
            if self.log_path.exists():
                log_size_mb = self.log_path.stat().st_size / (1024 * 1024)
                if log_size_mb > self._compaction_threshold_mb:
                    # Trigger background compaction (non-blocking)
                    threading.Thread(target=self._compact_background, daemon=True).start()
        
        return 1
    
    def read_record(self, type_name: str, id_value: str) -> dict[str, Any] | None:
        """
        Read record (check log first using O(1) index lookup).
        
        Args:
            type_name: Record type
            id_value: Record ID
        
        Returns:
            Latest record from log, or None if not in log
        """
        key = f"{type_name}:{id_value}"
        
        with self._lock:
            # Check in-memory cache first (O(1))
            if key in self._log_cache:
                entry = self._log_cache[key]
                return entry.get('record')  # Return the stored record
            
            # Check log file using index (O(1) lookup, not full scan)
            if key in self._log_index:
                log_offset = self._log_index[key]
                try:
                    with open(self.log_path, 'rb') as f:
                        f.seek(log_offset)
                        line = f.readline()
                        if line:
                            entry = json.loads(line.strip())
                            record = entry.get('record')
                            self._log_cache[key] = entry
                            return record
                except Exception:
                    pass
        
        # Not in log, return None (caller should read from main file)
        return None
    
    def _compact_background(self):
        """Merge log into main file (background thread)."""
        try:
            print(f"Starting background compaction of append-only log...")
            print(f"  Log entries: {len(self._log_index)}")
            print(f"  This would merge log into main file and clear log")
            # In a full implementation, this would:
            # 1. Read all log entries (grouped by key, latest wins)
            # 2. Read main file
            # 3. Apply updates
            # 4. Write new main file atomically
            # 5. Clear log file and index
        except Exception as e:
            print(f"Compaction failed: {e}")


def atomic_update_record_by_key_append_log(
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
        use_append_log: If True, use append-only log; if None, auto-detect
    
    Returns:
        Number of records updated
    """
    # Auto-detect: use append-only log for files >100MB
    if use_append_log is None:
        if db_path.exists():
            file_size_mb = db_path.stat().st_size / (1024 * 1024)
            use_append_log = file_size_mb > 100
        else:
            use_append_log = False
    
    # Use append-only log if requested
    if use_append_log:
        try:
            log = AppendOnlyLog(db_path)
            return log.update_record(type_name, id_value, updater)
        except Exception as e:
            print(f"Append-only log failed, falling back to full rewrite: {e}")
            # Fall through to full rewrite
    
    # Fall back to full rewrite (original implementation)
    return atomic_update_full_rewrite(
        db_path,
        type_name,
        id_value,
        updater=updater,
        backup=backup,
    )
