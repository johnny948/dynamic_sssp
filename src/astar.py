# src/astar.py
from __future__ import annotations
from typing import Dict, Tuple, Optional, Callable, Any
from .pq import BinaryMinHeap
from .graph import GridMap, Coord

def manhattan(a: Coord, b: Coord) -> float:
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def euclidean(a: Coord, b: Coord) -> float:
    dx, dy = a[0]-b[0], a[1]-b[1]
    return (dx*dx + dy*dy) ** 0.5

def reconstruct_path(parent: Dict[Coord, Optional[Coord]], start: Coord, goal: Coord):
    if goal not in parent:
        return None
    cur = goal
    path = [cur]
    while cur != start:
        cur = parent[cur]
        if cur is None:
            return None
        path.append(cur)
    path.reverse()
    return path

def astar(grid: GridMap, start: Coord, goal: Coord,
          h: Callable[[Coord, Coord], float] = manhattan):
    """
    Returns:
      path, dist, stats
    stats:
      expanded: popped from pq
      relaxed: edge relax attempts that improved
      visited: number of nodes that got a g-score
    """
    openpq = BinaryMinHeap()
    g: Dict[Coord, float] = {start: 0.0}
    parent: Dict[Coord, Optional[Coord]] = {start: None}

    openpq.push(start, h(start, goal))  # f = g+h, here g=0
    expanded = 0
    relaxed = 0

    closed = set()

    while len(openpq) > 0:
        fcur, cur = openpq.pop()
        if cur in closed:
            continue
        closed.add(cur)
        expanded += 1

        if cur == goal:
            path = reconstruct_path(parent, start, goal)
            return path, g[cur], {"expanded": expanded, "relaxed": relaxed, "visited": len(g)}

        for nxt, w in grid.neighbors(cur):
            ng = g[cur] + w
            if nxt not in g or ng < g[nxt]:
                g[nxt] = ng
                parent[nxt] = cur
                relaxed += 1
                openpq.push(nxt, ng + h(nxt, goal))

    return None, float("inf"), {"expanded": expanded, "relaxed": relaxed, "visited": len(g)}