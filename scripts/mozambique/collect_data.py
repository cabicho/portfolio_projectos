# scripts/mozambique/collect_data.py
#!/usr/bin/env python3
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

print("🇲🇿 Iniciando coleta de dados SSO Moçambique...")

# Garantir que diretórios existam
os.makedirs('data/mozambique/raw', exist_ok=True)
os.makedirs('data/mozambique/processed', exist_ok=True)
os.makedirs('data/mozambique/reports', exist_ok=True)

# Gerar dados de exemplo
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
setores = ['Mineração', 'Agricultura', 'Construção Civil', 'Manufactura', 'Comércio', 'Serviços', 'Transportes']
provincias = ['Maputo', 'Gaza', 'Inhambane', 'Sofala', 'Manica', 'Zambézia', 'Nampula', 'Cabo Delgado']

for i in range(200):
    setor = np.random.choice(setores)
    
    parametros = {
        'Mineração': {'risco': 8.0, 'burnout': 4.2, 'prod_base': 70},
        'Agricultura': {'risco': 7.0, 'burnout': 3.8, 'prod_base': 60},
        'Construção Civil': {'risco': 8.5, 'burnout': 4.1, 'prod_base': 65},
        'Manufactura': {'risco': 6.5, 'burnout': 3.9, 'prod_base': 75},
        'Comércio': {'risco': 4.0, 'burnout': 3.2, 'prod_base': 80},
        'Serviços': {'risco': 3.5, 'burnout': 3.5, 'prod_base': 85},
        'Transportes': {'risco': 7.5, 'burnout': 4.0, 'prod_base': 70}
    }
    
    param = parametros.get(setor, {'risco': 5.0, 'burnout': 3.5, 'prod_base': 70})
    
    empresa = {
        'empresa_id': i + 1,
        'setor': setor,
        'provincia': np.random.choice(provincias),
        'tamanho': np.random.choice(['Pequena', 'Média', 'Grande'], p=[0.6, 0.3, 0.1]),
        'invest_ergonomia': max(10000, np.random.normal(50000, 20000)),
        'invest_saude_mental': max(5000, np.random.normal(25000, 10000)),
        'burnout_medio': max(1, min(7, np.random.normal(param['burnout'], 0.6))),
        'acidentes_ano': max(0, np.random.poisson(param['risco'])),
        'produtividade': max(20, np.random.normal(param['prod_base'], 15)),
        'lucratividade_mil': max(50, np.random.normal(400, 150)),
        'turnover': max(5, np.random.normal(18, 6)),
        'satisfacao': max(1, min(10, np.random.normal(6.8, 1.3)))
    }
    empresas.append(empresa)

df_empresas = pd.DataFrame(empresas)
df_empresas['invest_total'] = df_empresas['invest_ergonomia'] + df_empresas['invest_saude_mental']
df_empresas['custo_acidentes'] = df_empresas['acidentes_ano'] * 7500
df_empresas['roi'] = ((df_empresas['lucratividade_mil'] * 1000 - df_empresas['custo_acidentes'] - df_empresas['invest_total']) / 
                     df_empresas['invest_total'] * 100)

df_empresas.to_csv('data/mozambique/raw/empresas.csv', index=False)

# Relatório de coleta
report = {
    'data_coleta': datetime.now().isoformat(),
    'total_empresas': len(df_empresas),
    'fontes': ['INE', 'MISAU', 'Empresas Simuladas'],
    'status': 'completo'
}

with open('data/mozambique/raw/relatorio_coleta.json', 'w') as f:
    json.dump(report, f, indent=2)

print(f"✅ Coleta concluída: {len(df_empresas)} empresas criadas")
print("📊 Dados salvos em data/mozambique/raw/")