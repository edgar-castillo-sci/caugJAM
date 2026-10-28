#!/usr/bin/env python3
"""
export_dag.py — export the augmentation DAG to JSON for downstream TikZ.

Writes a JSON with:
  - nodes: id, level, canonical key
  - edges: from, to, direction (prepend/append), row index

Deduplicated: an edge (from, to, dir, row) appears at most once even if
several raw extensions collapse to the same canonical child.

Usage:
    python scripts/export_dag.py --option 1 --levels 2 3 4 \
        --output ../paper3/data/dag_op1_n2-4.json
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

from canonjam import canonical_key
from caugjam.generation import chain_to_array, rows_for_option
from caugjam.pruning import generate_poda_timed


def compute_dag(option, levels):
    n_max = max(levels)
    classes, _ = generate_poda_timed(n_max, option)
    single = [np.array(r).reshape(1, -1) for r in rows_for_option(option)]

    nodes = {}
    for n in levels:
        for key in classes[n]:
            nodes[key] = {"id": len(nodes), "level": n}

    edges = []
    for n in levels:
        if n >= n_max:
            continue
        for parent_key in classes[n]:
            parent = chain_to_array(parent_key)
            for r_idx, r in enumerate(single):
                for direction, child_raw in (
                    ("prepend", np.vstack([r, parent])),
                    ("append", np.vstack([parent, r])),
                ):
                    child_key = canonical_key(child_raw, option)
                    if child_key in nodes:
                        edges.append({
                            "from": nodes[parent_key]["id"],
                            "to": nodes[child_key]["id"],
                            "dir": direction,
                            "row": r_idx,
                        })
    return nodes, edges


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--option", type=int, required=True)
    p.add_argument("--levels", type=int, nargs="+", required=True)
    p.add_argument("--output", type=str, required=True)
    args = p.parse_args()

    print(f"Computing DAG for option {args.option}, levels {sorted(args.levels)} ...",
          flush=True)
    nodes, edges = compute_dag(args.option, args.levels)

    # Deduplicate edges by (from, to, dir, row).
    seen = set()
    unique_edges = []
    for e in edges:
        t = (e["from"], e["to"], e["dir"], e["row"])
        if t in seen:
            continue
        seen.add(t)
        unique_edges.append(e)

    node_list = sorted(
        [{"id": v["id"], "level": v["level"], "key": k} for k, v in nodes.items()],
        key=lambda x: (x["level"], x["id"]),
    )

    out = {
        "option": args.option,
        "levels": sorted(args.levels),
        "n_nodes": len(node_list),
        "n_edges": len(unique_edges),
        "nodes": node_list,
        "edges": unique_edges,
    }

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(out, indent=2))
    print(f"Saved {args.output}  ({out['n_nodes']} nodes, {out['n_edges']} edges)")


if __name__ == "__main__":
    main()
