import pandas as pd
from config.database import get_async_connection
import os

class DatabaseLoader:
    """Carrega dados no PostgreSQL"""
    
    async def load_who_data(self, df: pd.DataFrame):
        """Carrega dados da OMS"""
        if df.empty:
            return
        
        conn = await get_async_connection()
        try:
            for _, row in df.iterrows():
                await conn.execute('''
                    INSERT INTO who_data (indicador, ano, valor, categoria, fonte)
                    VALUES ($1, $2, $3, $4, $5)
                ''', row['indicador'], row['ano'], row['valor'], row['categoria'], row['fonte'])
            
            print(f"✅ Dados OMS carregados: {len(df)} registros")
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados OMS: {e}")
        finally:
            await conn.close()
    
    async def load_occupational_diseases(self, df: pd.DataFrame):
        """Carrega dados de doenças ocupacionais"""
        if df.empty:
            return
        
        conn = await get_async_connection()
        try:
            for _, row in df.iterrows():
                await conn.execute('''
                    INSERT INTO occupational_diseases 
                    (ano, doencas_respiratorias, lesoes_musculoesqueleticas, perda_auditiva, 
                     doencas_pele, intoxicacoes_quimicas, setor_agricultura, setor_construcao,
                     setor_industria, setor_minas, fonte)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                ''', row['ano'], row['doencas_respiratorias'], row['lesoes_musculoesqueleticas'],
                   row['perda_auditiva'], row['doencas_pele'], row['intoxicacoes_quimicas'],
                   row['setor_agricultura'], row['setor_construcao'], row['setor_industria'],
                   row['setor_minas'], row['fonte'])
            
            print(f"✅ Dados doenças ocupacionais carregados: {len(df)} registros")
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados doenças: {e}")
        finally:
            await conn.close()
    
    async def load_risk_assessment(self, df: pd.DataFrame):
        """Carrega avaliação de risco"""
        if df.empty:
            return
        
        conn = await get_async_connection()
        try:
            # Limpar dados antigos
            await conn.execute('DELETE FROM risk_assessment')
            
            for _, row in df.iterrows():
                await conn.execute('''
                    INSERT INTO risk_assessment 
                    (provincia, score_risco, nivel_risco, populacao_exposta, principal_exposicao)
                    VALUES ($1, $2, $3, $4, $5)
                ''', row['provincia'], row['score_risco'], row['nivel_risco'], 
                   row['populacao_exposta'], row['principal_exposicao'])
            
            print(f"✅ Avaliação de risco carregada: {len(df)} registros")
            
        except Exception as e:
            print(f"❌ Erro ao carregar avaliação de risco: {e}")
        finally:
            await conn.close()
