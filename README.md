# Dynamic Single-Source Shortest Path (SSSP): Experiments and Evaluation

Course project: design, implementation, and experimental evaluation of algorithms for dynamic shortest path on grid graphs.

---

## 1. Problem Motivation

- **Problem**: Shortest path on a grid when the graph can **change over time** (e.g., a cell on the current path becomes blocked). Applications: robotics, game AI, routing.
- **Why it matters**: Recomputing from scratch after every change is expensive; incremental or repair-based strategies can be faster when changes are local.
- **Algorithmic interest**: We compare **full recomputation** (Dijkstra, A*) with **incremental repair** under one obstacle addition, and study scalability and statistical behavior.

---

## 2. Algorithms Employed

- **Dijkstra**: Standard SSSP with a binary min-heap priority queue; no heuristic. Time O((V + E) log V), space O(V).
- **A***: Best-first search with admissible heuristics (Manhattan, Euclidean). Same worst-case complexity; typically expands fewer nodes when the heuristic is good.
- **Dynamic setting**: After finding an initial path, we block one cell on that path, then compare:
  - **Rerun A***: Run A* from scratch on the updated grid.
  - **Incremental repair**: A simplified repair strategy (e.g., restricted search around the old path and the changed cell) to reflect the benefit of not recomputing globally.

Implementation details, data structures (e.g., `BinaryMinHeap` in `src/pq.py`), and pseudocode are in the written report.

---

## 3. Experimental Configuration and Implementation Details

### 3.1 Implementation

- **Language**: Python 3.
- **Libraries**: Standard library plus `matplotlib`, `pandas` (for plotting and aggregation). See `requirements.txt`.
- **Code**: All algorithms implemented in this repository (`src/`). No external SSSP libraries used for the core algorithms.

### 3.2 Hardware and Environment (to be filled for your report)

- **Machine**: [e.g. CPU model, RAM, OS]
- **Python**: [e.g. Python 3.10]
- **Interpreter**: CPython (no special JIT unless noted).

You should run experiments on a single machine and report its specs so results are reproducible in context.

### 3.3 Datasets

- **Type**: **Synthetic** grid graphs.
- **Structure**: 4-connected (or 8-connected if `allow_diagonal: true`) grids; each cell is blocked independently with probability `obstacle_p`; start (0,0) and goal (w−1, h−1) are kept free.
- **Parameters** (see `experiments/configs.json`):
  - **Static**: Grid sizes (e.g. 50×50, 100×100, 150×150, 200×200), obstacle probabilities (0.1, 0.2, 0.3), multiple seeds, multiple runs per configuration.
  - **Dynamic**: Fixed grid size and obstacle probability; multiple seeds and multiple runs per (seed, heuristic) to obtain variance.

### 3.4 Methodology

- **Runs**: Each (configuration, seed) is run **multiple times** (`runs_per_config` in `configs.json`); each run is timed separately.
- **Measurement**: Wall-clock time via `time.perf_counter()`; we also record **expanded nodes**, **relaxed edges**, and **visited set size** for analysis.
- **Statistical treatment**: For each group (e.g. grid size × algorithm × heuristic), we compute **mean** and **variance** over all runs and seeds; plots use **mean ± standard error** (SE = sqrt(variance / n)).

---

## 4. How to Run

### 4.1 Install dependencies

```bash
pip install -r requirements.txt
```

### 4.2 Run experiments

From the **project root** (directory containing `run_experiments.py`):

```bash
python run_experiments.py
```

This will:

- Run all static and dynamic configurations in `experiments/configs.json`.
- Write raw results to `experiments/results_static.csv` and `experiments/results_dynamic.csv`.
- Write summary statistics (mean, variance, n_runs) to `experiments/summary_static.csv` and `experiments/summary_dynamic.csv`.

**Note**: With larger grids and `runs_per_config` ≥ 5, the script may take several minutes.

### 4.3 Generate figures

From the project root:

```bash
python experiments/plot_results.py
```

Figures are saved under `experiments/figures/` (e.g. `static_time_vs_area.png`, `static_expanded_vs_area.png`, `static_vs_obstacle_p.png`, `dynamic_phase_comparison.png`). Use these in your report.

---

## 5. Deliverables (for submission)

- **Source code**: This repository (all of `src/`, `run_experiments.py`, `experiments/plot_results.py`, `experiments/configs.json`).
- **Datasets**: No external datasets; graphs are generated from `configs.json` (seeds and parameters). To reproduce, use the same `configs.json` and Python version.
- **Run instructions**: This README (Sections 4.1–4.3).
- **Report**: Written report and (if required) oral presentation covering problem motivation, algorithms, experimental setup, results with tables/figures, and discussion/conclusions.

---

## 6. Results and Performance Analysis

- Use `summary_static.csv` and `summary_dynamic.csv` for tables (mean ± SE or variance).
- Use the figures in `experiments/figures/` to discuss:
  - **Scalability**: Runtime and expanded nodes vs grid area.
  - **Obstacle density**: Effect of obstacle probability on time and expanded nodes.
  - **Dynamic**: Comparison of first A* vs rerun vs incremental repair (time and expanded nodes).

Interpret results in light of theoretical complexity and explain any discrepancies (e.g., cache effects, implementation constants).

---

## 7. File layout

- `run_experiments.py` — runs static and dynamic experiments, writes raw and summary CSVs.
- `experiments/configs.json` — grid sizes, seeds, `runs_per_config`, algorithms, heuristics.
- `experiments/results_*.csv` — raw per-run results.
- `experiments/summary_*.csv` — mean/variance per group.
- `experiments/plot_results.py` — generates figures with error bars.
- `experiments/figures/` — output directory for PNGs.
- `src/` — graph, priority queue, Dijkstra, A*, dynamic repair, generators, utils, metrics.
