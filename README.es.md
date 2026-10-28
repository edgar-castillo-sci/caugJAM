# caugJAM

*[Read in English](README.md)*

Aumentación canónica (poda) para la generación de cadenas JAM.

## Autor

Edgar Castillo (Independent Researcher)

## Base científica

Construye sobre la notación JAM descrita en:

> Arcudia, J., Ortiz-Chi, F., Sanchez-Valenzuela, A., Aspuru-Guzik, A.,
> Merino, G. (2023). "Joining and arrangement of multilayers: A string
> representation for honeycomb layered materials." Matter, 6(5),
> 1503–1513. doi: 10.1016/j.matt.2023.02.014

## Qué hace

El método completo de generación JAM produce todos los candidatos y
filtra duplicados. El método de poda genera solo las extensiones de los
representantes canónicos de n-1 capas, evitando la generación de
candidatos que de todas formas serían filtrados.

El resultado empírico: para las 8 opciones de JAM, la poda produce
exactamente las mismas clases canónicas que el método completo, con un
speedup que crece con n.

## Instalación

Requiere `canonJAM`, instalado desde GitHub:

```bash
pip install git+https://github.com/edgar-castillo-sci/canonJAM.git
```

Luego instala este paquete:

```bash
pip install -e ".[tests]"
```

## Uso

```python
from caugjam import verify_option

result = verify_option(option=1, levels=[2, 3, 4, 5])
print(result["match"])     # True
print(result["speedup"])   # ~3.2x
```

## Contenido

- `caugjam/generation.py`: generación de monocapas para las 8 opciones.
- `caugjam/pruning.py`: método de poda y verificación.
- `caugjam/fibration.py`: relación entre clases de n y n+1.
- `scripts/`: scripts CLI originales.
- `data/`, `graphs/`: datos y grafos generados (evidencia).

## Correr los tests

```bash
pytest tests/ -v
```

## Correr el CLI

```bash
python3 scripts/pruning_benchmark.py --options 1 5 7 --levels 2 3 4
python3 scripts/fibration.py
```

## Paquetes relacionados

- [`canonJAM`](https://github.com/edgar-castillo-sci/canonJAM):
  filtrado canónico (este paquete depende de él).
- [`caugJAM`](https://github.com/edgar-castillo-sci/caugJAM): este repo.

## Licencia

MIT (ver `LICENSE`).
