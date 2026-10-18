#!/usr/bin/env python3

"""
Pruning (canonical augmentation) for JAM string generation.

The full method generates all candidates and filters duplicates.
The pruning method generates only the extensions of the canonical
representatives of n-1 layers.
"""

from time import perf_counter

import numpy as np

from jam_canonical import canonical_key, filter_duplicates

from .generation import chain_to_array, rows_for_option


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
    """
    Verify that poda and full method produce the same classes.

    Returns a dict with:
      - 'option': the option number
      - 'levels': list of levels checked
      - 'full_classes': dict {n: count} for the full method
      - 'poda_classes': dict {n: count} for the poda method
      - 'match': bool, True if all levels match
      - 't_full': total time of full method (s)
      - 't_poda': total time of poda method (s)
      - 'speedup': t_full / t_poda
    """
    t0_full = perf_counter()
    full_results = {}
    for n in levels:
        n_cand, keys = generate_full(n, option)
        full_results[n] = (n_cand, keys)
    t_full = perf_counter() - t0_full

    t0_poda = perf_counter()
    poda_classes = generate_poda(max(levels), option)
    t_poda = perf_counter() - t0_poda

    all_match = True
    for n in levels:
        n_cand, full_keys = full_results[n]
        poda_keys = poda_classes[n]
        if set(full_keys) != set(poda_keys):
            all_match = False

    return {
        "option": option,
        "levels": levels,
        "full_classes": {n: len(full_results[n][1]) for n in levels},
        "poda_classes": {n: len(poda_classes[n]) for n in levels},
        "match": all_match,
        "t_full": t_full,
        "t_poda": t_poda,
        "speedup": t_full / t_poda if t_poda > 0 else float("inf"),
    }
