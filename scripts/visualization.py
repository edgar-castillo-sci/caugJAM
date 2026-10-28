#!/usr/bin/env python3

"""
visualizacion.py

Visualiza la relación entre niveles consecutivos como un grafo
de 3 columnas (n-1, n, n+1) para opción 1.

Nomenclatura:
  M1   = monocapa con vacío en columna 0  [+0, +j, +j]   → rojo
  M2   = monocapa con vacío en columna 1  [+j, +0, +j]   → azul
  M3   = monocapa con vacío en columna 2  [+j, +j, +0]   → verde
  prepend = añadir monocapa al principio  → línea sólida
  append  = añadir monocapa al final      → línea punteada

Cada nodo es una clase canónica de k capas. Cada arista es una
conexión padre → hijo. La columna 0 es n-1, la columna 1 es n,
la columna 2 es n+1.

Genera:
  graphs/individual_nX/grafo.png   Grafo individual para n=X
  graphs/individual_nX/labels.txt  Mapeo de etiquetas a claves completas
  graphs/individual_nX/leyenda.txt Nomenclatura y qué buscar
  graphs/combinado/grafo.png       Grafo combinado n=n_min..n_max
  graphs/combinado/labels.txt
  graphs/combinado/leyenda.txt
  graphs/README.md                 Guía global de la carpeta
"""

import numpy as np
import sys
import os
import csv
from itertools import permutations

# ─────────────────────────────────────────────
# Dependencias
# ─────────────────────────────────────────────

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import networkx as nx
except ImportError as e:
    print(f"Falta dependencia: {e}")
    print("Instalar con: pip install networkx matplotlib")
    sys.exit(1)

# ─────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_CANONJAM_DIR = os.path.dirname(_SCRIPT_DIR)
_XJAM2_DIR = os.path.join(os.path.dirname(_CANONJAM_DIR), 'xjam2')
_PRUEBAS_DIR = os.path.join(_XJAM2_DIR, 'pruebas')

sys.path.insert(0, _XJAM2_DIR)
sys.path.insert(0, _PRUEBAS_DIR)

from xjam.libjamstd import nparray2chain, chain2nparray
from prueba_grupo import canonical_key_std


# ─────────────────────────────────────────────
# Configuración
# ─────────────────────────────────────────────

OPTIONX = 1
COLORES = {0: '#e41a1c', 1: '#377eb8', 2: '#4daf4a'}  # M1, M2, M3
NOMBRES_M = {0: 'M1 (vacío en 0)', 1: 'M2 (vacío en 1)', 2: 'M3 (vacío en 2)'}
ESTILOS = {'prepend': 'solid', 'append': 'dashed'}
NOMBRES_DIR = {'prepend': 'prepend (abajo)', 'append': 'append (arriba)'}


# ─────────────────────────────────────────────
# Monocapas
# ─────────────────────────────────────────────

def filas_opcion_1():
    opt = ['+0', '+j', '+j']
    filas = list(set(permutations(opt, 3)))
    return [np.array(i) for i in filas]


# ─────────────────────────────────────────────
# Carga de datos
# ─────────────────────────────────────────────

def cargar_canonicas(n):
    archivo = os.path.join(_CANONJAM_DIR, 'datos', f'n{n}', 'canonicas.txt')
    with open(archivo) as f:
        return [line.strip() for line in f if line.strip()]


def cargar_fibracion(n):
    """Carga la relación de n a n+1 desde TSV."""
    archivo = os.path.join(_CANONJAM_DIR, 'datos', 'fibracion', f'fib_n{n}_n{n+1}.tsv')
    fib = []
    with open(archivo) as f:
        reader = csv.reader(f, delimiter='\t')
        next(reader)
        for row in reader:
            if len(row) == 2:
                fib.append((row[0], row[1]))
    return fib


# ─────────────────────────────────────────────
# Clasificación de conexiones
# ─────────────────────────────────────────────

def clasificar_conexion(padre, hijo, optionx=OPTIONX):
    """
    Dada una conexión padre → hijo, identifica qué extensión la produjo.
    Devuelve (m, direccion) donde m ∈ {0,1,2} es la monocapa y
    direccion ∈ {'prepend', 'append'}.

    Si hay varias extensiones que producen el mismo hijo, devuelve
    la primera en el orden: M1-prepend, M1-append, M2-prepend,
    M2-append, M3-prepend, M3-append.
    """
    matriz = chain2nparray(padre)
    filas = filas_opcion_1()

    for i, f in enumerate(filas):
        ext = np.vstack([f, matriz])
        if canonical_key_std(ext, optionx) == hijo:
            return (i, 'prepend')

    for i, f in enumerate(filas):
        ext = np.vstack([matriz, f])
        if canonical_key_std(ext, optionx) == hijo:
            return (i, 'append')

    return (None, None)


# ─────────────────────────────────────────────
# Construcción del grafo
# ─────────────────────────────────────────────

def construir_grafo_individual(n):
    """Grafo de 3 columnas: n-1, n, n+1."""
    fib_prev = cargar_fibracion(n - 1) if n > 1 else []
    fib_curr = cargar_fibracion(n)

    G = nx.DiGraph()

    col0 = set(p for p, _ in fib_prev)
    col1 = set(h for _, h in fib_prev) | set(p for p, _ in fib_curr)
    col2 = set(h for _, h in fib_curr)

    for nodo in col0:
        G.add_node(nodo, layer=0)
    for nodo in col1:
        G.add_node(nodo, layer=1)
    for nodo in col2:
        G.add_node(nodo, layer=2)

    for padre, hijo in fib_prev:
        m, d = clasificar_conexion(padre, hijo)
        G.add_edge(padre, hijo, color=m, style=d)

    for padre, hijo in fib_curr:
        m, d = clasificar_conexion(padre, hijo)
        G.add_edge(padre, hijo, color=m, style=d)

    return G


def construir_grafo_combinado(n_min, n_max):
    """Grafo con columnas n_min-1, n_min, ..., n_max+1."""
    G = nx.DiGraph()

    for n in range(n_min - 1, n_max + 2):
        try:
            canonicas = cargar_canonicas(n)
        except FileNotFoundError:
            continue
        for clave in canonicas:
            G.add_node(clave, layer=n - (n_min - 1))

    for n in range(n_min - 1, n_max + 1):
        try:
            fib = cargar_fibracion(n)
        except FileNotFoundError:
            continue
        for padre, hijo in fib:
            m, d = clasificar_conexion(padre, hijo)
            G.add_edge(padre, hijo, color=m, style=d)

    return G


# ─────────────────────────────────────────────
# Etiquetas cortas
# ─────────────────────────────────────────────

def generar_etiquetas(G, archivo):
    """
    Asigna etiquetas cortas a cada nodo: L{layer}_{idx:02d}.
    Guarda el mapeo en un archivo para referencia.
    """
    layers = nx.get_node_attributes(G, 'layer')
    etiquetas = {}
    por_layer = {}

    for nodo, layer in layers.items():
        por_layer.setdefault(layer, []).append(nodo)

    with open(archivo, 'w') as f:
        f.write("Etiquetas de nodos\n")
        f.write("=" * 60 + "\n\n")
        f.write("Formato: L{layer}_{idx:02d}  →  clave completa\n\n")

        for layer in sorted(por_layer.keys()):
            nodos = sorted(por_layer[layer])
            f.write(f"Capa {layer} ({len(nodos)} nodos):\n")
            for i, nodo in enumerate(nodos, 1):
                et = f"L{layer}_{i:02d}"
                etiquetas[nodo] = et
                f.write(f"  {et}  →  {nodo}\n")
            f.write("\n")

    return etiquetas


# ─────────────────────────────────────────────
# Dibujo
# ─────────────────────────────────────────────

def _layout_por_capas(G, escala_y=1.0):
    layers = nx.get_node_attributes(G, 'layer')
    pos = {}
    for layer in sorted(set(layers.values())):
        nodos = sorted([n for n, l in layers.items() if l == layer])
        n = len(nodos)
        for i, nodo in enumerate(nodos):
            x = layer
            y = escala_y * (i + 0.5) / n if n > 0 else 0.5
            pos[nodo] = (x, y)
    return pos


def _dibujar(G, archivo, etiquetas, titulo, n_min=None, n_max=None):
    fig, ax = plt.subplots(figsize=(18, 14))

    pos = _layout_por_capas(G)

    # Aristas
    for (u, v, data) in G.edges(data=True):
        color = COLORES.get(data.get('color'), 'gray')
        estilo = ESTILOS.get(data.get('style'), 'solid')
        nx.draw_networkx_edges(
            G, pos, edgelist=[(u, v)], ax=ax,
            edge_color=color, style=estilo,
            alpha=0.45, arrows=True, arrowsize=7,
            width=1.0, connectionstyle='arc3,rad=0.08'
        )

    # Nodos
    layers = nx.get_node_attributes(G, 'layer')
    for layer in sorted(set(layers.values())):
        nodos = [n for n, l in layers.items() if l == layer]
        nx.draw_networkx_nodes(
            G, pos, nodelist=nodos, ax=ax,
            node_color='white', node_size=260,
            edgecolors='black', linewidths=0.6
        )

    # Etiquetas
    nx.draw_networkx_labels(G, pos, etiquetas, font_size=6, ax=ax)

    # Títulos de columnas
    n_layers = len(set(layers.values()))
    for layer in range(n_layers):
        x = layer
        if n_min is not None:
            nivel = n_min - 1 + layer
            label = f"n={nivel}"
        else:
            label = f"L{layer}"
        ax.text(x, 1.03, label, ha='center',
                fontsize=13, fontweight='bold')

    # Leyenda
    from matplotlib.lines import Line2D
    elementos = []
    for m in [0, 1, 2]:
        elementos.append(Line2D([0], [0], color=COLORES[m], lw=2.5,
                                label=NOMBRES_M[m]))
    for d in ['prepend', 'append']:
        elementos.append(Line2D([0], [0], color='black', lw=2,
                                linestyle=ESTILOS[d],
                                label=NOMBRES_DIR[d]))
    ax.legend(handles=elementos, loc='upper right',
              fontsize=10, framealpha=0.95)

    ax.set_title(titulo, fontsize=15, pad=20)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(archivo, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Guardado: {archivo}")


# ─────────────────────────────────────────────
# Leyenda / notas
# ─────────────────────────────────────────────

def escribir_leyenda(archivo, n_min, n_max=None):
    with open(archivo, 'w') as f:
        f.write("Leyenda del grafo\n")
        f.write("=" * 60 + "\n\n")

        f.write("NODOS\n")
        f.write("  Cada nodo es una clase canónica de k capas.\n")
        f.write("  La etiqueta es L{columna}_{indice:02d}.\n")
        f.write("  El mapeo completo está en labels.txt.\n\n")

        f.write("COLUMNAS\n")
        if n_max is None:
            f.write(f"  Columna 0: n={n_min-1}\n")
            f.write(f"  Columna 1: n={n_min}\n")
            f.write(f"  Columna 2: n={n_min+1}\n\n")
        else:
            for layer, n in enumerate(range(n_min - 1, n_max + 2)):
                f.write(f"  Columna {layer}: n={n}\n")
            f.write("\n")

        f.write("COLORES (monocapa añadida)\n")
        for m in [0, 1, 2]:
            f.write(f"  {COLORES[m]}  {NOMBRES_M[m]}\n")
        f.write("\n")

        f.write("ESTILOS DE LÍNEA (dirección)\n")
        f.write(f"  sólida     prepend: añadir monocapa al principio (abajo)\n")
        f.write(f"  punteada   append:  añadir monocapa al final (arriba)\n\n")

        f.write("CLASIFICACIÓN DE CONEXIONES\n")
        f.write("  Cuando varias extensiones producen el mismo hijo,\n")
        f.write("  se dibuja la primera en el orden:\n")
        f.write("    M1-prepend > M1-append > M2-prepend >\n")
        f.write("    M2-append > M3-prepend > M3-append\n\n")

        f.write("QUÉ BUSCAR\n")
        f.write("  - Nodos con muchas aristas salientes: padres con\n")
        f.write("    fibra grande.\n")
        f.write("  - Nodos con muchas aristas entrantes: hijos con\n")
        f.write("    múltiples padres (convergencias).\n")
        f.write("  - Zonas del grafo con mucha densidad: posibles\n")
        f.write("    patrones de redundancia.\n")
        f.write("  - Nodos con aristas de un solo color: extensiones\n")
        f.write("    que siempre vienen de la misma monocapa.\n\n")

        f.write("FIBRACIÓN\n")
        f.write("  Cada columna k → k+1 es una fibración parcial.\n")
        f.write("  La fibra de un nodo es el conjunto de sus hijos.\n")
        f.write("  El tamaño de fibra máximo observado es 6.\n")

# ─────────────────────────────────────────────
# README global
# ─────────────────────────────────────────────

def _escribir_readme_grafos(archivo):
    """Genera el README global de la carpeta grafos."""
    with open(archivo, 'w') as f:
        f.write("# Grafos de la relación entre niveles\n\n")
        f.write("Cada subdirectorio contiene un grafo y sus archivos de apoyo.\n\n")

        f.write("## Estructura\n\n")
        f.write("```\n")
        f.write("graphs/\n")
        f.write("├── README.md\n")
        f.write("├── individual_n3/\n")
        f.write("│   ├── grafo.png      Grafo de 3 columnas (n=2, 3, 4)\n")
        f.write("│   ├── labels.txt     Mapeo L{col}_{idx} → clave completa\n")
        f.write("│   └── leyenda.txt    Nomenclatura y qué buscar\n")
        f.write("├── individual_n4/\n")
        f.write("│   ├── grafo.png      Grafo de 3 columnas (n=3, 4, 5)\n")
        f.write("│   ├── labels.txt\n")
        f.write("│   └── leyenda.txt\n")
        f.write("├── individual_n5/\n")
        f.write("│   ├── grafo.png      Grafo de 3 columnas (n=4, 5, 6)\n")
        f.write("│   ├── labels.txt\n")
        f.write("│   └── leyenda.txt\n")
        f.write("└── combinado/\n")
        f.write("    ├── grafo.png      Grafo de 5 columnas (n=2..6)\n")
        f.write("    ├── labels.txt\n")
        f.write("    └── leyenda.txt\n")
        f.write("```\n\n")

        f.write("## Nomenclatura\n\n")
        f.write("### Nodos\n\n")
        f.write("Cada nodo es una clase canónica de k capas.\n")
        f.write("La etiqueta es `L{columna}_{indice:02d}`:\n\n")
        f.write("- `L0_01`, `L0_02`, ... → columna 0 (nivel n-1)\n")
        f.write("- `L1_01`, `L1_02`, ... → columna 1 (nivel n)\n")
        f.write("- `L2_01`, `L2_02`, ... → columna 2 (nivel n+1)\n\n")
        f.write("El mapeo completo etiqueta → clave está en `labels.txt`.\n\n")

        f.write("### Colores (monocapa añadida)\n\n")
        f.write("| Color | Monocapa | Fila |\n")
        f.write("|---|---|---|\n")
        f.write("| rojo  | M1 | `[+0, +j, +j]` |\n")
        f.write("| azul  | M2 | `[+j, +0, +j]` |\n")
        f.write("| verde | M3 | `[+j, +j, +0]` |\n\n")

        f.write("### Estilos de línea (dirección)\n\n")
        f.write("| Estilo | Dirección | Significado |\n")
        f.write("|---|---|---|\n")
        f.write("| sólida | prepend | añadir monocapa al principio (abajo) |\n")
        f.write("| punteada | append | añadir monocapa al final (arriba) |\n\n")

        f.write("## Cómo leer un grafo\n\n")
        f.write("1. Las columnas van de izquierda (n-1) a derecha (n+1).\n")
        f.write("2. Cada nodo es una clase canónica.\n")
        f.write("3. Cada arista conecta un padre (izquierda) con un hijo (derecha).\n")
        f.write("4. El color indica qué monocapa se añadió.\n")
        f.write("5. El estilo indica la dirección (prepend/append).\n\n")

        f.write("## Qué buscar\n\n")
        f.write("- **Abanicos**: nodos con muchas aristas salientes → fibra grande.\n")
        f.write("- **Embudos**: nodos con muchas aristas entrantes → convergencias.\n")
        f.write("- **Colores puros**: padres que solo tienen aristas de un color.\n")
        f.write("- **Zonas densas**: posibles patrones de redundancia.\n\n")

        f.write("## Regenerar\n\n")
        f.write("```bash\n")
        f.write("cd ~/Labs/JAM_canonicalización/canonJAM\n")
        f.write("python3 scripts/visualization.py\n")
        f.write("```\n")
# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

if __name__ == "__main__":
    grafos = os.path.join(_CANONJAM_DIR, 'grafos')
    os.makedirs(grafos, exist_ok=True)

    # 1. Grafos individuales
    for n in [3, 4, 5]:
        print(f"Grafo individual n={n}...")
        dir_n = os.path.join(grafos, f'individual_n{n}')
        os.makedirs(dir_n, exist_ok=True)

        G = construir_grafo_individual(n)
        etiquetas = generar_etiquetas(
            G, os.path.join(dir_n, 'labels.txt')
        )
        _dibujar(
            G,
            os.path.join(dir_n, 'grafo.png'),
            etiquetas,
            f'Relación n={n-1} → n={n} → n={n+1}',
            n_min=n
        )
        escribir_leyenda(
            os.path.join(dir_n, 'leyenda.txt'),
            n
        )
        print(f"  {G.number_of_nodes()} nodos, "
              f"{G.number_of_edges()} aristas\n")

    # 2. Grafo combinado
    print("Grafo combinado n=3..5...")
    dir_comb = os.path.join(grafos, 'combinado')
    os.makedirs(dir_comb, exist_ok=True)

    G = construir_grafo_combinado(3, 5)
    etiquetas = generar_etiquetas(
        G, os.path.join(dir_comb, 'labels.txt')
    )
    _dibujar(
        G,
        os.path.join(dir_comb, 'grafo.png'),
        etiquetas,
        'Relación n=2 → n=3 → n=4 → n=5 → n=6',
        n_min=3,
        n_max=5
    )
    escribir_leyenda(
        os.path.join(dir_comb, 'leyenda.txt'),
        3, 5
    )
    print(f"  {G.number_of_nodes()} nodos, "
          f"{G.number_of_edges()} aristas\n")

    # 3. README global
    _escribir_readme_grafos(os.path.join(grafos, 'README.md'))

    print("Listo.")
