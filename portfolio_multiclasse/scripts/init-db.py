# scripts/init-db.py
import pandas as pd
import numpy as np
import os

def generate_sample_data():
    """Gera dados de exemplo para o banco"""
    np.random.seed(42)
    n_samples = 500
    
    data = pd.DataFrame({
        'id': range(1, n_samples + 1),
        'segmento': np.random.choice(['B2B Enterprise', 'SMB', 'Consumer', 'Emerging'], n_samples),
        'valor_estimado': np.random.lognormal(10, 1, n_samples),
        'crescimento_projetado': np.random.uniform(5, 25, n_samples),
        'roi_esperado': np.random.uniform(8, 35, n_samples),
        'potencial_mercado': np.random.uniform(1, 10, n_samples),
        'tamanho_oportunidade': np.random.uniform(10000, 500000, n_samples),
        'data_criacao': pd.date_range('2023-01-01', periods=n_samples, freq='H')
    })
    
    # Classificação multiclasse
    conditions = [
        (data['roi_esperado'] > 25) & (data['crescimento_projetado'] > 15),
        (data['roi_esperado'] > 20) & (data['crescimento_projetado'] > 10),
        (data['roi_esperado'] > 15),
        (data['roi_esperado'] <= 15)
    ]
    
    choices = [
        'Oportunidade Estratégica',
        'Crescimento Acelerado', 
        'Manutenção Eficiente',
        'Otimização de Custos'
    ]
    
    data['classe_predita'] = np.select(conditions, choices, default='Otimização de Custos')
    
    return data

if __name__ == "__main__":
    # Salvar dados de exemplo
    sample_data = generate_sample_data()
    os.makedirs('../data', exist_ok=True)
    sample_data.to_csv('../data/sample_data.csv', index=False)
    print("✅ Dados de exemplo gerados em data/sample_data.csv")