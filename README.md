# Entrega final para Windows (sin instalar Python)

El `.bat` anterior necesitaba Python instalado; el mensaje `No suitable Python runtime found` proviene de ese requisito. **El paquete final se compila en Windows con GitHub Actions**, no con ese `.bat`.

1. Abre [Entrega final Windows en Actions](https://github.com/mecott03/Actividad-4.3-Optimizaci-n-Estoc-stica/actions/workflows/entrega-windows.yml).
2. La compilación se activa al subir los cambios a `main`. También puedes pulsar **Run workflow → Run workflow**.
3. Espera un resultado verde. En **Releases** descarga `ENTREGA_ACTIVIDAD_4.3.zip`. También está en **Artifacts → ENTREGA_ACTIVIDAD_4.3** de la ejecución (GitHub envuelve el archivo en otro ZIP).
4. Extrae la carpeta y abre **Caminata_Aleatoria.exe**. No requiere instalar Python, dependencias ni Internet.

[Descargar ZIP de la última entrega publicada](https://github.com/mecott03/Actividad-4.3-Optimizaci-n-Estoc-stica/releases/latest/download/ENTREGA_ACTIVIDAD_4.3.zip) — el enlace solo funcionará después de una compilación y publicación correctas.

La carpeta final contiene únicamente el ejecutable, `resultados/`, `graficas/`, `codigo_fuente/` e `INSTRUCCIONES.txt`. Se conservan los datos originales. La interfaz permite guardar CSV y generar un PNG de las distancias de la última simulación mediante un selector de ubicación. No escribe en la carpeta temporal del ejecutable.

El workflow ejecuta las pruebas, compila un PE de interfaz gráfica con PyInstaller, traslada el `.exe` a una ruta con espacios y lo abre desde otra carpeta con `PATH` sin Python ni variables de su entorno. Verifica la GUI real, resultados 1D/2D, tabla, promedio, exportación CSV, PNG y rechazo de entradas inválidas. `verificacion-windows` conserva la evidencia JSON de esa ejecución. El runner tiene Python para compilar: esta prueba aísla el binario de su búsqueda en PATH, pero no equivale a desinstalar Python físicamente del runner.

El empaquetador exige un PE sin consola y un informe correcto del mismo binario ejecutado en Windows, identificado por SHA-256. **No crea el ZIP final sin un ejecutable probado.** La carpeta de entrega se genera, no se mantiene como duplicado de los archivos originales en Git. No se incluyen cachés, `.venv`, compilación ni pruebas en el paquete final.

Para desarrolladores: `python preparar_entrega.py --exe dist/Caminata_Aleatoria.exe --evidencia ruta/verificacion_windows.json --salida paquete`. `--sin-ejecutable` prepara solamente una carpeta claramente marcada como incompleta y no crea el ZIP final.

---

# Actividad 4.3 – Caminata Aleatoria y Validaciones Estadísticas

Simulador de movimiento browniano discreto para Optimización Estocástica. La partícula inicia en el origen y realiza pasos unitarios sobre los ejes de Zᵈ. En cada paso se elige uniformemente una de las 2d direcciones: eje `dirección // 2` y signo positivo/negativo según su paridad. Se registra la mayor distancia euclidiana al origen durante **toda** la caminata, no solo la distancia final.

## Inicio en Windows

1. Descarga el ZIP del repositorio y **extrae todos sus archivos**.
2. Instala **Python 3.12 de python.org**, incluyendo Tcl/Tk y el lanzador `py`.
3. Haz doble clic en **`ejecutar.bat`**. La primera ejecución crea `.venv` e instala las dos dependencias con Internet. Después abre la interfaz sin editar código. Si existe el ejecutable compilado, el script lo abre directamente.

El archivo `.bat` requiere Python: **no es un ejecutable autónomo**. La copia del código fuente no incluye un `.exe` compilado en Linux; descarga el paquete Windows desde Releases o Actions. Para generarlo en Windows, haz doble clic en **`compilar_windows.bat`**: instala PyInstaller 6.16.0, ejecuta las pruebas y construye `dist/Caminata_Aleatoria.exe`. Prueba ese archivo en Windows antes de entregarlo. Puedes distribuirlo junto con este repositorio; el destinatario del `.exe` no requiere Python. PyInstaller no compila Windows desde Linux.

## Instalación manual (Windows, Linux o macOS)

Desde la carpeta del proyecto:

```bash
python -m venv .venv
```

Activa el entorno con `.venv\Scripts\activate` en Windows o `source .venv/bin/activate` en Linux/macOS. Luego:

```bash
python -m pip install -r requirements.txt
python main.py
```

En algunos sistemas se llama `python3`. Se validó con Python 3.12.14, NumPy 2.3.5 y Matplotlib 3.10.8. Tkinter forma parte de la instalación de Python; en Linux puede requerir el paquete del sistema `python3-tk`. La interfaz requiere una pantalla gráfica. Los experimentos y las gráficas PNG no requieren pantalla.

## Uso de la interfaz

Selecciona **1D o 2D**, introduce pasos, repeticiones y una semilla entera no negativa y pulsa **Ejecutar simulación**. La misma semilla y parámetros producen las mismas distancias (el tiempo puede cambiar). El cálculo usa un hilo de trabajo para mantener activa la ventana.

La interfaz muestra todas las distancias máximas individuales, su promedio y el tiempo del cálculo. Permite exportar la última simulación a CSV y un resumen de todas las ejecuciones de la sesión. Los archivos no se guardan automáticamente desde la interfaz: usa los botones de exportación.

Límites de interfaz: 1–100,000 pasos, 1–10,000 repeticiones y como máximo 100 millones de pasos totales por ejecución. Estos límites incluyen todas las configuraciones obligatorias. Los resultados se procesan por lotes para limitar la memoria. La lógica numérica admite otras dimensiones positivas; la interfaz se limita a las dos requeridas.

## Experimentos obligatorios y resultados

```bash
python experimentos.py
python validaciones.py
```

Se ejecutan las **18 combinaciones** del producto cartesiano de dimensiones `{1,2}`, pasos `{100,1000,10000}` y repeticiones `{100,1000,10000}`. Se entregan resultados reales ya generados:

- `resultados/resumen_experimentos.csv`: dimensión, pasos, repeticiones, semilla, promedio máximo y segundos de cálculo.
- `resultados/distancias_individuales/`: 18 CSV, una fila por repetición con su distancia máxima y parámetros.
- `resultados/trayectoria_1d.csv` y `trayectoria_2d.csv`: coordenadas de las caminatas ilustradas, incluyendo el origen.
- `resultados/metadatos.json`: versiones, plataforma, generador y criterio de semilla.
- `resultados/validacion_uniformidad.json`: frecuencias observadas y prueba chi cuadrado de direcciones.
- `resultados/verificacion.txt`: evidencia de las comprobaciones realizadas en el entorno de desarrollo.

Por defecto se usa semilla **2026** en cada configuración. Para un mismo número de pasos y dimensión, las muestras con más repeticiones extienden las anteriores: **las configuraciones no son muestras independientes**. Esto facilita comparar promedios al aumentar repeticiones. El tiempo mide la generación y cálculo de máximos; excluye archivos, gráficas y actualización de la interfaz. No se promete reproducibilidad bit a bit con otras versiones de NumPy.

Para cambiar semilla o guardar otra ejecución sin sobrescribir la entrega:

```bash
python experimentos.py --semilla 123 --salida otra_ejecucion
```

La ejecución por defecto sobrescribe los resultados y gráficas anteriores. El resumen y las gráficas se generan a partir de los mismos resultados en memoria. Los CSV usan coma como separador y punto decimal; en Excel usa **Datos → Desde texto/CSV** si la configuración regional lo necesita.

## Gráficas

Los cinco PNG de `graficas/` incluyen trayectorias en 1D y 2D (1,000 pasos), promedio máximo por pasos, comparación 1D/2D con 10,000 repeticiones y promedios según el número de repeticiones. Las trayectorias son ejemplos independientes; sus coordenadas están guardadas en CSV. Los ejes indican pasos, repeticiones o unidades de distancia según corresponda.

## Pruebas

```bash
python -m unittest discover -s tests -v
python validaciones.py
```

Las pruebas verifican origen, pasos unitarios, un solo eje modificado, máximos contra un cálculo independiente, número de repeticiones, promedios, límites, reproducción, exportación y entradas inválidas. También **recalculan las 18 configuraciones completas** y comparan cada distancia guardada y cada promedio. Esta auditoría tarda más que las pruebas unitarias.

La validación estadística usa 200,000 pasos por dimensión, semilla 731 y chi cuadrado de Pearson con nivel 0.001 (1 y 3 grados de libertad). No rechazar la hipótesis de uniformidad no prueba que un generador sea perfecto; la selección equiprobable también se garantiza por la construcción del algoritmo.

Para probar funcionalmente la interfaz en una máquina con pantalla:

```bash
python tests/gui_smoke.py
```

Esta comprobación abre Tkinter, ejecuta 1D y 2D, verifica tabla y resultados, exporta CSV y prueba el mensaje de entrada inválida. Los `.bat` y el `.exe` deben probarse adicionalmente en Windows.

## Archivos principales

| Archivo | Función |
|---|---|
| `main.py` | Interfaz gráfica y validación de entradas |
| `simulacion.py` | Trayectorias, experimentos por lotes, máximos y exportación |
| `experimentos.py` | Matriz experimental y gráficas |
| `validaciones.py` | Validación estadística de direcciones |
| `tests/` | Pruebas numéricas, auditoría de datos y prueba gráfica |
| `ejecutar.bat` | Inicio de la aplicación en Windows |
| `compilar_windows.bat` | Generación del ejecutable en Windows |

Se entrega únicamente programación, experimentación, tablas, gráficas y validación. Las conclusiones de convergencia y el documento final quedan para una etapa posterior. El código fuente se entrega como `.py`, según la preferencia de Python de esta implementación; el documento original menciona `.txt` o `.cs` como formatos posibles.
