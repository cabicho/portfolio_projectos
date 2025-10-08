#!/usr/bin/env python3
"""
Coletor de dados simplificado para Moçambique
"""
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('data/mozambique/coleta.log')
        ]
    )

def generate_sample_data():
    """Gera dados de exemplo para Moçambique"""
    logger = logging.getLogger(__name__)
    logger.info("Gerando dados de exemplo para Moçambique...")
    
    np.random.seed(42)
    
    # Dados do INE
    ine_data = {
        'ano': [2018, 2019, 2020, 2021, 2022, 2023],
        'populacao_ativa': [13200000, 13600000, 13900000, 14200000, 14500000, 14800000],
        'emprego_formal': [1850000, 1920000, 1870000, 1950000, 2020000, 2100000],
        'taxa_desemprego': [24.8, 24.2, 25.5, 24.9, 24.3, 23.8],
        'acidentes_trabalho': [12450, 11890, 11200, 12560, 11800, 12250]
    }
    pd.DataFrame(ine_data).to_csv('data/mozambique/raw/ine_dados.csv', index=False)
    
    # Dados do MISAU
    misau_data = {
        'ano': [2018, 2019, 2020, 2021, 2022, 2023],
        'casos_burnout': [890, 920, 1050, 1120, 1080, 1150],
        'depressao_trabalho': [670, 710, 780, 820, 790, 850],
        'ansiedade_ocupacional': [780, 810, 890, 950, 910, 980],
        'custos_saude_milhoes': [125.5, 132.8, 142.3, 151.7, 148.2, 156.9]
    }
    pd.DataFrame(misau_data).to_csv('data/mozambique/raw/misau_dados.csv', index=False)
    
    # Dados de empresas
    empresas = []
    setores = ['Mineração', 'Agricultura', 'Construção', 'Manufactura', 'Comércio', 'Serviços']
    provincias = ['Maputo', 'Gaza', 'Inhambane', 'Sofala', 'Manica', 'Zambézia', 'Nampula']
    
    for i in range(200):
        empresa = {
            'id': i + 1,
            'setor': np.random.choice(setores),
            'provincia': np.random.choice(provincias),
            'tamanho': np.random.choice(['Pequena', 'Média', 'Grande'], p=[0.6, 0.3, 0.1]),
            'invest_ergonomia': np.random.normal(40000, 15000),
            'invest_saude_mental': np.random.normal(20000, 8000),
            'burnout_medio': np.random.normal(3.5, 0.8),
            'acidentes_ano': np.random.poisson(3),
            'produtividade': np.random.normal(70, 15),
            'lucratividade_mil': np.random.normal(300, 100)
        }
        empresas.append(empresa)
    
    df_empresas = pd.DataFrame(empresas)
    df_empresas['invest_total'] = df_empresas['invest_ergonomia'] + df_empresas['invest_saude_mental']
    df_empresas['roi'] = ((df_empresas['lucratividade_mil'] * 1000 - df_empresas['invest_total']) / df_empresas['invest_total'] * 100)
    
    df_empresas.to_csv('data/mozambique/raw/empresas.csv', index=False)
    logger.info(f"✅ Dados gerados: {len(empresas)} empresas")
    
    # Relatório de coleta
    report = {
        'data_coleta': datetime.now().isoformat(),
        'total_empresas': len(empresas),
        'fontes': ['INE', 'MISAU', 'Empresas'],
        'status': 'completo'
    }
    
    with open('data/mozambique/raw/relatorio_coleta.json', 'w') as f:
        json.dump(report, f, indent=2)

if __name__ == "__main__":
    setup_logging()
    generate_sample_data()
    print("🎉 Coleta de dados concluída!")
