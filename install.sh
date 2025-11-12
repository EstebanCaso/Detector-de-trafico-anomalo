#!/bin/bash

# Script de instalación y configuración del Detector de Tráfico Anómalo

set -e

echo "======================================"
echo "Detector de Tráfico Anómalo"
echo "Instalador del Sistema"
echo "======================================"
echo ""

# Verificar Python
echo "[1/5] Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 no está instalado"
    exit 1
fi
echo "✓ Python 3 encontrado"

# Crear entorno virtual
echo ""
echo "[2/5] Configurando entorno virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Entorno virtual creado"
else
    echo "✓ Entorno virtual existente"
fi

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias Python
echo ""
echo "[3/5] Instalando dependencias Python..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo "✓ Dependencias Python instaladas"

# Instalar dependencias Frontend
echo ""
echo "[4/5] Instalando dependencias Frontend..."
if [ -f "frontend/package.json" ]; then
    cd frontend
    npm install
    cd ..
    echo "✓ Dependencias Frontend instaladas"
else
    echo "⚠ package.json no encontrado en frontend"
fi

# Crear directorios necesarios
echo ""
echo "[5/5] Creando directorios..."
mkdir -p data logs backend/logs
echo "✓ Directorios creados"

echo ""
echo "======================================"
echo "✓ Instalación completada!"
echo "======================================"
echo ""
echo "Para iniciar la aplicación:"
echo ""
echo "Backend:"
echo "  source venv/bin/activate"
echo "  python backend/app.py"
echo ""
echo "Frontend (en otra terminal):"
echo "  cd frontend"
echo "  npm start"
echo ""
echo "La API estará disponible en http://localhost:5000"
echo "El Dashboard en http://localhost:3000"
echo ""
