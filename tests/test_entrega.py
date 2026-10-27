import hashlib
import tempfile
import unittest
from pathlib import Path
from preparar_entrega import preparar, verificar_pe, NOMBRE
from graficas_simulacion import guardar_grafica
from simulacion import simular

BASE = Path(__file__).resolve().parents[1]


class PruebasEntrega(unittest.TestCase):
    def test_no_acepta_fuente_como_exe(self):
        with self.assertRaises(ValueError):
            verificar_pe(BASE / 'main.py')

    def test_preparacion_incompleta_sin_zip_y_copias_identicas(self):
        with tempfile.TemporaryDirectory() as carpeta:
            destino = preparar(salida=carpeta)
            self.assertFalse((destino / 'Caminata_Aleatoria.exe').exists())
            self.assertFalse((Path(carpeta) / f'{NOMBRE}.zip').exists())
            self.assertIn('INCOMPLETA', (destino / 'INSTRUCCIONES.txt').read_text(encoding='utf-8'))
            self.assertEqual(len(list((destino / 'resultados/distancias_individuales').glob('*.csv'))),18)
            self.assertEqual(len(list((destino / 'graficas').glob('*.png'))),5)
            for sub in ('resultados','graficas'):
                for archivo in (destino / sub).rglob('*'):
                    if archivo.is_file():
                        original = BASE / archivo.relative_to(destino)
                        self.assertEqual(hashlib.sha256(archivo.read_bytes()).digest(), hashlib.sha256(original.read_bytes()).digest())
            self.assertFalse(list(destino.rglob('*.bat')))
            with self.assertRaises(FileExistsError):
                preparar(salida=carpeta)

    def test_grafica_nueva_desde_resultados_existentes(self):
        r = simular(2,100,50,42)
        anteriores = r.maximas.copy()
        with tempfile.TemporaryDirectory() as carpeta:
            archivo = guardar_grafica(r, Path(carpeta) / 'ruta con espacios' / 'grafica.png')
            self.assertEqual(archivo.read_bytes()[:8], b'\x89PNG\r\n\x1a\n')
            self.assertGreater(archivo.stat().st_size,1000)
        self.assertTrue((anteriores == r.maximas).all())
