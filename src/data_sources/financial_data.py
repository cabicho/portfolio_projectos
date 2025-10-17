import pandas as pd
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CreditControlData:
    def __init__(self, sample_size=1000):
        self.sample_size = sample_size
        np.random.seed(42)
    
    def generate_portfolio_data(self):
        """Gera dados de portfolio de clientes para análise"""
        logger.info("Gerando dados de portfolio...")
        
        data = {
            'cliente_id': range(1, self.sample_size + 1),
            'segmento': np.random.choice(['Corporate', 'SME', 'Individual'], self.sample_size),
            'valor_contrato': np.random.uniform(1000, 50000, self.sample_size),
            'dias_atraso': np.random.randint(0, 120, self.sample_size),
            'limite_credito': np.random.uniform(5000, 100000, self.sample_size),
            'utilizacao_credito': np.random.uniform(0.1, 0.95, self.sample_size),
            'score_credito': np.random.randint(300, 850, self.sample_size),
            'estado_conta': np.random.choice(['Ativo', 'Inativo', 'Suspenso'], self.sample_size),
            'satisfacao_cliente': np.random.uniform(1, 5, self.sample_size),
            'tempo_cliente_meses': np.random.randint(1, 60, self.sample_size),
            'regiao': np.random.choice(['Norte', 'Sul', 'Centro', 'Litoral'], self.sample_size)
        }
        
        df = pd.DataFrame(data)
        
        # Calcular métricas de risco
        df['risco_credito'] = df.apply(self.calculate_credit_risk, axis=1)
        df['categoria_atraso'] = df['dias_atraso'].apply(self.categorize_delay)
        df['valor_em_risco'] = df.apply(self.calculate_risk_exposure, axis=1)
        
        logger.info(f"Dados gerados: {len(df)} registros")
        return df
    
    def calculate_credit_risk(self, row):
        """Calcula risco de crédito baseado em múltiplos fatores"""
        risk_score = 0
        
        # Fator dias em atraso
        if row['dias_atraso'] > 90:
            risk_score += 3
        elif row['dias_atraso'] > 30:
            risk_score += 2
        elif row['dias_atraso'] > 0:
            risk_score += 1
            
        # Fator utilização de crédito
        if row['utilizacao_credito'] > 0.8:
            risk_score += 2
        elif row['utilizacao_credito'] > 0.5:
            risk_score += 1
            
        # Fator score de crédito
        if row['score_credito'] < 500:
            risk_score += 3
        elif row['score_credito'] < 650:
            risk_score += 2
            
        return min(risk_score, 5)
    
    def categorize_delay(self, dias):
        """Categoriza dias em atraso"""
        if dias == 0:
            return 'Em dia'
        elif dias <= 30:
            return 'Atraso leve'
        elif dias <= 90:
            return 'Atraso moderado'
        else:
            return 'Atraso severo'
    
    def calculate_risk_exposure(self, row):
        """Calcula valor em risco"""
        risk_multiplier = {
            0: 0.01,  # Baixo risco
            1: 0.05,  # Risco moderado-baixo
            2: 0.10,  # Risco moderado
            3: 0.25,  # Risco moderado-alto
            4: 0.50,  # Alto risco
            5: 0.75   # Risco muito alto
        }
        return row['valor_contrato'] * risk_multiplier.get(row['risco_credito'], 0.1)

if __name__ == "__main__":
    generator = CreditControlData()
    data = generator.generate_portfolio_data()
    data.to_csv('/app/data/processed/portfolio_data.csv', index=False)
    print("Dados gerados e salvos em /app/data/processed/portfolio_data.csv")
