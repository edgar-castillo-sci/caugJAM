#!/usr/bin/env python3
"""
run_obstruction.py

For each option and level, count classes with v-composed element in Stab.

If any level has v_composed > 0, then no G-equivariant position selector
exists at that level. This is the obstruction.
"""

import argparse
import sys
from pathlib import Path

# Add the parent directory to sys.path so `iso_free` is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from iso_free.obstruction import count_obstruction, save_obstruction


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--option", type=int, required=True)
    parser.add_argument("--levels", type=int, nargs="+", required=True)
    parser.add_argument("--output", type=str, required=True)
    args = parser.parse_args()

    print(f"Option {args.option}, levels {args.levels}")
    results = count_obstruction(args.option, args.levels, verbose=True)
    save_obstruction(results, args.output)
    print(f"\nSaved to {args.output}")

    n_impossible = sum(1 for r in results if r["position_selector"] == "NO")
    if n_impossible == len(results):
        print("\nALL levels have v-composed stabilizer: no position selector.")
    elif n_impossible == 0:
        print("\nNO level has v-composed stabilizer: position selector MAY exist.")
    else:
        print(f"\n{n_impossible}/{len(results)} levels have obstruction.")


if __name__ == "__main__":
    main()
