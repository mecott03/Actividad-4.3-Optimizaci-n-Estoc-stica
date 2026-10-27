@echo off
setlocal
cd /d "%~dp0"
if exist "dist\CaminataAleatoria.exe" (
    start "" "dist\CaminataAleatoria.exe"
    exit /b 0
)
where py >nul 2>nul
if errorlevel 1 (
    echo Instala Python 3.12 desde python.org, incluyendo Tcl/Tk y el lanzador py.
    pause
    exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
    py -3.12 -m venv .venv
    if errorlevel 1 goto error
)
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto error
.venv\Scripts\python.exe main.py
if errorlevel 1 goto error
exit /b 0
:error
echo No se pudo iniciar. Revisa el mensaje anterior y la conexion a Internet.
pause
exit /b 1
