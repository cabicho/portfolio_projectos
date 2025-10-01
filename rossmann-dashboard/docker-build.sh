#!/bin/bash

echo "🐳 Building Rossmann Dashboard..."

# Build da imagem de desenvolvimento
docker build -f Dockerfile.dev -t rossmann-dashboard:dev .

# Build da imagem de produção
docker build -f Dockerfile -t rossmann-dashboard:prod .

echo "✅ Build completed!"
echo ""
echo "🚀 Para executar desenvolvimento:"
echo "docker run -p 8050:8050 -v $(pwd):/app rossmann-dashboard:dev"
echo ""
echo "🏗️ Para executar produção:"
echo "docker run -p 8050:8050 rossmann-dashboard:prod"
