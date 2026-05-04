# run_experiments.py
from __future__ import annotations
from typing import Dict, Any, List
from src.utils import load_json, perf_time, write_csv
from src.metrics import summarize
from src.generators import make_random_grid, ensure_free
from src.dijstra import dijkstra
from src.astar import astar, manhattan, euclidean
from src.dynamic import toggle_obstacle_on_path, rerun_astar, incremental_repair_like

def run_static(cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    diag = bool(cfg.get("allow_diagonal", False))
    algos = cfg["algorithms"]
    heuristics = cfg["heuristics"]
    runs_per = int(cfg.get("runs_per_config", 1))

    for (w, h) in cfg["grid_sizes"]:
        for p in cfg["obstacle_ps"]:
            for seed in cfg["seeds"]:
                start = (0, 0)
                goal = (w - 1, h - 1)
                grid = make_random_grid(w, h, p, seed, allow_diagonal=diag)
                ensure_free(grid, start, goal)

                for algo in algos:
                    if algo == "dijkstra":
                        for run_id in range(runs_per):
                            t0 = perf_time()
                            path, dist, stats = dijkstra(grid, start, goal)
                            t1 = perf_time()
                            rows.append({
                                "run_id": run_id, "w": w, "h": h, "p": p, "seed": seed, "diag": diag,
                                "algo": "dijkstra", "heuristic": "none",
                                "time_s": t1 - t0,
                                "dist": dist,
                                "path_len_nodes": len(path) if path else 0,
                                **stats
                            })
                    elif algo == "astar":
                        for heur in heuristics:
                            hfun = manhattan if heur == "manhattan" else euclidean
                            for run_id in range(runs_per):
                                t0 = perf_time()
                                path, dist, stats = astar(grid, start, goal, h=hfun)
                                t1 = perf_time()
                                rows.append({
                                    "run_id": run_id, "w": w, "h": h, "p": p, "seed": seed, "diag": diag,
                                    "algo": "astar", "heuristic": heur,
                                    "time_s": t1 - t0,
                                    "dist": dist,
                                    "path_len_nodes": len(path) if path else 0,
                                    **stats
                                })
                    else:
                        raise ValueError(f"Unknown algo: {algo}")
    return rows

def run_dynamic(cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    w, h = cfg["grid_size"]
    p = cfg["obstacle_p"]
    diag = bool(cfg.get("allow_diagonal", False))
    toggle_ratio = float(cfg.get("toggle_index_ratio", 0.5))
    runs_per = int(cfg.get("runs_per_config", 1))

    for seed in cfg["seeds"]:
        for run_id in range(runs_per):
            grid = make_random_grid(w, h, p, seed, allow_diagonal=diag)
            start = (0, 0)
            goal = (w - 1, h - 1)
            ensure_free(grid, start, goal)

            for heur in cfg["heuristics"]:
                hfun = manhattan if heur == "manhattan" else euclidean

                t0 = perf_time()
                path1, dist1, s1 = astar(grid, start, goal, h=hfun)
                t1 = perf_time()
                rows.append({
                    "run_id": run_id, "seed": seed, "w": w, "h": h, "p": p, "diag": diag,
                    "heuristic": heur, "phase": "first_astar",
                    "time_s": t1 - t0, "dist": dist1,
                    "path_len_nodes": len(path1) if path1 else 0,
                    **s1
                })

                if path1 and len(path1) >= 3:
                    idx = int(len(path1) * toggle_ratio)
                else:
                    idx = 1
                changed = toggle_obstacle_on_path(grid, path1, index=idx, blocked=True)

                t2 = perf_time()
                path2, dist2, s2 = rerun_astar(grid, start, goal, hfun)
                t3 = perf_time()
                rows.append({
                    "run_id": run_id, "seed": seed, "w": w, "h": h, "p": p, "diag": diag,
                    "heuristic": heur, "phase": "rerun_after_add",
                    "time_s": t3 - t2, "dist": dist2,
                    "path_len_nodes": len(path2) if path2 else 0,
                    **s2
                })

                t4 = perf_time()
                path3, dist3, s3 = incremental_repair_like(grid, start, goal, hfun, changed, path1)
                t5 = perf_time()
                rows.append({
                    "run_id": run_id, "seed": seed, "w": w, "h": h, "p": p, "diag": diag,
                    "heuristic": heur, "phase": "repair_after_add",
                    "time_s": t5 - t4, "dist": dist3,
                    "path_len_nodes": len(path3) if path3 else 0,
                    **{k: v for k, v in s3.items() if k in ("expanded", "relaxed", "visited", "note")}
                })

    return rows

def main():
    cfg = load_json("experiments/configs.json")
    static_rows = run_static(cfg["static"])
    write_csv("experiments/results_static.csv", static_rows)
    static_summary = summarize(
        static_rows,
        group_by=["w", "h", "p", "algo", "heuristic"],
        metrics=["time_s", "expanded", "relaxed", "visited", "path_len_nodes", "dist"],
    )
    write_csv("experiments/summary_static.csv", static_summary)

    dynamic_rows = run_dynamic(cfg["dynamic"])
    write_csv("experiments/results_dynamic.csv", dynamic_rows)
    dynamic_summary = summarize(
        dynamic_rows,
        group_by=["heuristic", "phase"],
        metrics=["time_s", "expanded", "relaxed", "visited", "path_len_nodes", "dist"],
    )
    write_csv("experiments/summary_dynamic.csv", dynamic_summary)

    print("Done.")
    print("Wrote: experiments/results_static.csv")
    print("Wrote: experiments/summary_static.csv")
    print("Wrote: experiments/results_dynamic.csv")
    print("Wrote: experiments/summary_dynamic.csv")

if __name__ == "__main__":
    main()