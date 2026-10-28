"""
poda.py

CLI for the pruning verification.

The implementation lives in caugjam.pruning.

Baselines
---------
Three baselines are reported, to keep the comparison honest:

  t_naive_ext
      Time to extend every chain of X_{n-1} by prepend and append
      (2q * |X_{n-1}| extensions) and canonicalize each.
      This is the baseline that the pruning method replaces
      (it does 2q * |X_{n-1}/G| canonicalizations instead).
      The speedup against it converges to |G| = 12.

  t_full
      Time to compute level n from scratch with the full method
      (generate X_n, filter_duplicates, then recompute the
      canonical keys of the surviving classes). It includes a
      double canonicalization pass, so the speedup against it
      is lower than against t_naive_ext.

  t_poda_inc / t_poda_cum
      Incremental and cumulative time of the pruning method.
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
    parser.add_argument(
        "--verbose", action="store_true",
        help="Print per-level progress to stdout (flushed immediately).",
    )
    return parser.parse_args()


def save_results(results, path):
    """Save results to a TSV file with per-level timing.

    Columns:
      option, n,
      full_classes, poda_classes, match,
      t_full,        time of the full method, from scratch
      t_naive_ext,   time of the naive extension baseline
      t_poda_lvl,    incremental time of the pruning method
      t_poda_cum,    cumulative time of the pruning method
      speedup_naive, t_naive_ext / t_poda_lvl   (approaches |G|)
      speedup_full,  t_full     / t_poda_lvl   (secondary)
    """
    with open(path, "w", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow([
            "option", "n", "full_classes", "poda_classes", "match",
            "t_full", "t_naive_ext", "t_poda_lvl", "t_poda_cum",
            "speedup_naive", "speedup_full",
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
                    f"{r['t_naive_ext'].get(n, 0.0):.4f}",
                    f"{r['t_poda_inc'][n]:.4f}",
                    f"{r['t_poda_cum'][n]:.4f}",
                    f"{r['speedup'].get(n, 0.0):.2f}",
                    f"{r['speedup_vs_full'].get(n, 0.0):.2f}",
                ])


def main():
    args = parse_args()

    print("=" * 70)
    print("Poda verification: full method vs poda")
    print("=" * 70)
    print(f"Options: {args.options}")
    print(f"Levels: {args.levels}")
    print()
    print("speedup_naive = t_naive_ext / t_poda_lvl  (approaches |G| = 12)")
    print("speedup_full  = t_full      / t_poda_lvl  (secondary)")

    results = []
    all_pass = True

    for option in args.options:
        print(f"\nComputing option {option} ...", flush=True)
        result = verify_option(option, args.levels, verbose=args.verbose)
        results.append(result)

        print(f"\nOption {option}:")
        print(f"  {'n':>3} {'full':>8} {'poda':>8} {'match':>6} "
              f"{'t_full':>9} {'t_naive':>9} {'t_poda':>9} "
              f"{'s_naive':>8} {'s_full':>8}")
        for n in args.levels:
            full = result["full_classes"][n]
            poda = result["poda_classes"][n]
            match = "YES" if full == poda else "NO"
            print(f"  {n:>3} {full:>8} {poda:>8} {match:>6} "
                  f"{result['t_full'][n]:>9.3f} "
                  f"{result['t_naive_ext'].get(n, 0.0):>9.3f} "
                  f"{result['t_poda_inc'][n]:>9.3f} "
                  f"{result['speedup'].get(n, 0.0):>7.2f}x "
                  f"{result['speedup_vs_full'].get(n, 0.0):>7.2f}x")

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

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
