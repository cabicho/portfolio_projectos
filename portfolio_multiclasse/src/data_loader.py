import pandas as pd
import numpy as np
import requests
from io import StringIO

class DataLoader:
    def __init__(self):
        self.sample_data = None
    
    def load_public_data(self):
        """Carrega dados públicos para demonstração"""
        try:
            # Dataset sample gerado
            data = self.generate_sample_data()
            
            # Adicionar features estratégicas
            data = self.enrich_data(data)
            return data
            
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            return self.generate_sample_data()
    
    def generate_sample_data(self):
        """Gera dados de sample para demonstração"""
        np.random.seed(42)
        n_samples = 500
        
        data = pd.DataFrame({
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
    
    def enrich_data(self, data):
        """Adiciona features estratégicas aos dados"""
        # Adicionar métricas calculadas
        data['valor_vida_cliente'] = data['valor_estimado'] * data['roi_esperado'] / 100
        data['score_prioridade'] = (data['roi_esperado'] * 0.6 + data['crescimento_projetado'] * 0.4)
        
        return data
