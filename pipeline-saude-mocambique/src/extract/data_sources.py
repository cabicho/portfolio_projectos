import pandas as pd
import requests
import json
from typing import Dict, List, Optional
import os
from datetime import datetime

class MozambiqueDataExtractor:
    """
    Extrator de dados públicos de saúde e trabalho de Moçambique
    """
    
    def __init__(self):
        self.sources = {
            'who': 'https://ghoapi.azureedge.net/api/',
            'world_bank': 'http://api.worldbank.org/v2/country/MZ/',
        }
    
    def extract_who_data(self) -> pd.DataFrame:
        """Extrai dados da OMS para Moçambique"""
        try:
            indicators = [
                'SA_0000001400',  # Exposição a riscos ocupacionais
                'SA_0000001401',  # Exposição a longas horas de trabalho
                'SA_0000001402',  # Exposição a riscos ergonômicos
                'SH_STA_TB08',    # Tuberculose ocupacional
                'SA_0000001403',  # Exposição a riscos químicos
            ]
            
            all_data = []
            for indicator in indicators:
                url = f"{self.sources['who']}{indicator}"
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get('value', []):
                        if item.get('SpatialDim') == 'MOZ':
                            all_data.append({
                                'indicador': indicator,
                                'ano': item.get('TimeDim'),
                                'valor': item.get('NumericValue'),
                                'categoria': item.get('Dim1', 'Total'),
                                'fonte': 'OMS'
                            })
            
            return pd.DataFrame(all_data)
            
        except Exception as e:
            print(f"Erro ao extrair dados OMS: {e}")
            return pd.DataFrame()
    
    def extract_occupational_diseases(self) -> pd.DataFrame:
        """Extrai dados simulados de doenças ocupacionais"""
        diseases_data = {
            'ano': [2020, 2021, 2022, 2023],
            'doencas_respiratorias': [1250, 1320, 1400, 1480],
            'lesoes_musculoesqueleticas': [890, 920, 950, 980],
            'perda_auditiva': [340, 360, 380, 400],
            'doencas_pele': [210, 230, 250, 270],
            'intoxicacoes_quimicas': [95, 105, 115, 125],
            'setor_agricultura': [650, 680, 710, 740],
            'setor_construcao': [420, 450, 480, 510],
            'setor_industria': [580, 610, 640, 670],
            'setor_minas': [180, 190, 200, 210],
        }
        
        df = pd.DataFrame(diseases_data)
        df['fonte'] = 'INS Moçambique (Dados Simulados)'
        return df
    
    def extract_environmental_exposure(self) -> pd.DataFrame:
        """Extrai dados de exposição ambiental"""
        exposure_data = {
            'provincia': ['Maputo', 'Gaza', 'Inhambane', 'Sofala', 'Manica', 'Tete', 'Zambézia', 'Nampula', 'Cabo Delgado', 'Niassa'],
            'exposicao_particulas': [45.6, 38.2, 32.1, 41.3, 36.7, 39.8, 34.5, 37.9, 35.2, 31.8],
            'exposicao_quimicos': [28.7, 25.3, 22.1, 26.9, 24.5, 27.1, 23.8, 25.9, 24.2, 21.7],
            'temperatura_extrema': [15.2, 18.7, 16.3, 14.8, 17.1, 19.5, 16.8, 15.9, 17.3, 16.1],
            'ruido_ocupacional': [62.3, 58.7, 55.4, 60.1, 57.8, 59.6, 56.3, 58.9, 57.1, 54.8],
            'populacao_exposta': [125000, 89000, 67000, 95000, 78000, 82000, 105000, 115000, 92000, 58000],
        }
        
        df = pd.DataFrame(exposure_data)
        df['fonte'] = 'INE Moçambique (Dados Simulados)'
        return df
