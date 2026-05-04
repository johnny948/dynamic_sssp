# src/dynamic.py
from __future__ import annotations
from typing import Tuple, Callable, Optional, Dict, Set, List
from .graph import GridMap, Coord
from .astar import astar, manhattan, euclidean

def toggle_obstacle_on_path(grid: GridMap, path: List[Coord], index: int, blocked: bool) -> Optional[Coord]:
    """force change one cell on path (not start/goal)"""
    if path is None or len(path) < 3:
        return None
    idx = max(1, min(len(path)-2, index))
    x, y = path[idx]
    grid.blocked[y][x] = blocked
    return (x, y)

def rerun_astar(grid: GridMap, start: Coord, goal: Coord,
               h: Callable[[Coord, Coord], float]):
    return astar(grid, start, goal, h=h)

def incremental_repair_like(grid: GridMap, start: Coord, goal: Coord,
                            h: Callable[[Coord, Coord], float],
                            changed: Coord,
                            prev_path: Optional[List[Coord]]):
    """
    Simplified incremental repair:
    - If changed not on/near previous path, just return previous path.
    - Otherwise rerun A* but with a "warm start" idea: reduce search by
      restricting expansion to a bounding box around old path + changed.
    This is NOT full LPA*, but demonstrates incremental-style speedups
    and is easy to justify/implement for coursework.
    """
    if prev_path is None:
        return astar(grid, start, goal, h=h)

    # quick relevance check
    if changed not in set(prev_path):
        # still might affect if near path; keep simple
        return prev_path, float("nan"), {"expanded": 0, "relaxed": 0, "visited": 0, "note": "unchanged"}

    xs = [p[0] for p in prev_path] + [changed[0], start[0], goal[0]]
    ys = [p[1] for p in prev_path] + [changed[1], start[1], goal[1]]
    minx, maxx = max(0, min(xs)-5), min(grid.w-1, max(xs)+5)
    miny, maxy = max(0, min(ys)-5), min(grid.h-1, max(ys)+5)

    # Create a wrapper grid that only allows nodes within the box (outside treated as blocked)
    class BoxGrid(GridMap):
        def passable(self, p: Coord) -> bool:
            x, y = p
            if x < minx or x > maxx or y < miny or y > maxy:
                return False
            return super().passable(p)

    boxgrid = BoxGrid(w=grid.w, h=grid.h, blocked=grid.blocked, allow_diagonal=grid.allow_diagonal)
    path, dist, stats = astar(boxgrid, start, goal, h=h)
    stats["note"] = "boxed_repair"
    return path, dist, stats