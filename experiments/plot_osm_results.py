from __future__ import annotations

import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


RAW_PATH = Path("experiments/results_osm.csv")
SUMMARY_PATH = Path("experiments/summary_osm.csv")
FIG_DIR = Path("experiments/figures_osm")


def _se(var_s: pd.Series, n_s: pd.Series) -> pd.Series:
    return np.sqrt(var_s / n_s.clip(lower=1))


def _short_graph_name(name: str) -> str:
    return name.replace("_new_jersey_usa_drive.graphml", "").replace(".graphml", "")


def plot_bars(summary: pd.DataFrame) -> None:
    summary = summary.copy()
    summary["graph_short"] = summary["graph"].map(_short_graph_name)
    summary["time_se"] = _se(summary["time_s_var"], summary["n_runs"])
    summary["expanded_se"] = _se(summary["expanded_var"], summary["n_runs"])

    graphs = summary["graph_short"].drop_duplicates().tolist()
    x = np.arange(len(graphs))
    width = 0.35

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.3))
    for i, algo in enumerate(["dijkstra", "astar"]):
        sub = summary[summary["algo"] == algo].set_index("graph_short").reindex(graphs)
        off = (i - 0.5) * width
        ax1.bar(
            x + off,
            sub["time_s_mean"].values,
            width,
            yerr=sub["time_se"].values,
            capsize=3,
            label=algo,
        )
        ax2.bar(
            x + off,
            sub["expanded_mean"].values,
            width,
            yerr=sub["expanded_se"].values,
            capsize=3,
            label=algo,
        )

    ax1.set_xticks(x)
    ax1.set_xticklabels(graphs, rotation=10, ha="right")
    ax1.set_ylabel("Runtime (s, mean ± SE)")
    ax1.set_title("OSM: Runtime by graph")
    ax1.legend()

    ax2.set_xticks(x)
    ax2.set_xticklabels(graphs, rotation=10, ha="right")
    ax2.set_ylabel("Expanded nodes (mean ± SE)")
    ax2.set_title("OSM: Expanded nodes by graph")
    ax2.legend()

    plt.tight_layout()
    plt.savefig(FIG_DIR / "osm_bar_runtime_expanded.png", dpi=160)
    plt.close(fig)


def plot_pair_scatter(raw: pd.DataFrame) -> None:
    # aggregate by graph + pair + algo over repeated runs
    pair_mean = (
        raw.groupby(["graph", "pair_id", "algo"], dropna=False)
        .agg(
            dist_m=("dist_m", "mean"),
            time_s=("time_s", "mean"),
            expanded=("expanded", "mean"),
        )
        .reset_index()
    )
    pair_mean["graph_short"] = pair_mean["graph"].map(_short_graph_name)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.3), sharey=True)
    for ax, graph in zip(axes, pair_mean["graph_short"].drop_duplicates()):
        g = pair_mean[pair_mean["graph_short"] == graph]
        for algo, color in [("dijkstra", "tab:blue"), ("astar", "tab:orange")]:
            sub = g[g["algo"] == algo]
            ax.scatter(sub["dist_m"], sub["time_s"], s=30, alpha=0.75, label=algo, color=color)
        ax.set_title(graph)
        ax.set_xlabel("Shortest-path distance (m)")
        ax.grid(alpha=0.25)
    axes[0].set_ylabel("Runtime per pair (s)")
    axes[0].legend()
    plt.suptitle("OSM: Runtime vs path distance")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "osm_scatter_runtime_vs_dist.png", dpi=160)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.3), sharey=True)
    for ax, graph in zip(axes, pair_mean["graph_short"].drop_duplicates()):
        g = pair_mean[pair_mean["graph_short"] == graph]
        for algo, color in [("dijkstra", "tab:blue"), ("astar", "tab:orange")]:
            sub = g[g["algo"] == algo]
            ax.scatter(sub["dist_m"], sub["expanded"], s=30, alpha=0.75, label=algo, color=color)
        ax.set_title(graph)
        ax.set_xlabel("Shortest-path distance (m)")
        ax.grid(alpha=0.25)
    axes[0].set_ylabel("Expanded nodes per pair")
    axes[0].legend()
    plt.suptitle("OSM: Expanded nodes vs path distance")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "osm_scatter_expanded_vs_dist.png", dpi=160)
    plt.close(fig)


def print_key_conclusions(summary: pd.DataFrame) -> None:
    print("\nKey OSM conclusions:")
    for graph in summary["graph"].drop_duplicates():
        g = summary[summary["graph"] == graph].set_index("algo")
        if "dijkstra" not in g.index or "astar" not in g.index:
            continue
        td = float(g.loc["dijkstra", "time_s_mean"])
        ta = float(g.loc["astar", "time_s_mean"])
        ed = float(g.loc["dijkstra", "expanded_mean"])
        ea = float(g.loc["astar", "expanded_mean"])
        speedup = td / ta if ta > 0 else float("inf")
        expand_reduction = (ed - ea) / ed * 100.0 if ed > 0 else 0.0
        print(
            f"- {_short_graph_name(graph)}: "
            f"A* is {speedup:.2f}x faster, expanded nodes reduced by {expand_reduction:.1f}%."
        )


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    if not RAW_PATH.exists() or not SUMMARY_PATH.exists():
        print("Missing OSM CSVs. Please run: python run_osm_experiments.py")
        return

    raw = pd.read_csv(RAW_PATH)
    summary = pd.read_csv(SUMMARY_PATH)

    plot_bars(summary)
    plot_pair_scatter(raw)
    print_key_conclusions(summary)
    print(f"\nSaved OSM figures to: {FIG_DIR}")


if __name__ == "__main__":
    main()
