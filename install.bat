@echo off
REM Script de instalación y configuración para Windows

echo.
echo ======================================
echo Detector de Tráfico Anómalo
echo Instalador del Sistema
echo ======================================
echo.

REM Verificar Python
echo [1/5] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python no está instalado
    exit /b 1
)
echo ✓ Python encontrado

REM Crear entorno virtual
echo.
echo [2/5] Configurando entorno virtual...
if not exist "venv\" (
    python -m venv venv
    echo ✓ Entorno virtual creado
) else (
    echo ✓ Entorno virtual existente
)

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Instalar dependencias Python
echo.
echo [3/5] Instalando dependencias Python...
python -m pip install --upgrade pip > nul 2>&1
pip install -r requirements.txt
echo ✓ Dependencias Python instaladas

REM Instalar dependencias Frontend
echo.
echo [4/5] Instalando dependencias Frontend...
if exist "frontend\package.json" (
    cd frontend
    call npm install
    cd ..
    echo ✓ Dependencias Frontend instaladas
) else (
    echo ⚠ package.json no encontrado en frontend
)

REM Crear directorios necesarios
echo.
echo [5/5] Creando directorios...
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "backend\logs" mkdir backend\logs
echo ✓ Directorios creados

echo.
echo ======================================
echo ✓ Instalación completada!
echo ======================================
echo.
echo Para iniciar la aplicación:
echo.
echo Backend (Requiere permisos de administrador):
echo   venv\Scripts\activate.bat
echo   python backend\app.py
echo.
echo Frontend (en otra terminal):
echo   cd frontend
echo   npm start
echo.
echo La API estará disponible en http://localhost:5000
echo El Dashboard en http://localhost:3000
echo.
pause
