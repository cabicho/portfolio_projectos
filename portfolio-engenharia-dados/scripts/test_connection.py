#!/usr/bin/env python3
"""
test_connection.py
Testa a conexão com o Neon PostgreSQL na região Ohio
"""

import os
import asyncpg
import asyncio
import sys

async def test_neon_connection():
    """Test connection to Neon PostgreSQL"""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL não encontrada nas variáveis de ambiente")
        print("💡 Configure no Render.com: Settings -> Environment Variables")
        return False
    
    try:
        print("🔗 Conectando ao Neon PostgreSQL (Ohio)...")
        conn = await asyncpg.connect(database_url)
        
        # Test basic queries
        version = await conn.fetchval('SELECT version()')
        print(f"✅ Conectado com sucesso!")
        print(f"📊 PostgreSQL: {version.split(',')[0]}")
        
        # Check tables
        tables = await conn.fetch('''
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        ''')
        
        print(f"📋 Tabelas existentes: {len(tables)}")
        for table in tables:
            print(f"   - {table['table_name']}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_neon_connection())
    sys.exit(0 if success else 1)
