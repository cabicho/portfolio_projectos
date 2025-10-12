import os
import asyncpg
import asyncio

async def init_database():
    """Inicializa o banco de dados no Render"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL não encontrada")
        return
    
    try:
        conn = await asyncpg.connect(database_url)
        
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS who_data (
                id SERIAL PRIMARY KEY,
                indicador VARCHAR(255),
                ano INTEGER,
                valor DECIMAL,
                categoria VARCHAR(100),
                fonte VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(indicador, ano, categoria)
            )
        ''')
        
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS occupational_diseases (
                id SERIAL PRIMARY KEY,
                ano INTEGER UNIQUE,
                doencas_respiratorias INTEGER,
                lesoes_musculoesqueleticas INTEGER,
                perda_auditiva INTEGER,
                doencas_pele INTEGER,
                intoxicacoes_quimicas INTEGER,
                setor_agricultura INTEGER,
                setor_construcao INTEGER,
                setor_industria INTEGER,
                setor_minas INTEGER,
                fonte VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS risk_assessment (
                id SERIAL PRIMARY KEY,
                provincia VARCHAR(100) UNIQUE,
                score_risco DECIMAL,
                nivel_risco VARCHAR(50),
                populacao_exposta INTEGER,
                principal_exposicao VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        print("✅ Tabelas criadas/verificadas com sucesso")
        await conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao inicializar banco: {e}")

if __name__ == "__main__":
    asyncio.run(init_database())
