import pandas as pd
import numpy as np
from typing import Dict, List

class DataTransformer:
    """Classe para limpeza e transformação de dados"""
    
    def __init__(self):
        self.quality_metrics = {}
    
    def clean_occupational_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpa dados ocupacionais"""
        if df.empty:
            return df
        
        # Remover duplicatas
        df_clean = df.drop_duplicates()
        
        # Tratar valores missing
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        df_clean[numeric_cols] = df_clean[numeric_cols].fillna(0)
        
        # Normalizar nomes de colunas
        df_clean.columns = [col.lower().replace(' ', '_') for col in df_clean.columns]
        
        # Calcular métricas de qualidade
        self.quality_metrics['total_registros'] = len(df_clean)
        self.quality_metrics['registros_completos'] = len(df_clean.dropna())
        if self.quality_metrics['total_registros'] > 0:
            self.quality_metrics['taxa_completude'] = (
                self.quality_metrics['registros_completos'] / self.quality_metrics['total_registros']
            )
        else:
            self.quality_metrics['taxa_completude'] = 0
        
        return df_clean
    
    def calculate_health_indicators(self, diseases_df: pd.DataFrame, exposure_df: pd.DataFrame) -> Dict:
        """Calcula indicadores de saúde combinados"""
        diseases_indicators = diseases_df.copy()
        
        # Calcular taxas (supondo população de referência)
        populacao_referencia = 1000000
        
        for col in diseases_indicators.select_dtypes(include=[np.number]).columns:
            if col != 'ano' and not col.startswith('setor_'):
                diseases_indicators[f'taxa_{col}'] = (
                    diseases_indicators[col] / populacao_referencia * 100000
                )
        
        # Transformar dados de exposição
        exposure_melted = exposure_df.melt(
            id_vars=['provincia', 'fonte'],
            value_vars=['exposicao_particulas', 'exposicao_quimicos', 'temperatura_extrema', 'ruido_ocupacional'],
            var_name='tipo_exposicao',
            value_name='nivel_exposicao'
        )
        
        return {
            'doencas_indicadores': diseases_indicators,
            'exposicao_long': exposure_melted
        }
    
    def create_risk_assessment(self, diseases_df: pd.DataFrame, exposure_df: pd.DataFrame) -> pd.DataFrame:
        """Cria avaliação de risco combinada"""
        risk_data = []
        
        for _, province_row in exposure_df.iterrows():
            provincia = province_row['provincia']
            
            # Score de risco ponderado
            risk_score = (
                province_row['exposicao_particulas'] * 0.3 +
                province_row['exposicao_quimicos'] * 0.3 +
                province_row['temperatura_extrema'] * 0.2 +
                province_row['ruido_ocupacional'] * 0.2
            )
            
            # Classificar risco
            if risk_score > 50:
                risk_level = 'Alto'
            elif risk_score > 30:
                risk_level = 'Médio'
            else:
                risk_level = 'Baixo'
            
            risk_data.append({
                'provincia': provincia,
                'score_risco': round(risk_score, 2),
                'nivel_risco': risk_level,
                'populacao_exposta': province_row['populacao_exposta'],
                'principal_exposicao': self.get_principal_exposure(province_row)
            })
        
        return pd.DataFrame(risk_data)
    
    def get_principal_exposure(self, province_row: pd.Series) -> str:
        """Identifica a principal exposição"""
        exposures = {
            'exposicao_particulas': province_row['exposicao_particulas'],
            'exposicao_quimicos': province_row['exposicao_quimicos'],
            'temperatura_extrema': province_row['temperatura_extrema'],
            'ruido_ocupacional': province_row['ruido_ocupacional']
        }
        
        principal = max(exposures, key=exposures.get)
        return principal.replace('exposicao_', '').replace('_', ' ').title()
