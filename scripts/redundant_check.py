#!/usr/bin/env python3
"""
redundantes_v2.py

Adaptation of redundantes.py for all 8 JAM options.
"""

import argparse
import numpy as np
import os
import csv
from collections import defaultdict
from time import perf_counter

from canonjam import canonical_key, array_to_chain
from caugjam import generate_raw, rows_for_option

OPTIONS = [1, 2, 3, 4, 5, 6, 7, 8]


def niveles_para(option):
    n_rows = len(rows_for_option(option))
    if n_rows == 3:
        return list(range(2, 11))
    elif n_rows == 6:
        return list(range(2, 8))
    else:
        return list(range(2, 6))


def canon_key_str(matriz, option):
    key = canonical_key(matriz, optionx=option)
    if isinstance(key, str):
        return key
    if isinstance(key, np.ndarray):
        return array_to_chain(key)
    return str(key)


def filas_opcion(option):
    filas = rows_for_option(option)
    return sorted(filas, key=lambda f: tuple(np.asarray(f).flatten()))


def generar_extensiones(matriz, option):
    filas = filas_opcion(option)
    matriz = np.asarray(matriz)
    extensiones = []
    for i, f in enumerate(filas):
        f = np.asarray(f)
        extensiones.append((np.vstack([f.reshape(1, -1), matriz]), 'prepend', i))
        extensiones.append((np.vstack([matriz, f.reshape(1, -1)]), 'append', i))
    return extensiones


def construir_relacion(n, option):
    cadenas = generate_raw(n, option)
    clases = defaultdict(list)
    for matriz in cadenas:
        clave = canon_key_str(matriz, option)
        clases[clave].append(matriz)
    return dict(clases)


def procesar_clase(redundantes, option):
    resultados = []
    for red_matriz in redundantes:
        hijos = []
        for ext_matriz, direccion, m_idx in generar_extensiones(red_matriz, option):
            hijo = canon_key_str(ext_matriz, option)
            hijos.append((hijo, m_idx, direccion))
        resultados.append((red_matriz, hijos))
    return resultados


def escribir_resumen(n, option, clases, archivo):
    all_yes = True
    n_no = 0
    with open(archivo, 'w') as f:
        sep = "=" * 80
        sub = "-" * 80
        f.write(f"{sep}\n")
        f.write(f"RESUMEN: REDUNDANTES → CANÓNICOS (option={option}, n={n})\n")
        f.write(f"{sep}\n\n")
        f.write(f"Clases de {n} capas: {len(clases)}\n\n")

        for i, (padre, redundantes) in enumerate(sorted(clases.items()), 1):
            resultados = procesar_clase(redundantes, option)
            hijos_por_red = {}
            for red_matriz, hijos in resultados:
                red_str = array_to_chain(red_matriz)
                hijos_por_red[red_str] = frozenset(h for h, _, _ in hijos)

            conjuntos = list(hijos_por_red.values())
            todos_iguales = all(c == conjuntos[0] for c in conjuntos)
            if not todos_iguales:
                all_yes = False
                n_no += 1

            hijos_todos = set()
            for c in conjuntos:
                hijos_todos |= c

            f.write(f"{sub}\n")
            f.write(f"CLASE {i}: {padre}\n")
            f.write(f"{sub}\n")
            f.write(f"  Redundantes: {len(redundantes)}\n")
            f.write(f"  Hijos únicos de la clase: {len(hijos_todos)}\n")
            f.write(f"  ¿Todos los redundantes producen los mismos hijos? "
                    f"{'SÍ' if todos_iguales else 'NO'}\n\n")

        f.write(f"{sep}\n")
        f.write(f"RESUMEN GLOBAL: "
                f"{'TODAS SÍ' if all_yes else f'{n_no} clases NO'}\n")
        f.write(f"{sep}\n")
    return all_yes, len(clases), n_no


def guardar_clases_tsv(n, option, clases, archivo):
    with open(archivo, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['option', 'n', 'padre_canonico', 'redundante',
                         'hijo', 'monocapa', 'direccion'])
        for padre, redundantes in clases.items():
            resultados = procesar_clase(redundantes, option)
            for red_matriz, hijos in resultados:
                red_str = array_to_chain(red_matriz)
                for hijo, m_idx, direccion in hijos:
                    writer.writerow([option, n, padre, red_str,
                                     hijo, m_idx, direccion])


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--options', type=int, nargs='+', default=OPTIONS)
    parser.add_argument('--no-tsv', action='store_true')
    parser.add_argument('--max-classes-for-tsv', type=int, default=5000)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    base = os.path.join("datos", "redundantes_v2")
    os.makedirs(base, exist_ok=True)

    global_summary = {}

    for option in args.options:
        n_rows = len(rows_for_option(option))
        print(f"\n=== Option {option} (q={n_rows}) ===")
        for n in niveles_para(option):
            t0 = perf_counter()
            print(f"  n={n}...", end=" ", flush=True)
            dir_n = os.path.join(base, f"opt{option}", f"n{n}")
            os.makedirs(dir_n, exist_ok=True)
            try:
                clases = construir_relacion(n, option)
                archivo_res = os.path.join(dir_n, 'resumen.txt')
                all_yes, n_classes, n_no = escribir_resumen(
                    n, option, clases, archivo_res)

                if not args.no_tsv and n_classes <= args.max_classes_for_tsv:
                    archivo_tsv = os.path.join(dir_n, 'clases.tsv')
                    guardar_clases_tsv(n, option, clases, archivo_tsv)

                t1 = perf_counter()
                status = "SÍ" if all_yes else f"NO ({n_no})"
                print(f"{n_classes} clases, {status} ({t1-t0:.2f}s)")
                global_summary[(option, n)] = (all_yes, n_classes, n_no)
            except Exception as e:
                print(f"ERROR: {type(e).__name__}: {e}")
                global_summary[(option, n)] = (None, 0, 0)

    print("\n" + "=" * 80)
    print("GLOBAL SUMMARY")
    print("=" * 80)
    if not global_summary:
        print("(no results)")
    else:
        max_n = max(n for (_, n) in global_summary.keys())
        header = "option  q  " + "  ".join(f"n={n}" for n in range(2, max_n + 1))
        print(header)
        print("-" * len(header))
        for option in args.options:
            q = len(rows_for_option(option))
            row = f"  {option:>3}  {q:>2}  "
            for n in range(2, max_n + 1):
                entry = global_summary.get((option, n))
                if entry is None:
                    row += "  -  "
                elif entry[0] is None:
                    row += "  E  "
                elif entry[0]:
                    row += "  S  "
                else:
                    row += f" {entry[2]:>2}N "
            print(row)
    print()
    print("S = todas SÍ, N = clases NO (con número), - = no testeado, E = error")
    print("\nListo.")
