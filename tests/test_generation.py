#!/usr/bin/env python3

"""Tests for the generation module."""

import numpy as np
import pytest

from canonjam import rows_for_option, chain_to_array


@pytest.mark.parametrize("option,expected", [
    (1, 3), (2, 6), (3, 6), (4, 12),
    (5, 6), (6, 6), (7, 12), (8, 12),
])
def test_rows_count(option, expected):
    """Each option has the expected number of single layers."""
    assert len(rows_for_option(option)) == expected


def test_chain_to_array_simple():
    """chain_to_array returns a 2D array."""
    a = chain_to_array("+0+0/+j+j/+j+j")
    assert a.shape == (2, 3)
    assert a[0, 0] == '+0'
    assert a[1, 0] == '+0'


def test_chain_to_array_single_layer():
    """chain_to_array works for a single layer."""
    a = chain_to_array("+0/+j/+j")
    assert a.shape == (1, 3)
