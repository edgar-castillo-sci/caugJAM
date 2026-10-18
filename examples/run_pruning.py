#!/usr/bin/env python3

"""
Example: run the pruning verification for a few options.

Usage:
    python3 run_pruning.py
"""

from canonjam import verify_option


if __name__ == "__main__":
    for option in [1, 5, 7]:
        result = verify_option(option, [2, 3, 4])
        status = "MATCH" if result["match"] else "MISMATCH"
        print(f"Option {option}: {status}")
        print(f"  Full:   {result['full_classes']}")
        print(f"  Poda:   {result['poda_classes']}")
        print(f"  Speedup: {result['speedup']:.2f}x")
        print()
