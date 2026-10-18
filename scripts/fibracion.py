#!/usr/bin/env python3
"""
fibracion.py

Genera datos crudos y análisis de la fibración para opción 1
(monoelemental planar, sin buckling).

Estructura de salida:
    datos/nX/cadenas.txt
    datos/nX/canonicas.txt
    datos/fibracion/fib_nX_nY.tsv          (crudo, TSV)
    datos/fibracion/fib_nX_nY_detalle.txt  (legible, para humanos)
    datos/fibracion/resumen.txt            (análisis global)
"""

import numpy as np
import sys
import os
from itertools import permutations
from time import perf_counter
from collections import Counter

# ─────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_CANONJAM_DIR = os.path.dirname(_SCRIPT_DIR)
_XJAM2_DIR = os.path.join(os.path.dirname(_CANONJAM_DIR), 'xjam2')
_PRUEBAS_DIR = os.path.join(_XJAM2_DIR, 'pruebas')

sys.path.insert(0, _XJAM2_DIR)
sys.path.insert(0, _PRUEBAS_DIR)

from xjam.libjamstd import conv2pseudocanonic, nparray2chain, chain2nparray
from prueba_grupo import (
    canonical_key_std,
    disc_equivalents_canonical_std,
)


# ─────────────────────────────────────────────
# Configuración
# ─────────────────────────────────────────────

OPTIONX = 1
N_MAX_CADENAS = 8
N_MAX_CANONICAS = 8
N_MAX_FIBRACION = 8


# ─────────────────────────────────────────────
# Monocapas
# ─────────────────────────────────────────────

def filas_opcion_1():
    opt = ['+0', '+j', '+j']
    filas = list(set(permutations(opt, 3)))
    return [np.array(i) for i in filas]


# ─────────────────────────────────────────────
# Generación
# ─────────────────────────────────────────────

def generar_cadenas_crudas(n):
    filas = filas_opcion_1()
    candidatos = [np.array(f).reshape(1, -1) for f in filas]

    for _ in range(2, n + 1):
        nuevos = []
        for c in candidatos:
            for f in filas:
                nuevos.append(np.vstack([c, f]))
        candidatos = nuevos

    return [nparray2chain(c) for c in candidatos]


def generar_canonicas(n, optionx=OPTIONX):
    cadenas = generar_cadenas_crudas(n)
    matrices = [chain2nparray(c) for c in cadenas]
    unicas = disc_equivalents_canonical_std(matrices, optionx)
    claves = sorted(set(canonical_key_std(u, optionx) for u in unicas))
    return claves


def generar_extensiones(clave, optionx=OPTIONX):
    matriz = chain2nparray(clave)
    filas = filas_opcion_1()
    extensiones = []
    for f in filas:
        extensiones.append(np.vstack([matriz, f]))
        extensiones.append(np.vstack([f, matriz]))
    return extensiones


def construir_fibracion(n, optionx=OPTIONX):
    canonicas_n = generar_canonicas(n, optionx)
    fibracion = {}

    for padre in canonicas_n:
        hijos = set()
        for ext in generar_extensiones(padre, optionx):
            hijo = canonical_key_std(ext, optionx)
            hijos.add(hijo)
        fibracion[padre] = sorted(hijos)

    return fibracion


# ─────────────────────────────────────────────
# Guardado crudo
# ─────────────────────────────────────────────

def guardar_lineas(lineas, archivo):
    with open(archivo, 'w') as f:
        for linea in lineas:
            f.write(linea + '\n')


def guardar_fibracion_tsv(fibracion, archivo):
    with open(archivo, 'w') as f:
        f.write("padre\thijo\n")
        for padre, hijos in fibracion.items():
            for hijo in hijos:
                f.write(f"{padre}\t{hijo}\n")


# ─────────────────────────────────────────────
# Detalle legible por transición
# ─────────────────────────────────────────────

def escribir_detalle(fibracion, n, archivo):
    n_padres = len(fibracion)
    hijos_todos = []
    for hijos in fibracion.values():
        hijos_todos.extend(hijos)
    hijos_unicos = set(hijos_todos)
    n_conexiones = len(hijos_todos)

    tamaños = {padre: len(hijos) for padre, hijos in fibracion.items()}
    dist = Counter(tamaños.values())
    prom = sum(tamaños.values()) / len(tamaños) if tamaños else 0
    maximo = max(tamaños.values()) if tamaños else 0

    # Convergencias: hijos que aparecen en 2+ padres
    hijos_por_padre = {}
    for padre, hijos in fibracion.items():
        for h in hijos:
            hijos_por_padre.setdefault(h, []).append(padre)
    convergencias = {h: ps for h, ps in hijos_por_padre.items() if len(ps) > 1}

    with open(archivo, 'w') as f:
        sep = "=" * 80
        sub = "-" * 80

        f.write(f"{sep}\n")
        f.write(f"FIBRACIÓN DE n={n} A n={n+1}\n")
        f.write(f"{sep}\n\n")

        f.write("¿Qué muestra esta tabla?\n")
        f.write("  Cada estructura de {} capas se forma añadiendo una\n".format(n+1))
        f.write("  monocapa a una estructura de {} capas. Esta tabla lista,\n".format(n))
        f.write("  para cada estructura de {} capas (el 'padre'), todas las\n".format(n))
        f.write("  estructuras de {} capas (los 'hijos') que se pueden formar\n".format(n+1))
        f.write("  a partir de ella.\n\n")
        f.write("  La 'fibra' de un padre es el conjunto de sus hijos.\n")
        f.write("  Si un padre tiene fibra grande, sus extensiones producen\n")
        f.write("  muchas clases distintas. Si tiene fibra pequeña, muchas\n")
        f.write("  extensiones producen la misma clase (hay convergencia).\n\n")

        f.write(f"{sub}\n")
        f.write("Estadísticas de esta transición\n")
        f.write(f"{sub}\n\n")
        f.write(f"  Padres (clases de n={n}):           {n_padres}\n")
        f.write(f"  Hijos únicos (clases de n={n+1}):   {len(hijos_unicos)}\n")
        f.write(f"  Conexiones padre-hijo:               {n_conexiones}\n")
        f.write(f"  Tamaño promedio de fibra:            {prom:.2f}\n")
        f.write(f"  Tamaño máximo de fibra:              {maximo}\n")
        dist_str = ", ".join(f"{k}→{v}" for k, v in sorted(dist.items()))
        f.write(f"  Distribución de tamaños de fibra:    {dist_str}\n\n")

        # Padres e hijos
        for i, (padre, hijos) in enumerate(fibracion.items(), 1):
            f.write(f"{sub}\n")
            f.write(f"PADRE {i} [fibra de tamaño {len(hijos)}]\n")
            f.write(f"  Clave: {padre}\n")
            f.write("  Hijos:\n")
            for j, hijo in enumerate(hijos, 1):
                marca = " ←" if hijo in convergencias else ""
                f.write(f"    [{j}] {hijo}{marca}\n")
            f.write("\n")

        # Convergencias
        f.write(f"{sub}\n")
        f.write("CONVERGENCIAS\n")
        f.write(f"{sub}\n\n")
        if not convergencias:
            f.write("  Ninguna en esta transición.\n")
            f.write("  (Cada hijo aparece en exactamente un padre.)\n\n")
        else:
            f.write(f"  Hijos que aparecen en más de un padre ({len(convergencias)}):\n\n")
            for hijo, padres in convergencias.items():
                f.write(f"  Hijo: {hijo}\n")
                f.write(f"    Aparece en {len(padres)} padres:\n")
                for p in padres:
                    f.write(f"      - {p}\n")
                f.write("\n")

        f.write(f"{sep}\n")


# ─────────────────────────────────────────────
# Resumen global
# ─────────────────────────────────────────────
def escribir_resumen(archivo, info_canonicas, info_fibracion):
            with open(archivo, 'w') as f:
                sep = "=" * 80
                sub = "-" * 80
        
                f.write(f"{sep}\n")
                f.write("RESUMEN DE LA RELACIÓN ENTRE NIVELES CONSECUTIVOS\n")
                f.write(f"{sep}\n\n")
        
                # ─────────────────────────────────────
                # 1. Qué contiene este archivo
                # ─────────────────────────────────────
                f.write(f"{sub}\n")
                f.write("1. QUÉ CONTIENE ESTE ARCHIVO\n")
                f.write(f"{sub}\n\n")
                f.write("Este archivo documenta la relación entre clases canónicas\n")
                f.write("de n capas y clases canónicas de n+1 capas, para la opción 1\n")
                f.write("de JAM (monocapas monoelementales, planares, sin buckling).\n\n")
                f.write("Contiene tres bloques:\n\n")
                f.write("  A. Crecimiento de las clases canónicas por nivel.\n")
                f.write("  B. Relación entre clases de n capas y clases de n+1 capas.\n")
                f.write("  C. Listado de archivos generados.\n\n")
        
                # ─────────────────────────────────────
                # 2. Definición de la relación
                # ─────────────────────────────────────
                f.write(f"{sub}\n")
                f.write("2. DEFINICIÓN DE LA RELACIÓN\n")
                f.write(f"{sub}\n\n")
        
                f.write("Relación entre niveles:\n\n")
                f.write("  - Para cada clase de n capas (llamada 'padre'), se\n")
                f.write("    generan sus extensiones: añadir una monocapa al\n")
                f.write("    principio o al final.\n")
                f.write("  - Cada extensión se reduce a su clave canónica. Las\n")
                f.write("    claves resultantes son los 'hijos' del padre.\n")
                f.write("  - El conjunto de hijos de un padre es su 'fibra'.\n")
                f.write("  - El máximo de hijos por padre es 6: 2 direcciones de\n")
                f.write("    apilado (arriba/abajo) × 3 monocapas posibles.\n\n")
        
                # ─────────────────────────────────────
                # 3. Crecimiento de clases canónicas
                # ─────────────────────────────────────
                f.write(f"{sub}\n")
                f.write("3. CRECIMIENTO DE LAS CLASES CANÓNICAS\n")
                f.write(f"{sub}\n\n")
                f.write("Tabla por nivel n:\n\n")
                f.write("  - Estructuras:  número total de estructuras generadas\n")
                f.write("                  (con duplicados).\n")
                f.write("  - Clases:       número de clases de equivalencia\n")
                f.write("                  (claves canónicas únicas).\n")
                f.write("  - Crecimiento:  clases(n) / clases(n-1).\n\n")
        
                f.write(f"  {'n':>3}  {'Estructuras':>14}  {'Clases':>10}  {'Crecimiento':>12}\n")
                f.write(f"  {'-'*3}  {'-'*14}  {'-'*10}  {'-'*12}\n")
        
                prev = None
                for n, n_cad, n_can in info_canonicas:
                    cad_str = str(n_cad) if n_cad is not None else "—"
                    if prev is None or prev == 0:
                        ratio_str = "—"
                    else:
                        ratio_str = f"{n_can / prev:.4f}"
                    f.write(f"  {n:>3}  {cad_str:>14}  {n_can:>10}  {ratio_str:>12}\n")
                    prev = n_can
        
                f.write("\n")
                f.write("  El número de estructuras generadas crece como 3^n.\n")
                f.write("  El número de clases crece aproximadamente como 2.8^n.\n")
                f.write("  La diferencia entre ambos números es lo que la\n")
                f.write("  canonicalización elimina.\n\n")
        
                # ─────────────────────────────────────
                # 4. Relación entre niveles consecutivos
                # ─────────────────────────────────────
                f.write(f"{sub}\n")
                f.write("4. RELACIÓN ENTRE NIVELES CONSECUTIVOS\n")
                f.write(f"{sub}\n\n")
                f.write("Para cada transición n → n+1:\n\n")
                f.write("  - Padres:      clases canónicas en n.\n")
                f.write("  - Hijos:       clases canónicas distintas en n+1\n")
                f.write("                 alcanzables desde algún padre.\n")
                f.write("  - Conexiones:  número total de pares (padre, hijo).\n")
                f.write("  - Promedio:    conexiones / padres. Es el tamaño\n")
                f.write("                 promedio de la fibra.\n")
                f.write("  - Máx:         tamaño máximo de fibra observado.\n\n")
        
                f.write(f"  {'Transición':>12}  {'Padres':>8}  {'Hijos':>8}  "
                        f"{'Conex.':>8}  {'Prom.':>8}  {'Máx.':>6}\n")
                f.write(f"  {'-'*12}  {'-'*8}  {'-'*8}  {'-'*8}  {'-'*8}  {'-'*6}\n")
        
                for n, n_padres, n_hijos, n_cone, prom, maximo in info_fibracion:
                    f.write(f"  {f'{n} → {n+1}':>12}  {n_padres:>8}  {n_hijos:>8}  "
                            f"{n_cone:>8}  {prom:>8.4f}  {maximo:>6}\n")
        
                f.write("\n")
                f.write("  El número promedio de conexiones por padre crece con n,\n")
                f.write("  acercándose a 6.\n\n")
        
                # ─────────────────────────────────────
                # 5. Ratios de la relación
                # ─────────────────────────────────────
                f.write(f"{sub}\n")
                f.write("5. RATIOS DE LA RELACIÓN\n")
                f.write(f"{sub}\n\n")
                f.write("Para cada transición:\n\n")
                f.write("  - hijos / padres:      cuántas clases nuevas de n+1 se\n")
                f.write("                         alcanzan, por cada clase de n.\n")
                f.write("  - conexiones / padres: tamaño promedio de fibra.\n")
                f.write("  - conexiones / hijos:  cuántos padres contribuyen en\n")
                f.write("                         promedio a cada hijo.\n\n")
        
                f.write(f"  {'Transición':>12}  {'Hijos/Padres':>14}  "
                        f"{'Conex/Padres':>14}  {'Conex/Hijos':>14}\n")
                f.write(f"  {'-'*12}  {'-'*14}  {'-'*14}  {'-'*14}\n")
        
                for n, n_padres, n_hijos, n_cone, prom, maximo in info_fibracion:
                    r_hp = n_hijos / n_padres if n_padres else 0
                    r_cp = n_cone / n_padres if n_padres else 0
                    r_ch = n_cone / n_hijos if n_hijos else 0
                    f.write(f"  {f'{n} → {n+1}':>12}  {r_hp:>14.4f}  "
                            f"{r_cp:>14.4f}  {r_ch:>14.4f}\n")
        
                f.write("\n")
        
                # ─────────────────────────────────────
                # 6. Archivos generados
                # ─────────────────────────────────────
                f.write(f"{sub}\n")
                f.write("6. ARCHIVOS GENERADOS\n")
                f.write(f"{sub}\n\n")
                f.write("Los datos crudos se encuentran en la carpeta datos/.\n\n")
        
                f.write("Por cada nivel n:\n\n")
                f.write("  datos/nX/cadenas.txt\n")
                f.write("    Estructuras generadas, una por línea, en formato\n")
                f.write("    cadena JAM. Incluye duplicados.\n\n")
                f.write("  datos/nX/canonicas.txt\n")
                f.write("    Claves canónicas únicas, una por línea.\n")
                f.write("    Cada línea representa una clase de equivalencia.\n\n")
        
                f.write("Por cada transición n → n+1:\n\n")
                f.write("  datos/fibracion/fib_nX_nY.tsv\n")
                f.write("    Relaciones padre-hijo en formato TSV.\n")
                f.write("    Columnas: padre, hijo.\n\n")
                f.write("  datos/fibracion/fib_nX_nY_detalle.txt\n")
                f.write("    Versión legible de la relación. Incluye estadísticas\n")
                f.write("    de la transición, listado de padres con sus hijos, y\n")
                f.write("    listado de hijos que aparecen en más de un padre.\n\n")
                f.write("  datos/fibracion/resumen.txt\n")
                f.write("    Este archivo.\n\n")
        
                f.write(f"{sep}\n")

# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

if __name__ == "__main__":
    base = os.path.join(_CANONJAM_DIR, 'datos')
    os.makedirs(base, exist_ok=True)
    os.makedirs(os.path.join(base, 'fibracion'), exist_ok=True)

    print(f"Opción {OPTIONX}: monocapas monoelementales, planares")
    print()

    # 1. Canónicas y cadenas
    info_canonicas = []
    for n in range(1, N_MAX_CANONICAS + 1):
        dir_n = os.path.join(base, f'n{n}')
        os.makedirs(dir_n, exist_ok=True)

        t0 = perf_counter()

        if n <= N_MAX_CADENAS:
            cadenas = generar_cadenas_crudas(n)
            guardar_lineas(cadenas, os.path.join(dir_n, 'cadenas.txt'))
            n_cadenas = len(cadenas)
        else:
            n_cadenas = None

        canonicas = generar_canonicas(n)
        guardar_lineas(canonicas, os.path.join(dir_n, 'canonicas.txt'))

        t1 = perf_counter()
        info_canonicas.append((n, n_cadenas, len(canonicas)))

        cad_str = f"{n_cadenas:>7}" if n_cadenas is not None else f"{'—':>7}"
        print(f"  n={n}: {cad_str} cadenas, {len(canonicas):>5} canónicas "
              f"({t1-t0:.2f}s)")

    print()

    # 2. Fibración
    info_fibracion = []
    for n in range(1, N_MAX_FIBRACION):
        t0 = perf_counter()
        fibracion = construir_fibracion(n)

        # TSV crudo
        archivo_tsv = os.path.join(base, 'fibracion', f'fib_n{n}_n{n+1}.tsv')
        guardar_fibracion_tsv(fibracion, archivo_tsv)

        # Detalle legible
        archivo_det = os.path.join(base, 'fibracion', f'fib_n{n}_n{n+1}_detalle.txt')
        escribir_detalle(fibracion, n, archivo_det)

        # Estadísticas
        n_padres = len(fibracion)
        hijos_todos = []
        for hijos in fibracion.values():
            hijos_todos.extend(hijos)
        n_hijos = len(set(hijos_todos))
        n_conex = len(hijos_todos)
        prom = n_conex / n_padres if n_padres else 0
        maximo = max((len(h) for h in fibracion.values()), default=0)

        t1 = perf_counter()
        info_fibracion.append((n, n_padres, n_hijos, n_conex, prom, maximo))

        print(f"  Fib n={n}→{n+1}: {n_padres:>4} padres, "
              f"{n_hijos:>4} hijos únicos, {n_conex:>5} conexiones "
              f"(prom {prom:.2f}, máx {maximo}) ({t1-t0:.2f}s)")

    print()

    # 3. Resumen global
    resumen_path = os.path.join(base, 'fibracion', 'resumen.txt')
    escribir_resumen(resumen_path, info_canonicas, info_fibracion)
    print(f"Resumen guardado en: {resumen_path}")
    print("Listo.")
