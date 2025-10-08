# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements-mozambique.txt .

# Instalar dependências Python (incluindo Jupyter)
RUN pip install --no-cache-dir -r requirements-mozambique.txt && \
    pip install --no-cache-dir jupyter dash

# Copiar código
COPY . .

# Criar diretórios necessários
RUN mkdir -p data/mozambique/{raw,processed,reports} && \
    mkdir -p notebooks

# Expor portas
EXPOSE 8050 8888

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8050/ || exit 1

# Comando padrão (dashboard)
CMD ["python", "scripts/mozambique/dashboard_app.py"]