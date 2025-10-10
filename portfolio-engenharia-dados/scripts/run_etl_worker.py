#!/usr/bin/env python3
"""
run_etl_worker.py - Worker ETL para Neon
"""
import asyncio
import asyncpg
import os
from datetime import datetime

async def etl_worker():
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL não encontrada")
        return
    
    try:
        conn = await asyncpg.connect(database_url)
        print("🚀 ETL Worker iniciado")
        
        while True:
            # Simular trabalho ETL
            job_id = await conn.fetchval('''
                INSERT INTO etl_jobs (job_name, status) 
                VALUES ($1, $2) RETURNING id
            ''', 'data_sync', 'completed')
            
            print(f"✅ Job {job_id} processado")
            await asyncio.sleep(300)  # 5 minutos
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    asyncio.run(etl_worker())
