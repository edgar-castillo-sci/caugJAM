"""
poda.py

CLI for the pruning verification.

The implementation lives in caugjam.pruning.
"""

import argparse
import csv
import sys

from caugjam import verify_option


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
    parser.add_argument(
        "--output", type=str, default=None,
        help="Output TSV file path (optional).",
    )
    return parser.parse_args()


def save_results(results, path):
    """Save results to a TSV file with per-level timing."""
    with open(path, "w", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow([
            "option", "n", "full_classes", "poda_classes",
            "match", "t_full_n", "t_poda_cum_n", "speedup_n",
        ])
        for r in results:
            for n in r["levels"]:
                full = r["full_classes"][n]
                poda = r["poda_classes"][n]
                writer.writerow([
                    r["option"],
                    n,
                    full,
                    poda,
                    "YES" if full == poda else "NO",
                    f"{r['t_full'][n]:.4f}",
                    f"{r['t_poda_cum'][n]:.4f}",
                    f"{r['speedup'][n]:.2f}",
                ])


if __name__ == "__main__":
    args = parse_args()

    print("=" * 70)
    print("Poda verification: full method vs poda")
    print("=" * 70)
    print(f"Options: {args.options}")
    print(f"Levels: {args.levels}")

    results = []
    all_pass = True

    for option in args.options:
        result = verify_option(option, args.levels)
        results.append(result)

        print(f"\nOption {option}:")
        print(f"  {'n':>3} {'full':>8} {'poda':>8} {'match':>6} "
              f"{'t_full':>10} {'t_poda':>10} {'speedup':>10}")
        for n in args.levels:
            full = result["full_classes"][n]
            poda = result["poda_classes"][n]
            match = "YES" if full == poda else "NO"
            print(f"  {n:>3} {full:>8} {poda:>8} {match:>6} "
                  f"{result['t_full'][n]:>10.3f} "
                  f"{result['t_poda_cum'][n]:>10.3f} "
                  f"{result['speedup'][n]:>9.2f}x")

        if not result["match"]:
            all_pass = False

    print()
    if all_pass:
        print("Result: ALL MATCH")
    else:
        print("Result: SOME MISMATCH")

    if args.output:
        save_results(results, args.output)
        print(f"\nResults saved to: {args.output}")

    sys.exit(0 if all_pass else 1)
