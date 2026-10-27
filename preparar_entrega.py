"""Empaquetado con lista explícita; nunca crea el ZIP final sin un PE real."""
import argparse
import csv
import hashlib
import itertools
import json
import shutil
import struct
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

BASE = Path(__file__).resolve().parent
NOMBRE = 'ENTREGA_ACTIVIDAD_4.3'
FUENTES = ('main.py', 'simulacion.py', 'experimentos.py', 'validaciones.py', 'graficas_simulacion.py', 'comprobacion_ejecutable.py', 'requirements.txt')


def verificar_pe(archivo):
    datos = archivo.read_bytes()
    if len(datos) < 64 or datos[:2] != b'MZ':
        raise ValueError('No es un ejecutable Windows PE real.')
    offset = struct.unpack_from('<I', datos, 60)[0]
    if datos[offset:offset+4] != b'PE\0\0' or struct.unpack_from('<H', datos, offset+24+68)[0] != 2:
        raise ValueError('Se requiere un ejecutable PE de interfaz gráfica, sin consola.')


def preparar(exe=None, salida=BASE, evidencia=None):
    salida = Path(salida).resolve()
    destino = salida / NOMBRE
    if destino.exists():
        raise FileExistsError(f'La carpeta ya existe: {destino}. No se sobrescribirá.')
    # Comprobar los datos originales antes de copiar, sin alterarlos.
    with (BASE / 'resultados/resumen_experimentos.csv').open() as f:
        filas = list(csv.DictReader(f))
    configuraciones = {(int(r['dimension']), int(r['pasos']), int(r['repeticiones'])) for r in filas}
    esperadas = set(itertools.product((1,2),(100,1000,10000),(100,1000,10000)))
    if len(filas) != 18 or configuraciones != esperadas:
        raise ValueError('El resumen no contiene las 18 configuraciones requeridas.')
    individuales = []
    for d,p,n in sorted(esperadas):
        archivo = BASE / f'resultados/distancias_individuales/{d}d_p{p}_n{n}.csv'
        with archivo.open() as f:
            datos = list(csv.DictReader(f))
        if len(datos) != n:
            raise ValueError(f'Repeticiones incorrectas en {archivo.name}')
        individuales.append(archivo)
    if exe:
        exe = Path(exe).resolve()
        verificar_pe(exe)
        if evidencia is None:
            raise ValueError('Falta evidencia de la prueba del ejecutable en Windows.')
        prueba = json.loads(Path(evidencia).read_text(encoding='utf-8'))
        if not (prueba.get('correcto') and prueba.get('compilado') and prueba.get('plataforma') == 'Windows'):
            raise ValueError('La evidencia no confirma una prueba Windows correcta del binario.')
        if prueba.get('sha256_ejecutable') != hashlib.sha256(exe.read_bytes()).hexdigest():
            raise ValueError('La evidencia corresponde a otro ejecutable.')
    destino.mkdir(parents=True)
    (destino / 'resultados/distancias_individuales').mkdir(parents=True)
    for archivo in individuales:
        shutil.copy2(archivo, destino / 'resultados/distancias_individuales' / archivo.name)
    for archivo in (BASE / 'resultados').glob('*.csv'):
        shutil.copy2(archivo, destino / 'resultados' / archivo.name)
    (destino / 'graficas').mkdir()
    pngs = list((BASE / 'graficas').glob('*.png'))
    if len(pngs) != 5:
        raise ValueError('Faltan las cinco gráficas originales.')
    for archivo in pngs:
        shutil.copy2(archivo, destino / 'graficas' / archivo.name)
    (destino / 'codigo_fuente').mkdir()
    for nombre in FUENTES:
        shutil.copy2(BASE / nombre, destino / 'codigo_fuente' / nombre)
    texto = '''ACTIVIDAD 4.3 - CAMINATA ALEATORIA Y VALIDACIONES ESTADÍSTICAS

1. Extrae TODA la carpeta del ZIP en una ubicación con permiso de escritura.
2. En Windows 10/11 de 64 bits, abre Caminata_Aleatoria.exe con doble clic.
   No necesitas instalar Python, dependencias ni abrir el código fuente.
3. Selecciona dimensión 1 o 2, pasos, repeticiones y semilla. Pulsa Ejecutar.
   La tabla muestra las distancias máximas; arriba aparecen promedio y tiempo.
4. Guarda CSV individuales, resumen de sesión o una gráfica PNG con los botones.
   Puedes elegir cualquier carpeta con permiso de escritura. No se modifica
   automáticamente la carpeta de resultados originales. Espera a que termine.
5. Consulta resultados/resumen_experimentos.csv y distancias_individuales/:
   contienen las 18 configuraciones obligatorias y todas sus distancias reales.
   Las cinco gráficas originales están en graficas/. Código: codigo_fuente/.

Límites: 100,000 pasos, 10,000 repeticiones y 100 millones de pasos por ejecución.
La misma semilla reproduce las distancias (el tiempo puede variar).
La primera apertura del ejecutable puede tardar mientras extrae sus bibliotecas.
No se necesita Internet para usarlo. El binario no está firmado digitalmente;
Windows puede mostrar un aviso de reputación. Verifica el origen del archivo.
No se incluyen conclusiones ni documento final.
'''
    if exe:
        shutil.copy2(exe, destino / 'Caminata_Aleatoria.exe')
        texto += '\nVerificación automática: binario abierto en Windows, GUI 1D/2D, cálculo,\ntabla, exportación CSV y PNG; inicio desde otra carpeta con PATH sin Python.\nSHA-256 del ejecutable: ' + hashlib.sha256(exe.read_bytes()).hexdigest() + '\n'
    else:
        texto = 'PREPARACIÓN INCOMPLETA: FALTA EL EJECUTABLE WINDOWS.\nNO ENTREGAR ESTA CARPETA TODAVÍA.\n\n' + texto
    (destino / 'INSTRUCCIONES.txt').write_text(texto, encoding='utf-8')
    if exe:
        zip_path = salida / f'{NOMBRE}.zip'
        with ZipFile(zip_path, 'w', ZIP_DEFLATED) as z:
            for archivo in sorted(destino.rglob('*')):
                if archivo.is_file():
                    z.write(archivo, archivo.relative_to(salida))
        with ZipFile(zip_path) as z:
            assert z.testzip() is None
        print(zip_path)
    return destino


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    grupo = parser.add_mutually_exclusive_group(required=True)
    grupo.add_argument('--exe', type=Path)
    grupo.add_argument('--sin-ejecutable', action='store_true', help='Solo preparación incompleta, sin ZIP final')
    parser.add_argument('--evidencia', type=Path)
    parser.add_argument('--salida', type=Path, default=BASE)
    args = parser.parse_args()
    preparar(args.exe, args.salida, args.evidencia)
