import time
import logging
import os
from datetime import datetime
import redis
import pandas as pd
import numpy as np

# Configuração
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Conectar ao Redis
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'redis'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=0,
    decode_responses=True
)

def process_background_tasks():
    """Processa tarefas em background"""
    try:
        # Simular processamento de dados
        timestamp = datetime.now().isoformat()
        
        # Atualizar métricas no Redis para cache
        metrics = {
            'last_processed': timestamp,
            'total_predictions': int(redis_client.get('total_predictions') or 0),
            'active_alerts': np.random.randint(0, 10),
            'system_status': 'healthy'
        }
        
        for key, value in metrics.items():
            redis_client.set(f'dashboard:{key}', str(value))
        
        logger.info(f"Background task executada - {timestamp}")
        
    except Exception as e:
        logger.error(f"Erro no worker: {e}")

def main():
    """Loop principal do worker"""
    logger.info("Iniciando worker de background...")
    
    while True:
        try:
            process_background_tasks()
            time.sleep(60)  # Executar a cada 1 minuto
            
        except KeyboardInterrupt:
            logger.info("Worker interrompido pelo usuário")
            break
        except Exception as e:
            logger.error(f"Erro no loop principal: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()
