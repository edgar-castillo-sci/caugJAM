#!/usr/bin/env bash
# Run Q1 + Q2 for the remaining options: 2, 4, 6, 7, 8.

set -e

# Option 2 (BPL, planar, q=6) — n up to 6
echo "=== op2 ==="
python scripts/run_obstruction.py --option 2 --levels 2 3 4 5 6 \
    --output datos/obstruction_op2.tsv
python scripts/run_argmin.py --option 2 --n-max 6 \
    --output datos/argmin_op2.tsv

# Option 4 (BBU, buckled, q=12) — n up to 5
echo "=== op4 ==="
python scripts/run_obstruction.py --option 4 --levels 2 3 4 5 \
    --output datos/obstruction_op4.tsv
python scripts/run_argmin.py --option 4 --n-max 5 \
    --output datos/argmin_op4.tsv

# Option 6 (ext BPL, buckled, q=6) — n up to 6
echo "=== op6 ==="
python scripts/run_obstruction.py --option 6 --levels 2 3 4 5 6 \
    --output datos/obstruction_op6.tsv
python scripts/run_argmin.py --option 6 --n-max 6 \
    --output datos/argmin_op6.tsv

# Option 7 (ext Janus 1H, buckled, q=12) — n up to 5
echo "=== op7 ==="
python scripts/run_obstruction.py --option 7 --levels 2 3 4 5 \
    --output datos/obstruction_op7.tsv
python scripts/run_argmin.py --option 7 --n-max 5 \
    --output datos/argmin_op7.tsv

# Option 8 (ext Janus 1T, buckled, q=12) — n up to 5
echo "=== op8 ==="
python scripts/run_obstruction.py --option 8 --levels 2 3 4 5 \
    --output datos/obstruction_op8.tsv
python scripts/run_argmin.py --option 8 --n-max 5 \
    --output datos/argmin_op8.tsv

echo
echo "All remaining options done."
