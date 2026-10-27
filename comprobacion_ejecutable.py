"""Prueba funcional del mismo binario distribuido; salida JSON fuera del bundle."""
import csv
import hashlib
import json
import platform
import sys
import time
import traceback
from pathlib import Path
from unittest.mock import patch


def verificar(carpeta):
    carpeta = Path(carpeta).resolve()
    carpeta.mkdir(parents=True, exist_ok=True)
    informe = {'correcto': False, 'plataforma': platform.system(), 'compilado': bool(getattr(sys, 'frozen', False)), 'ejecutable': sys.executable, 'sha256_ejecutable': hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(), 'directorio_trabajo': str(Path.cwd()), 'verificaciones': []}
    root = None
    try:
        import tkinter as tk
        import numpy as np
        from main import Aplicacion
        from simulacion import trayectoria
        root = tk.Tk()
        app = Aplicacion(root)
        root.update()
        for d in (1, 2):
            for variable, valor in zip(app.variables, (d, 100, 1, 42)):
                variable.set(str(valor))
            app.boton.invoke()
            limite = time.monotonic() + 30
            while app.ocupado and time.monotonic() < limite:
                root.update(); time.sleep(.01)
            assert not app.ocupado, 'La simulación no terminó'
            assert len(app.resultados) == d, 'No se recibió el resultado'
            assert len(app.tabla.get_children()) == 1
            esperado = np.linalg.norm(trayectoria(d, 100, 42), axis=1).max()
            assert app.resultados[-1].maximas[0] == esperado
            assert f'{esperado:.6f}' in app.estado.get()
            csv_path = carpeta / f'distancias_{d}d.csv'
            with patch('main.filedialog.asksaveasfilename', return_value=str(csv_path)):
                app.exportar_boton.invoke()
            with csv_path.open(encoding='utf-8') as f:
                filas = list(csv.DictReader(f))
            assert len(filas) == 1 and float(filas[0]['distancia_maxima']) == esperado
            png_path = carpeta / f'grafica_{d}d.png'
            with patch('main.filedialog.asksaveasfilename', return_value=str(png_path)):
                app.grafica_boton.invoke()
            assert png_path.read_bytes()[:8] == b'\x89PNG\r\n\x1a\n'
            informe['verificaciones'].append(f'GUI {d}D: cálculo, tabla, promedio, CSV y PNG')
        with patch('main.filedialog.asksaveasfilename', return_value=str(carpeta / 'resumen.csv')):
            app.resumen_boton.invoke()
        with (carpeta / 'resumen.csv').open() as f:
            assert len(list(csv.DictReader(f))) == 2
        app.variables[1].set('-1')
        with patch('main.messagebox.showerror') as error:
            app.boton.invoke()
            error.assert_called_once()
        informe['verificaciones'].extend(['Resumen de sesión', 'Rechazo de parámetros inválidos'])
        informe['correcto'] = True
    except Exception:
        informe['error'] = traceback.format_exc()
    finally:
        if root is not None:
            root.destroy()
        (carpeta / 'verificacion_windows.json').write_text(json.dumps(informe, ensure_ascii=False, indent=2), encoding='utf-8')
    return 0 if informe['correcto'] else 1
