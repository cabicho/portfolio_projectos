import os
import asyncio
import asyncpg
from datetime import datetime

async def populate_data_warehouse():
    """Popula o data warehouse com dados iniciais"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL não encontrada")
        return
    
    try:
        conn = await asyncpg.connect(database_url)
        
        await conn.execute('''
            INSERT INTO occupational_diseases 
            (ano, doencas_respiratorias, lesoes_musculoesqueleticas, perda_auditiva, 
             doencas_pele, intoxicacoes_quimicas, setor_agricultura, setor_construcao,
             setor_industria, setor_minas, fonte)
            VALUES 
            (2020, 1250, 890, 340, 210, 95, 650, 420, 580, 180, 'INS Moçambique'),
            (2021, 1320, 920, 360, 230, 105, 680, 450, 610, 190, 'INS Moçambique'),
            (2022, 1400, 950, 380, 250, 115, 710, 480, 640, 200, 'INS Moçambique'),
            (2023, 1480, 980, 400, 270, 125, 740, 510, 670, 210, 'INS Moçambique')
            ON CONFLICT (ano) DO NOTHING
        ''')
        
        await conn.execute('''
            INSERT INTO risk_assessment 
            (provincia, score_risco, nivel_risco, populacao_exposta, principal_exposicao)
            VALUES 
            ('Maputo', 45.6, 'Médio', 125000, 'Particulas'),
            ('Gaza', 38.2, 'Médio', 89000, 'Particulas'),
            ('Inhambane', 32.1, 'Baixo', 67000, 'Particulas'),
            ('Sofala', 41.3, 'Médio', 95000, 'Particulas'),
            ('Manica', 36.7, 'Médio', 78000, 'Particulas'),
            ('Tete', 39.8, 'Médio', 82000, 'Particulas'),
            ('Zambézia', 34.5, 'Baixo', 105000, 'Particulas'),
            ('Nampula', 37.9, 'Médio', 115000, 'Particulas'),
            ('Cabo Delgado', 35.2, 'Médio', 92000, 'Particulas'),
            ('Niassa', 31.8, 'Baixo', 58000, 'Particulas')
            ON CONFLICT (provincia) DO NOTHING
        ''')
        
        print("✅ Data warehouse populado com sucesso")
        await conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao popular data warehouse: {e}")

if __name__ == "__main__":
    asyncio.run(populate_data_warehouse())
