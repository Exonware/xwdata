"""Small in-memory LRU cache used by chatdb_bigfile demos."""

from __future__ import annotations
from collections import OrderedDict
from dataclasses import dataclass
from typing import Generic, TypeVar
K = TypeVar("K")
V = TypeVar("V")
@dataclass


class CacheStats:
    hits: int = 0
    misses: int = 0


class LRUCache(Generic[K, V]):

    def __init__(self, capacity: int = 1024):
        if capacity <= 0:
            raise ValueError("capacity must be > 0")
        self._cap = capacity
        self._data: OrderedDict[K, V] = OrderedDict()
        self.stats = CacheStats()

    def get(self, key: K) -> V | None:
        if key in self._data:
            self._data.move_to_end(key)
            self.stats.hits += 1
            return self._data[key]
        self.stats.misses += 1
        return None

    def put(self, key: K, value: V) -> None:
        if key in self._data:
            self._data.move_to_end(key)
        self._data[key] = value
        if len(self._data) > self._cap:
            self._data.popitem(last=False)

    def __len__(self) -> int:
        return len(self._data)
