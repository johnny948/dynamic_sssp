# src/generators.py
from __future__ import annotations
import random
from typing import Tuple
from .graph import GridMap

def make_random_grid(w: int, h: int, obstacle_p: float, seed: int,
                     allow_diagonal: bool = False) -> GridMap:
    rng = random.Random(seed)
    blocked = []
    for y in range(h):
        row = []
        for x in range(w):
            row.append(rng.random() < obstacle_p)
        blocked.append(row)
    return GridMap(w=w, h=h, blocked=blocked, allow_diagonal=allow_diagonal)

def ensure_free(grid: GridMap, start: Tuple[int,int], goal: Tuple[int,int]) -> None:
    sx, sy = start
    gx, gy = goal
    grid.blocked[sy][sx] = False
    grid.blocked[gy][gx] = False