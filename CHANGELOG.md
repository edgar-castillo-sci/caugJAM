# Changelog

All notable changes to caugJAM are documented here. The format is based
on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `CITATION.cff` (DOI will be added after Zenodo publication).
- `CHANGELOG.md` (this file).

## [0.1.0] - 2026-10-27

Initial release, accompanying the manuscript *Growing as Pruning:
Isomorph-free generation of JAM chains via canonical augmentation* (in
preparation, target: MATCH).

### Added

- `caugjam/pruning.py`: canonical augmentation (pruning) method for JAM
  chains. Generates only the extensions of the canonical
  representatives at level n-1, avoiding the generation of candidates
  that will be filtered out by the full method.
- `caugjam/fibration.py`: relation between the classes of level n and
  the classes of level n+1 (parent → child edges of the augmentation
  DAG).
- `caugjam/generation.py`: single-layer generation for all 8 JAM
  options.
- Verification and benchmark scripts under `scripts/`:
  - `pruning_benchmark.py`: verification of the pruning method against
    the full method, plus timing against two baselines (the naive
    extension baseline and the full method).
  - `fibration.py`: fibration data between consecutive levels.
  - `redundant_check.py`: structural verification across all 8 options.
  - `stabilizer_dist.py`: distribution of |Stab| per level.
  - `dag_figure.py`, `export_dag.py`: augmentation DAG figure and JSON
    export.
  - `visualization.py`: fibration graphs.
- `isomorph_free_experiments/`: strict isomorph-free generation via
  argmin-parent, with exhaustive verification of G-equivariance on
  options 1, 3, and 5.
- Evidence data under `data/`: canonical classes for all 8 options up
  to tractable levels, fibration summaries, pruning benchmarks, and
  redundant class checks.
- Figures and TikZ sources under `figures/` and `graphs/`.

### Verified

- **Fiber G-invariance** (Theorem 1 of the paper): the fiber of a class
  depends only on the orbit, not on the chosen representative.
  Verified on 188,412 classes across 45 levels and 8 options, with
  zero exceptions.
- **Correctness** (Theorem 2 of the paper): for all 8 options and
  n = 2, 3, 4, the pruning method produces the same class counts as
  the full method of canonJAM.
- **Speedup against the naive extension baseline** converges to
  |G| = 12 from below (measured 11.25 for option 1 at n = 10,
  11.38 for option 3 at n = 6, 11.39 for option 5 at n = 6, 11.39 for
  option 7 at n = 5).
- **Speedup against the full method** converges to |G|/2 ≈ 6 (measured
  6.14 for option 1 at n = 10, 6.20 for option 3 at n = 6, 6.17 for
  option 5 at n = 6, 6.25 for option 7 at n = 5).
- **The augmentation DAG is not a tree**: on average ≈1.9 parents per
  class at level n+1 (measured on option 1 for n ≤ 8), a consequence
  of the asymmetry between `prepend` and `append` under κ.
- **Strict isomorph-free generation** is possible via argmin-parent at
  exactly 2.5× the cost of the deduplication-based pruning method,
  universal across the 8 options.

### Dependencies

- `canonjam` (installed from GitHub; pinned to v1.2.1). caugJAM uses
  `canonical_key`, `filter_duplicates`, and `rows_for_option` from the
  companion package.
- `numpy` (runtime).

### Notes

- caugJAM does **not** depend on `xjam2`. The comparison against the
  pairwise method of the JAM framework is in canonJAM's
  `tests/comparison/`, not here.
- This is a pre-publication release. The DOI will be assigned by
  Zenodo after the corresponding manuscript is submitted.
