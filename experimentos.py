"""Genera las 18 configuraciones, datos individuales y cinco gráficas."""
import argparse
import csv
import json
import platform
from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR', str(Path(__file__).resolve().parent / '.cache' / 'matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from simulacion import CABECERA, simular, trayectoria

BASE = Path(__file__).resolve().parent


def graficar(filas, carpeta, semilla):
    carpeta.mkdir(parents=True, exist_ok=True)
    for d in (1, 2):
        p = trayectoria(d, 1000, semilla)
        fig, ax = plt.subplots(figsize=(8, 5))
        if d == 1:
            ax.plot(np.arange(len(p)), p[:, 0], label='Posición')
            ax.set(xlabel='Paso', ylabel='Posición (unidades)')
        else:
            ax.plot(p[:, 0], p[:, 1], label='Trayectoria')
            ax.scatter([0], [0], label='Origen', color='green')
            ax.scatter(p[-1, 0], p[-1, 1], label='Final', color='red')
            ax.set(xlabel='x (unidades)', ylabel='y (unidades)', aspect='equal')
        ax.set_title(f'Caminata en {d}D: 1,000 pasos; semilla {semilla}')
        ax.legend(); ax.grid(alpha=.3)
        fig.tight_layout(); fig.savefig(carpeta / f'trayectoria_{d}d.png', dpi=160); plt.close(fig)
        np.savetxt(carpeta.parent / 'resultados' / f'trayectoria_{d}d.csv', np.column_stack((np.arange(len(p)), p)), delimiter=',', header='paso,' + ','.join(f'eje_{i+1}' for i in range(d)), comments='', fmt='%d')
    for nombre, xindice, fijo in [('promedio_por_pasos', 1, None), ('comparacion_dimensiones', 1, 10000), ('promedio_por_repeticiones', 2, None)]:
        fig, ax = plt.subplots(figsize=(9, 6))
        for d in (1, 2):
            grupos = [fijo] if fijo else [100, 1000, 10000]
            for grupo in grupos:
                datos = sorted([r for r in filas if r[0] == d and r[2 if xindice == 1 else 1] == grupo], key=lambda r:r[xindice])
                ax.plot([r[xindice] for r in datos], [r[4] for r in datos], marker='o', label=f'{d}D; {grupo:,} ' + ('repeticiones' if xindice == 1 else 'pasos'))
        ax.set(xscale='log', xlabel='Número de pasos' if xindice == 1 else 'Número de repeticiones', ylabel='Distancia máxima promedio (unidades)', title=nombre.replace('_', ' ').capitalize())
        ax.legend(fontsize=8); ax.grid(alpha=.3); fig.tight_layout()
        fig.savefig(carpeta / f'{nombre}.png', dpi=160); plt.close(fig)


def ejecutar(base=BASE, semilla=2026):
    base = Path(base)
    resultados = base / 'resultados'
    resultados.mkdir(parents=True, exist_ok=True)
    filas = []
    for d in (1, 2):
        for pasos in (100, 1000, 10000):
            for n in (100, 1000, 10000):
                r = simular(d, pasos, n, semilla)
                r.exportar(resultados / 'distancias_individuales' / f'{d}d_p{pasos}_n{n}.csv')
                filas.append(r.fila())
                print(f'{d}D pasos={pasos} n={n}: promedio={r.promedio:.6f}, {r.segundos:.3f}s', flush=True)
    with (resultados / 'resumen_experimentos.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, lineterminator='\n'); w.writerow(CABECERA); w.writerows(filas)
    (resultados / 'metadatos.json').write_text(json.dumps({'python':platform.python_version(), 'numpy':np.__version__, 'matplotlib':matplotlib.__version__, 'plataforma':platform.platform(), 'generador':'numpy.random.default_rng / PCG64', 'semilla':semilla, 'nota':'Misma semilla por configuración: repeticiones anidadas, no muestras independientes entre configuraciones. Tiempos medidos, variables según máquina.'}, indent=2, ensure_ascii=False), encoding='utf-8')
    graficar(filas, base / 'graficas', semilla)
    return filas


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--semilla', type=int, default=2026)
    parser.add_argument('--salida', type=Path, default=BASE)
    args = parser.parse_args()
    ejecutar(args.salida, args.semilla)
