"""Sanity tests for the G-action and parent functions."""

import numpy as np
import pytest

from canonjam import canonical_key
from caugjam.generation import chain_to_array

from iso_free.action import G_SIZE, g_action, stabilizer, G_ELEMENTS
from iso_free.parents import p_first, p_last, p_argmin


def test_g_size():
    assert G_SIZE == 12


def test_orbit_size_divides_12():
    """|Orb(c)| = |G| / |Stab(c)| must be an integer."""
    key = "+0+0/+j+j/+j+j"
    chain = chain_to_array(key)
    stab = stabilizer(chain, option=1)
    orbit_size = G_SIZE // len(stab)
    assert G_SIZE % len(stab) == 0
    # For the all-+0-first class, |Stab| = 4 and |Orb| = 3
    assert len(stab) == 4
    assert orbit_size == 3


def test_argmin_parent_is_g_equivariant_on_keys():
    """kappa(p_argmin(g.c)) == kappa(p_argmin(c)) for all g in G.

    The chain equality p_argmin(g.c) == g.p_argmin(c) does NOT hold:
    argmin picks the parent by lex-min canonical key, and when both
    parents are equivalent (same key), the tie-break by position
    (first vs last) is not G-equivariant. But the algorithm only uses
    the canonical key, which IS G-equivariant.
    """
    key = "+0+j/+j+0/+j+j"
    chain = chain_to_array(key)
    _, base_key = p_argmin(chain, 1)
    for sigma, eps in G_ELEMENTS:
        g_chain = g_action(chain, sigma, eps, option=1)
        _, p_key_of_g = p_argmin(g_chain, 1)
        assert p_key_of_g == base_key, (
            f"Failed for g=({sigma}, {eps}): "
            f"kappa(p(g.c)) != kappa(p(c))"
        )

def test_sign_flip_is_involution_op3():
    """sign_flip(sign_flip(tok)) == tok for op3 tokens."""
    from iso_free.action import sign_flip_token
    for tok in ["+0", "+j", "-j"]:
        assert sign_flip_token(sign_flip_token(tok)) == tok


def test_v_action_op3_preserves_multiset():
    """v acts on op3 rows as a permutation of [+0, +j, -j]."""
    from caugjam.generation import rows_for_option
    from iso_free.action import v_action
    rows = rows_for_option(3)
    for r in rows:
        chain = np.array(r).reshape(1, -1)
        v_chain = v_action(chain, option=3)
        assert sorted(str(x) for x in chain.flatten()) == \
               sorted(str(x) for x in v_chain.flatten())

def test_sign_flip_janus_pair_identification():
    """(+k-k) and (-k+k) are the same token (Definition 3)."""
    from iso_free.action import sign_flip_token
    # Both flip to the canonical form (+k-k).
    assert sign_flip_token("(+k-k)") == "(+k-k)"
    assert sign_flip_token("(-k+k)") == "(+k-k)"
    # Janus pair with x != y is preserved as a pair, not identified.
    assert sign_flip_token("(+k-l)") == "(-k+l)"
    assert sign_flip_token("(-k+l)") == "(+k-l)"


def test_closure_of_all_buckled_options():
    """All buckled options are closed under sign flip (Lemma 1)."""
    from caugjam.generation import rows_for_option
    from iso_free.action import sign_flip_token
    for opt in [3, 4, 5, 6, 7, 8]:
        rows = rows_for_option(opt)
        rows_str = {tuple(str(x).strip() for x in r) for r in rows}
        for r in rows:
            flipped = tuple(sign_flip_token(x) for x in r)
            assert flipped in rows_str, (
                f"op{opt}: row {r} flips to {flipped}, not in row set"
            )
