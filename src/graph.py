# src/graph.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, List, Tuple, Dict, Optional

Coord = Tuple[int, int]

@dataclass
class GridMap:
    w: int
    h: int
    blocked: List[List[bool]]  # True = obstacle
    allow_diagonal: bool = False

    def in_bounds(self, p: Coord) -> bool:
        x, y = p
        return 0 <= x < self.w and 0 <= y < self.h

    def passable(self, p: Coord) -> bool:
        x, y = p
        return not self.blocked[y][x]

    def neighbors(self, p: Coord) -> Iterable[Tuple[Coord, float]]:
        x, y = p
        steps4 = [(1,0),(-1,0),(0,1),(0,-1)]
        steps8 = steps4 + [(1,1),(1,-1),(-1,1),(-1,-1)]
        steps = steps8 if self.allow_diagonal else steps4

        for dx, dy in steps:
            q = (x + dx, y + dy)
            if not self.in_bounds(q) or not self.passable(q):
                continue
            # cost: 1 for cardinal, sqrt(2) for diagonal
            if dx != 0 and dy != 0:
                cost = 2 ** 0.5
            else:
                cost = 1.0
            yield q, cost