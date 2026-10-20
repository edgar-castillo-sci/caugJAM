#!/usr/bin/env python3

"""Canonical augmentation (pruning) for JAM string generation."""

from .generation import rows_for_option, chain_to_array
from .pruning import generate_full, generate_poda, verify_option
from .fibration import (
    generate_raw,
    generate_canonical,
    generate_extensions,
    build_fibration,
)

__all__ = [
    "rows_for_option",
    "chain_to_array",
    "generate_full",
    "generate_poda",
    "verify_option",
    "generate_raw",
    "generate_canonical",
    "generate_extensions",
    "build_fibration",
]

__version__ = "0.1.0"
