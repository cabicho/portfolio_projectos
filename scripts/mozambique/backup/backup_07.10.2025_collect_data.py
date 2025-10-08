#!/usr/bin/env python3
import pandas as pd
import numpy as np
import json
from datetime import datetime

print("📊 Gerando dados de exemplo para Moçambique...")

# Dados simples
np.random.seed(42)

# Empresas
empresas = []
for i in range(100):
    empresas.append({
        'id': i+1,
        'setor': np.random.choice(['Mineração', 'Agricultura', 'Construção', 'Comércio']),
        'provincia': np.random.choice(['Maputo', 'Gaza', 'Nampula']),
        'invest_ergonomia': np.random.normal(50000, 15000),
        'invest_saude_mental': np.random.normal(25000, 8000),
        'burnout': np.random.normal(3.5, 0.8),
        'acidentes': np.random.poisson(3),
        'produtividade': np.random.normal(70, 15),
        'lucro': np.random.normal(300000, 100000)
    })

df = pd.DataFrame(empresas)
df['roi'] = ((df['lucro'] - df['invest_ergonomia'] - df['invest_saude_mental']) / 
             (df['invest_ergonomia'] + df['invest_saude_mental']) * 100)
df.to_csv('data/mozambique/raw/empresas.csv', index=False)

print(f"✅ {len(empresas)} empresas criadas")
