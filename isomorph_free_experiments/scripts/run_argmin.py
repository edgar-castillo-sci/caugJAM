#!/usr/bin/env python3
"""
run_argmin.py

Test whether argmin-parent gives isomorph-free generation.

For each parent p in T_n, for each child c in Children(p), compute
kappa(p_argmin(c)) and check if it equals p. If so, accept c and add
kappa(c) to T_{n+1}. Count canonicalizations and verify that T_{n+1}
equals the class count from caugJAM.

Cost accounting
---------------
For each child c processed:
  - p_argmin(c) does 2 kappa calls (one for p_first, one for p_last).
  - If the parent test passes, 1 additional kappa call for the child.

So per child the cost is 2 kappa (rejected) or 3 kappa (accepted),
versus 1 kappa per child in caugJAM's `generate_poda_timed`.
"""

import argparse
import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from canonjam import canonical_key
from caugjam.generation import chain_to_array, rows_for_option
from caugjam.pruning import generate_poda

from iso_free.parents import p_argmin


def run_argmin(option, n_max, verbose=False):
    """Run argmin-parent generation up to level n_max.

    Returns a list of dicts, one per level n >= 2, with:
      option, n, n_classes, match_caugjam,
      n_canon_argmin, n_canon_caugjam, ratio
    """
    single = [np.array(r).reshape(1, -1) for r in rows_for_option(option)]

    # Reference: caugJAM's class sets up to n_max.
    ref_classes = generate_poda(n_max, option)

    T = {1: list(ref_classes[1])}
    results = []

    for n in range(2, n_max + 1):
        accepted = set()
        n_canon = 0
        children_count = 0

        for parent_key in T[n - 1]:
            parent = chain_to_array(parent_key)
            for f in single:
                for child in (np.vstack([parent, f]),
                              np.vstack([f, parent])):
                    children_count += 1
                    p_chain, p_key = p_argmin(child, option)
                    n_canon += 2   # 2 kappa calls inside p_argmin
                    if p_key == parent_key:
                        accepted.add(canonical_key(child, option))
                        n_canon += 1   # 1 kappa call for the accepted child

        T[n] = sorted(accepted)

        ref = set(ref_classes[n])
        got = set(T[n])
        match = got == ref

        # caugJAM's cost at level n: one kappa per child, 2q per parent
        n_canon_caugjam = children_count

        ratio = n_canon / n_canon_caugjam if n_canon_caugjam > 0 else 0.0

        results.append({
            "option": option,
            "n": n,
            "n_classes": len(T[n]),
            "match_caugjam": "YES" if match else "NO",
            "n_canon_argmin": n_canon,
            "n_canon_caugjam": n_canon_caugjam,
            "ratio": f"{ratio:.2f}",
        })

        if verbose:
            print(f"  n={n}: classes={len(T[n])}, match={match}, "
                  f"canon_argmin={n_canon}, "
                  f"canon_caugjam={n_canon_caugjam}, "
                  f"ratio={ratio:.2f}", flush=True)

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--option", type=int, required=True)
    parser.add_argument("--n-max", type=int, required=True)
    parser.add_argument("--output", type=str, required=True)
    args = parser.parse_args()

    print(f"Option {args.option}, n_max {args.n_max}")
    results = run_argmin(args.option, args.n_max, verbose=True)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "option", "n", "n_classes", "match_caugjam",
            "n_canon_argmin", "n_canon_caugjam", "ratio",
        ], delimiter="\t")
        writer.writeheader()
        writer.writerows(results)
    print(f"\nSaved to {args.output}")


if __name__ == "__main__":
    main()
