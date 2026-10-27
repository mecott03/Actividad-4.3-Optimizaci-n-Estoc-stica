"""Comprobación estadística de las 2d direcciones (Pearson chi cuadrado)."""
import json
from pathlib import Path
import numpy as np
from simulacion import trayectoria


def validar_uniformidad(dimension, muestras=200000, semilla=731):
    # Se comprueban movimientos generados por la función de trayectoria real.
    movimientos = np.diff(trayectoria(dimension, muestras, semilla), axis=0)
    ejes = np.abs(movimientos).argmax(axis=1)
    signos = movimientos[np.arange(muestras), ejes] < 0
    frecuencias = np.bincount(2 * ejes + signos, minlength=2 * dimension)
    esperado = muestras / (2 * dimension)
    estadistico = float(np.sum((frecuencias - esperado) ** 2 / esperado))
    # Cuantiles 0.999 de chi² para 1 y 3 grados de libertad.
    umbral = {1: 10.8275661707, 2: 16.2662361962}[dimension]
    return {'dimension':dimension, 'muestras':muestras, 'semilla':semilla, 'frecuencias':frecuencias.tolist(), 'chi_cuadrado':estadistico, 'grados_libertad':2*dimension-1, 'alfa':0.001, 'umbral':umbral, 'no_rechaza_uniformidad':estadistico < umbral, 'interpretacion':'No rechazar no demuestra uniformidad; la equiprobabilidad también se verifica por construcción del muestreo entero.'}


if __name__ == '__main__':
    datos = [validar_uniformidad(d) for d in (1, 2)]
    archivo = Path(__file__).resolve().parent / 'resultados' / 'validacion_uniformidad.json'
    archivo.parent.mkdir(parents=True, exist_ok=True)
    archivo.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(datos, ensure_ascii=False, indent=2))
    raise SystemExit(0 if all(r['no_rechaza_uniformidad'] for r in datos) else 1)
