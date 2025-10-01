import time
import logging
import os
from datetime import datetime
import pandas as pd
import numpy as np

# Configuração
RENDER = os.getenv('RENDER', False)
GITHUB_REPO = os.getenv('GITHUB_REPO', 'https://github.com/cabicho/portfolio_projectos/tree/sst-dashboard/sst-dashboard-render')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_metrics_update():
    """Gera atualização de métricas para demonstração"""
    try:
        timestamp = datetime.now().isoformat()
        
        # Simular algumas métricas
        metrics = {
            'last_updated': timestamp,
            'active_alerts': np.random.randint(0, 5),
            'total_predictions': np.random.randint(100, 1000),
            'avg_turnover_rate': round(np.random.uniform(0.1, 0.2), 3),
            'avg_burnout_score': round(np.random.uniform(50, 70), 1),
            'system_status': 'healthy',
            'environment': 'production' if RENDER else 'development'
        }
        
        logger.info(f"📊 Métricas atualizadas - {timestamp}")
        logger.info(f"   Alertas ativos: {metrics['active_alerts']}")
        logger.info(f"   Total de predições: {metrics['total_predictions']}")
        
        return metrics
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar métricas: {e}")
        return {'error': str(e), 'last_updated': datetime.now().isoformat()}

def process_background_tasks():
    """Processa tarefas em background"""
    try:
        logger.info("🔄 Iniciando processamento de tarefas em background...")
        
        # 1. Atualizar métricas
        metrics = generate_metrics_update()
        
        # 2. Simular limpeza de dados temporários
        logger.info("🧹 Simulando limpeza de dados temporários...")
        
        # 3. Simular backup de métricas
        logger.info("💾 Simulando backup de métricas...")
        
        logger.info("✅ Tarefas em background concluídas")
        
        return metrics
        
    except Exception as e:
        logger.error(f"❌ Erro no processamento: {e}")
        return None

def main():
    """Loop principal do worker"""
    logger.info("🚀 Iniciando worker de background...")
    logger.info(f"📁 Repositório: {GITHUB_REPO}")
    logger.info(f"🌍 Ambiente: {'Production' if RENDER else 'Development'}")
    
    iteration = 0
    
    while True:
        try:
            iteration += 1
            logger.info(f"🔁 Iteração #{iteration} - {datetime.now().isoformat()}")
            
            # Processar tarefas
            result = process_background_tasks()
            
            if result and 'error' not in result:
                logger.info("✅ Ciclo de processamento concluído com sucesso")
            else:
                logger.warning("⚠️ Ciclo de processamento com avisos")
            
            # Intervalo baseado no ambiente
            sleep_interval = 300 if RENDER else 60  # 5min em prod, 1min em dev
            logger.info(f"⏰ Próxima execução em {sleep_interval} segundos...")
            time.sleep(sleep_interval)
            
        except KeyboardInterrupt:
            logger.info("🛑 Worker interrompido pelo usuário")
            break
        except Exception as e:
            logger.error(f"💥 Erro no loop principal: {e}")
            logger.info("⏰ Tentando novamente em 30 segundos...")
            time.sleep(30)

if __name__ == "__main__":
    main()
