@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 goto error
if not exist ".venv\Scripts\python.exe" py -3.12 -m venv .venv
if errorlevel 1 goto error
.venv\Scripts\python.exe -m pip install -r requirements.txt pyinstaller==6.16.0
if errorlevel 1 goto error
.venv\Scripts\python.exe -m unittest discover -s tests -v
if errorlevel 1 goto error
.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --onefile --windowed --name CaminataAleatoria main.py
if errorlevel 1 goto error
echo Ejecutable generado en dist\CaminataAleatoria.exe
pause
exit /b 0
:error
echo Fallo la compilacion. Se requiere Windows, Python 3.12 con Tcl/Tk e Internet.
pause
exit /b 1
