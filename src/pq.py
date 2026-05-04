# src/pq.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Any

@dataclass
class HeapItem:
    key: float
    node: Any

class BinaryMinHeap:
    """
    Min-heap with decrease-key via position map.
    Operations:
      - push(node, key)
      - pop() -> (key, node)
      - decrease_key(node, new_key)
    """
    def __init__(self) -> None:
        self.a: List[HeapItem] = []
        self.pos: Dict[Any, int] = {}  # node -> index in a

    def __len__(self) -> int:
        return len(self.a)

    def _swap(self, i: int, j: int) -> None:
        self.a[i], self.a[j] = self.a[j], self.a[i]
        self.pos[self.a[i].node] = i
        self.pos[self.a[j].node] = j

    def _sift_up(self, i: int) -> None:
        while i > 0:
            p = (i - 1) // 2
            if self.a[p].key <= self.a[i].key:
                break
            self._swap(p, i)
            i = p

    def _sift_down(self, i: int) -> None:
        n = len(self.a)
        while True:
            l = 2 * i + 1
            r = 2 * i + 2
            m = i
            if l < n and self.a[l].key < self.a[m].key:
                m = l
            if r < n and self.a[r].key < self.a[m].key:
                m = r
            if m == i:
                break
            self._swap(i, m)
            i = m

    def push(self, node: Any, key: float) -> None:
        if node in self.pos:
            # treat as decrease-key if better
            if key < self.a[self.pos[node]].key:
                self.decrease_key(node, key)
            return
        self.a.append(HeapItem(key=key, node=node))
        self.pos[node] = len(self.a) - 1
        self._sift_up(len(self.a) - 1)

    def pop(self) -> Tuple[float, Any]:
        if not self.a:
            raise IndexError("pop from empty heap")
        self._swap(0, len(self.a) - 1)
        item = self.a.pop()
        self.pos.pop(item.node, None)
        if self.a:
            self._sift_down(0)
        return item.key, item.node

    def decrease_key(self, node: Any, new_key: float) -> None:
        i = self.pos.get(node)
        if i is None:
            self.push(node, new_key)
            return
        if new_key >= self.a[i].key:
            return
        self.a[i].key = new_key
        self._sift_up(i)