# caugJAM

*[Leer en español](README.es.md)*

Canonical augmentation (isomorph-free generation) for JAM chains.

## Author

Edgar Castillo (Independent Researcher)

## Scientific basis

Builds on the JAM notation and canonicalization described in:

> Arcudia, J., Ortiz-Chi, F., Sanchez-Valenzuela, A., Aspuru-Guzik, A.,
> Merino, G. (2023). "Joining and arrangement of multilayers: A string
> representation for honeycomb layered materials." Matter, 6(5),
> 1503–1513. doi: 10.1016/j.matt.2023.02.014

and in the companion canonicalization paper (in preparation),
which formalizes the symmetry group `G = S₃ × ℤ/2`, the canonical
representative `κ`, and the Burnside closed forms.

The correctness proof, the complexity theorem, and the empirical
verification of the pruning method are the content of the companion
paper *Growing as Pruning: Isomorph-free generation of JAM chains via
canonical augmentation* (in preparation, target: MATCH).

## What it does

The full method for JAM generation produces all candidates at level `n`
and filters duplicates. The pruning method generates only the extensions
of the canonical representatives at level `n-1`, avoiding the generation
of candidates that will be filtered out anyway.

Formally, the **fiber** of a canonical representative `a ∈ X_{n-1}` is
the set of canonical children obtained by extending `a` with `prepend`
and `append` over the single-layer rows of the option:

    Fib(a) = { κ(c) : c ∈ Children(a) }

The key theorem (proved in the paper) is that `Fib` is invariant under
the group action, `Fib(g·a) = Fib(a)` for every `g ∈ G`. Hence the fiber
depends only on the orbit of `a`, and the pruning method can extend only
the canonical representatives of level `n-1`, with no need to test each
redundant.

The result is exactly the same set of canonical classes as the full
method, with a speedup that converges to `|G| = 12` against the naive
extension baseline (and to `|G|/2 ≈ 6` against the full method; see
[Speedup](#speedup) below).

## Current status

| Component | Status |
|---|---|
| `caugjam/pruning.py` (the method) | implemented |
| `caugjam/fibration.py` (n → n+1 relation) | implemented |
| `scripts/pruning_benchmark.py` (verification + benchmark) | implemented |
| `scripts/redundant_check.py` (structural verification) | implemented |
| `scripts/stabilizer_dist.py` (stabilizer distribution) | implemented |
| `scripts/dag_figure.py` (augmentation DAG figure) | implemented |
| `scripts/export_dag.py` (DAG → JSON) | implemented |
| Formal proof of `G`-equivariance | **closed** (§4 of paper) |
| Formal proof of correctness | **closed** (§5 of paper) |
| Formal proof of complexity | **closed** (§6 of paper) |
| Paper (draft) | in preparation |

## What we have demonstrated (empirically)

### The fiber depends only on the orbit

For all 8 JAM options and all levels tested, **every class produces a
uniform set of canonical children**: if two raw chains canonicalize to
the same representative, they produce exactly the same set of canonical
children at the next level.

| Option | q | Levels tested | Classes verified | Result |
|---|---|---|---|---|
| 1 | 3 | n=2..10 | 7,564 | all yes |
| 2 | 6 | n=2..7 | 28,208 | all yes |
| 3 | 6 | n=2..7 | 28,208 | all yes |
| 4 | 12 | n=2..5 | 22,672 | all yes |
| 5 | 6 | n=2..7 | 28,208 | all yes |
| 6 | 6 | n=2..7 | 28,208 | all yes |
| 7 | 12 | n=2..5 | 22,672 | all yes |
| 8 | 12 | n=2..5 | 22,672 | all yes |
| **Total** | | **45 levels** | **188,412 classes** | **0 exceptions** |

**Interpretation:** the canonical representative alone determines the
fiber. No finer invariant (stabilizer, position in the fiber, or
word-canonical form) is needed.

### Pruning produces the same classes as the full method

For all eight canonical options and `n = 2, 3, 4`, the class counts
produced by the pruning method coincide exactly with those of the full
method:

| Option | n=2 | n=3 | n=4 |
|---|---|---|---|
| 1 | 2 | 4 | 10 |
| 2, 3, 5, 6 | 5 | 21 | 120 |
| 4, 7, 8 | 16 | 144 | 1776 |

These match the published values of Arcudia et al. (2023) for options
1–4 and extend them to the four extended options 5–8.

### The augmentation DAG is not a tree

Each class at level `n+1` has on average ≈1.9 parents at level `n`
(measured on option 1 for `n ≤ 8`; the ratio converges to 2 from below).
This is a consequence of the asymmetry between `prepend` and `append`
under `κ`: the same orbit can be reached from two different classes of
the previous level. The pruning method removes a factor `|G|` of
duplicates in the number of canonicalization calls, but it does not
eliminate this residual duplication; that duplication is handled by the
set-deduplication step.

### Stabilizer distribution converges to trivial

The fraction of orbits with trivial stabilizer goes to 1, which is what
makes the speedup converge to `|G|`. For option 1, the average stabilizer
size `avg|Stab|` decreases from 2.25 (n=3) to 1.033 (n=10). See
`scripts/stabilizer_dist.py` and `data/pruning/stabilizer_op1.tsv`.

## Speedup

Two baselines are reported, to separate the algorithmic saving (which is
`|G|`) from the saving against a specific implementation (which is lower
by a constant factor).

- **Naive extension baseline** (`t_naive`): extend every chain of
  `X_{n-1}` by `prepend` and `append`, deduplicate by content, canonicalize
  each extension once. The speedup against this baseline converges to
  `|G| = 12`.
- **Full method** (`t_full`): generate `X_n` from scratch, call
  `filter_duplicates`, recompute canonical keys of the surviving classes.
  It includes a double canonicalization pass, so the speedup converges to
  `|G|/2 ≈ 6`.

Measured speedups (see `data/pruning/op{1,3,5,7}_corrected.tsv`):

| Option | n | `t_naive` | `t_poda` | `t_full` | speedup (naive / full) |
|---|---|---|---|---|---|
| 1 | 10 | 28.381 | 2.522 | 15.480 | 11.25 / 6.14 |
| 3 | 6 | 28.232 | 2.481 | 15.390 | 11.38 / 6.20 |
| 5 | 6 | 26.964 | 2.368 | 14.607 | 11.39 / 6.17 |
| 7 | 5 | 140.423 | 12.327 | 77.059 | 11.39 / 6.25 |

Options 3 (buckled binary, `v = sign∘flip`) and 5 (Janus 1H,
`v = flip`) have different `v`-involutions but the same class counts,
and their speedups at `n = 6` are essentially identical
(`11.38/6.20` and `11.39/6.17`). The buckled composition does not affect
the complexity of the pruning method.

## What we prove (summary of the paper)

### `G`-equivariance of extension

The extension operation commutes with the group action, up to relabeling
of the single-layer row and the direction (prepend/append).

- Under `σ ∈ S₃` (column permutation): `σ·prepend(f, a) = prepend(σ·f, σ·a)`
  and `σ·append(f, a) = append(σ·f, σ·a)`. Direction preserved.
- Under `v` (flip, or `sign∘flip` for buckled): `v·prepend(f, a) = append(v·f, v·a)`
  and `v·append(f, a) = prepend(v·f, v·a)`. Direction swapped.

Since `Rows` is closed under `G` and `{prepend, append}` is closed under
the swap induced by `v`, the set of extensions is preserved as a set:

    g · Children(a) = Children(g · a)   for all g ∈ G, a ∈ X_k

Therefore `Fib(g·a) = κ(Children(g·a)) = κ(g·Children(a)) = κ(Children(a)) = Fib(a)`,
using the `G`-invariance of `κ`. This is Theorem 1 of the paper.

### Correctness

If every orbit in `X_{n-1}/G` is represented by its canonical
representative and every canonical representative is extended to its
children, then `T_n = { κ(c) : c ∈ Children(a), a ∈ T_{n-1} }` contains
exactly one representative per orbit of `X_n/G`. This is Theorem 2 of
the paper. The saving is in the number of canonicalization calls, not in
the absence of duplicates (see the DAG observation above).

### Complexity

Generating from level `k` to `k+1` requires `|X_k/G| · 2q`
canonicalizations, each `O(k)`. Total: `O(|X_k/G| · q · k)`. The naive
extension baseline is `O(|X_k| · q · k) = O(|G| · |X_k/G| · q · k)`, a
factor `|G| = 12` more. Confirmed empirically (see [Speedup](#speedup)).

## Where we are going

### Paper: *Growing as Pruning: Isomorph-free generation of JAM chains via canonical augmentation*

- **§1** Introduction (McKay 1998, isomorph-free generation, JAM)
- **§2** Preliminaries (`G`, `κ`, `X_k`, notation)
- **§3** The fiber of a class
- **§4** `G`-equivariance of extension (Theorem 1)
- **§5** Correctness of the algorithm (Theorem 2)
- **§6** Complexity analysis (Theorem 3, two baselines)
- **§7** Empirical verification (8 options, 188,412 classes, benchmark)
- **§8** Conclusions and open problems

Target: MATCH, J. Math. Chem., or a journal in algorithms.

### Downstream work

- **`Laminar`** (Rust software, three modes: exhaustive, sampling,
  specific-chain): uses the fiber structure from this paper.
- **`Stacking as words`** (combinatorial paper): provides the cell
  classification and the `κ` vs `κ^word` divergence, both cited here.

## Open problems

1. Extension to materials with more than two atoms per unit cell, where
   the group is no longer `S₃ × ℤ/2` and the row set is larger.
2. Integration with the MCMC sampling scheme of the `Laminar` project,
   where the fiber structure is used as a transition kernel.
3. Complexity analysis of the full generation pipeline (not just per-level
   cost), in terms of total classes visited vs. total classes generated.
4. A finer pruning that also removes the ≈1.9-fold residual duplication
   of the augmentation DAG, yielding a truly isomorph-free generator in
   McKay's sense. Whether such a pruning exists for `G = S₃ × ℤ/2`, or
   whether the residual duplication is irreducible for these lattices, is
   open.

## Installation

Requires `canonJAM`, installed from GitHub:

```bash
pip install git+https://github.com/edgar-castillo-sci/canonJAM.git
```

Then install this package:

```bash
pip install -e ".[tests]"
```

## Usage

```python
from caugjam import verify_option

result = verify_option(option=1, levels=[2, 3, 4, 5])
print(result["match"])            # True
print(result["speedup"])          # {2: 2.75, 3: 4.38, 4: 6.65, 5: 7.95}
print(result["speedup_vs_full"])  # {2: 1.80, 3: 2.59, 4: 3.76, 5: 4.42}
```

## Contents

- `caugjam/generation.py`: single-layer generation for all JAM options.
- `caugjam/pruning.py`: pruning method and verification.
- `caugjam/fibration.py`: relation between classes of n and n+1.
- `scripts/`: CLI scripts.
  - `scripts/pruning_benchmark.py`: verification and benchmark vs full method.
  - `scripts/fibration.py`: fibration data.
  - `scripts/redundant_check.py`: structural verification (all 8 options).
  - `scripts/stabilizer_dist.py`: distribution of `|Stab|` per level.
  - `scripts/dag_figure.py`: augmentation DAG figure (B/N, `TikZ` or `matplotlib`).
  - `scripts/export_dag.py`: augmentation DAG exported to JSON.
  - `scripts/visualization.py`: fibration graphs.
- `figures/`: standalone `TikZ` figures for the paper.
- `data/`, `graphs/`: generated data and graphs (evidence).

## Running the tests

```bash
pytest tests/ -v
```

## Running the CLI

```bash
# Verification + benchmark, option 1 up to n=10
python3 scripts/pruning_benchmark.py --options 1 --levels 2 3 4 5 6 7 8 9 10 \
    --verbose --output data/pruning/op1_corrected.tsv

# Benchmark options 3, 5, 7
python3 scripts/pruning_benchmark.py --options 3 --levels 2 3 4 5 6 \
    --output data/pruning/op3_corrected.tsv
python3 scripts/pruning_benchmark.py --options 5 --levels 2 3 4 5 6 \
    --output data/pruning/op5_corrected.tsv
python3 scripts/pruning_benchmark.py --options 7 --levels 2 3 4 5 \
    --output data/pruning/op7_corrected.tsv

# Cross-check all 8 options at n=2,3,4
python3 scripts/pruning_benchmark.py --options 1 2 3 4 5 6 7 8 --levels 2 3 4 \
    --output data/pruning/all_opts_small.tsv

# Stabilizer distribution
python3 scripts/stabilizer_dist.py --option 1 --levels 3 4 5 6 7 8 9 10

# Augmentation DAG
python3 scripts/dag_figure.py --option 1 --levels 2 3 4 \
    --output graphs/dag_op1_n2-4.pdf
```

## Related packages

- [`canonJAM`](https://github.com/edgar-castillo-sci/canonJAM):
  canonical filtering (this package depends on it).
- [`caugJAM`](https://github.com/edgar-castillo-sci/caugJAM): this repo.

## License

MIT (see `LICENSE`).
