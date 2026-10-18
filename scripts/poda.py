"""
poda.py

Verifica que la poda produce las mismas clases canónicas que el
método completo, para cualquier opción de JAM.

Método completo: genera todos los candidatos y filtra con jam-canonical.
Método de poda: genera solo las extensiones de los representantes
canónicos de n-1 capas, y filtra con jam-canonical.

Uso:
    python3 poda.py --options 1 5 7 --levels 2 3 4 5
    python3 poda.py --options 1 --levels 2 3 4 5 6 7 8
"""

import argparse
import numpy as np
import sys
import os
from itertools import permutations
from time import perf_counter

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _SCRIPT_DIR)

from jam_canonical import canonical_key, filter_duplicates


DEFAULT_OPTIONS = [1, 5, 7]
DEFAULT_LEVELS = [2, 3, 4, 5]


def rows_for_option(option):
    """Return the possible single layers for the given JAM option."""
    if option == 1:
        tokens = ['+0', '+j', '+j']
    elif option == 2:
        tokens = ['+0', '+j', '+k']
    elif option == 3:
        tokens = ['+0', '+j', '-j']
    elif option == 4:
        a = ['+0', '+j', '-k']
        b = ['+0', '-j', '+k']
        rows = list(set(permutations(a, 3))) + list(set(permutations(b, 3)))
        return [list(r) for r in rows]
    elif option == 5:
        tokens = ['+0', '*j', '(+k-k)']
    elif option == 6:
        tokens = ['*j', '+k', '-k']
    elif option == 7:
        a = ['+0', '*j', '(+k-l)']
        b = ['+0', '*j', '(-k+l)']
        rows = list(set(permutations(a, 3))) + list(set(permutations(b, 3)))
        return [list(r) for r in rows]
    elif option == 8:
        a = ['*j', '+k', '-l']
        b = ['*j', '-k', '+l']
        rows = list(set(permutations(a, 3))) + list(set(permutations(b, 3)))
        return [list(r) for r in rows]
    else:
        raise ValueError(f"Invalid option: {option}")
    return [list(r) for r in set(permutations(tokens, 3))]


def chain_to_array(chain):
    """Convert a JAM string to an array of tokens."""
    blocks = chain.split('/')
    columns = []
    for block in blocks:
        tokens = []
        i = 0
        while i < len(block):
            if block[i] == '(':
                tokens.append(block[i:i+6])
                i += 6
            else:
                tokens.append(block[i:i+2])
                i += 2
        columns.append(tokens)
    return np.array(columns).T


def generate_full(n, option):
    """Full method: generate all candidates and filter."""
    single = [np.array(r).reshape(1, -1) for r in rows_for_option(option)]
    candidates = single
    for _ in range(2, n + 1):
        new = []
        for c in candidates:
            for s in single:
                new.append(np.vstack([c, s]))
        candidates = new
    uniques = filter_duplicates(candidates, option)
    return len(candidates), sorted(set(canonical_key(u, option) for u in uniques))


def generate_poda(n_max, option):
    """
    Poda method: generate only the extensions of the canonical
    representatives of n-1 layers.
    """
    single = [np.array(r).reshape(1, -1) for r in rows_for_option(option)]
    classes = {1: sorted(set(canonical_key(s, option) for s in single))}

    for n in range(2, n_max + 1):
        children = set()
        for parent_key in classes[n - 1]:
            parent = chain_to_array(parent_key)
            for s in single:
                    # Append: parent · s
                    ext_append = np.vstack([parent, s])
                    children.add(canonical_key(ext_append, option))
                    # Prepend: s · parent
                    ext_prepend = np.vstack([s, parent])
                    children.add(canonical_key(ext_prepend, option))
        classes[n] = sorted(children)

    return classes


def verify_option(option, levels):
    """Verify that poda and full method produce the same classes."""
    print(f"\n{'=' * 70}")
    print(f"Option {option}")
    print(f"{'=' * 70}\n")
    print(f"{'n':>3} {'Candidates':>12} {'Full classes':>14} "
          f"{'Poda classes':>14} {'Match':>8}")
    print("-" * 60)

    # Full method (all levels)
    t0_full = perf_counter()
    full_results = {}
    for n in levels:
        n_cand, keys = generate_full(n, option)
        full_results[n] = (n_cand, keys)
    t_full = perf_counter() - t0_full

    # Poda method (up to max level, reuses classes at each step)
    t0_poda = perf_counter()
    poda_classes = generate_poda(max(levels), option)
    t_poda = perf_counter() - t0_poda

    all_match = True
    for n in levels:
        n_cand, full_keys = full_results[n]
        poda_keys = poda_classes[n]
        match = set(full_keys) == set(poda_keys)
        mark = "YES" if match else "NO"
        if not match:
            all_match = False
        print(f"{n:>3} {n_cand:>12} {len(full_keys):>14} "
              f"{len(poda_keys):>14} {mark:>8}")

    print(f"\nFull method total time: {t_full:.3f}s")
    print(f"Poda total time:        {t_poda:.3f}s")
    speedup = t_full / t_poda if t_poda > 0 else float("inf")
    print(f"Speedup:                {speedup:.2f}x")
    print(f"Result: {'ALL MATCH' if all_match else 'MISMATCH'}")

    return all_match


def parse_args():
    parser = argparse.ArgumentParser(
        description="Verify that poda produces the same classes as full method."
    )
    parser.add_argument(
        "--options", type=int, nargs="+", default=DEFAULT_OPTIONS,
        help="JAM options to verify (default: 1 5 7)",
    )
    parser.add_argument(
        "--levels", type=int, nargs="+", default=DEFAULT_LEVELS,
        help="Layer counts to verify (default: 2 3 4 5)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    print("=" * 70)
    print("Poda verification: full method vs poda")
    print("=" * 70)
    print(f"Options: {args.options}")
    print(f"Levels: {args.levels}")

    all_pass = True
    for option in args.options:
        if not verify_option(option, args.levels):
            all_pass = False

    print("\n" + "=" * 70)
    if all_pass:
        print("Result: ALL OPTIONS MATCH")
        sys.exit(0)
    else:
        print("Result: SOME OPTIONS MISMATCH")
        sys.exit(1)
