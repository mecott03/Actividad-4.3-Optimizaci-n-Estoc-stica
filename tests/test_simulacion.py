import csv
import tempfile
import unittest
from pathlib import Path
import numpy as np
from simulacion import simular, trayectoria
from main import leer_entradas
from validaciones import validar_uniformidad


class PruebasSimulacion(unittest.TestCase):
    def test_origen_pasos_y_ejes(self):
        for d in (1, 2, 3):
            p = trayectoria(d, 2000, 42)
            np.testing.assert_array_equal(p[0], np.zeros(d))
            cambios = np.diff(p, axis=0)
            np.testing.assert_array_equal(np.linalg.norm(cambios, axis=1), np.ones(2000))
            np.testing.assert_array_equal(np.count_nonzero(cambios, axis=1), np.ones(2000))

    def test_maximo_con_oraculo_independiente(self):
        for d in (1, 2, 3):
            for pasos in (1, 100, 10000):
                p = trayectoria(d, pasos, 91)
                esperado = max(sum(int(x)**2 for x in fila)**0.5 for fila in p)
                self.assertEqual(simular(d, pasos, 1, 91).maximas[0], esperado)

    def test_repeticiones_promedio_y_limites(self):
        r = simular(2, 100, 123, 12)
        self.assertEqual(len(r.maximas), 123)
        self.assertTrue(np.all(r.maximas >= 1))
        self.assertTrue(np.all(r.maximas <= 100))
        self.assertAlmostEqual(r.promedio, sum(r.maximas) / 123)
        self.assertGreaterEqual(r.segundos, 0)

    def test_reproducibilidad_y_prefijo_entre_lotes(self):
        a = simular(2, 5000, 300, 3)
        np.testing.assert_array_equal(a.maximas, simular(2, 5000, 300, 3).maximas)
        np.testing.assert_array_equal(a.maximas[:215], simular(2, 5000, 215, 3).maximas)
        self.assertFalse(np.array_equal(a.maximas, simular(2, 5000, 300, 4).maximas))

    def test_todas_caminatas_con_oraculo(self):
        d, pasos, n, semilla = 2, 23, 17, 12
        rng = np.random.default_rng(semilla)
        esperados = []
        for _ in range(n):
            posicion = [0, 0]; maxima = 0
            for direccion in rng.integers(0, 2*d, size=pasos):
                posicion[direccion // 2] += 1 if direccion % 2 == 0 else -1
                maxima = max(maxima, sum(x*x for x in posicion)**.5)
            esperados.append(maxima)
        np.testing.assert_allclose(simular(d, pasos, n, semilla).maximas, esperados)

    def test_uniformidad(self):
        for d in (1, 2):
            resultado = validar_uniformidad(d)
            self.assertTrue(resultado['no_rechaza_uniformidad'], resultado)

    def test_exportacion_real(self):
        r = simular(1, 100, 10, 7)
        with tempfile.TemporaryDirectory() as carpeta:
            archivo = Path(carpeta) / 'datos.csv'
            r.exportar(archivo)
            with archivo.open() as f:
                filas = list(csv.DictReader(f))
            self.assertEqual(len(filas), 10)
            np.testing.assert_array_equal([float(f['distancia_maxima']) for f in filas], r.maximas)

    def test_entradas_invalidas(self):
        for args in [(0, 1, 1, 0), (1, 0, 1, 0), (1, 1, -1, 0), (1, 1, 1, -1), (True, 1, 1, 0), (1, 1.5, 1, 0)]:
            with self.assertRaises(ValueError):
                simular(*args)
        for args in [('a','1','1','0'), ('3','1','1','0'), ('1','0','1','0'), ('1','100000','10000','0'), ('1','1','1','-1')]:
            with self.assertRaises(ValueError):
                leer_entradas(*args)
        self.assertEqual(leer_entradas('2','10000','10000','2026'), (2,10000,10000,2026))


if __name__ == '__main__':
    unittest.main()
