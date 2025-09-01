
from __future__ import annotations
from typing import Any, Dict, Optional, Tuple
from collections import OrderedDict
import threading

class RadixNode:
    __slots__ = ("children", "value")
    def __init__(self):
        self.children: Dict[str, 'RadixNode'] = {}
        self.value: Optional[Any] = None

class RadixTrieCache:
    """
    Simple Radix Trie + LRU entry list.
    Key is a string (e.g., prompt or its normalized prefix). Value is any serializable object.
    Thread-safe for concurrent get/put. Capacity is number of stored keys (not bytes) for MVP.
    """
    def __init__(self, capacity:int=2048):
        self.root = RadixNode()
        self.capacity = max(8, int(capacity))
        self._lru = OrderedDict()   # key -> True
        self._lock = threading.RLock()

    def _touch(self, key:str):
        if key in self._lru:
            self._lru.move_to_end(key)
        else:
            self._lru[key] = True
            if len(self._lru) > self.capacity:
                self._lru.popitem(last=False)  # prune oldest key from LRU (trie nodes not reclaimed in MVP)

    def _find_node(self, key:str) -> Optional[RadixNode]:
        node = self.root
        for ch in key:
            nxt = node.children.get(ch)
            if nxt is None:
                return None
            node = nxt
        return node

    def put(self, key:str, value:Any):
        with self._lock:
            node = self.root
            for ch in key:
                node = node.children.setdefault(ch, RadixNode())
            node.value = value
            self._touch(key)

    def get(self, key:str) -> Optional[Any]:
        with self._lock:
            node = self._find_node(key)
            if node and (node.value is not None):
                self._touch(key)
                return node.value
            return None

    def longest_matching_prefix(self, key:str) -> int:
        node = self.root
        best = -1
        for i, ch in enumerate(key):
            node = node.children.get(ch)
            if node is None:
                break
            if node.value is not None:
                best = i
        return best + 1

    def get_with_lmp(self, key:str) -> Tuple[int, Optional[Any]]:
        with self._lock:
            m = self.longest_matching_prefix(key)
            if m <= 0:
                return 0, None
            val = self.get(key[:m])  # reuses _touch
            return m, val
