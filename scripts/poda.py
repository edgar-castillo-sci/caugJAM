"""
poda.py

CLI for the pruning verification.

The implementation lives in canonjam.pruning.
"""

import argparse
import sys

from canonjam import verify_option


DEFAULT_OPTIONS = [1, 5, 7]
DEFAULT_LEVELS = [2, 3, 4, 5]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Verify that poda produces the same classes as full method."
    )
    parser.add_argument(
        "--options", type=int, nargs="+", default=DEFAULT_OPTIONS,
        help="JAM options to verify (default: 1 5 7)",
    )
    parser.add_argument(
        "--levels", type=int, nargs="+", default=DEFAULT_LEVELS,
        help="Layer counts to verify (default: 2 3 4 5)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    print("=" * 70)
    print("Poda verification: full method vs poda")
    print("=" * 70)
    print(f"Options: {args.options}")
    print(f"Levels: {args.levels}")

    all_pass = True
    for option in args.options:
        result = verify_option(option, args.levels)
        print(f"\nOption {option}:")
        for n in args.levels:
            full = result["full_classes"][n]
            poda = result["poda_classes"][n]
            match = "YES" if full == poda else "NO"
            print(f"  n={n}: full={full}, poda={poda}, match={match}")
        print(f"  Speedup: {result['speedup']:.2f}x")
        if not result["match"]:
            all_pass = False

    print()
    if all_pass:
        print("Result: ALL MATCH")
        sys.exit(0)
    else:
        print("Result: SOME MISMATCH")
        sys.exit(1)
