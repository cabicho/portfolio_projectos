# Dockerfile - CORRIGIDO
FROM python:3.9-slim

WORKDIR /app

# Instalar dependências do sistema INCLUINDO postgresql-client
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copiar requirements primeiro (para cache de camadas)
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fonte
COPY src/ ./src/
COPY scripts/ ./scripts/

# Criar diretórios necessários
RUN mkdir -p /app/data/raw /app/data/processed /app/data/analytics /app/logs

# Tornar scripts executáveis
RUN chmod +x ./scripts/*.sh
RUN chmod +x ./src/data-ingestion/*.py
RUN chmod +x ./src/data-processing/*.py
RUN chmod +x ./src/data-mart/*.py

CMD ["./scripts/run-etl.sh"]