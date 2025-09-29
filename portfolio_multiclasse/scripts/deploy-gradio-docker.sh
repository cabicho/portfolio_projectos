#!/bin/bash

echo "🐳 Deploy com Docker Compose..."

# Build e deploy
docker-compose -f docker-compose-gradio.yml down
docker-compose -f docker-compose-gradio.yml build --no-cache
docker-compose -f docker-compose-gradio.yml up -d

echo "✅ Deploy completo!"
echo "🌐 Acesse: http://localhost:7860"
echo "📊 Dashboard multiclasse disponível"