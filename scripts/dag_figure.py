#!/usr/bin/env python3
"""
dag_figure.py — draw the augmentation DAG directly from caugjam.pruning.

No external data files needed: the edges are computed on the fly from
generate_poda_timed and canonical_key. Suitable for small levels only
(op1 n=2..5 takes a few seconds).

Usage:
    python scripts/dag_figure.py --option 1 --levels 2 3 4 \
        --output graphs/dag_op1_n2-4.pdf
    python scripts/dag_figure.py --option 1 --levels 2 3 4 5 \
        --output graphs/dag_op1_n2-5.png --figsize 14 9
"""

import argparse
import sys
from pathlib import Path

import numpy as np

try:
    import networkx as nx
    import matplotlib.pyplot as plt
except ImportError:
    print("Requires networkx and matplotlib: "
          "pip install networkx matplotlib", file=sys.stderr)
    sys.exit(1)

from canonjam import canonical_key
from caugjam.generation import chain_to_array, rows_for_option
from caugjam.pruning import generate_poda_timed


def compute_edges(option, levels):
    """Return (classes_by_level, edges) for the given option and levels."""
    n_max = max(levels)
    classes, _ = generate_poda_timed(n_max, option)
    single = [np.array(r).reshape(1, -1) for r in rows_for_option(option)]

    edges = set()
    for n in levels:
        if n >= n_max:
            continue
        for parent_key in classes[n]:
            parent = chain_to_array(parent_key)
            for r in single:
                for child_raw in (np.vstack([parent, r]), np.vstack([r, parent])):
                    child_key = canonical_key(child_raw, option)
                    edges.add((parent_key, child_key))
    return classes, edges


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--option", type=int, required=True)
    p.add_argument("--levels", type=int, nargs="+", required=True,
                   help="Levels to draw (edges are drawn for n -> n+1 for n < max)")
    p.add_argument("--output", type=str, required=True)
    p.add_argument("--figsize", type=float, nargs=2, default=[10, 7])
    p.add_argument("--label-level", type=int, default=None,
                   help="Level whose nodes get text labels (default: smallest)")
    args = p.parse_args()

    levels = sorted(args.levels)
    print(f"Computing DAG for option {args.option}, levels {levels} ...",
          flush=True)
    classes, edges = compute_edges(args.option, levels)
    print(f"  {sum(len(classes[n]) for n in levels)} nodes, "
          f"{len(edges)} edges", flush=True)

    G = nx.DiGraph()
    layers = {}
    for n in levels:
        for key in classes[n]:
            G.add_node(key)
            layers[key] = n
    for parent, child in edges:
        G.add_edge(parent, child)

    # Position: y = -level (top to bottom), x = sorted within level.
    pos = {}
    by_level = {}
    for node, lvl in layers.items():
        by_level.setdefault(lvl, []).append(node)
    for lvl, nodes in by_level.items():
        nodes.sort()
        for i, node in enumerate(nodes):
            pos[node] = (i - (len(nodes) - 1) / 2.0, -lvl)

    plt.figure(figsize=tuple(args.figsize))
    nx.draw_networkx_edges(G, pos, alpha=0.35, arrows=True, arrowsize=8,
                           node_size=40, width=0.7)
    nx.draw_networkx_nodes(G, pos, node_size=60, node_color="#3b7dd8",
                           edgecolors="white", linewidths=0.4)

    label_level = args.label_level if args.label_level is not None else min(by_level)
    labels = {node: node[:12] for node, lvl in layers.items() if lvl == label_level}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=5)

    x_min = min(x for x, y in pos.values())
    for lvl in sorted(by_level):
        plt.text(x_min - 1.0, -lvl, f"n={lvl}", ha="right", va="center",
                 fontsize=9)

    plt.axis("off")
    plt.tight_layout()
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(args.output, bbox_inches="tight", dpi=200)
    print(f"Saved {args.output}")


if __name__ == "__main__":
    main()
