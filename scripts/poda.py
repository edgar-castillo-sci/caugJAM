#!/usr/bin/env python3

#!/usr/bin/env python3
"""
poda.py

Implementa la poda: genera las clases canónicas de n capas
extendiendo únicamente los representantes canónicos de n-1 capas,
en lugar de generar todos los candidatos crudos y filtrar.

Compara el resultado con el método actual (generación completa +
canonicalización) para verificar que producen las mismas clases.

También mide el tiempo de ambos métodos para cuantificar el speedup.
"""

import numpy as np
import sys
import os
import csv
from itertools import permutations
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
from prueba_grupo import (
    canonical_key_std,
    disc_equivalents_canonical_std,
)


# ─────────────────────────────────────────────
# Configuración
# ─────────────────────────────────────────────

OPTIONX = 1
N_MAX = 9


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
# Método actual: generar todo y filtrar
# ─────────────────────────────────────────────

def generar_canonicas_actual(n, optionx=OPTIONX):
    """Método actual: genera todos los candidatos y filtra."""
    cadenas = generar_cadenas_crudas(n)
    matrices = [chain2nparray(c) for c in cadenas]
    unicas = disc_equivalents_canonical_std(matrices, optionx)
    claves = sorted(set(canonical_key_std(u, optionx) for u in unicas))
    return claves


# ─────────────────────────────────────────────
# Método de poda: solo extiende los canónicos
# ─────────────────────────────────────────────

def generar_extensiones(clave, optionx=OPTIONX):
    """Genera las 6 extensiones de una estructura."""
    matriz = chain2nparray(clave)
    filas = filas_opcion_1()
    extensiones = []
    for f in filas:
        extensiones.append(np.vstack([f, matriz]))
        extensiones.append(np.vstack([matriz, f]))
    return extensiones


def generar_canonicas_poda(n_max, optionx=OPTIONX):
    """
    Método de poda: genera las clases de n capas extendiendo
    únicamente los representantes canónicos de n-1 capas.

    Devuelve un diccionario {n: [claves_canonicas]}.
    """
    clases = {}
    clases[1] = sorted(set(
        canonical_key_std(np.array(f).reshape(1, -1), optionx)
        for f in filas_opcion_1()
    ))

    for n in range(2, n_max + 1):
        hijos = set()
        for padre in clases[n-1]:
            for ext in generar_extensiones(padre, optionx):
                hijo = canonical_key_std(ext, optionx)
                hijos.add(hijo)
        clases[n] = sorted(hijos)

    return clases


# ─────────────────────────────────────────────
# Verificación
# ─────────────────────────────────────────────

def comparar_poda_vs_actual(n_max, optionx=OPTIONX):
    """Compara las clases generadas por poda vs el método actual."""
    print(f"\n{'='*80}")
    print(f"VERIFICACIÓN: poda vs método actual (opción {optionx})")
    print(f"{'='*80}\n")

    # Generar con poda (tiempo)
    t0 = perf_counter()
    clases_poda = generar_canonicas_poda(n_max, optionx)
    t_poda_total = perf_counter() - t0

    print(f"Poda generada en {t_poda_total:.3f}s\n")

    # Comparar nivel por nivel
    print(f"{'n':>3}  {'Poda':>8}  {'Actual':>8}  {'¿Iguales?':>10}  {'t_actual':>10}")
    print(f"{'-'*3}  {'-'*8}  {'-'*8}  {'-'*10}  {'-'*10}")

    todos_ok = True
    for n in range(1, n_max + 1):
        t0 = perf_counter()
        clases_actual = generar_canonicas_actual(n, optionx)
        t_actual = perf_counter() - t0

        set_poda = set(clases_poda[n])
        set_actual = set(clases_actual)

        iguales = set_poda == set_actual
        marca = "✓" if iguales else "✗"

        print(f"{n:>3}  {len(set_poda):>8}  {len(set_actual):>8}  "
              f"{marca:>10}  {t_actual:>10.3f}")

        if not iguales:
            todos_ok = False
            solo_poda = set_poda - set_actual
            solo_actual = set_actual - set_poda
            if solo_poda:
                print(f"    Solo en poda: {len(solo_poda)}")
                for c in list(solo_poda)[:3]:
                    print(f"      {c}")
            if solo_actual:
                print(f"    Solo en actual: {len(solo_actual)}")
                for c in list(solo_actual)[:3]:
                    print(f"      {c}")

    print()
    if todos_ok:
        print("✓ La poda produce exactamente las mismas clases "
              "que el método actual.")
    else:
        print("✗ La poda NO produce las mismas clases. "
              "Revisar los niveles marcados.")

    return todos_ok, clases_poda


# ─────────────────────────────────────────────
# Speedup
# ─────────────────────────────────────────────

def medir_speedup(n_max, optionx=OPTIONX):
    """
    Mide el tiempo de cada método para cada n, y calcula el speedup.
    """
    print(f"\n{'='*80}")
    print(f"SPEEDUP: poda vs método actual (opción {optionx})")
    print(f"{'='*80}\n")

    print(f"{'n':>3}  {'t_actual':>12}  {'t_poda':>12}  "
          f"{'Speedup':>10}  {'Cand. actual':>14}  {'Cand. poda':>12}")
    print(f"{'-'*3}  {'-'*12}  {'-'*12}  {'-'*10}  {'-'*14}  {'-'*12}")

    resultados = []
    for n in range(1, n_max + 1):
        # Tiempo actual
        t0 = perf_counter()
        clases_actual = generar_canonicas_actual(n, optionx)
        t_actual = perf_counter() - t0

        # Tiempo poda (acumulado hasta n)
        t0 = perf_counter()
        clases_poda = generar_canonicas_poda(n, optionx)
        t_poda = perf_counter() - t0

        # Número de candidatos
        cand_actual = 3 ** n
        cand_poda = len(clases_poda[n-1]) * 6 if n > 1 else 3

        speedup = t_actual / t_poda if t_poda > 0 else float('inf')

        print(f"{n:>3}  {t_actual:>12.4f}  {t_poda:>12.4f}  "
              f"{speedup:>9.2f}x  {cand_actual:>14}  {cand_poda:>12}")

        resultados.append({
            'n': n,
            't_actual': t_actual,
            't_poda': t_poda,
            'speedup': speedup,
            'cand_actual': cand_actual,
            'cand_poda': cand_poda,
        })

    print()
    return resultados


# ─────────────────────────────────────────────
# Guardar resultados
# ─────────────────────────────────────────────

def guardar_verificacion(archivo, todos_ok, clases_poda):
    with open(archivo, 'w') as f:
        f.write("VERIFICACIÓN DE LA PODA\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Opción: {OPTIONX}\n")
        f.write(f"Resultado: {'ÉXITO' if todos_ok else 'FALLO'}\n\n")
        f.write("Clases por nivel:\n\n")
        for n in sorted(clases_poda.keys()):
            f.write(f"n={n}: {len(clases_poda[n])} clases\n")


def guardar_speedup(archivo, resultados):
    with open(archivo, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['n', 't_actual', 't_poda', 'speedup',
                         'cand_actual', 'cand_poda'])
        for r in resultados:
            writer.writerow([
                r['n'],
                f"{r['t_actual']:.4f}",
                f"{r['t_poda']:.4f}",
                f"{r['speedup']:.2f}",
                r['cand_actual'],
                r['cand_poda'],
            ])


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

if __name__ == "__main__":
    base = os.path.join(_CANONJAM_DIR, 'datos', 'poda')
    os.makedirs(base, exist_ok=True)

    # 1. Verificación
    todos_ok, clases_poda = comparar_poda_vs_actual(N_MAX)
    guardar_verificacion(os.path.join(base, 'verificacion.txt'),
                         todos_ok, clases_poda)

    # 2. Speedup (solo si la verificación pasó)
    if todos_ok:
        resultados = medir_speedup(N_MAX)
        guardar_speedup(os.path.join(base, 'speedup.tsv'), resultados)
        print(f"Resultados guardados en {base}/")
    else:
        print("Verificación falló. No se mide speedup.")

    print("\nListo.")
