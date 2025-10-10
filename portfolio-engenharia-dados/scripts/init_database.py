#!/usr/bin/env python3
"""
init_database.py - Inicialização robusta do banco Neon
"""
import os
import asyncpg
import asyncio
import sys

async def initialize_database():
    """Initialize all required tables in Neon"""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL não encontrada")
        return False
    
    try:
        print("🔗 Conectando ao Neon PostgreSQL...")
        conn = await asyncpg.connect(database_url)
        
        # Criar tabela projects
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id SERIAL PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                technology_stack TEXT[],
                github_url VARCHAR(300),
                live_demo_url VARCHAR(300),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        ''')
        print("✅ Tabela 'projects' criada/verificada")
        
        # Criar tabela etl_jobs
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS etl_jobs (
                id SERIAL PRIMARY KEY,
                job_name VARCHAR(100) NOT NULL,
                status VARCHAR(50) NOT NULL,
                records_processed INTEGER,
                start_time TIMESTAMP DEFAULT NOW(),
                end_time TIMESTAMP,
                error_message TEXT
            )
        ''')
        print("✅ Tabela 'etl_jobs' criada/verificada")
        
        # Criar tabela sales_data (a que está faltando)
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS sales_data (
                id SERIAL PRIMARY KEY,
                product_name VARCHAR(100),
                category VARCHAR(50),
                quantity INTEGER,
                price DECIMAL(10,2),
                sale_date DATE,
                region VARCHAR(50),
                created_at TIMESTAMP DEFAULT NOW()
            )
        ''')
        print("✅ Tabela 'sales_data' criada/verificada")
        
        # Inserir dados de exemplo em projects
        await conn.execute('''
            INSERT INTO projects (name, description, technology_stack, github_url, live_demo_url)
            VALUES 
            ('Pipeline ETL Completo', 'Pipeline de dados com extração, transformação e carga', 
            '{"Python", "PostgreSQL", "FastAPI", "Docker"}', 
            'https://github.com/cabicho/portfolio_projectos', 
            'https://portfolio-engenharia-api-42tz.onrender.com'),
            
            ('Data Warehouse Cloud', 'Armazém de dados na nuvem com modelagem dimensional', 
            '{"PostgreSQL", "dbt", "SQL", "Neon"}', 
            'https://github.com/cabicho/portfolio_projectos', 
            'https://portfolio-engenharia-api-42tz.onrender.com')
            ON CONFLICT DO NOTHING
        ''')
        print("✅ Dados de exemplo inseridos em 'projects'")
        
        # Inserir alguns jobs ETL de exemplo
        await conn.execute('''
            INSERT INTO etl_jobs (job_name, status, records_processed)
            VALUES 
            ('initial_load', 'completed', 150),
            ('daily_sync', 'completed', 45),
            ('data_validation', 'completed', 200)
            ON CONFLICT DO NOTHING
        ''')
        print("✅ Jobs ETL de exemplo inseridos")
        
        # Verificar tabelas criadas
        tables = await conn.fetch('''
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        ''')
        
        print("📋 Tabelas no banco de dados:")
        for table in tables:
            print(f"   - {table['table_name']}")
        
        await conn.close()
        print("🎉 Banco de dados inicializado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao inicializar banco: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando inicialização do banco de dados...")
    success = asyncio.run(initialize_database())
    if success:
        print("💫 Banco de dados pronto para uso!")
        sys.exit(0)
    else:
        print("💥 Falha na inicialização do banco")
        sys.exit(1)
