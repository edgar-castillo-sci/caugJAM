"""
iso_free/obstruction.py

Count classes with v-composed element in their stabilizer.

Key theorem (this module tests it empirically):
    If Stab(c) contains (sigma, v) for any sigma, no G-equivariant
    position selector s: X_{n+1} -> {first, last} exists, because
    equivariance forces s(c) = s((sigma, v) . c) = phi((sigma, v)) . s(c)
    = opposite(s(c)), which is impossible.

Consequence: p_first and p_last are not G-equivariant for classes with
v-composed stabilizer. A position-based parent function is impossible.
"""

import csv
from pathlib import Path

import numpy as np

from canonjam import canonical_key
from caugjam.generation import chain_to_array
from caugjam.pruning import generate_poda

from .action import has_v_composed_in_stab


def count_obstruction(option, levels, verbose=True):
    """For each level, count classes with v-composed element in Stab.

    Returns a list of dicts with keys:
      option, n, total_classes, v_composed, fraction, position_selector
    where position_selector is 'NO' if v_composed > 0 else 'MAYBE'.
    """
    results = []
    classes_by_level = generate_poda(max(levels), option)
    for n in levels:
        classes = classes_by_level[n]
        total = len(classes)
        v_comp = 0
        for key in classes:
            chain = chain_to_array(key)
            if has_v_composed_in_stab(chain, option):
                v_comp += 1
        results.append({
            "option": option,
            "n": n,
            "total_classes": total,
            "v_composed": v_comp,
            "fraction": v_comp / total if total > 0 else 0.0,
            "position_selector": "NO" if v_comp > 0 else "MAYBE",
        })
        if verbose:
            print(f"  op{option} n={n}: total={total}, v_composed={v_comp}",
                  flush=True)
    return results


def save_obstruction(results, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "option", "n", "total_classes", "v_composed", "fraction",
            "position_selector",
        ], delimiter="\t")
        writer.writeheader()
        writer.writerows(results)
