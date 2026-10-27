"""Caminatas unitarias sobre Z^d; generador PCG64 de NumPy."""
from dataclasses import dataclass
from time import perf_counter
from pathlib import Path
import csv
import numpy as np


def entero(valor, nombre, minimo=1):
    if isinstance(valor, (bool, np.bool_)) or not isinstance(valor, (int, np.integer)) or valor < minimo:
        raise ValueError(f'{nombre} debe ser un entero mayor o igual a {minimo}.')
    return int(valor)


def parametros(dimension, pasos, repeticiones, semilla):
    entero(dimension, 'Dimensión')
    entero(pasos, 'Pasos')
    entero(repeticiones, 'Repeticiones')
    entero(semilla, 'Semilla', 0)


def trayectoria(dimension, pasos, semilla=2026):
    parametros(dimension, pasos, 1, semilla)
    direcciones = np.random.default_rng(semilla).integers(0, 2 * dimension, size=pasos)
    movimientos = np.zeros((pasos, dimension), dtype=np.int64)
    movimientos[np.arange(pasos), direcciones // 2] = np.where(direcciones % 2 == 0, 1, -1)
    return np.vstack((np.zeros((1, dimension), dtype=np.int64), movimientos.cumsum(axis=0)))


@dataclass
class Resultado:
    dimension: int
    pasos: int
    repeticiones: int
    semilla: int
    maximas: np.ndarray
    segundos: float

    @property
    def promedio(self):
        return float(np.mean(self.maximas))

    def fila(self):
        return [self.dimension, self.pasos, self.repeticiones, self.semilla, self.promedio, self.segundos]

    def exportar(self, archivo):
        archivo = Path(archivo)
        archivo.parent.mkdir(parents=True, exist_ok=True)
        with archivo.open('w', newline='', encoding='utf-8') as f:
            w = csv.writer(f, lineterminator='\n')
            w.writerow(['repeticion', 'distancia_maxima', 'dimension', 'pasos', 'semilla'])
            w.writerows((i, float(v), self.dimension, self.pasos, self.semilla) for i, v in enumerate(self.maximas, 1))


CABECERA = ['dimension', 'pasos', 'repeticiones', 'semilla', 'promedio_distancia_maxima', 'tiempo_segundos']


def simular(dimension, pasos, repeticiones, semilla=2026):
    """Procesa lotes de hasta un millón de pasos para limitar memoria.

    Cada fila es una caminata; un entero uniforme en [0,2d) elige eje y signo.
    El lote depende solo de pasos: aumentar repeticiones conserva el prefijo.
    Tiempo: generación, movimientos y máximos; excluye exportación y gráficas.
    """
    parametros(dimension, pasos, repeticiones, semilla)
    inicio = perf_counter()
    rng = np.random.default_rng(semilla)
    maximas = np.empty(repeticiones)
    lote = max(1, min(256, 1_000_000 // pasos))
    for inicio_lote in range(0, repeticiones, lote):
        cantidad = min(lote, repeticiones - inicio_lote)
        direcciones = rng.integers(0, 2 * dimension, size=(cantidad, pasos))
        radios2 = np.zeros((cantidad, pasos), dtype=np.float64)
        for eje in range(dimension):
            incrementos = np.where(direcciones // 2 == eje, np.where(direcciones % 2 == 0, 1, -1), 0)
            posiciones = incrementos.cumsum(axis=1)
            radios2 += posiciones.astype(np.float64) ** 2
        maximas[inicio_lote:inicio_lote + cantidad] = np.sqrt(radios2.max(axis=1))
    return Resultado(dimension, pasos, repeticiones, semilla, maximas, perf_counter() - inicio)
