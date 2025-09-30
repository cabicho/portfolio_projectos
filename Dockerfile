FROM python:3.9-slim

WORKDIR /app

# Instalar dependências do sistema e curl para health check
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro para aproveitar cache do Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação
COPY app.py .

# Expor a porta que será usada
EXPOSE 10000

# Health check para o Render
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:10000 || exit 1

# Comando para iniciar a aplicação
CMD ["python", "app.py"]