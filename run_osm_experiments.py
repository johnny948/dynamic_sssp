from __future__ import annotations

import random
from pathlib import Path
from typing import Any, Dict, List, Tuple

import osmnx as ox

from src.metrics import summarize
from src.road_algorithms import astar_road, dijkstra_road
from src.utils import load_json, perf_time, write_csv


def _sample_pairs(nodes: List[Any], k: int, rng: random.Random) -> List[Tuple[Any, Any]]:
    pairs: List[Tuple[Any, Any]] = []
    if len(nodes) < 2:
        return pairs
    for _ in range(k):
        s = rng.choice(nodes)
        t = rng.choice(nodes)
        while t == s:
            t = rng.choice(nodes)
        pairs.append((s, t))
    return pairs


def run_osm(cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    rng = random.Random(int(cfg.get("seed", 42)))
    pairs_per_graph = int(cfg.get("pairs_per_graph", 20))
    runs_per_pair = int(cfg.get("runs_per_pair", 1))
    algos = cfg.get("algorithms", ["dijkstra", "astar"])

    for graphml_path in cfg["graphml_paths"]:
        p = Path(graphml_path)
        if not p.exists():
            print(f"Skip missing GraphML: {graphml_path}")
            continue

        graph = ox.load_graphml(graphml_path)
        graph = ox.convert.to_undirected(graph)
        nodes = list(graph.nodes())
        pairs = _sample_pairs(nodes, pairs_per_graph, rng)

        for pair_id, (start, goal) in enumerate(pairs):
            for run_id in range(runs_per_pair):
                for algo in algos:
                    t0 = perf_time()
                    if algo == "dijkstra":
                        path, dist, stats = dijkstra_road(graph, start, goal)
                    elif algo == "astar":
                        path, dist, stats = astar_road(graph, start, goal)
                    else:
                        raise ValueError(f"Unknown algorithm: {algo}")
                    t1 = perf_time()

                    rows.append(
                        {
                            "graph": p.name,
                            "algo": algo,
                            "pair_id": pair_id,
                            "run_id": run_id,
                            "time_s": t1 - t0,
                            "dist_m": dist,
                            "path_len_nodes": len(path) if path else 0,
                            "reachable": bool(path is not None),
                            **stats,
                        }
                    )
    return rows


def main() -> None:
    cfg = load_json("experiments/osm_configs.json")
    rows = run_osm(cfg)
    if not rows:
        print("No OSM rows generated. Check GraphML paths in experiments/osm_configs.json")
        return

    write_csv("experiments/results_osm.csv", rows)
    summary = summarize(
        rows,
        group_by=["graph", "algo"],
        metrics=["time_s", "dist_m", "path_len_nodes", "expanded", "relaxed", "visited"],
    )
    write_csv("experiments/summary_osm.csv", summary)

    print("Done.")
    print("Wrote: experiments/results_osm.csv")
    print("Wrote: experiments/summary_osm.csv")


if __name__ == "__main__":
    main()
