"""
fibracion.py

CLI for generating raw data and the fibration between consecutive levels.

The implementation lives in caugjam.fibration and caugjam.generation.
"""

import argparse
import csv
import os
import sys
from time import perf_counter

# Add the parent directory to the path so we can import caugjam
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_CANONJAM_DIR = os.path.dirname(_SCRIPT_DIR)
sys.path.insert(0, _CANONJAM_DIR)

from caugjam import (
    generate_raw,
    generate_canonical,
    generate_extensions,
    build_fibration,
    rows_for_option,
)
from caugjam import canonical_key, array_to_chain


DEFAULT_OPTION = 1
DEFAULT_N_MAX_RAW = 6
DEFAULT_N_MAX_CANONICAL = 8
DEFAULT_N_MAX_FIBRATION = 8


def save_lines(lines, path):
    """Save a list of strings, one per line."""
    with open(path, "w") as f:
        for line in lines:
            f.write(line + "\n")


def save_fibration_tsv(fibration, path):
    """Save the fibration as a TSV (parent, child)."""
    with open(path, "w", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["parent", "child"])
        for parent, children in fibration.items():
            for child in children:
                writer.writerow([parent, child])


def save_fibration_detail(fibration, n, path):
    """Save a human-readable detail of the fibration for a given level."""
    with open(path, "w") as f:
        f.write("=" * 80 + "\n")
        f.write(f"FIBRATION FROM n={n} TO n={n+1}\n")
        f.write("=" * 80 + "\n\n")

        n_parents = len(fibration)
        all_children = []
        for children in fibration.values():
            all_children.extend(children)
        unique_children = set(all_children)

        sizes = {p: len(c) for p, c in fibration.items()}
        avg = sum(sizes.values()) / len(sizes) if sizes else 0
        max_size = max(sizes.values()) if sizes else 0

        f.write(f"Parents (n={n}):          {n_parents}\n")
        f.write(f"Unique children (n={n+1}): {len(unique_children)}\n")
        f.write(f"Total connections:         {len(all_children)}\n")
        f.write(f"Average fiber size:        {avg:.2f}\n")
        f.write(f"Max fiber size:            {max_size}\n\n")

        for i, (parent, children) in enumerate(fibration.items(), 1):
            f.write(f"{'-' * 80}\n")
            f.write(f"PARENT {i} [fiber size {len(children)}]\n")
            f.write(f"  Key: {parent}\n")
            f.write("  Children:\n")
            for j, child in enumerate(children, 1):
                f.write(f"    [{j}] {child}\n")
            f.write("\n")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate raw data and fibration for a JAM option."
    )
    parser.add_argument(
        "--option", type=int, default=DEFAULT_OPTION,
        help="JAM option (default: 1)",
    )
    parser.add_argument(
        "--n-raw", type=int, default=DEFAULT_N_MAX_RAW,
        help="Max n for raw candidates (default: 6)",
    )
    parser.add_argument(
        "--n-canonical", type=int, default=DEFAULT_N_MAX_CANONICAL,
        help="Max n for canonical classes (default: 8)",
    )
    parser.add_argument(
        "--n-fibration", type=int, default=DEFAULT_N_MAX_FIBRATION,
        help="Max n for fibration (default: 8)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    option = args.option

    base = os.path.join(_CANONJAM_DIR, "datos")
    os.makedirs(base, exist_ok=True)
    os.makedirs(os.path.join(base, "fibracion"), exist_ok=True)

    print(f"Option {option}")
    print()

    # 1. Raw candidates and canonical classes per level
    for n in range(1, args.n_canonical + 1):
        dir_n = os.path.join(base, f"n{n}")
        os.makedirs(dir_n, exist_ok=True)

        t0 = perf_counter()

        n_raw = None
        if n <= args.n_raw:
            raw = generate_raw(n, option)
            chains = [array_to_chain(r) for r in raw]
            save_lines(chains, os.path.join(dir_n, "cadenas.txt"))
            n_raw = len(raw)

        canonical = generate_canonical(n, option)
        save_lines(canonical, os.path.join(dir_n, "canonicas.txt"))

        t1 = perf_counter()

        raw_str = f"{n_raw:>8}" if n_raw is not None else f"{'—':>8}"
        print(f"  n={n}: {raw_str} raw, {len(canonical):>5} canonical "
              f"({t1-t0:.2f}s)")

    print()

    # 2. Fibration between consecutive levels
    for n in range(1, args.n_fibration):
        t0 = perf_counter()
        fibration = build_fibration(n, option)

        tsv_path = os.path.join(base, "fibracion", f"fib_n{n}_n{n+1}.tsv")
        save_fibration_tsv(fibration, tsv_path)

        detail_path = os.path.join(base, "fibracion",
                                   f"fib_n{n}_n{n+1}_detalle.txt")
        save_fibration_detail(fibration, n, detail_path)

        t1 = perf_counter()

        n_parents = len(fibration)
        n_connections = sum(len(c) for c in fibration.values())
        print(f"  Fib n={n}→{n+1}: {n_parents:>4} parents, "
              f"{n_connections:>5} connections ({t1-t0:.2f}s)")

    print()
    print("Done.")
