# src/metrics.py
from __future__ import annotations
from typing import Any, Dict, List, Tuple
from .utils import mean, var, safe_float

def group_key(row: Dict[str, Any], keys: List[str]) -> Tuple[Any, ...]:
    return tuple(row.get(k) for k in keys)

def summarize(rows: List[Dict[str, Any]],
              group_by: List[str],
              metrics: List[str]) -> List[Dict[str, Any]]:
    """
    Produce summary rows with mean/var for specified metrics.
    """
    buckets: Dict[Tuple[Any, ...], List[Dict[str, Any]]] = {}
    for r in rows:
        k = group_key(r, group_by)
        buckets.setdefault(k, []).append(r)

    out: List[Dict[str, Any]] = []
    for k, rs in buckets.items():
        base = {group_by[i]: k[i] for i in range(len(group_by))}
        base["n_runs"] = len(rs)
        for m in metrics:
            vals = [safe_float(x.get(m)) for x in rs]
            base[f"{m}_mean"] = mean(vals)
            base[f"{m}_var"] = var(vals)
        out.append(base)

    # stable order
    out.sort(key=lambda r: tuple(r.get(k) for k in group_by))
    return out