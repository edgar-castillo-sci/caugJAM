# caugJAM

*[Read in English](README.md)*

Aumentación canónica (generación isomorfa-libre) para cadenas JAM.

## Autor

Edgar Castillo (Independent Researcher)

## Base científica

Construye sobre la notación JAM y la canonicalización descritas en:

> Arcudia, J., Ortiz-Chi, F., Sanchez-Valenzuela, A., Aspuru-Guzik, A.,
> Merino, G. (2023). "Joining and arrangement of multilayers: A string
> representation for honeycomb layered materials." Matter, 6(5),
> 1503–1513. doi: 10.1016/j.matt.2023.02.014

y en el paper de canonicalización compañero (en preparación), que
formaliza el grupo de simetría `G = S₃ × ℤ/2`, el representante canónico
`κ`, y las formas cerradas de Burnside.

La prueba de correctitud, el teorema de complejidad y la verificación
empírica del método de poda son el contenido del paper compañero
*Growing as Pruning: Isomorph-free generation of JAM chains via canonical
augmentation* (en preparación, objetivo: MATCH).

## Qué hace

El método completo para generación JAM produce todos los candidatos en el
nivel `n` y filtra duplicados. El método de poda genera solo las
extensiones de los representantes canónicos en el nivel `n-1`, evitando
la generación de candidatos que serán filtrados de todos modos.

Formalmente, la **fibra** de un representante canónico `a ∈ X_{n-1}` es
el conjunto de hijos canónicos obtenidos al extender `a` con `prepend` y
`append` sobre las filas de una sola capa de la opción:

    Fib(a) = { κ(c) : c ∈ Children(a) }

El teorema clave (probado en el paper) es que `Fib` es invariante bajo
la acción del grupo, `Fib(g·a) = Fib(a)` para todo `g ∈ G`. Por lo tanto
la fibra depende solo de la órbita de `a`, y el método de poda puede
extender solo los representantes canónicos del nivel `n-1`, sin
necesidad de probar cada redundante.

El resultado es exactamente el mismo conjunto de clases canónicas que el
método completo, con una aceleración que converge a `|G| = 12` contra la
línea base de extensión ingenua (y a `|G|/2 ≈ 6` contra el método
completo; ver [Aceleración](#aceleración) abajo).

## Estado actual

| Componente | Estado |
|---|---|
| `caugjam/pruning.py` (el método) | implementado |
| `caugjam/fibration.py` (relación n → n+1) | implementado |
| `scripts/pruning_benchmark.py` (verificación + benchmark) | implementado |
| `scripts/redundant_check.py` (verificación estructural) | implementado |
| `scripts/stabilizer_dist.py` (distribución de estabilizadores) | implementado |
| `scripts/dag_figure.py` (figura del DAG de aumentación) | implementado |
| `scripts/export_dag.py` (DAG → JSON) | implementado |
| Prueba formal de `G`-equivarianza | **cerrada** (§4 del paper) |
| Prueba formal de correctitud | **cerrada** (§5 del paper) |
| Prueba formal de complejidad | **cerrada** (§6 del paper) |
| Paper (borrador) | en preparación |

## Qué hemos demostrado (empíricamente)

### La fibra depende solo de la órbita

Para las 8 opciones JAM y todos los niveles probados, **cada clase
produce un conjunto uniforme de hijos canónicos**: si dos cadenas crudas
canonicalizan al mismo representante, producen exactamente el mismo
conjunto de hijos canónicos en el siguiente nivel.

| Opción | q | Niveles probados | Clases verificadas | Resultado |
|---|---|---|---|---|
| 1 | 3 | n=2..10 | 7,564 | all yes |
| 2 | 6 | n=2..7 | 28,208 | all yes |
| 3 | 6 | n=2..7 | 28,208 | all yes |
| 4 | 12 | n=2..5 | 22,672 | all yes |
| 5 | 6 | n=2..7 | 28,208 | all yes |
| 6 | 6 | n=2..7 | 28,208 | all yes |
| 7 | 12 | n=2..5 | 22,672 | all yes |
| 8 | 12 | n=2..5 | 22,672 | all yes |
| **Total** | | **45 niveles** | **188,412 clases** | **0 excepciones** |

**Interpretación:** el representante canónico por sí solo determina la
fibra. No se necesita un invariante más fino (estabilizador, posición en
la fibra, o forma canónica de palabra).

### La poda produce las mismas clases que el método completo

Para las ocho opciones canónicas y `n = 2, 3, 4`, los conteos de clases
producidos por el método de poda coinciden exactamente con los del
método completo:

| Opción | n=2 | n=3 | n=4 |
|---|---|---|---|
| 1 | 2 | 4 | 10 |
| 2, 3, 5, 6 | 5 | 21 | 120 |
| 4, 7, 8 | 16 | 144 | 1776 |

Coinciden con los valores publicados de Arcudia et al. (2023) para las
opciones 1–4 y los extienden a las cuatro opciones extendidas 5–8.

### El DAG de aumentación no es un árbol

Cada clase en el nivel `n+1` tiene en promedio ≈1.9 padres en el nivel
`n` (medido en opción 1 para `n ≤ 8`; el cociente converge a 2 desde
abajo). Esto es consecuencia de la asimetría entre `prepend` y `append`
bajo `κ`: la misma órbita puede alcanzarse desde dos clases distintas
del nivel anterior. El método de poda elimina un factor `|G|` de
duplicados en el número de llamadas a canonicalización, pero no elimina
esta duplicación residual; esa duplicación se maneja en el paso de
deduplicación por conjunto.

### La distribución de estabilizadores converge a trivial

La fracción de órbitas con estabilizador trivial tiende a 1, que es lo
que hace que la aceleración converja a `|G|`. Para la opción 1, el
tamaño promedio del estabilizador `avg|Stab|` decrece de 2.25 (n=3) a
1.033 (n=10). Ver `scripts/stabilizer_dist.py` y
`data/pruning/stabilizer_op1.tsv`.

## Aceleración

Se reportan dos líneas base, para separar el ahorro algorítmico (que es
`|G|`) del ahorro contra una implementación específica (que es menor por
un factor constante).

- **Línea base de extensión ingenua** (`t_naive`): extender cada cadena
  de `X_{n-1}` por `prepend` y `append`, deduplicar por contenido,
  canonicalizar cada extensión una vez. La aceleración contra esta línea
  base converge a `|G| = 12`.
- **Método completo** (`t_full`): generar `X_n` desde cero, llamar a
  `filter_duplicates`, recalcular las claves canónicas de las clases
  sobrevivientes. Incluye una doble pasada de canonicalización, así que
  la aceleración converge a `|G|/2 ≈ 6`.

Aceleraciones medidas (ver `data/pruning/op{1,3,5,7}_corrected.tsv`):

| Opción | n | `t_naive` | `t_poda` | `t_full` | aceleración (naive / full) |
|---|---|---|---|---|---|
| 1 | 10 | 28.381 | 2.522 | 15.480 | 11.25 / 6.14 |
| 3 | 6 | 28.232 | 2.481 | 15.390 | 11.38 / 6.20 |
| 5 | 6 | 26.964 | 2.368 | 14.607 | 11.39 / 6.17 |
| 7 | 5 | 140.423 | 12.327 | 77.059 | 11.39 / 6.25 |

Las opciones 3 (binaria con buckling, `v = sign∘flip`) y 5 (Janus 1H,
`v = flip`) tienen `v`-involuciones distintas pero los mismos conteos de
clases, y sus aceleraciones en `n = 6` son esencialmente idénticas
(`11.38/6.20` y `11.39/6.17`). La composición buckled no afecta la
complejidad del método de poda.

## Qué probamos (resumen del paper)

### `G`-equivarianza de la extensión

La operación de extensión conmuta con la acción del grupo, salvo por
renombrado de la fila de una sola capa y por el intercambio de dirección
(prepend/append).

- Bajo `σ ∈ S₃` (permutación de columnas):
  `σ·prepend(f, a) = prepend(σ·f, σ·a)` y
  `σ·append(f, a) = append(σ·f, σ·a)`. Dirección preservada.
- Bajo `v` (flip, o `sign∘flip` para buckled):
  `v·prepend(f, a) = append(v·f, v·a)` y
  `v·append(f, a) = prepend(v·f, v·a)`. Dirección intercambiada.

Como `Rows` es cerrado bajo `G` y `{prepend, append}` es cerrado bajo el
intercambio inducido por `v`, el conjunto de extensiones se preserva
como conjunto:

    g · Children(a) = Children(g · a)   para todo g ∈ G, a ∈ X_k

Por lo tanto `Fib(g·a) = κ(Children(g·a)) = κ(g·Children(a)) = κ(Children(a)) = Fib(a)`,
usando la `G`-invarianza de `κ`. Este es el Teorema 1 del paper.

### Correctitud

Si cada órbita en `X_{n-1}/G` está representada por su representante
canónico y cada representante canónico se extiende a sus hijos,
entonces `T_n = { κ(c) : c ∈ Children(a), a ∈ T_{n-1} }` contiene
exactamente un representante por órbita de `X_n/G`. Este es el Teorema 2
del paper. El ahorro está en el número de llamadas a canonicalización,
no en la ausencia de duplicados (ver la observación del DAG arriba).

### Complejidad

Generar del nivel `k` al `k+1` requiere `|X_k/G| · 2q`
canonicalizaciones, cada una `O(k)`. Total: `O(|X_k/G| · q · k)`. La
línea base de extensión ingenua es
`O(|X_k| · q · k) = O(|G| · |X_k/G| · q · k)`, un factor `|G| = 12` más.
Confirmado empíricamente (ver [Aceleración](#aceleración)).

## Hacia dónde vamos

### Paper: *Growing as Pruning: Isomorph-free generation of JAM chains via canonical augmentation*

- **§1** Introducción (McKay 1998, generación isomorfa-libre, JAM)
- **§2** Preliminares (`G`, `κ`, `X_k`, notación)
- **§3** La fibra de una clase
- **§4** `G`-equivarianza de la extensión (Teorema 1)
- **§5** Correctitud del algoritmo (Teorema 2)
- **§6** Análisis de complejidad (Teorema 3, dos líneas base)
- **§7** Verificación empírica (8 opciones, 188,412 clases, benchmark)
- **§8** Conclusiones y problemas abiertos

Objetivo: MATCH, J. Math. Chem., o una revista de algoritmos.

### Trabajo downstream

- **`Laminar`** (software Rust, tres modos: exhaustivo, muestreo,
  cadena específica): usa la estructura de fibra de este paper.
- **`Stacking as words`** (paper combinatorio): provee la clasificación
  en celdas y la divergencia `κ` vs `κ^word`, ambas citadas aquí.

## Problemas abiertos

1. Extensión a materiales con más de dos átomos por celda unitaria, donde
   el grupo ya no es `S₃ × ℤ/2` y el conjunto de filas es mayor.
2. Integración con el esquema de muestreo MCMC del proyecto `Laminar`,
   donde la estructura de fibra se usa como kernel de transición.
3. Análisis de complejidad del pipeline de generación completo (no solo
   el costo por nivel), en términos de clases totales visitadas vs.
   clases totales generadas.
4. Una poda más fina que también elimine la duplicación residual ≈1.9
   del DAG de aumentación, produciendo un generador verdaderamente
   isomorfo-libre en el sentido de McKay. Si tal poda existe para
   `G = S₃ × ℤ/2`, o si la duplicación residual es irreducible para
   estos retículos, está abierto.

## Instalación

Requiere `canonJAM` v1.2.1 o superior. Instalar desde GitHub:

```bash
pip install "canonjam @ git+https://github.com/edgar-castillo-sci/canonJAM.git@v1.2.1"
```

Luego instalar este paquete (con dependencias de test):

```bash
pip install -e ".[tests]"
```

## Uso

```python
from caugjam import verify_option

result = verify_option(option=1, levels=[2, 3, 4, 5])
print(result["match"])            # True
print(result["speedup"])          # {2: 2.75, 3: 4.38, 4: 6.65, 5: 7.95}
print(result["speedup_vs_full"])  # {2: 1.80, 3: 2.59, 4: 3.76, 5: 4.42}
```

## Contenido

- `caugjam/generation.py`: generación de una sola capa para las 8 opciones JAM.
- `caugjam/pruning.py`: método de poda y verificación.
- `caugjam/fibration.py`: relación entre clases de n y n+1.
- `scripts/`: scripts CLI.
  - `scripts/pruning_benchmark.py`: verificación y benchmark vs método completo.
  - `scripts/fibration.py`: datos de fibración.
  - `scripts/redundant_check.py`: verificación estructural (las 8 opciones).
  - `scripts/stabilizer_dist.py`: distribución de `|Stab|` por nivel.
  - `scripts/dag_figure.py`: figura del DAG de aumentación (TikZ o matplotlib).
  - `scripts/export_dag.py`: DAG de aumentación exportado a JSON.
  - `scripts/visualization.py`: grafos de fibración.
- `figures/`: figuras `TikZ` independientes para el paper.
- `data/`, `graphs/`: datos y grafos generados (evidencia).

### Nota sobre versionado de datos

Los volcados de texto grandes bajo `data/` **no se versionan** (exceden
el límite blando de 50 MB de GitHub):
- `data/n*/**/*.txt` (listas de cadenas canónicas, hasta 106 MB en n=15)
- `data/opt*/**/*.txt` (listas de cadenas canónicas, hasta 74 MB en n=9)
- `data/redundant_v2/**/clases.tsv` (volcados por clase, hasta 114 MB)

Sí se versiona la evidencia estructurada: tablas `.tsv` bajo
`data/pruning/`, resúmenes `resumen.txt` bajo `data/redundant/`,
`figures/*.tex`, y `graphs/*.png`. Los archivos excluidos se regeneran
con los scripts en `scripts/`.

## Cómo correr los tests

```bash
pytest -v
```

## Cómo correr la CLI

```bash
# Verificación + benchmark, opción 1 hasta n=10
python3 scripts/pruning_benchmark.py --options 1 \
    --levels 2 3 4 5 6 7 8 9 10 --verbose \
    --output data/pruning/op1_corrected.tsv

# Benchmark opciones 3, 5, 7
python3 scripts/pruning_benchmark.py --options 3 --levels 2 3 4 5 6 \
    --output data/pruning/op3_corrected.tsv
python3 scripts/pruning_benchmark.py --options 5 --levels 2 3 4 5 6 \
    --output data/pruning/op5_corrected.tsv
python3 scripts/pruning_benchmark.py --options 7 --levels 2 3 4 5 \
    --output data/pruning/op7_corrected.tsv

# Cross-check las 8 opciones en n=2,3,4
python3 scripts/pruning_benchmark.py --options 1 2 3 4 5 6 7 8 \
    --levels 2 3 4 --output data/pruning/all_opts_small.tsv

# Distribución de estabilizadores
python3 scripts/stabilizer_dist.py --option 1 --levels 3 4 5 6 7 8 9 10

# DAG de aumentación
python3 scripts/dag_figure.py --option 1 --levels 2 3 4 \
    --output graphs/dag_op1_n2-4.pdf
```

## Paquetes relacionados

- [`canonJAM`](https://github.com/edgar-castillo-sci/canonJAM):
  filtrado canónico (este paquete depende de él, pinneado a `v1.2.1`).
- [`Laminar`](https://github.com/edgar-castillo-sci/Laminar): suite Rust
  (downstream, usa la estructura de fibra).
- [`Stacking as words`](https://github.com/edgar-castillo-sci/stacking-as-words):
  exploración combinatoria (compañero, no dependencia).

## Citación

Si usas caugJAM en tu investigación, cítalo como:

```bibtex
@software{caugjam,
  author       = {Castillo, Edgar},
  title        = {{caugJAM: Canonical augmentation for JAM string generation}},
  year         = {2026},
  publisher    = {Zenodo},
  howpublished = {\url{https://github.com/edgar-castillo-sci/caugJAM}},
  note         = {DOI to be assigned}
}
```

El archivo `CITATION.cff` está incluido en el repositorio; GitHub
renderizará un botón "Cite this repository" automáticamente.

## Licencia

MIT (ver `LICENSE`).
