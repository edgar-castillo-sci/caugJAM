#!/usr/bin/env python3

"""Layer generation for JAM options."""

from itertools import permutations

import numpy as np


def rows_for_option(option):
    """Return the possible single layers for the given JAM option."""
    if option == 1:
        tokens = ['+0', '+j', '+j']
    elif option == 2:
        tokens = ['+0', '+j', '+k']
    elif option == 3:
        tokens = ['+0', '+j', '-j']
    elif option == 4:
        a = ['+0', '+j', '-k']
        b = ['+0', '-j', '+k']
        rows = list(set(permutations(a, 3))) + list(set(permutations(b, 3)))
        return [list(r) for r in rows]
    elif option == 5:
        tokens = ['+0', '*j', '(+k-k)']
    elif option == 6:
        tokens = ['*j', '+k', '-k']
    elif option == 7:
        a = ['+0', '*j', '(+k-l)']
        b = ['+0', '*j', '(-k+l)']
        rows = list(set(permutations(a, 3))) + list(set(permutations(b, 3)))
        return [list(r) for r in rows]
    elif option == 8:
        a = ['*j', '+k', '-l']
        b = ['*j', '-k', '+l']
        rows = list(set(permutations(a, 3))) + list(set(permutations(b, 3)))
        return [list(r) for r in rows]
    else:
        raise ValueError(f"Invalid option: {option}")

    return [list(r) for r in set(permutations(tokens, 3))]


def chain_to_array(chain):
    """Convert a JAM string to an array of tokens."""
    blocks = chain.split('/')
    columns = []
    for block in blocks:
        tokens = []
        i = 0
        while i < len(block):
            if block[i] == '(':
                tokens.append(block[i:i+6])
                i += 6
            else:
                tokens.append(block[i:i+2])
                i += 2
        columns.append(tokens)
    return np.array(columns).T
