import asyncpg
import os
import asyncio
from datetime import datetime

async def demonstrate_data_warehouse():
    """Demonstrar capacidades do Data Warehouse"""
    database_url = os.getenv("DATABASE_URL")
    conn = await asyncpg.connect(database_url)
    
    print("📊 DEMONSTRANDO CAPACIDADES DO DATA WAREHOUSE")
    print("=" * 50)
    
    # 1. Modelagem Dimensional
    print("1. 📐 MODELAGEM DIMENSIONAL")
    tables = await conn.fetch('''
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    ''')
    
    print("   Tabelas no Data Warehouse:")
    for table in tables:
        count = await conn.fetchval(f"SELECT COUNT(*) FROM {table['table_name']}")
        print(f"   - {table['table_name']}: {count} registros")
    
    # 2. Consultas Analíticas
    print("\n2. 🔍 CONSULTAS ANALÍTICAS")
    
    # Vendas por região
    vendas_regiao = await conn.fetch('''
        SELECT regiao, SUM(valor_total) as total_vendas, COUNT(*) as num_vendas
        FROM vendas 
        GROUP BY regiao 
        ORDER BY total_vendas DESC
    ''')
    
    print("   📈 Vendas por Região:")
    for venda in vendas_regiao:
        print(f"   - {venda['regiao']}: R$ {venda['total_vendas']:,.2f} ({venda['num_vendas']} vendas)")
    
    # 3. Performance de Pipelines
    print("\n3. ⚙️ PERFORMANCE DE PIPELINES ETL")
    pipelines = await conn.fetch('''
        SELECT nome_pipeline, status, registros_processados, ultima_execucao
        FROM pipelines_etl 
        ORDER BY ultima_execucao DESC
    ''')
    
    for pipeline in pipelines:
        print(f"   - {pipeline['nome_pipeline']}: {pipeline['status']} ({pipeline['registros_processados']} registros)")
    
    # 4. Requisitos de Negócio
    print("\n4. 💼 GESTÃO DE REQUISITOS DE NEGÓCIO")
    requisitos = await conn.fetch('''
        SELECT unidade_negocio, descricao, prioridade, status
        FROM requisitos_negocio 
        ORDER BY prioridade DESC
    ''')
    
    for req in requisitos:
        print(f"   - {req['unidade_negocio']} ({req['prioridade']}): {req['descricao'][:50]}...")
    
    await conn.close()
    print("\n✅ Demonstração do Data Warehouse concluída!")

if __name__ == "__main__":
    asyncio.run(demonstrate_data_warehouse())
