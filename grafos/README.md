# Grafos de la relación entre niveles

Cada subdirectorio contiene un grafo y sus archivos de apoyo.

## Estructura

```
grafos/
├── README.md
├── individual_n3/
│   ├── grafo.png      Grafo de 3 columnas (n=2, 3, 4)
│   ├── labels.txt     Mapeo L{col}_{idx} → clave completa
│   └── leyenda.txt    Nomenclatura y qué buscar
├── individual_n4/
│   ├── grafo.png      Grafo de 3 columnas (n=3, 4, 5)
│   ├── labels.txt
│   └── leyenda.txt
├── individual_n5/
│   ├── grafo.png      Grafo de 3 columnas (n=4, 5, 6)
│   ├── labels.txt
│   └── leyenda.txt
└── combinado/
    ├── grafo.png      Grafo de 5 columnas (n=2..6)
    ├── labels.txt
    └── leyenda.txt
```

## Nomenclatura

### Nodos

Cada nodo es una clase canónica de k capas.
La etiqueta es `L{columna}_{indice:02d}`:

- `L0_01`, `L0_02`, ... → columna 0 (nivel n-1)
- `L1_01`, `L1_02`, ... → columna 1 (nivel n)
- `L2_01`, `L2_02`, ... → columna 2 (nivel n+1)

El mapeo completo etiqueta → clave está en `labels.txt`.

### Colores (monocapa añadida)

| Color | Monocapa | Fila |
|---|---|---|
| rojo  | M1 | `[+0, +j, +j]` |
| azul  | M2 | `[+j, +0, +j]` |
| verde | M3 | `[+j, +j, +0]` |

### Estilos de línea (dirección)

| Estilo | Dirección | Significado |
|---|---|---|
| sólida | prepend | añadir monocapa al principio (abajo) |
| punteada | append | añadir monocapa al final (arriba) |

## Cómo leer un grafo

1. Las columnas van de izquierda (n-1) a derecha (n+1).
2. Cada nodo es una clase canónica.
3. Cada arista conecta un padre (izquierda) con un hijo (derecha).
4. El color indica qué monocapa se añadió.
5. El estilo indica la dirección (prepend/append).

## Qué buscar

- **Abanicos**: nodos con muchas aristas salientes → fibra grande.
- **Embudos**: nodos con muchas aristas entrantes → convergencias.
- **Colores puros**: padres que solo tienen aristas de un color.
- **Zonas densas**: posibles patrones de redundancia.

## Regenerar

```bash
cd ~/Labs/JAM_canonicalización/canonJAM
python3 scripts/visualizacion.py
```
