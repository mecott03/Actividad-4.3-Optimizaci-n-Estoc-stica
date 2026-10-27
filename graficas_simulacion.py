"""Exportación PNG de los resultados calculados, sin generar datos nuevos."""
import os
import tempfile
from pathlib import Path


def guardar_grafica(resultado, archivo):
    # Un ejecutable onefile se extrae a una ubicación temporal: nunca escribir ahí.
    os.environ.setdefault('MPLCONFIGDIR', str(Path(tempfile.gettempdir()) / 'caminata-matplotlib'))
    import matplotlib
    matplotlib.use('Agg')
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    import numpy as np
    fig = Figure(figsize=(9, 5), layout='constrained')
    FigureCanvasAgg(fig)
    ax = fig.subplots()
    ax.hist(resultado.maximas, bins=min(30, max(1, int(np.sqrt(resultado.repeticiones)))), edgecolor='white', label='Caminatas')
    ax.axvline(resultado.promedio, color='red', linestyle='--', label=f'Promedio: {resultado.promedio:.4f}')
    ax.set(title=f'Caminata {resultado.dimension}D · {resultado.pasos:,} pasos · {resultado.repeticiones:,} repeticiones · semilla {resultado.semilla}', xlabel='Distancia máxima al origen (unidades)', ylabel='Número de caminatas')
    ax.legend(); ax.grid(axis='y', alpha=.25)
    destino = Path(archivo).expanduser().resolve()
    destino.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destino, format='png', dpi=160)
    return destino
