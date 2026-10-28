#!/usr/bin/env python3
"""
test_hybrid.py

Compare three strategies for isomorph-free generation:

  "argmin" : accept c iff kappa(p_argmin(c)) == parent_key
             (2 + 1 kappa per child, the current baseline)

  "hybrid" : if Stab(c) has no v-composed element, use p_first(c)
             (1 kappa); otherwise use p_argmin (2 kappa)
             (+1 kappa per accepted child)

  "first"  : always use p_first(c) (1 kappa per child, no G-equivariance)

Reports, per level: n_classes, match_caugJAM, missing, extra, kappa_calls.
"""

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from caugjam.generation import chain_to_array, rows_for_option
from caugjam.pruning import generate_poda
from canonjam import canonical_key

from iso_free.action import has_v_composed_in_stab
from iso_free.parents import p_first, p_argmin


def run_strategy(option, n_max, strategy):
    single = [np.array(r).reshape(1, -1) for r in rows_for_option(option)]
    ref = generate_poda(n_max, option)
    T = {1: list(ref[1])}
    rows = []

    for n in range(2, n_max + 1):
        accepted = set()
        n_canon = 0
        for parent_key in T[n - 1]:
            parent = chain_to_array(parent_key)
            for f in single:
                for c in (np.vstack([parent, f]), np.vstack([f, parent])):
                    if strategy == "first":
                        p_chain = p_first(c)
                        p_key = canonical_key(p_chain, option)
                        n_canon += 1
                    elif strategy == "argmin":
                        _, p_key = p_argmin(c, option)
                        n_canon += 2
                    elif strategy == "hybrid":
                        if has_v_composed_in_stab(c, option):
                            _, p_key = p_argmin(c, option)
                            n_canon += 2
                        else:
                            p_key = canonical_key(p_first(c), option)
                            n_canon += 1
                    else:
                        raise ValueError(f"unknown strategy: {strategy}")

                    if p_key == parent_key:
                        accepted.add(canonical_key(c, option))
                        n_canon += 1

        got = accepted
        ref_set = set(ref[n])
        missing = ref_set - got
        extra = got - ref_set
        rows.append({
            "n": n,
            "classes": len(got),
            "match": "YES" if got == ref_set else "NO",
            "missing": len(missing),
            "extra": len(extra),
            "kappa": n_canon,
        })
        T[n] = sorted(got)
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--option", type=int, required=True)
    parser.add_argument("--n-max", type=int, default=6)
    args = parser.parse_args()

    ref = generate_poda(args.n_max, args.option)
    ref_counts = {n: len(ref[n]) for n in range(2, args.n_max + 1)}

    print(f"Option {args.option}, n_max {args.n_max}")
    print(f"Reference class counts (caugJAM): {ref_counts}\n")

    for strategy in ["first", "hybrid", "argmin"]:
        print(f"Strategy: {strategy}")
        rows = run_strategy(args.option, args.n_max, strategy)
        for r in rows:
            print(f"  n={r['n']}: classes={r['classes']}, "
                  f"match={r['match']}, missing={r['missing']}, "
                  f"extra={r['extra']}, kappa={r['kappa']}", flush=True)
        print()


if __name__ == "__main__":
    main()
