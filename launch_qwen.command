#!/bin/bash

# Script de lanzamiento para Qwen-Image 2.0
# Optimizado para macOS

# Obtener el directorio donde reside el script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "------------------------------------------------"
echo "🚀 Iniciando Qwen-Image 2.0 Local (M4 Pro)..."
echo "------------------------------------------------"

# Verificar si el entorno virtual existe
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📥 Instalando dependencias iniciales..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source venv/bin/activate
    # Forzar verificación de dependencias nuevas (torch, torchvision, gradio)
    echo "📦 Verificando dependencias..."
    pip install -r requirements.txt --quiet
fi

# Verificar si el modelo existe, si no, descargarlo
if [ ! -d "models/Qwen-Image-2.0-7B-Instruct-MLX" ]; then
    echo "🔍 No se ha encontrado el modelo. Iniciando descarga automática..."
    python download_model.py
fi

echo "🌐 Iniciando servidor web..."
echo "La interfaz se abrirá automáticamente en su navegador."
python app_web.py

# Mantener la terminal abierta si hay un error
if [ $? -ne 0 ]; then
    echo "❌ Hubo un error al iniciar la aplicación."
    read -p "Presione Enter para cerrar..."
fi
