"""
Pruning (canonical augmentation) for JAM string generation.

The full method generates all candidates and filters duplicates.
The pruning method generates only the extensions of the canonical
representatives of n-1 layers.

Baselines measured by verify_option
-----------------------------------
  t_full[n]       Full method from scratch: generate X_n, filter_duplicates,
                  recompute canonical keys of the surviving classes.
                  Includes a double canonicalization pass
                  (filter_duplicates + set(canonical_key(...))).

  t_naive_ext[n]  Naive extension baseline: extend every chain of X_{n-1}
                  by prepend and append, deduplicate by content so that
                  |X_{n-1}| = q^{n-1} (raw chains, NOT canonical classes),
                  and canonicalize each extension once. This measures the
                  2q * q^{n-1} = 2q^n canonicalization calls that poda
                  replaces with 2q * |X_{n-1}/G|. The speedup against it
                  converges to |G| = 12.

                  Note: without the dedup step, |prev_chains| grows as
                  2^{n-1} q^n and the baseline becomes a strawman.

  t_poda_inc[n]   Incremental time of the pruning method at level n.
  t_poda_cum[n]   Cumulative time of the pruning method up to level n.
"""

from time import perf_counter

import numpy as np

from canonjam import canonical_key, filter_duplicates

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


def generate_poda_timed(n_max, option, verbose=False):
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
    if verbose:
        print(f"    [poda]  n=1  {times[1]:6.2f}s  "
              f"({len(classes[1])} classes)", flush=True)

    for n in range(2, n_max + 1):
        t0 = perf_counter()
        children = set()
        for parent_key in classes[n - 1]:
            parent = chain_to_array(parent_key)
            for s in single:
                # Append: parent . s
                ext_append = np.vstack([parent, s])
                children.add(canonical_key(ext_append, option))
                # Prepend: s . parent
                ext_prepend = np.vstack([s, parent])
                children.add(canonical_key(ext_prepend, option))
        classes[n] = sorted(children)
        times[n] = perf_counter() - t0
        if verbose:
            print(f"    [poda]  n={n}  {times[n]:6.2f}s  "
                  f"({len(classes[n])} classes)", flush=True)

    return classes, times


def generate_poda(n_max, option):
    """Same as generate_poda_timed, but only returns classes."""
    classes, _ = generate_poda_timed(n_max, option)
    return classes


def verify_option(option, levels, verbose=False):
    """
    Verify that poda and full method produce the same classes.

    Returns a dict with per-level timing:
      - t_full[n]: time to compute level n from scratch (full method)
      - t_naive_ext[n]: time to extend all X_{n-1} chains by 2q and
                        canonicalize each (naive extension baseline)
      - t_poda_inc[n]: time to compute level n from level n-1 (poda)
      - t_poda_cum[n]: cumulative time to reach level n (poda)
      - speedup[n]: t_naive_ext[n] / t_poda_inc[n]  (approaches |G|)
      - speedup_vs_full[n]: t_full[n] / t_poda_inc[n]  (secondary)

    Set verbose=True to print progress to stdout (flushed immediately).
    """
    levels = sorted(levels)
    n_max = max(levels)

    # Full method: time per level (from scratch each time)
    full_results = {}
    t_full = {}
    for n in levels:
        t0 = perf_counter()
        n_cand, keys = generate_full(n, option)
        t_full[n] = perf_counter() - t0
        full_results[n] = (n_cand, keys)
        if verbose:
            print(f"    [full]  n={n}  {t_full[n]:6.2f}s  "
                  f"({n_cand} candidates, {len(keys)} classes)", flush=True)

    # Naive extension baseline: build X_1..X_{n_max} incrementally.
    # For each n >= 2, extend every raw chain of X_{n-1} by prepend and
    # append (2q * |X_{n-1}| = 2q^n extensions), deduplicate by content
    # (so that |prev_chains| = q^n and not 2^{n-1} q^n), and canonicalize
    # each extension once. This measures the 2q * |X_{n-1}| canonicalization
    # calls that poda replaces with 2q * |X_{n-1}/G|.
    single = [np.array(r).reshape(1, -1) for r in rows_for_option(option)]
    prev_chains = list(single)
    t_naive_ext = {1: 0.0}
    for n in range(2, n_max + 1):
        t0 = perf_counter()
        # Generate extensions of every raw chain of X_{n-1}.
        children = []
        for c in prev_chains:
            for s in single:
                children.append(np.vstack([c, s]))
                children.append(np.vstack([s, c]))
        # Canonicalize each extension once.
        for c in children:
            canonical_key(c, option)
        t_naive_ext[n] = perf_counter() - t0

        # Deduplicate by content to keep |prev_chains| = q^n.
        # Without this step, prev_chains would grow as 2^{n-1} q^n
        # and the baseline would be a strawman.
        seen = set()
        unique = []
        for c in children:
            b = c.tobytes()
            if b not in seen:
                seen.add(b)
                unique.append(c)
        prev_chains = unique

        if verbose:
            print(f"    [naive] n={n}  {t_naive_ext[n]:6.2f}s  "
                  f"({len(children)} extensions, "
                  f"{len(unique)} unique chains)", flush=True)

    # Poda method: incremental times
    poda_classes, t_poda_inc = generate_poda_timed(n_max, option, verbose=verbose)

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
            if verbose:
                print(f"    [MISMATCH] n={n}: full and poda class sets differ",
                      flush=True)

    return {
        "option": option,
        "levels": levels,
        "full_classes": {n: len(full_results[n][1]) for n in levels},
        "poda_classes": {n: len(poda_classes[n]) for n in levels},
        "match": all_match,
        "t_full": t_full,
        "t_naive_ext": t_naive_ext,
        "t_poda_inc": t_poda_inc,
        "t_poda_cum": t_poda_cum,
        "speedup": {
            n: (t_naive_ext[n] / t_poda_inc[n] if t_poda_inc[n] > 0 else float("inf"))
            for n in levels if n >= 2
        },
        "speedup_vs_full": {
            n: (t_full[n] / t_poda_inc[n] if t_poda_inc[n] > 0 else float("inf"))
            for n in levels if n >= 2
        },
    }
