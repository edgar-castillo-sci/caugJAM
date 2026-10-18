#!/usr/bin/env python3

"""
Fibration: relation between canonical classes of n and n+1 layers.

For each canonical class of n layers (the "parent"), generate its
extensions and compute the canonical key of each one. The resulting
set of keys are the "children" of the parent.
"""

from itertools import permutations

import numpy as np

from jam_canonical import canonical_key, filter_duplicates

from .generation import chain_to_array, rows_for_option


def generate_raw(n, option):
    """Generate all raw candidates of n layers, without filtering."""
    single = [np.array(r).reshape(1, -1) for r in rows_for_option(option)]
    candidates = single
    for _ in range(2, n + 1):
        new = []
        for c in candidates:
            for s in single:
                new.append(np.vstack([c, s]))
        candidates = new
    return candidates


def generate_canonical(n, option):
    """Generate the canonical classes of n layers."""
    candidates = generate_raw(n, option)
    uniques = filter_duplicates(candidates, option)
    return sorted(set(canonical_key(u, option) for u in uniques))


def generate_extensions(parent_key, option):
    """Generate the extensions (append and prepend) of a canonical class."""
    parent = chain_to_array(parent_key)
    single = [np.array(r).reshape(1, -1) for r in rows_for_option(option)]
    extensions = []
    for s in single:
        extensions.append(np.vstack([parent, s]))
        extensions.append(np.vstack([s, parent]))
    return extensions


def build_fibration(n, option):
    """
    Build the fibration from n to n+1.

    Returns a dict {parent_key: [child_keys]}.
    """
    parents = generate_canonical(n, option)
    fibration = {}
    for parent_key in parents:
        children = set()
        for ext in generate_extensions(parent_key, option):
            children.add(canonical_key(ext, option))
        fibration[parent_key] = sorted(children)
    return fibration
