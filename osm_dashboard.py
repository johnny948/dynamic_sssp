from __future__ import annotations

from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st


RAW_PATH = Path("experiments/results_osm.csv")
SUMMARY_PATH = Path("experiments/summary_osm.csv")


def short_graph_name(name: str) -> str:
    return name.replace("_new_jersey_usa_drive.graphml", "").replace(".graphml", "")


@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    raw = pd.read_csv(RAW_PATH)
    summary = pd.read_csv(SUMMARY_PATH)
    raw["graph_short"] = raw["graph"].map(short_graph_name)
    summary["graph_short"] = summary["graph"].map(short_graph_name)
    return raw, summary


def plot_runtime_bar(summary: pd.DataFrame, algos: List[str]) -> None:
    sub = summary[summary["algo"].isin(algos)].copy()
    if sub.empty:
        st.warning("No data for selected filters.")
        return
    sub = sub.sort_values(["graph_short", "algo"])
    graphs = sub["graph_short"].drop_duplicates().tolist()
    x = np.arange(len(graphs))
    width = 0.8 / max(1, len(algos))

    fig, ax = plt.subplots(figsize=(5.2, 2.9))
    for i, algo in enumerate(algos):
        part = sub[sub["algo"] == algo].set_index("graph_short").reindex(graphs)
        off = (i - (len(algos) - 1) / 2) * width
        ax.bar(x + off, part["time_s_mean"].values, width=width, label=algo)
    ax.set_xticks(x)
    ax.set_xticklabels(graphs, rotation=10, ha="right")
    ax.set_ylabel("Runtime mean (s)")
    ax.set_title("OSM Runtime by City")
    ax.legend()
    plt.tight_layout()
    st.pyplot(fig, use_container_width=False)


def plot_expanded_bar(summary: pd.DataFrame, algos: List[str]) -> None:
    sub = summary[summary["algo"].isin(algos)].copy()
    if sub.empty:
        st.warning("No data for selected filters.")
        return
    sub = sub.sort_values(["graph_short", "algo"])
    graphs = sub["graph_short"].drop_duplicates().tolist()
    x = np.arange(len(graphs))
    width = 0.8 / max(1, len(algos))

    fig, ax = plt.subplots(figsize=(5.2, 2.9))
    for i, algo in enumerate(algos):
        part = sub[sub["algo"] == algo].set_index("graph_short").reindex(graphs)
        off = (i - (len(algos) - 1) / 2) * width
        ax.bar(x + off, part["expanded_mean"].values, width=width, label=algo)
    ax.set_xticks(x)
    ax.set_xticklabels(graphs, rotation=10, ha="right")
    ax.set_ylabel("Expanded nodes mean")
    ax.set_title("OSM Expanded Nodes by City")
    ax.legend()
    plt.tight_layout()
    st.pyplot(fig, use_container_width=False)


def plot_runtime_vs_dist(raw: pd.DataFrame, city: str, algos: List[str]) -> None:
    sub = raw[(raw["graph_short"] == city) & (raw["algo"].isin(algos))].copy()
    if sub.empty:
        st.warning("No data for selected filters.")
        return
    pair_mean = (
        sub.groupby(["pair_id", "algo"], dropna=False)
        .agg(dist_m=("dist_m", "mean"), time_s=("time_s", "mean"))
        .reset_index()
    )
    fig, ax = plt.subplots(figsize=(5.2, 2.9))
    for algo in algos:
        part = pair_mean[pair_mean["algo"] == algo]
        ax.scatter(part["dist_m"], part["time_s"], s=18, alpha=0.75, label=algo)
    ax.set_xlabel("Shortest-path distance (m)")
    ax.set_ylabel("Runtime per pair (s)")
    ax.set_title(f"Runtime vs Distance ({city})")
    ax.legend()
    ax.grid(alpha=0.25)
    plt.tight_layout()
    st.pyplot(fig, use_container_width=False)


def plot_expanded_vs_dist(raw: pd.DataFrame, city: str, algos: List[str]) -> None:
    sub = raw[(raw["graph_short"] == city) & (raw["algo"].isin(algos))].copy()
    if sub.empty:
        st.warning("No data for selected filters.")
        return
    pair_mean = (
        sub.groupby(["pair_id", "algo"], dropna=False)
        .agg(dist_m=("dist_m", "mean"), expanded=("expanded", "mean"))
        .reset_index()
    )
    fig, ax = plt.subplots(figsize=(5.2, 2.9))
    for algo in algos:
        part = pair_mean[pair_mean["algo"] == algo]
        ax.scatter(part["dist_m"], part["expanded"], s=18, alpha=0.75, label=algo)
    ax.set_xlabel("Shortest-path distance (m)")
    ax.set_ylabel("Expanded nodes per pair")
    ax.set_title(f"Expanded Nodes vs Distance ({city})")
    ax.legend()
    ax.grid(alpha=0.25)
    plt.tight_layout()
    st.pyplot(fig, use_container_width=False)


def show_speedup(summary: pd.DataFrame, city: str) -> None:
    city_df = summary[summary["graph_short"] == city].set_index("algo")
    if "dijkstra" not in city_df.index or "astar" not in city_df.index:
        st.info("Need both dijkstra and astar to compute speedup.")
        return
    d_t = float(city_df.loc["dijkstra", "time_s_mean"])
    a_t = float(city_df.loc["astar", "time_s_mean"])
    d_e = float(city_df.loc["dijkstra", "expanded_mean"])
    a_e = float(city_df.loc["astar", "expanded_mean"])
    speedup = d_t / a_t if a_t > 0 else float("inf")
    reduce = (d_e - a_e) / d_e * 100.0 if d_e > 0 else 0.0
    st.metric("A* speedup over Dijkstra", f"{speedup:.2f}x")
    st.metric("Expanded nodes reduction", f"{reduce:.1f}%")


def main() -> None:
    st.set_page_config(page_title="OSM Experiment Dashboard", layout="wide")
    st.title("OSM Shortest-Path Dashboard")
    st.caption("Interactive view for New Brunswick / Piscataway OSM experiments.")

    if not RAW_PATH.exists() or not SUMMARY_PATH.exists():
        st.error("Missing OSM result files. Run: python run_osm_experiments.py")
        return

    raw, summary = load_data()
    cities = sorted(summary["graph_short"].dropna().unique().tolist())
    all_algos = sorted(summary["algo"].dropna().unique().tolist())

    col1, col2 = st.columns(2)
    with col1:
        city = st.selectbox("Choose city", cities, index=0)
    with col2:
        algos = st.multiselect("Choose algorithm(s)", all_algos, default=all_algos)

    st.subheader("Quick Conclusion")
    show_speedup(summary, city)

    st.subheader("Choose chart(s) to display")
    c1, c2, c3, c4 = st.columns(4)
    show_rt_bar = c1.checkbox("Runtime by city", value=True)
    show_ex_bar = c2.checkbox("Expanded by city", value=True)
    show_rt_sc = c3.checkbox("Runtime vs distance", value=True)
    show_ex_sc = c4.checkbox("Expanded vs distance", value=False)

    if not algos:
        st.warning("Please choose at least one algorithm.")
        return

    if show_rt_bar:
        plot_runtime_bar(summary, algos)
    if show_ex_bar:
        plot_expanded_bar(summary, algos)
    if show_rt_sc:
        plot_runtime_vs_dist(raw, city, algos)
    if show_ex_sc:
        plot_expanded_vs_dist(raw, city, algos)

    with st.expander("Raw data preview"):
        st.write("results_osm.csv (head)")
        st.dataframe(raw.head(20))
        st.write("summary_osm.csv")
        st.dataframe(summary)


if __name__ == "__main__":
    main()
