"""
iso_free/parents.py

Parent functions p: X_{n+1} -> X_n for JAM chains.

Two natural candidates:
  p_first(c)  : remove first layer
  p_last(c)   : remove last layer

Neither is G-equivariant alone (Lemma 3 of the paper: v swaps them).
But the argmin-parent

    p_argmin(c) = argmin over {p_first(c), p_last(c)} of kappa(.)

is G-equivariant, because kappa is G-invariant and the two parents of
c and g.c are related by g (paper's Lemma 3).

This module implements p_argmin and tests whether it gives isomorph-free
generation at the same or higher cost than the caugJAM approach.
"""

import numpy as np

from canonjam import canonical_key
from caugjam.generation import chain_to_array, rows_for_option


def p_first(chain):
    """Remove first layer."""
    return chain[1:, :]


def p_last(chain):
    """Remove last layer."""
    return chain[:-1, :]


def p_argmin(chain, option):
    """Return the parent of `chain` whose canonical key is lex-min.

    Returns the parent chain (not the canonical key).
    """
    cand_first = p_first(chain)
    cand_last = p_last(chain)
    k_first = canonical_key(cand_first, option)
    k_last = canonical_key(cand_last, option)
    if k_first <= k_last:
        return cand_first, k_first
    return cand_last, k_last


def parent_candidates(chain):
    """Return [p_first(c), p_last(c)] (both parents, uncanonicalized)."""
    return [p_first(chain), p_last(chain)]
