# src/utils.py
from __future__ import annotations
import json
import time
import csv
from dataclasses import dataclass
from typing import Any, Dict, List, Iterable, Optional

def perf_time() -> float:
    return time.perf_counter()

def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_csv(path: str, rows: List[Dict[str, Any]]) -> None:
    if not rows:
        raise ValueError("No rows to write.")
    keys = sorted({k for r in rows for k in r.keys()})
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)

def mean(xs: List[float]) -> float:
    return sum(xs) / len(xs) if xs else float("nan")

def var(xs: List[float]) -> float:
    if len(xs) < 2:
        return 0.0
    m = mean(xs)
    return sum((x - m) ** 2 for x in xs) / (len(xs) - 1)

def safe_float(x: Any) -> float:
    try:
        return float(x)
    except Exception:
        return float("nan")
