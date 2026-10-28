#!/usr/bin/env python3
"""
test_equivariance_exhaustive.py

For each option in {1, 3, 5} and each n up to a configurable bound,
verify that

    kappa(p_argmin(g . c)) == kappa(p_argmin(c))

for every raw chain c in X_n and every g in G.

If this holds for all c, the G-equivariance claim of Section 7.1 of
the paper is verified exhaustively for the tested levels, not just on
samples.
"""

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from caugjam.generation import rows_for_option
from canonjam import canonical_key

from iso_free.action import G_ELEMENTS, g_action
from iso_free.parents import p_argmin


def raw_chains(option, n):
    """Return all raw chains of length n (list of numpy arrays)."""
    single = [np.array(r).reshape(1, -1) for r in rows_for_option(option)]
    chains = single
    for _ in range(2, n + 1):
        new = []
        for c in chains:
            for r in single:
                new.append(np.vstack([c, r]))
        chains = new
    return chains


def check_equivariance(option, n, verbose=True):
    chains = raw_chains(option, n)
    n_chains = len(chains)
    n_failures = 0
    first_failure = None

    for c in chains:
        _, base_key = p_argmin(c, option)
        for sigma, eps in G_ELEMENTS:
            g_c = g_action(c, sigma, eps, option=option)
            _, g_key = p_argmin(g_c, option)
            if g_key != base_key:
                n_failures += 1
                if first_failure is None:
                    first_failure = (c.copy(), sigma, eps, base_key, g_key)
                break   # count at most one failure per chain

    ok = (n_failures == 0)
    if verbose:
        status = "OK" if ok else f"FAIL ({n_failures} chains)"
        print(f"  op{option} n={n}: {n_chains} chains, {status}", flush=True)
        if first_failure is not None:
            c, sigma, eps, base, got = first_failure
            print(f"    first failure: sigma={sigma}, eps={eps}")
            print(f"    kappa(p(c))     = {base}")
            print(f"    kappa(p(g.c))   = {got}")

    return ok, n_chains, n_failures


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--options", type=int, nargs="+", default=[1, 3, 5])
    parser.add_argument("--max-n", type=int, default=5,
                        help="Exhaustive up to this n (op1 may use n+1).")
    args = parser.parse_args()

    print(f"Exhaustive G-equivariance check, n <= {args.max_n}")
    print()

    all_ok = True
    for opt in args.options:
        for n in range(2, args.max_n + 1):
            ok, n_chains, n_failures = check_equivariance(opt, n)
            if not ok:
                all_ok = False

    print()
    if all_ok:
        print("PASS: kappa(p_argmin(g.c)) == kappa(p_argmin(c)) for all tested c, g.")
        sys.exit(0)
    else:
        print("FAIL: G-equivariance of p_argmin is broken on some chains.")
        sys.exit(1)


if __name__ == "__main__":
    main()
