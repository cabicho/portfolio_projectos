#!/usr/bin/env python3
"""
Pipeline principal de coleta de dados SST Moçambique
"""

import pandas as pd
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Iniciando pipeline SST Moçambique")
    
    # Simular extração de dados
    ine_data = extract_ine_data()
    mitess_data = extract_mitess_data()
    ilo_data = extract_ilo_data()
    
    # Processar dados
    processed_data = process_data(ine_data, mitess_data, ilo_data)
    
    # Salvar dados
    save_data(processed_data)
    
    logger.info("Pipeline concluído com sucesso")

def extract_ine_data():
    """Extrair dados do INE"""
    logger.info("Extraindo dados do INE")
    
    # Dados simulados do INE
    data = {
        'ano': [2020, 2021, 2022, 2023, 2024],
        'provincia': ['Maputo Cidade'] * 5,
        'total_empresas': [14000, 14200, 14500, 14800, 15000],
        'total_trabalhadores': [420000, 426000, 435000, 444000, 450000]
    }
    
    return pd.DataFrame(data)

def extract_mitess_data():
    """Extrair dados do MITESS"""
    logger.info("Extraindo dados do MITESS")
    
    # Dados simulados do MITESS
    data = {
        'ano': [2020, 2021, 2022, 2023, 2024],
        'total_acidentes': [2200, 2300, 2400, 2450, 2500],
        'acidentes_fatais': [44, 46, 48, 49, 50],
        'dias_perdidos': [15400, 16100, 16800, 17150, 17500]
    }
    
    return pd.DataFrame(data)

def extract_ilo_data():
    """Extrair dados da OIT"""
    logger.info("Extraindo dados da OIT")
    
    # Dados simulados da OIT
    data = {
        'ano': [2020, 2021, 2022, 2023, 2024],
        'taxa_frequencia_global': [3.2, 3.1, 3.0, 3.0, 3.0],
        'taxa_frequencia_africa': [4.8, 4.7, 4.6, 4.5, 4.5],
        'fatalidades_global': [0.16, 0.15, 0.15, 0.15, 0.15]
    }
    
    return pd.DataFrame(data)

def process_data(ine_df, mitess_df, ilo_df):
    """Processar e consolidar dados"""
    logger.info("Processando dados")
    
    # Consolidar dados
    consolidated = ine_df.merge(mitess_df, on='ano', how='left')
    consolidated = consolidated.merge(ilo_df, on='ano', how='left')
    
    # Calcular métricas
    consolidated['taxa_acidentes_por_mil'] = (
        consolidated['total_acidentes'] / consolidated['total_trabalhadores'] * 1000
    )
    
    consolidated['taxa_fatalidade'] = (
        consolidated['acidentes_fatalis'] / consolidated['total_trabalhadores'] * 100000
    )
    
    return consolidated

def save_data(data):
    """Salvar dados processados"""
    logger.info("Salvando dados processados")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"/app/data_sources/processed/sst_data_{timestamp}.csv"
    
    data.to_csv(filename, index=False)
    logger.info(f"Dados salvos em: {filename}")

if __name__ == "__main__":
    main()
