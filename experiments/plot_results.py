# experiments/plot_results.py
"""
Generate figures for the report: scalability, algorithm comparison,
statistical treatment (mean ± standard error). Saves to experiments/figures/.
"""
from __future__ import annotations
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

FIG_DIR = "experiments/figures"
RAW_STATIC = "experiments/results_static.csv"
RAW_DYNAMIC = "experiments/results_dynamic.csv"
SUMMARY_STATIC = "experiments/summary_static.csv"
SUMMARY_DYNAMIC = "experiments/summary_dynamic.csv"


def ensure_fig_dir():
    os.makedirs(FIG_DIR, exist_ok=True)


def se_from_var(var_series: pd.Series, n_runs: pd.Series) -> pd.Series:
    """Standard error = sqrt(variance / n)."""
    return np.sqrt(var_series / n_runs.clip(lower=1))


def plot_static_scalability():
    """Time and expanded nodes vs grid area (mean ± SE), by algorithm."""
    ensure_fig_dir()
    if not os.path.isfile(SUMMARY_STATIC):
        print("Run experiments first to generate summary_static.csv")
        return
    df = pd.read_csv(SUMMARY_STATIC)
    df["area"] = df["w"] * df["h"]
    df["time_se"] = se_from_var(df["time_s_var"], df["n_runs"])
    df["expanded_se"] = se_from_var(df["expanded_var"], df["n_runs"])

    g = df.groupby(["algo", "heuristic", "area"], dropna=False).agg(
        time_mean=("time_s_mean", "mean"),
        time_se=("time_se", "mean"),
        expanded_mean=("expanded_mean", "mean"),
        expanded_se=("expanded_se", "mean"),
    ).reset_index()

    for (algo, heur), sub in g.groupby(["algo", "heuristic"], dropna=False):
        sub = sub.sort_values("area")
        label = f"{algo}" if heur == "none" or pd.isna(heur) else f"{algo} ({heur})"
        plt.errorbar(
            sub["area"],
            sub["time_mean"],
            yerr=sub["time_se"],
            marker="o",
            capsize=3,
            label=label,
        )
    plt.xlabel("Grid area (w × h)")
    plt.ylabel("Runtime (s, mean ± SE)")
    plt.title("Static SSSP: Runtime vs grid size")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "static_time_vs_area.png"), dpi=150)
    plt.close()

    for (algo, heur), sub in g.groupby(["algo", "heuristic"], dropna=False):
        sub = sub.sort_values("area")
        label = f"{algo}" if heur == "none" or pd.isna(heur) else f"{algo} ({heur})"
        plt.errorbar(
            sub["area"],
            sub["expanded_mean"],
            yerr=sub["expanded_se"],
            marker="o",
            capsize=3,
            label=label,
        )
    plt.xlabel("Grid area (w × h)")
    plt.ylabel("Expanded nodes (mean ± SE)")
    plt.title("Static SSSP: Expanded nodes vs grid size")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "static_expanded_vs_area.png"), dpi=150)
    plt.close()


def plot_static_by_obstacle():
    """Runtime and expanded nodes vs obstacle probability (fixed size), with error bars."""
    ensure_fig_dir()
    if not os.path.isfile(SUMMARY_STATIC):
        return
    df = pd.read_csv(SUMMARY_STATIC)
    df["area"] = df["w"] * df["h"]
    df["time_se"] = se_from_var(df["time_s_var"], df["n_runs"])
    df["expanded_se"] = se_from_var(df["expanded_var"], df["n_runs"])

    # Pick one grid size for clarity (e.g. 100x100)
    mid = df["area"].median()
    sub = df[df["area"] == mid].copy()
    if sub.empty:
        sub = df[df["area"] == df["area"].min()].copy()
    sub = sub.sort_values(["p", "algo", "heuristic"])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    for (algo, heur), g in sub.groupby(["algo", "heuristic"], dropna=False):
        g = g.sort_values("p")
        lbl = f"{algo}" if heur == "none" or pd.isna(heur) else f"{algo} ({heur})"
        ax1.errorbar(g["p"], g["time_s_mean"], yerr=g["time_se"], marker="o", capsize=3, label=lbl)
        ax2.errorbar(g["p"], g["expanded_mean"], yerr=g["expanded_se"], marker="o", capsize=3, label=lbl)
    ax1.set_xlabel("Obstacle probability")
    ax1.set_ylabel("Runtime (s, mean ± SE)")
    ax1.set_title("Runtime vs obstacle probability")
    ax1.legend()
    ax2.set_xlabel("Obstacle probability")
    ax2.set_ylabel("Expanded nodes (mean ± SE)")
    ax2.set_title("Expanded nodes vs obstacle probability")
    ax2.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "static_vs_obstacle_p.png"), dpi=150)
    plt.close()


def plot_dynamic_comparison():
    """Dynamic: compare first_astar, rerun_after_add, repair_after_add (mean ± SE)."""
    ensure_fig_dir()
    if not os.path.isfile(SUMMARY_DYNAMIC):
        print("Run experiments first to generate summary_dynamic.csv")
        return
    df = pd.read_csv(SUMMARY_DYNAMIC)
    df["time_se"] = se_from_var(df["time_s_var"], df["n_runs"])
    df["expanded_se"] = se_from_var(df["expanded_var"], df["n_runs"])

    phases = ["first_astar", "rerun_after_add", "repair_after_add"]
    df = df[df["phase"].isin(phases)]
    if df.empty:
        return

    x = np.arange(len(phases))
    width = 0.35
    heuristics = df["heuristic"].dropna().unique().tolist()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    for i, heur in enumerate(heuristics):
        sub = df[df["heuristic"] == heur].set_index("phase").reindex(phases)
        off = (i - len(heuristics) / 2 + 0.5) * width
        t_vals = sub["time_s_mean"].values
        t_err = sub["time_se"].values
        e_vals = sub["expanded_mean"].values
        e_err = sub["expanded_se"].values
        ax1.bar(x + off, t_vals, width, yerr=t_err, capsize=3, label=heur)
        ax2.bar(x + off, e_vals, width, yerr=e_err, capsize=3, label=heur)
    ax1.set_xticks(x)
    ax1.set_xticklabels(phases, rotation=15, ha="right")
    ax1.set_ylabel("Runtime (s, mean ± SE)")
    ax1.set_title("Dynamic: runtime by phase")
    ax1.legend()
    ax2.set_xticks(x)
    ax2.set_xticklabels(phases, rotation=15, ha="right")
    ax2.set_ylabel("Expanded nodes (mean ± SE)")
    ax2.set_title("Dynamic: expanded nodes by phase")
    ax2.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "dynamic_phase_comparison.png"), dpi=150)
    plt.close()


def print_dynamic_summary():
    """Print dynamic summary table for report."""
    if not os.path.isfile(SUMMARY_DYNAMIC):
        return
    df = pd.read_csv(SUMMARY_DYNAMIC)
    df["time_se"] = se_from_var(df["time_s_var"], df["n_runs"])
    print("Dynamic summary (mean ± SE):")
    print(df.to_string())


def main():
    plot_static_scalability()
    plot_static_by_obstacle()
    plot_dynamic_comparison()
    print_dynamic_summary()
    print(f"Figures saved to {FIG_DIR}/")


if __name__ == "__main__":
    main()
