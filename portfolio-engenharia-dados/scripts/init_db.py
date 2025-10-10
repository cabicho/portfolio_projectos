#!/usr/bin/env python3
"""
init_db.py - Inicialização do Neon PostgreSQL
Repositório: https://github.com/cabicho/portfolio_projectos
"""
import os
import sys
import asyncio

try:
    import asyncpg
    print("✅ asyncpg importado com sucesso")
except ImportError as e:
    print(f"❌ Erro importando asyncpg: {e}")
    sys.exit(1)

async def init_neon_database():
    """Initialize Neon database"""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL não encontrada")
        return False
    
    try:
        print("🔗 Conectando ao Neon PostgreSQL...")
        conn = await asyncpg.connect(database_url)
        
        # Create tables
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id SERIAL PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                technology_stack TEXT[],
                github_url VARCHAR(300),
                created_at TIMESTAMP DEFAULT NOW()
            )
        ''')
        
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS etl_jobs (
                id SERIAL PRIMARY KEY,
                job_name VARCHAR(100) NOT NULL,
                status VARCHAR(50) NOT NULL,
                start_time TIMESTAMP DEFAULT NOW(),
                end_time TIMESTAMP
            )
        ''')
        
        print("✅ Tabelas criadas com sucesso!")
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(init_neon_database())
    sys.exit(0 if success else 1)
