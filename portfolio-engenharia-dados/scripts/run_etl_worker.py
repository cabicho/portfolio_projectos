#!/usr/bin/env python3
"""
run_etl_worker.py
Worker para processamento ETL no Neon Ohio
"""

import asyncio
import asyncpg
import os
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def etl_worker():
    """Main ETL worker function"""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        logger.error("DATABASE_URL not found")
        return
    
    try:
        conn = await asyncpg.connect(database_url)
        logger.info("🚀 ETL Worker iniciado para Neon Ohio")
        
        while True:
            # Simular processamento ETL
            await process_daily_data(conn)
            
            # Aguardar próximo ciclo (1 hora)
            await asyncio.sleep(3600)
            
    except Exception as e:
        logger.error(f"ETL Worker error: {e}")

async def process_daily_data(conn):
    """Process daily ETL data"""
    try:
        # Registrar início do job
        job_id = await conn.fetchval('''
            INSERT INTO etl_jobs (job_name, status, start_time)
            VALUES ($1, $2, $3) RETURNING id
        ''', 'daily_data_sync', 'running', datetime.now())
        
        # Dados de exemplo para ETL
        sample_data = [
            ('Laptop Dell', 'Electronics', 3, 1200.00, '2024-01-21', 'North'),
            ('Mouse Wireless', 'Electronics', 15, 45.99, '2024-01-21', 'South'),
            ('Notebook', 'Office', 30, 5.99, '2024-01-20', 'East'),
            ('Pen Set', 'Office', 50, 12.99, '2024-01-20', 'West')
        ]
        
        # Inserir dados
        for product in sample_data:
            await conn.execute('''
                INSERT INTO sales_data (product_name, category, quantity, price, sale_date, region)
                VALUES ($1, $2, $3, $4, $5, $6)
            ''', *product)
        
        # Atualizar status do job
        await conn.execute('''
            UPDATE etl_jobs 
            SET status = $1, records_processed = $2, end_time = $3
            WHERE id = $4
        ''', 'completed', len(sample_data), datetime.now(), job_id)
        
        logger.info(f"✅ ETL processado: {len(sample_data)} registros")
        
    except Exception as e:
        logger.error(f"❌ Erro no ETL: {e}")

if __name__ == "__main__":
    asyncio.run(etl_worker())
