FROM python:3.9-slim
WORKDIR /app

# Instala dependências do sistema necessárias
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instala setuptools primeiro
RUN pip install --upgrade pip setuptools==58.0.0 wheel

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 10000
CMD ["python", "portfolio_multiclasse/app_gradio.py"]
