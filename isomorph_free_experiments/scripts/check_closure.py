#!/usr/bin/env python3
"""
check_closure.py

Verify that each option's row set is closed under sign flip
(v_content for buckled options).

If a row set is not closed, then v = sign ∘ flip does not map
X_k to X_k for that option, and Lemma 1 of the main paper
(closure of the row set) has a gap for that option.

Usage:
    python scripts/check_closure.py
    python scripts/check_closure.py --options 3 4 5 6 7 8
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from caugjam.generation import rows_for_option
from iso_free.action import sign_flip_token


def check_option(option, verbose=True):
    """Return (closed, counterexamples) for the option's row set."""
    rows = rows_for_option(option)
    rows_str = {tuple(str(x).strip() for x in r) for r in rows}
    counterexamples = []
    for r in rows:
        flipped = tuple(sign_flip_token(x) for x in r)
        if flipped not in rows_str:
            counterexamples.append((tuple(str(x).strip() for x in r), flipped))
    closed = len(counterexamples) == 0
    if verbose:
        if closed:
            print(f"op{option}: closed under sign flip ({len(rows)} rows)")
        else:
            print(f"op{option}: NOT closed ({len(counterexamples)} of {len(rows)} rows break):")
            for orig, flip in counterexamples[:3]:
                print(f"    {orig}  ->  {flip}  (not in row set)")
            if len(counterexamples) > 3:
                print(f"    ... and {len(counterexamples) - 3} more")
    return closed, counterexamples


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--options", type=int, nargs="+",
                        default=[3, 4, 5, 6, 7, 8])
    args = parser.parse_args()

    print("Checking closure of row sets under sign flip...")
    print()

    results = {}
    for opt in args.options:
        closed, cex = check_option(opt)
        results[opt] = (closed, cex)
        print()

    print("=" * 60)
    closed_opts = [o for o, (c, _) in results.items() if c]
    open_opts = [o for o, (c, _) in results.items() if not c]

    if closed_opts:
        print(f"Closed:   {closed_opts}")
    if open_opts:
        print(f"NOT closed: {open_opts}")
    print()

    if open_opts:
        print("WARNING: For the options not closed, Lemma 1 of the main paper")
        print("(closure of the row set) does not hold with v = sign ∘ flip.")
        print("The paper must either restrict the lemma to the closed options,")
        print("or reformulate the action of v on those options.")
        sys.exit(1)
    else:
        print("All checked options are closed. Lemma 1 holds.")
        sys.exit(0)


if __name__ == "__main__":
    main()
