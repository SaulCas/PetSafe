@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo No se encontro el entorno virtual .venv
    echo Primero crea o revisa el entorno virtual del proyecto.
    pause
    exit /b 1
)

start "" http://127.0.0.1:5000
call ".venv\Scripts\activate.bat"
python app.py

pause
