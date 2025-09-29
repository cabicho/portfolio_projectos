#!/bin/bash

echo "🚀 Iniciando Sistema Multiclasse com Gradio..."

# Verificar dependências
python -c "import gradio" 2>/dev/null || {
    echo "📦 Instalando dependências..."
    pip install -r requirements_gradio.txt
}

# Iniciar aplicação
echo "🌐 Iniciando servidor Gradio na porta 7860..."
python app_gradio.py