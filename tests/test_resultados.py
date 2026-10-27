"""Audita todos los datos entregados, no solo la existencia de archivos."""
import csv
import itertools
import unittest
from pathlib import Path
import numpy as np
from simulacion import simular

BASE = Path(__file__).resolve().parents[1]


class PruebasResultados(unittest.TestCase):
    def test_18_configuraciones_y_reproduccion_completa(self):
        with (BASE / 'resultados/resumen_experimentos.csv').open() as f:
            filas = list(csv.DictReader(f))
        esperadas = set(itertools.product((1, 2), (100,1000,10000), (100,1000,10000)))
        self.assertEqual(len(filas), 18)
        self.assertEqual({(int(r['dimension']),int(r['pasos']),int(r['repeticiones'])) for r in filas}, esperadas)
        for r in filas:
            d,p,n,s = (int(r[k]) for k in ('dimension','pasos','repeticiones','semilla'))
            archivo = BASE / f'resultados/distancias_individuales/{d}d_p{p}_n{n}.csv'
            with archivo.open() as f:
                datos = list(csv.DictReader(f))
            self.assertEqual(len(datos), n)
            valores = np.array([float(x['distancia_maxima']) for x in datos])
            self.assertEqual([int(x['repeticion']) for x in datos], list(range(1,n+1)))
            self.assertTrue(all(int(x['dimension'])==d and int(x['pasos'])==p and int(x['semilla'])==s for x in datos))
            np.testing.assert_array_equal(valores, simular(d,p,n,s).maximas)
            self.assertAlmostEqual(float(r['promedio_distancia_maxima']), float(valores.mean()), places=12)
            self.assertGreater(float(r['tiempo_segundos']), 0)

    def test_trayectorias_y_png(self):
        from simulacion import trayectoria
        for d in (1,2):
            datos = np.loadtxt(BASE / f'resultados/trayectoria_{d}d.csv', delimiter=',', skiprows=1)
            np.testing.assert_array_equal(datos[:,0], np.arange(1001))
            np.testing.assert_array_equal(datos[:,1:], trayectoria(d,1000,2026))
        for nombre in ('trayectoria_1d','trayectoria_2d','promedio_por_pasos','comparacion_dimensiones','promedio_por_repeticiones'):
            archivo = BASE / 'graficas' / (nombre + '.png')
            self.assertGreater(archivo.stat().st_size, 1000)
            self.assertEqual(archivo.read_bytes()[:8], b'\x89PNG\r\n\x1a\n')
