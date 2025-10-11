import os
import asyncpg
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL do banco a partir de variável de ambiente
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError("DATABASE_URL não encontrada nas variáveis de ambiente")

# Configuração SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Configuração asyncpg - CORREÇÃO AQUI
async def get_async_connection():
    """Conexão assíncrona com o banco"""
    # REMOVER o '+asyncpg' da string de conexão
    async_conn_string = DATABASE_URL.replace('postgresql://', 'postgresql://')
    return await asyncpg.connect(async_conn_string)

async def create_tables():
    """Cria as tabelas no banco de dados"""
    conn = await get_async_connection()
    try:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS who_data (
                id SERIAL PRIMARY KEY,
                indicador VARCHAR(255),
                ano INTEGER,
                valor DECIMAL,
                categoria VARCHAR(100),
                fonte VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS occupational_diseases (
                id SERIAL PRIMARY KEY,
                ano INTEGER,
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
                provincia VARCHAR(100),
                score_risco DECIMAL,
                nivel_risco VARCHAR(50),
                populacao_exposta INTEGER,
                principal_exposicao VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        print("✅ Tabelas criadas/verificadas com sucesso")
        
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
    finally:
        await conn.close()