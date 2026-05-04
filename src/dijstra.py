# src/dijkstra.py
from __future__ import annotations
from typing import Dict, Optional, Tuple
from .pq import BinaryMinHeap
from .graph import GridMap, Coord
from .astar import reconstruct_path

def dijkstra(grid: GridMap, start: Coord, goal: Coord):
    """
    Dijkstra on grid with Binary Heap + decrease-key.
    Returns path, dist, stats
    """
    pq = BinaryMinHeap()
    dist: Dict[Coord, float] = {start: 0.0}
    parent: Dict[Coord, Optional[Coord]] = {start: None}
    pq.push(start, 0.0)

    expanded = 0
    relaxed = 0
    closed = set()

    while len(pq) > 0:
        dcur, cur = pq.pop()
        if cur in closed:
            continue
        closed.add(cur)
        expanded += 1

        if cur == goal:
            path = reconstruct_path(parent, start, goal)
            return path, dist[cur], {"expanded": expanded, "relaxed": relaxed, "visited": len(dist)}

        for nxt, w in grid.neighbors(cur):
            nd = dist[cur] + w
            if nxt not in dist or nd < dist[nxt]:
                dist[nxt] = nd
                parent[nxt] = cur
                relaxed += 1
                pq.push(nxt, nd)

    return None, float("inf"), {"expanded": expanded, "relaxed": relaxed, "visited": len(dist)}