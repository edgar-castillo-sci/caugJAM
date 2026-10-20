#!/usr/bin/env python3

"""Tests for the pruning module."""

import pytest

from caugjam import generate_full, generate_poda, verify_option


def test_generate_full_option_1_n2():
    """Full method for option 1, n=2 gives 2 classes."""
    n_cand, keys = generate_full(2, 1)
    assert n_cand == 9
    assert len(keys) == 2


def test_generate_poda_option_1_n2():
    """Poda method for option 1, n=2 gives 2 classes."""
    classes = generate_poda(2, 1)
    assert len(classes[2]) == 2


@pytest.mark.parametrize("option", [1, 2, 3, 4, 5, 6, 7, 8])
def test_verify_option_all_options_n2_n3(option):
    """All options match for n=2 and n=3."""
    result = verify_option(option, [2, 3])
    assert result["match"] is True


def test_verify_option_1_up_to_n5():
    """Option 1 matches up to n=5."""
    result = verify_option(1, [2, 3, 4, 5])
    assert result["match"] is True
