# Dockerfile
FROM python:3.9-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# Copiar requirements primeiro para cache eficiente
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --upgrade pip setuptools==58.0.0 wheel

RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Expor porta do Render
EXPOSE 10000

# Health check para Render
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:10000 || exit 1

# Comando de inicialização
CMD ["python", "app_gradio.py"]