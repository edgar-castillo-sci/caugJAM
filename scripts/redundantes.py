#!/usr/bin/env python3
"""
redundantes.py

Para cada nivel n, construye la relación:

    padre_canonico → elemento_redundante → [hijos]

donde:
  - padre_canonico: la clase canónica de n capas.
  - elemento_redundante: un candidato crudo de n capas que pertenece
    a esa clase (es decir, cuya clave canónica es la del padre).
  - hijos: las clases canónicas de n+1 capas que se obtienen al
    extender el redundante con cada una de las 6 extensiones posibles.

Objetivo: determinar si los redundantes de una misma clase producen
los mismos hijos o no. Si varían, identificar qué los distingue.

Salida:
  datos/redundantes/nX/clases.tsv     Relación completa
  datos/redundantes/nX/resumen.txt    Estadísticas por clase
"""

import numpy as np
import sys
import os
import csv
from itertools import permutations
from collections import defaultdict
from time import perf_counter

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
NIVELES = [3, 4, 5]


# ─────────────────────────────────────────────
# Monocapas y generación
# ─────────────────────────────────────────────

def filas_opcion_1():
    opt = ['+0', '+j', '+j']
    filas = list(set(permutations(opt, 3)))
    return [np.array(i) for i in filas]


def generar_cadenas_crudas(n):
    """Genera TODOS los candidatos de n capas, sin filtrar."""
    filas = filas_opcion_1()
    candidatos = [np.array(f).reshape(1, -1) for f in filas]

    for _ in range(2, n + 1):
        nuevos = []
        for c in candidatos:
            for f in filas:
                nuevos.append(np.vstack([c, f]))
        candidatos = nuevos

    return [nparray2chain(c) for c in candidatos]


# ─────────────────────────────────────────────
# Extensiones
# ─────────────────────────────────────────────

def generar_extensiones(clave, optionx=OPTIONX):
    """Genera las 6 extensiones de una estructura (3 monocapas × 2 direcciones)."""
    matriz = chain2nparray(clave)
    filas = filas_opcion_1()
    extensiones = []
    for f in filas:
        # prepend
        extensiones.append((np.vstack([f, matriz]), 'prepend', f))
        # append
        extensiones.append((np.vstack([matriz, f]), 'append', f))
    return extensiones


# ─────────────────────────────────────────────
# Construcción de la relación
# ─────────────────────────────────────────────

def construir_relacion(n, optionx=OPTIONX):
    """
    Para un nivel n, devuelve:
      clases: dict {clave_canonica: [redundantes]}
    donde cada redundante es una cadena cruda que pertenece a esa clase.
    """
    cadenas = generar_cadenas_crudas(n)
    clases = defaultdict(list)

    for cadena in cadenas:
        matriz = chain2nparray(cadena)
        clave = canonical_key_std(matriz, optionx)
        clases[clave].append(cadena)

    return dict(clases)


def procesar_clase(padre, redundantes, optionx=OPTIONX):
    """
    Para una clase, calcula para cada redundante sus hijos.

    Devuelve una lista de tuplas:
      (redundante, [(hijo, extension, direccion), ...])
    """
    resultados = []
    for red in redundantes:
        hijos = []
        for ext_matriz, direccion, monocapa in generar_extensiones(red, optionx):
            hijo = canonical_key_std(ext_matriz, optionx)
            m_idx = next(i for i, f in enumerate(filas_opcion_1())
                         if np.array_equal(f, monocapa))
            hijos.append((hijo, m_idx, direccion))
        resultados.append((red, hijos))
    return resultados


# ─────────────────────────────────────────────
# Guardado
# ─────────────────────────────────────────────

def guardar_clases_tsv(n, clases, archivo):
    """
    Guarda un TSV con:
      padre_canonico  redundante  hijo  monocapa  direccion
    """
    with open(archivo, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['padre_canonico', 'redundante',
                         'hijo', 'monocapa', 'direccion'])

        for padre, redundantes in clases.items():
            resultados = procesar_clase(padre, redundantes)
            for red, hijos in resultados:
                for hijo, m_idx, direccion in hijos:
                    writer.writerow([padre, red, hijo, m_idx, direccion])


def escribir_resumen(n, clases, archivo):
    """
    Escribe un resumen legible:
      - Número de clases.
      - Para cada clase: tamaño de la clase (redundantes),
        hijos únicos, y si todos los redundantes producen los mismos hijos.
    """
    with open(archivo, 'w') as f:
        sep = "=" * 80
        sub = "-" * 80

        f.write(f"{sep}\n")
        f.write(f"RESUMEN: RELACIÓN REDUNDANTES → CANÓNICOS (n={n})\n")
        f.write(f"{sep}\n\n")

        f.write(f"Clases de {n} capas: {len(clases)}\n\n")

        # Clasificar cada clase
        for i, (padre, redundantes) in enumerate(sorted(clases.items()), 1):
            resultados = procesar_clase(padre, redundantes)

            # Conjunto de hijos por redundante
            hijos_por_red = {}
            for red, hijos in resultados:
                hijos_por_red[red] = frozenset(h for h, _, _ in hijos)

            # ¿Todos los redundantes producen los mismos hijos?
            conjuntos = list(hijos_por_red.values())
            todos_iguales = all(c == conjuntos[0] for c in conjuntos)

            # Hijos únicos de toda la clase
            hijos_todos = set()
            for c in conjuntos:
                hijos_todos |= c

            f.write(f"{sub}\n")
            f.write(f"CLASE {i}: {padre}\n")
            f.write(f"{sub}\n")
            f.write(f"  Redundantes: {len(redundantes)}\n")
            f.write(f"  Hijos únicos de la clase: {len(hijos_todos)}\n")
            f.write(f"  ¿Todos los redundantes producen los mismos hijos? "
                    f"{'SÍ' if todos_iguales else 'NO'}\n")

            if todos_iguales:
                f.write(f"  → La clase determina los hijos. "
                        f"La preclave puede ser la clase.\n\n")
            else:
                f.write(f"  → Los redundantes producen hijos distintos. "
                        f"La clase NO determina los hijos.\n\n")
                f.write("  Desglose por redundante:\n\n")

                # Agrupar redundantes por el conjunto de hijos que producen
                grupos = defaultdict(list)
                for red, hijos in resultados:
                    grupos[frozenset(h for h, _, _ in hijos)].append(red)

                for j, (hijos, reds) in enumerate(grupos.items(), 1):
                    f.write(f"    Grupo {j} ({len(reds)} redundantes, "
                            f"{len(hijos)} hijos):\n")
                    for red in reds:
                        f.write(f"      - {red}\n")
                    f.write(f"      Hijos:\n")
                    for h in sorted(hijos):
                        f.write(f"        {h}\n")
                    f.write("\n")

        f.write(f"{sep}\n")


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

if __name__ == "__main__":
    base = os.path.join(_CANONJAM_DIR, 'datos', 'redundantes')
    os.makedirs(base, exist_ok=True)

    for n in NIVELES:
        print(f"Procesando n={n}...")
        t0 = perf_counter()

        dir_n = os.path.join(base, f'n{n}')
        os.makedirs(dir_n, exist_ok=True)

        clases = construir_relacion(n)
        print(f"  Clases: {len(clases)}, "
              f"redundantes totales: {sum(len(r) for r in clases.values())}")

        # TSV completo
        archivo_tsv = os.path.join(dir_n, 'clases.tsv')
        guardar_clases_tsv(n, clases, archivo_tsv)

        # Resumen
        archivo_res = os.path.join(dir_n, 'resumen.txt')
        escribir_resumen(n, clases, archivo_res)

        t1 = perf_counter()
        print(f"  Guardado en {dir_n}/ ({t1-t0:.2f}s)\n")

    print("Listo.")
