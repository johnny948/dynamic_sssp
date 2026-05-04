# Dynamic Single-Source Shortest Path (SSSP)

Implementation and experiments for shortest-path planning on **synthetic 4-connected grid maps** (Dijkstra, A* with Manhattan / Euclidean heuristics, dynamic obstacle update with rerun vs repair-like baseline), plus optional **OpenStreetMap (OSM)** road-network validation.

---

## Requirements

- **Python 3.10+** recommended (CPython).
- Install dependencies from the project root:

```bash
pip install -r requirements.txt
```

All commands below assume your **current working directory is the project root** (the folder that contains `run_experiments.py`).

---

## Quick start (synthetic experiments)

### 1. Run grid experiments

Runs static and dynamic sweeps defined in `experiments/configs.json`. Writes CSV outputs under `experiments/`.

```bash
python run_experiments.py
```

**Outputs**

| File | Description |
|------|-------------|
| `experiments/results_static.csv` | Raw rows per run (static). |
| `experiments/summary_static.csv` | Aggregated mean / variance / `n_runs`. |
| `experiments/results_dynamic.csv` | Raw rows per run (dynamic). |
| `experiments/summary_dynamic.csv` | Aggregated mean / variance / `n_runs`. |

Runtime may take several minutes depending on grid sizes and `runs_per_config` in `experiments/configs.json`.

### 2. Plot synthetic results

Generates PNG figures under `experiments/figures/`.

```bash
python experiments/plot_results.py
```

Typical figures: `static_time_vs_area.png`, `static_expanded_vs_area.png`, `static_vs_obstacle_p.png`, `dynamic_phase_comparison.png`.

---

## Optional: OSM road-network experiments

### 1. Download OSM graphs (GraphML)

```bash
python tools/download_osm.py
```

By default this saves drive networks under `data/osm/`. You can override places and output directory; see:

```bash
python tools/download_osm.py --help
```

Ensure paths in `experiments/osm_configs.json` match the GraphML files you downloaded.

### 2. Run OSM shortest-path experiments

```bash
python run_osm_experiments.py
```

**Outputs**

| File | Description |
|------|-------------|
| `experiments/results_osm.csv` | Raw per-query rows. |
| `experiments/summary_osm.csv` | Aggregated statistics by graph and algorithm. |

### 3. Plot OSM results

```bash
python experiments/plot_osm_results.py
```

Figures are written to `experiments/figures_osm/`.

---

## Optional: Interactive dashboard (OSM)

Requires `streamlit` (listed in `requirements.txt`).

```bash
streamlit run osm_dashboard.py
```

Open the URL shown in the terminal (usually `http://localhost:8501`). The dashboard reads `experiments/results_osm.csv` and `experiments/summary_osm.csv`; run `python run_osm_experiments.py` first if those files are missing.

---

## Configuration

| File | Role |
|------|------|
| `experiments/configs.json` | Synthetic static/dynamic parameters (grid sizes, obstacle probabilities, seeds, `runs_per_config`, algorithms, heuristics). |
| `experiments/osm_configs.json` | OSM GraphML paths, number of random OD pairs, repeats, algorithms. |

---

## Project layout

```
src/                    # Core algorithms and data structures
  astar.py              # A* (Manhattan / Euclidean on grids)
  dijstra.py            # Dijkstra on grids
  dynamic.py            # Dynamic obstacle + rerun / repair-like
  graph.py, pq.py, ...
  road_algorithms.py    # Dijkstra / A* on OSMnx graphs (optional track)
experiments/
  configs.json
  osm_configs.json
  plot_results.py       # Synthetic figures
  plot_osm_results.py   # OSM figures
run_experiments.py      # Main synthetic experiment driver
run_osm_experiments.py  # OSM experiment driver
tools/download_osm.py   # Download OSM GraphML via OSMnx
osm_dashboard.py        # Streamlit UI for OSM CSVs
requirements.txt
README.md
```

---

## Reproducibility and data

- **Synthetic data** are generated on the fly from `experiments/configs.json` (no fixed external grid files required).
- **OSM data** are obtained from OpenStreetMap via OSMnx; reproduce by running `tools/download_osm.py` and then `run_osm_experiments.py`.

For course submission, document your **hardware** (CPU, RAM, OS) and **Python version** next to reported runtimes.

---

## Troubleshooting

- **`ModuleNotFoundError: src`** — Run scripts from the **project root**, not from inside `src/`.
- **Missing OSM CSVs in the dashboard** — Run `python run_osm_experiments.py` after downloading GraphML files.
- **Long runtimes** — Reduce grid sizes, seeds, or `runs_per_config` in `experiments/configs.json`.
