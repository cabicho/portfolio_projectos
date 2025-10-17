import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class CustomerAnalytics:
    def __init__(self, data):
        self.data = data
        logger.info("Inicializando análise de clientes...")
    
    def calculate_kpis(self):
        """Calcula KPIs críticos para Credit Control"""
        logger.info("Calculando KPIs...")
        
        clientes_ativos = self.data[self.data['estado_conta'] == 'Ativo']
        clientes_inadimplentes = self.data[self.data['dias_atraso'] > 90]
        
        kpis = {
            'total_clientes': len(self.data),
            'clientes_ativos': len(clientes_ativos),
            'taxa_inadimplencia': len(clientes_inadimplentes) / len(self.data) * 100,
            'satisfacao_media': self.data['satisfacao_cliente'].mean(),
            'utilizacao_media_credito': self.data['utilizacao_credito'].mean() * 100,
            'exposicao_total_credito': self.data['valor_contrato'].sum(),
            'valor_total_risco': self.data['valor_em_risco'].sum(),
            'score_medio_credito': self.data['score_credito'].mean()
        }
        
        logger.info(f"KPIs calculados: {len(kpis)} métricas")
        return kpis
    
    def segment_clients(self):
        """Segmenta clientes por risco e valor"""
        logger.info("Segmentando clientes...")
        
        segments = []
        for _, client in self.data.iterrows():
            if client['risco_credito'] <= 2 and client['valor_contrato'] > 10000:
                segment = 'Premium'
            elif client['risco_credito'] >= 4:
                segment = 'Alto Risco'
            elif client['utilizacao_credito'] > 0.8:
                segment = 'Alta Utilização'
            elif client['dias_atraso'] > 30:
                segment = 'Atraso Crítico'
            else:
                segment = 'Standard'
                
            segments.append(segment)
            
        segment_counts = pd.Series(segments).value_counts()
        logger.info(f"Segmentação concluída: {segment_counts.to_dict()}")
            
        return segments
    
    def generate_retention_insights(self):
        """Gera insights sobre retenção de clientes"""
        logger.info("Analisando retenção de clientes...")
        
        insights = {
            'correlacao_satisfacao_tempo': self.data[['satisfacao_cliente', 'tempo_cliente_meses']].corr().iloc[0,1],
            'satisfacao_por_segmento': self.data.groupby('segmento')['satisfacao_cliente'].mean().to_dict(),
            'taxa_utilizacao_risco': self.data.groupby('risco_credito')['utilizacao_credito'].mean().to_dict()
        }
        
        return insights
