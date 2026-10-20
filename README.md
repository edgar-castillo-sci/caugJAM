# caugJAM

*[Leer en español](README.es.md)*

Canonical augmentation (pruning) for JAM string generation.
## Author

Edgar R. H. Castillo (Universidad Juárez Autónoma de Tabasco)

## Scientific basis

Builds on the JAM notation described in:

> Arcudia, J., Ortiz-Chi, F., Sanchez-Valenzuela, A., Aspuru-Guzik, A.,
> Merino, G. (2023). "Joining and arrangement of multilayers: A string
> representation for honeycomb layered materials." Matter, 6(5),
> 1503–1513. doi: 10.1016/j.matt.2023.02.014

## What it does

The full method for JAM generation produces all candidates and filters
duplicates. The pruning method generates only the extensions of the
canonical representatives of n-1 layers, avoiding the generation of
candidates that will be filtered out anyway.

The empirical result: for all 8 JAM options, pruning produces exactly
the same canonical classes as the full method, with a speedup that
grows with n.

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
print(result["match"])     # True
print(result["speedup"])   # ~3.2x
```

## Contents

- `caugjam/generation.py`: single-layer generation for all JAM options.
- `caugjam/pruning.py`: pruning method and verification.
- `caugjam/fibration.py`: relation between classes of n and n+1.
- `scripts/`: original CLI scripts.
- `datos/`, `grafos/`: generated data and graphs (evidence).

## Running the tests

```bash
pytest tests/ -v
```

## Running the CLI

```bash
python3 scripts/poda.py --options 1 5 7 --levels 2 3 4
python3 scripts/fibracion.py
```

## Related packages

- [`canonJAM`](https://github.com/edgar-castillo-sci/canonJAM):
  canonical filtering (this package depends on it).
- [`caugJAM`](https://github.com/edgar-castillo-sci/caugJAM): this repo.

## License

MIT (see `LICENSE`).
