"""Prueba funcional real de Tkinter; requiere pantalla o servidor X virtual.
Ejecutar desde la raíz: python -m tests.gui_smoke (o python tests/gui_smoke.py).
"""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[1]))
import tempfile
import time
from pathlib import Path
from unittest.mock import patch
import tkinter as tk
import numpy as np
from main import Aplicacion
from simulacion import simular

root = tk.Tk()
app = Aplicacion(root)
root.update()
with tempfile.TemporaryDirectory() as carpeta:
    for d in (1, 2):
        for variable, valor in zip(app.variables, (d, 100, 25, 42)):
            variable.set(str(valor))
        app.boton.invoke()
        limite = time.monotonic() + 15
        while app.ocupado and time.monotonic() < limite:
            root.update()
            time.sleep(.01)
        assert not app.ocupado, 'Tiempo de espera excedido'
        assert len(app.tabla.get_children()) == 25
        assert f'{app.resultados[-1].promedio:.6f}' in app.estado.get()
        np.testing.assert_array_equal(app.resultados[-1].maximas, simular(d,100,25,42).maximas)
        archivo = Path(carpeta) / f'{d}d.csv'
        with patch('main.filedialog.asksaveasfilename', return_value=str(archivo)):
            app.exportar_boton.invoke()
        assert len(archivo.read_text().splitlines()) == 26
    with patch('main.filedialog.asksaveasfilename', return_value=str(Path(carpeta)/'resumen.csv')):
        app.resumen_boton.invoke()
    assert len((Path(carpeta)/'resumen.csv').read_text().splitlines()) == 3
    app.variables[1].set('-1')
    with patch('main.messagebox.showerror') as mensaje:
        app.boton.invoke()
        mensaje.assert_called_once()
    assert not app.ocupado
root.destroy()
print('GUI OK: inicio, simulación 1D/2D, tabla, promedio, exportación individual/resumen y rechazo de entrada inválida.')
