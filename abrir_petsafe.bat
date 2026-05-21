@echo off
:: Moverse a la carpeta donde está guardado este archivo .bat
cd /d "%~dp0"

:: 1. Validar si existe el entorno virtual 
if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] No se encontro el entorno virtual en la carpeta "venv"
    echo Por favor, asegúrate de que el entorno este creado en este directorio.
    pause
    exit /b 1
)

:: 2. Activar el entorno virtual
echo Activando entorno virtual...
call venv\Scripts\activate

:: 3. Asegurar que las librerías básicas estén instaladas
echo Verificando e instalando librerias necesarias...
pip install flask flask-login flask-sqlalchemy flask-wtf bcrypt email-validator

:: 4. Abrir el navegador automáticamente en segundo plano
echo Abriendo navegador en http://127.0.0.1:5000...
start "" "http://127.0.0.1:5000"

:: 5. Ejecutar la aplicación de Python
echo Iniciando PetSafe...
python app.py

pause
