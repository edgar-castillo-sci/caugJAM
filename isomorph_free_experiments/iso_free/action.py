"""
iso_free/action.py

G-action on JAM chains.

For planar options (1, 2, 5): v = flip (row reversal, no content change).
For buckled options (3, 4, 6, 7, 8): v = sign ∘ flip (row reversal,
then sign flip of every token; buckled pairs are exchanged).

The general formula is
    (g . a)_{ij} = v_content^eps(a_{(k+1-i), sigma(j)})
with v_content the identity (planar) or sign flip (buckled).
"""

from itertools import permutations

import numpy as np

S3_ELEMENTS = list(permutations([0, 1, 2]))
G_ELEMENTS = [(sigma, eps) for sigma in S3_ELEMENTS for eps in (0, 1)]
G_SIZE = len(G_ELEMENTS)  # 12

# v = flip
PLANAR_OPTIONS = {1, 2, 5}

# v = sign ∘ flip
BUCKLED_OPTIONS = {3, 4, 6, 7, 8}


def _flip_sign_str(s):
    """Flip the sign of a signed string like '+j', '-j', '+0', '0'."""
    s = str(s).strip()
    if s in ("+0", "-0", "0"):
        return "+0"
    if s.startswith("+"):
        return "-" + s[1:]
    if s.startswith("-"):
        return "+" + s[1:]
    return s


def sign_flip_token(tok):
    """Flip the sign of a JAM token.

    - "+x" -> "-x"
    - "-x" -> "+x"
    - "+0" -> "+0"  (paper convention: sign(+0) = +0)
    - "*x" -> "*x"  (fixed-site, invariant)
    - "(+x-y)" -> "(-x+y)"  (buckled pair, exchange atoms)
      If x == y, the pair is normalized to the canonical form (+x-x),
      respecting the identification (+x-x) = (-x+x) of Definition 3.
    """
    s = str(tok).strip()
    if s.startswith("*"):
        return s
    if s.startswith("(") and s.endswith(")"):
        inner = s[1:-1]
        # Locate the second sign (skip the first character).
        split = None
        for i in range(1, len(inner)):
            if inner[i] in "+-":
                split = i
                break
        if split is None:
            # Not a pair; just flip the whole thing.
            return "(" + _flip_sign_str(inner) + ")"
        first_signed, second_signed = inner[:split], inner[split:]
        first_flipped = _flip_sign_str(first_signed)
        second_flipped = _flip_sign_str(second_signed)
        # Extract atom labels (drop the leading sign).
        first_atom = first_flipped[1:] if first_flipped[0] in "+-" else first_flipped
        second_atom = second_flipped[1:] if second_flipped[0] in "+-" else second_flipped
        # Identify (+x-x) = (-x+x); normalize to the (+x-x) form.
        if first_atom == second_atom:
            return "(+" + first_atom + "-" + second_atom + ")"
        return "(" + first_flipped + second_flipped + ")"
    return _flip_sign_str(s)


def sign_flip_chain(chain):
    """Apply sign flip to every token in the chain."""
    result = np.empty(chain.shape, dtype=object)
    for i in range(chain.shape[0]):
        for j in range(chain.shape[1]):
            result[i, j] = sign_flip_token(chain[i, j])
    return result


def sigma_action(chain, sigma):
    return chain[:, list(sigma)]


def flip_action(chain):
    return chain[::-1, :]


def v_action(chain, option=1):
    """v = flip for planar; v = sign ∘ flip for buckled."""
    flipped = flip_action(chain)
    if option in BUCKLED_OPTIONS:
        return sign_flip_chain(flipped)
    return flipped


def g_action(chain, sigma, eps, option=1):
    """Apply g = (sigma, v^eps) to chain."""
    result = sigma_action(chain, sigma)
    if eps == 1:
        result = v_action(result, option)
    return result


def stabilizer(chain, option=1):
    stab = []
    for sigma, eps in G_ELEMENTS:
        if np.array_equal(g_action(chain, sigma, eps, option), chain):
            stab.append((sigma, eps))
    return stab


def has_v_composed_in_stab(chain, option=1):
    for sigma in S3_ELEMENTS:
        if np.array_equal(g_action(chain, sigma, 1, option), chain):
            return True
    return False
