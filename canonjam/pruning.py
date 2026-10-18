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


def generate_poda_timed(n_max, option):
    """
    Poda method: generate only the extensions of the canonical
    representatives of n-1 layers, and return per-level incremental times.

    Returns:
        (classes, times)
        - classes: dict {n: sorted list of keys}
        - times: dict {n: time to compute level n from level n-1, in seconds}
    """
    single = [np.array(r).reshape(1, -1) for r in rows_for_option(option)]

    t0 = perf_counter()
    classes = {1: sorted(set(canonical_key(s, option) for s in single))}
    times = {1: perf_counter() - t0}

    for n in range(2, n_max + 1):
        t0 = perf_counter()
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
        times[n] = perf_counter() - t0

    return classes, times


def generate_poda(n_max, option):
    """Same as generate_poda_timed, but only returns classes."""
    classes, _ = generate_poda_timed(n_max, option)
    return classes


def verify_option(option, levels):
    """
    Verify that poda and full method produce the same classes.

    Returns a dict with per-level timing:
      - t_full[n]: time to compute level n from scratch (full method)
      - t_poda_inc[n]: time to compute level n from level n-1 (poda)
      - t_poda_cum[n]: cumulative time to reach level n (poda)
      - speedup[n]: t_full[n] / t_poda_cum[n]
    """
    # Full method: time per level (from scratch each time)
    full_results = {}
    t_full = {}
    for n in levels:
        t0 = perf_counter()
        n_cand, keys = generate_full(n, option)
        t_full[n] = perf_counter() - t0
        full_results[n] = (n_cand, keys)

    # Poda method: incremental times
    poda_classes, t_poda_inc = generate_poda_timed(max(levels), option)

    # Cumulative poda time
    t_poda_cum = {}
    cumul = 0.0
    for n in sorted(t_poda_inc):
        cumul += t_poda_inc[n]
        t_poda_cum[n] = cumul

    # Match check
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
        "t_poda_inc": t_poda_inc,
        "t_poda_cum": t_poda_cum,
        "speedup": {
            n: (t_full[n] / t_poda_cum[n] if t_poda_cum[n] > 0 else float("inf"))
            for n in levels
        },
    }
