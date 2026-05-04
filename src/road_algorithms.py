from __future__ import annotations

import math
from typing import Any, Dict, Iterable, Optional, Tuple

from .pq import BinaryMinHeap

Node = Any


def _best_out_edges(graph: Any, u: Node) -> Iterable[Tuple[Node, float]]:
    """
    Yield (v, w) with the minimum 'length' for each neighbor v.
    Works for networkx MultiDiGraph adjacency layout used by OSMnx.
    """
    nbrs = graph.adj[u]
    for v, key_map in nbrs.items():
        best = float("inf")
        for _, attrs in key_map.items():
            w = float(attrs.get("length", 1.0))
            if w < best:
                best = w
        if best < float("inf"):
            yield v, best


def _reconstruct(parent: Dict[Node, Optional[Node]], start: Node, goal: Node):
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


def _geo_heuristic(graph: Any, a: Node, b: Node) -> float:
    """
    Approximate metric distance in meters from lon/lat attributes x/y.
    """
    ax, ay = float(graph.nodes[a].get("x", 0.0)), float(graph.nodes[a].get("y", 0.0))
    bx, by = float(graph.nodes[b].get("x", 0.0)), float(graph.nodes[b].get("y", 0.0))
    lat = math.radians((ay + by) * 0.5)
    meters_per_deg_lon = 111320.0 * math.cos(lat)
    meters_per_deg_lat = 110540.0
    dx = (ax - bx) * meters_per_deg_lon
    dy = (ay - by) * meters_per_deg_lat
    return math.hypot(dx, dy)


def dijkstra_road(graph: Any, start: Node, goal: Node):
    pq = BinaryMinHeap()
    dist: Dict[Node, float] = {start: 0.0}
    parent: Dict[Node, Optional[Node]] = {start: None}
    closed = set()
    pq.push(start, 0.0)

    expanded = 0
    relaxed = 0

    while len(pq) > 0:
        dcur, cur = pq.pop()
        if cur in closed:
            continue
        closed.add(cur)
        expanded += 1

        if cur == goal:
            path = _reconstruct(parent, start, goal)
            return path, dist[cur], {"expanded": expanded, "relaxed": relaxed, "visited": len(dist)}

        for nxt, w in _best_out_edges(graph, cur):
            nd = dcur + w
            if nxt not in dist or nd < dist[nxt]:
                dist[nxt] = nd
                parent[nxt] = cur
                relaxed += 1
                pq.push(nxt, nd)

    return None, float("inf"), {"expanded": expanded, "relaxed": relaxed, "visited": len(dist)}


def astar_road(graph: Any, start: Node, goal: Node):
    pq = BinaryMinHeap()
    g: Dict[Node, float] = {start: 0.0}
    parent: Dict[Node, Optional[Node]] = {start: None}
    closed = set()
    pq.push(start, _geo_heuristic(graph, start, goal))

    expanded = 0
    relaxed = 0

    while len(pq) > 0:
        _, cur = pq.pop()
        if cur in closed:
            continue
        closed.add(cur)
        expanded += 1

        if cur == goal:
            path = _reconstruct(parent, start, goal)
            return path, g[cur], {"expanded": expanded, "relaxed": relaxed, "visited": len(g)}

        for nxt, w in _best_out_edges(graph, cur):
            ng = g[cur] + w
            if nxt not in g or ng < g[nxt]:
                g[nxt] = ng
                parent[nxt] = cur
                relaxed += 1
                pq.push(nxt, ng + _geo_heuristic(graph, nxt, goal))

    return None, float("inf"), {"expanded": expanded, "relaxed": relaxed, "visited": len(g)}
