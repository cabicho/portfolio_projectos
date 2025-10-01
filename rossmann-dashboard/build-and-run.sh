#!/bin/bash

# build-and-run.sh - Versão compatível
set -e

echo "🐳 Rossmann Dashboard Docker Manager"
echo "======================================"

case "${1:-dev}" in
    "dev")
        echo "🚀 Iniciando modo desenvolvimento..."
        docker-compose up rossmann-dashboard-dev
        ;;
    "prod")
        echo "🏗️ Iniciando produção..."
        docker-compose up rossmann-dashboard
        ;;
    "build")
        echo "🏗️ Buildando todas as imagens..."
        docker-compose build
        ;;
    "stop")
        echo "🛑 Parando todos os containers..."
        docker-compose down
        ;;
    "clean")
        echo "🧹 Limpando containers e imagens..."
        docker-compose down -v
        docker system prune -f
        ;;
    "logs")
        echo "📋 Mostrando logs..."
        docker-compose logs -f
        ;;
    "status")
        echo "📊 Status dos containers:"
        docker-compose ps
        ;;
    "shell")
        echo "🐚 Abrindo shell no container de desenvolvimento..."
        docker exec -it rossmann-dashboard-dev bash
        ;;
    *)
        echo "Usage: $0 {dev|prod|build|stop|clean|logs|status|shell}"
        echo ""
        echo "Comandos:"
        echo "  dev    - Modo desenvolvimento"
        echo "  prod   - Modo produção" 
        echo "  build  - Buildar imagens"
        echo "  stop   - Parar containers"
        echo "  clean  - Limpar tudo"
        echo "  logs   - Ver logs"
        echo "  status - Status containers"
        echo "  shell  - Shell no container"
        exit 1
        ;;
esac
