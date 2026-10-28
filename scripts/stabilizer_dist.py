#!/usr/bin/env python3
"""
stabilizer_dist.py — distribution of |Stab| per level, from the
redundantes_v2 summaries.

Each class in data/redundant_v2/opt<J>/n<N>/resumen.txt reports
"Redundantes: R", where R = |G| / |Stab|. We invert that to get |Stab|
and tabulate the distribution per (option, level).

Usage:
    python scripts/stabilizer_dist.py --option 1 --levels 3 4 5 6 7 8 9 10
    python scripts/stabilizer_dist.py --option 1 --levels 3 4 5 --tsv
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

# Possible locations of the summaries (try both, in order).
PATTERNS = [
    "data/redundant_v2/opt{opt}/n{n}/resumen.txt",
    "data/redundant/opt{opt}/n{n}/resumen.txt",
    "data/redundant/n{n}/resumen.txt",  # op1 legacy
]

# |G| = 12 for all eight options.
G = 12

# Only divisors of G can be stabilizer sizes.
DIVISORS = {1, 2, 3, 4, 6, 12}


def find_summary(option, level):
    for pat in PATTERNS:
        p = Path(pat.format(opt=option, n=level))
        if p.exists():
            return p
    return None


def parse_redundancies(path):
    """Return the list of 'Redundantes: R' values found in the file."""
    text = path.read_text()
    values = re.findall(r"Redundantes:\s*(\d+)", text)
    return [int(v) for v in values]


def stabilizer_of(redundancy):
    """|Stab| = |G| / redundancy, if redundancy divides |G|; else None."""
    if redundancy <= 0 or G % redundancy != 0:
        return None
    return G // redundancy


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--option", type=int, required=True)
    p.add_argument("--levels", type=int, nargs="+", required=True)
    p.add_argument("--tsv", action="store_true",
                   help="Emit TSV instead of a pretty table.")
    args = p.parse_args()

    rows = []
    missing = []

    for n in sorted(args.levels):
        path = find_summary(args.option, n)
        if path is None:
            missing.append(n)
            continue
        redundancies = parse_redundancies(path)
        if not redundancies:
            missing.append(n)
            continue

        counter = Counter()
        total = 0
        weighted = 0.0
        for r in redundancies:
            s = stabilizer_of(r)
            if s is None:
                continue
            counter[s] += 1
            total += 1
            weighted += s
        if total == 0:
            missing.append(n)
            continue

        row = {
            "n": n,
            "total": total,
            "avg_stab": weighted / total,
            "hist": {s: counter.get(s, 0) for s in sorted(DIVISORS)},
            "path": str(path),
        }
        rows.append(row)

    if missing:
        print(f"[warn] no usable summary for levels: {missing}", file=sys.stderr)

    if not rows:
        print("No data found. Check PATTERNS and the option/level values.",
              file=sys.stderr)
        sys.exit(1)

    if args.tsv:
        cols = ["n", "total", "avg_stab"] + [f"stab={s}" for s in sorted(DIVISORS)]
        print("\t".join(cols))
        for r in rows:
            vals = [str(r["n"]), str(r["total"]), f"{r['avg_stab']:.3f}"]
            vals += [str(r["hist"][s]) for s in sorted(DIVISORS)]
            print("\t".join(vals))
    else:
        header = (f"{'n':>3} {'total':>7} {'avg|Stab|':>10}  "
                  + "  ".join(f"|Stab|={s:>2}" for s in sorted(DIVISORS)))
        print(header)
        print("-" * len(header))
        for r in rows:
            hist = "  ".join(f"{r['hist'][s]:>9}" for s in sorted(DIVISORS))
            print(f"{r['n']:>3} {r['total']:>7} {r['avg_stab']:>10.3f}  {hist}")


if __name__ == "__main__":
    main()
