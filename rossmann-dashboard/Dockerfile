# Dockerfile para Produção - Dashboard Rossmann
FROM python:3.9-slim

# Define variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV DASH_DEBUG_MODE=False
ENV PORT=8050

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos de requirements primeiro (para cache do Docker)
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Cria usuário não-root para segurança
RUN useradd -m -r dashboard-user && \
    chown -R dashboard-user /app
USER dashboard-user

# Expõe a porta
EXPOSE 8050

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8050/_dash-health-check || exit 1

# Comando para rodar a aplicação
CMD ["python", "app.py"]
