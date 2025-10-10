#!/usr/bin/env python3
"""
init_db.py
Inicializa o banco de dados Neon PostgreSQL na região Ohio
"""

import asyncpg
import os
import asyncio
import sys

async def init_neon_database():
    """Initialize Neon database with portfolio tables"""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL não encontrada nas variáveis de ambiente")
        print("💡 Configure no Render.com: Settings -> Environment Variables")
        return False
    
    try:
        print("🔗 Conectando ao Neon PostgreSQL (Ohio)...")
        conn = await asyncpg.connect(database_url)
        
        # Create projects table
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
        
        # Create ETL jobs table
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
        
        # Create data tables for warehouse
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
        
        # Insert sample projects
        await conn.execute('''
            INSERT INTO projects (name, description, technology_stack, github_url, live_demo_url)
            VALUES 
            ('Data Pipeline ETL', 'Complete ETL pipeline with data validation', 
            '{"Python", "PostgreSQL", "Airflow", "Docker"}', 
            'https://github.com/cabicho/portfolio_projectos/tree/portfolio_engenharia_dados/portfolio-engenharia-dados', 
            'https://portfolio-engenharia-api.onrender.com'),
            
            ('Data Warehouse', 'Cloud data warehouse with dimension and fact tables', 
            '{"AWS Redshift", "dbt", "Snowflake", "SQL"}', 
            'https://github.com/cabicho/portfolio_projectos/tree/portfolio_engenharia_dados/portfolio-engenharia-dados', 
            'https://portfolio-engenharia-api.onrender.com')
            ON CONFLICT DO NOTHING
        ''')
        
        print("✅ Tabelas criadas com sucesso no Neon!")
        
        # Show created tables
        tables = await conn.fetch('''
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        ''')
        
        print(f"📋 Tabelas no banco: {len(tables)}")
        for table in tables:
            print(f"   - {table['table_name']}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao inicializar banco: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(init_neon_database())
    sys.exit(0 if success else 1)
