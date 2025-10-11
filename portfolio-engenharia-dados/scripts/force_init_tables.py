#!/usr/bin/env python3
"""
force_init_tables.py - Força a criação de todas as tabelas
"""
import os
import asyncpg
import asyncio
import sys

async def force_create_tables():
    """Força a criação de todas as tabelas necessárias"""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL não encontrada")
        return False
    
    try:
        print("🔗 Conectando ao Neon PostgreSQL...")
        conn = await asyncpg.connect(database_url)
        
        # DROP e CREATE da tabela sales_data (forçar recriação)
        print("🗑️ Recriando tabela sales_data...")
        await conn.execute('DROP TABLE IF EXISTS sales_data CASCADE')
        
        await conn.execute('''
            CREATE TABLE sales_data (
                id SERIAL PRIMARY KEY,
                product_name VARCHAR(100) NOT NULL,
                category VARCHAR(50) NOT NULL,
                quantity INTEGER NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                sale_date DATE NOT NULL,
                region VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
        ''')
        print("✅ Tabela 'sales_data' criada com sucesso!")
        
        # Inserir dados de exemplo em sales_data
        print("📥 Inserindo dados de exemplo em sales_data...")
        sample_sales = [
            ('Laptop Dell XPS', 'Electronics', 2, 1299.99, '2024-10-10', 'North'),
            ('Mouse Logitech', 'Electronics', 15, 45.50, '2024-10-10', 'South'),
            ('Notebook A4', 'Office', 25, 5.99, '2024-10-09', 'East'),
            ('Pen Set Premium', 'Office', 40, 15.99, '2024-10-09', 'West'),
            ('Monitor 27"', 'Electronics', 3, 299.99, '2024-10-10', 'North'),
            ('Keyboard Mechanical', 'Electronics', 8, 89.99, '2024-10-09', 'South'),
            ('Desk Organizer', 'Office', 12, 24.99, '2024-10-08', 'East'),
            ('Webcam HD', 'Electronics', 5, 79.99, '2024-10-08', 'West')
        ]
        
        for product in sample_sales:
            await conn.execute('''
                INSERT INTO sales_data (product_name, category, quantity, price, sale_date, region)
                VALUES ($1, $2, $3, $4, $5, $6)
            ''', *product)
        
        print(f"✅ {len(sample_sales)} registros inseridos em sales_data")
        
        # Garantir que outras tabelas existam
        print("🔧 Verificando outras tabelas...")
        
        # Tabela projects
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
        
        # Inserir projetos se a tabela estiver vazia
        projects_count = await conn.fetchval("SELECT COUNT(*) FROM projects")
        if projects_count == 0:
            await conn.execute('''
                INSERT INTO projects (name, description, technology_stack, github_url, live_demo_url)
                VALUES 
                ('Pipeline ETL Avançado', 'Sistema completo de engenharia de dados com ETL, Data Warehouse e BI', 
                '{"Python", "FastAPI", "PostgreSQL", "Neon", "Render"}', 
                'https://github.com/cabicho/portfolio_projectos', 
                'https://portfolio-engenharia-api-42tz.onrender.com'),
                
                ('Data Warehouse Cloud', 'Armazém de dados dimensional na nuvem', 
                '{"PostgreSQL", "SQL", "dbt", "Data Modeling"}', 
                'https://github.com/cabicho/portfolio_projectos', 
                'https://portfolio-engenharia-api-42tz.onrender.com')
            ''')
            print("✅ Projetos de exemplo inseridos")
        
        # Tabela etl_jobs
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
        
        # Verificar todas as tabelas
        tables = await conn.fetch('''
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        ''')
        
        print("📋 Tabelas existentes no banco:")
        for table in tables:
            count = await conn.fetchval(f"SELECT COUNT(*) FROM {table['table_name']}")
            print(f"   - {table['table_name']}: {count} registros")
        
        await conn.close()
        print("🎉 Todas as tabelas foram criadas/verificadas com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao forçar criação das tabelas: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Forçando criação de todas as tabelas...")
    success = asyncio.run(force_create_tables())
    if success:
        print("💫 Banco de dados totalmente inicializado!")
        sys.exit(0)
    else:
        print("💥 Falha na inicialização forçada")
        sys.exit(1)
