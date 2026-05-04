from __future__ import annotations

import argparse
from pathlib import Path
import re

import osmnx as ox


DEFAULT_PLACES = [
    "New Brunswick, New Jersey, USA",
    "Piscataway, New Jersey, USA",
]


def slugify(text: str) -> str:
    value = text.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "osm_place"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download OSM road network(s) and save as GraphML."
    )
    parser.add_argument(
        "--places",
        nargs="+",
        default=DEFAULT_PLACES,
        help='Place names, e.g. "New Brunswick, New Jersey, USA"',
    )
    parser.add_argument(
        "--network-type",
        default="drive",
        choices=["drive", "walk", "bike", "all", "all_public"],
        help="OSMnx network type (default: drive).",
    )
    parser.add_argument(
        "--out-dir",
        default="data/osm",
        help="Output directory for GraphML files (default: data/osm).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for place in args.places:
        print(f"Downloading: {place} (network_type={args.network_type})")
        graph = ox.graph_from_place(place, network_type=args.network_type)
        filename = f"{slugify(place)}_{args.network_type}.graphml"
        out_path = out_dir / filename
        ox.save_graphml(graph, out_path.as_posix())
        print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
