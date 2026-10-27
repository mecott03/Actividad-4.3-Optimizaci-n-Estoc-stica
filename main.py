"""Interfaz Tkinter; trabajo numérico fuera del hilo de eventos."""
import csv
import queue
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from simulacion import simular, CABECERA


def leer_entradas(dimension, pasos, repeticiones, semilla):
    try:
        valores = tuple(int(v) for v in (dimension, pasos, repeticiones, semilla))
    except (ValueError, TypeError):
        raise ValueError('Introduce números enteros en todos los campos.') from None
    d, p, n, s = valores
    if d not in (1, 2):
        raise ValueError('Selecciona dimensión 1 o 2.')
    if not 1 <= p <= 100000 or not 1 <= n <= 10000 or s < 0:
        raise ValueError('Pasos: 1–100,000. Repeticiones: 1–10,000. Semilla: entero no negativo.')
    if p * n > 100_000_000:
        raise ValueError('El límite por ejecución es 100 millones de pasos totales.')
    return valores


class Aplicacion(ttk.Frame):
    def __init__(self, root):
        super().__init__(root, padding=16)
        self.pack(fill='both', expand=True)
        root.title('Actividad 4.3 · Caminata aleatoria')
        root.geometry('960x650')
        self.resultados = []
        self.cola = queue.Queue()
        self.ocupado = False
        ttk.Label(self, text='Caminata aleatoria · Optimización Estocástica', font=('', 17, 'bold')).pack(anchor='w')
        ttk.Label(self, text='Origen en cero · pasos unitarios · distancia euclidiana · semilla reproducible').pack(anchor='w', pady=(4, 14))
        campos = ttk.Frame(self); campos.pack(fill='x')
        self.variables = [tk.StringVar(value=v) for v in ('1', '1000', '100', '2026')]
        for i, (nombre, variable) in enumerate(zip(('Dimensión', 'Pasos', 'Repeticiones', 'Semilla'), self.variables)):
            ttk.Label(campos, text=nombre).grid(row=0, column=i, sticky='w', padx=5)
            entrada = ttk.Combobox(campos, textvariable=variable, values=('1', '2'), state='readonly', width=14) if i == 0 else ttk.Entry(campos, textvariable=variable, width=18)
            entrada.grid(row=1, column=i, padx=5, pady=6)
        botones = ttk.Frame(self); botones.pack(fill='x', pady=10)
        self.boton = ttk.Button(botones, text='Ejecutar simulación', command=self.ejecutar); self.boton.pack(side='left')
        self.exportar_boton = ttk.Button(botones, text='Exportar última simulación', command=self.exportar, state='disabled'); self.exportar_boton.pack(side='left', padx=8)
        self.resumen_boton = ttk.Button(botones, text='Exportar resumen de sesión', command=self.exportar_resumen, state='disabled'); self.resumen_boton.pack(side='left')
        self.estado = tk.StringVar(value='Listo. La tabla muestra todas las distancias de la última simulación.')
        ttk.Label(self, textvariable=self.estado, wraplength=900).pack(anchor='w', pady=8)
        self.progreso = ttk.Progressbar(self, mode='indeterminate'); self.progreso.pack(fill='x')
        contenedor = ttk.Frame(self); contenedor.pack(fill='both', expand=True, pady=10)
        self.tabla = ttk.Treeview(contenedor, columns=('n', 'distancia'), show='headings')
        self.tabla.heading('n', text='Repetición'); self.tabla.heading('distancia', text='Distancia máxima (unidades)')
        scroll = ttk.Scrollbar(contenedor, orient='vertical', command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)
        self.tabla.pack(side='left', fill='both', expand=True); scroll.pack(side='right', fill='y')
        ttk.Label(self, text='Límites: 100,000 pasos, 10,000 repeticiones y 100 millones de pasos totales.\nEl tiempo excluye la visualización y la exportación. Las gráficas obligatorias están en graficas/.').pack(anchor='w')
        self.after(100, self.recibir)

    def ejecutar(self):
        if self.ocupado:
            return
        try:
            valores = leer_entradas(*(v.get() for v in self.variables))
        except ValueError as error:
            messagebox.showerror('Parámetros incorrectos', str(error)); return
        self.ocupado = True
        self.boton.configure(state='disabled')
        self.progreso.start()
        self.estado.set('Simulando… espera a que termine el cálculo.')
        def trabajo():
            try:
                self.cola.put((simular(*valores), None))
            except Exception as error:
                self.cola.put((None, str(error)))
        threading.Thread(target=trabajo, daemon=True).start()

    def recibir(self):
        try:
            resultado, error = self.cola.get_nowait()
        except queue.Empty:
            pass
        else:
            self.ocupado = False
            self.boton.configure(state='normal'); self.progreso.stop()
            if error:
                self.estado.set('No se completó la simulación.')
                messagebox.showerror('Error de simulación', error)
            else:
                self.resultados.append(resultado)
                self.tabla.delete(*self.tabla.get_children())
                for i, distancia in enumerate(resultado.maximas, 1):
                    self.tabla.insert('', 'end', values=(i, f'{distancia:.6f}'))
                self.estado.set(f'{resultado.dimension}D · {resultado.pasos:,} pasos · {resultado.repeticiones:,} repeticiones · semilla {resultado.semilla} | Promedio máximo: {resultado.promedio:.6f} unidades | Tiempo: {resultado.segundos:.4f} s')
                self.exportar_boton.configure(state='normal'); self.resumen_boton.configure(state='normal')
        self.after(100, self.recibir)

    def exportar(self):
        nombre = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV', '*.csv')], initialfile='distancias_simulacion.csv')
        if nombre:
            try:
                self.resultados[-1].exportar(nombre)
            except OSError as error:
                messagebox.showerror('No se pudo guardar', str(error))

    def exportar_resumen(self):
        nombre = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV', '*.csv')], initialfile='resumen_sesion.csv')
        if nombre:
            try:
                with Path(nombre).open('w', newline='', encoding='utf-8') as f:
                    w = csv.writer(f, lineterminator='\n'); w.writerow(CABECERA); w.writerows(r.fila() for r in self.resultados)
            except OSError as error:
                messagebox.showerror('No se pudo guardar', str(error))


if __name__ == '__main__':
    root = tk.Tk()
    Aplicacion(root)
    root.mainloop()
