import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import logging
from datetime import datetime
import os
import json

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RegulatoryDataPipeline:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        if not self.db_url:
            logger.warning("DATABASE_URL não encontrada, usando modo simulado")
            self.engine = None
        else:
            try:
                self.engine = create_engine(self.db_url)
                logger.info("Pipeline conectado ao banco de dados")
            except Exception as e:
                logger.error(f"Erro ao conectar ao banco: {e}")
                self.engine = None
    
    def extract_from_multiple_sources(self):
        """Simula extração de diversas fontes"""
        logger.info("Extraindo dados de múltiplas fontes...")
        
        # Dados simulados para demonstração
        np.random.seed(42)  # Para reproducibilidade
        
        # Fonte 1: Data Warehouse (simulado)
        dw_data = pd.DataFrame({
            'transaction_id': range(1, 101),
            'client_id': np.random.randint(1, 20, 100),
            'transaction_value': np.random.normal(15000, 5000, 100),
            'transaction_date': pd.date_range('2024-01-01', periods=100, freq='D'),
            'risk_category': np.random.choice(['Baixo', 'Médio', 'Alto'], 100, p=[0.6, 0.3, 0.1])
        })
        
        # Fonte 2: Excel/SharePoint (simulado)
        excel_data = pd.DataFrame({
            'compliance_id': range(1, 21),
            'client_id': range(1, 21),
            'compliance_status': np.random.choice(['Compliant', 'Pending', 'Non-Compliant'], 20, p=[0.7, 0.2, 0.1]),
            'last_review_date': pd.date_range('2024-01-01', periods=20, freq='D')
        })
        
        logger.info(f"Dados extraídos: {len(dw_data)} transações, {len(excel_data)} registros de compliance")
        return dw_data, excel_data
    
    def transform_data(self, dw_data, excel_data):
        """Manipulação e limpeza de dados"""
        logger.info("Transformando e limpando dados...")
        
        # Merge dos dados
        merged_data = pd.merge(
            dw_data, 
            excel_data, 
            on='client_id', 
            how='left'
        )
        
        # Limpeza e engenharia de features
        merged_data['transaction_value'] = merged_data['transaction_value'].fillna(0)
        merged_data['risk_score'] = merged_data['transaction_value'] / 10000
        
        # Cálculo de flags regulamentares
        merged_data['regulatory_flag'] = merged_data['compliance_status'] != 'Compliant'
        merged_data['high_risk_flag'] = merged_data['risk_category'] == 'Alto'
        
        # Feature adicional: dia da semana
        merged_data['transaction_day'] = merged_data['transaction_date'].dt.day_name()
        
        logger.info(f"Dados transformados: {len(merged_data)} registros")
        return merged_data
    
    def generate_regulatory_reports(self, data):
        """Gera relatórios regulamentares"""
        logger.info("Gerando relatórios regulamentares...")
        
        reports = {
            'risk_report': data.groupby('risk_category').agg({
                'transaction_value': ['sum', 'mean', 'count'],
                'client_id': 'nunique'
            }).round(2),
            
            'compliance_report': pd.DataFrame({
                'status_count': data['compliance_status'].value_counts(),
                'status_percentage': data['compliance_status'].value_counts(normalize=True) * 100
            }).round(2),
            
            'daily_summary': data.groupby('transaction_date').agg({
                'transaction_value': 'sum',
                'regulatory_flag': 'sum',
                'client_id': 'nunique'
            }).round(2),
            
            'ml_insights': self.generate_ml_insights(data)
        }
        
        logger.info("Relatórios gerados com sucesso")
        return reports
    
    def generate_ml_insights(self, data):
        """Análise preditiva"""
        logger.info("Gerando insights de machine learning...")
        
        try:
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.model_selection import train_test_split
            
            # Preparação dos dados para ML
            ml_data = data.copy()
            ml_data = ml_data[ml_data['compliance_status'].notna()]
            
            # Feature engineering simplificado
            features = pd.DataFrame({
                'transaction_value': ml_data['transaction_value'],
                'is_high_risk': (ml_data['risk_category'] == 'Alto').astype(int)
            })
            target = ml_data['regulatory_flag']
            
            if len(features) > 10:
                X_train, X_test, y_train, y_test = train_test_split(
                    features, target, test_size=0.3, random_state=42
                )
                
                model = RandomForestClassifier(n_estimators=50, random_state=42)
                model.fit(X_train, y_train)
                
                accuracy = model.score(X_test, y_test)
                
                insights = {
                    'model_accuracy': round(accuracy, 4),
                    'feature_importance': dict(zip(features.columns, model.feature_importances_)),
                    'total_samples': len(ml_data)
                }
            else:
                insights = {
                    'model_accuracy': 'Dados insuficientes',
                    'feature_importance': {},
                    'total_samples': len(ml_data)
                }
                
        except Exception as e:
            logger.error(f"Erro no ML: {e}")
            insights = {
                'model_accuracy': f'Erro: {str(e)}',
                'feature_importance': {},
                'total_samples': 0
            }
        
        return insights
    
    def save_reports(self, reports):
        """Salva relatórios em arquivos"""
        logger.info("Salvando relatórios...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for report_name, report_data in reports.items():
            if report_name == 'ml_insights':
                filename = f"data/regulatory_reports/{report_name}_{timestamp}.json"
                with open(filename, 'w') as f:
                    json.dump(report_data, f, indent=2)
            elif hasattr(report_data, 'to_csv'):
                filename = f"data/regulatory_reports/{report_name}_{timestamp}.csv"
                report_data.to_csv(filename)
        
        logger.info(f"Relatórios salvos com timestamp: {timestamp}")
    
    def run_pipeline(self):
        """Executa o pipeline completo"""
        logger.info("Iniciando pipeline de dados...")
        
        try:
            # Extração
            dw_data, excel_data = self.extract_from_multiple_sources()
            
            # Transformação
            transformed_data = self.transform_data(dw_data, excel_data)
            
            # Geração de relatórios
            reports = self.generate_regulatory_reports(transformed_data)
            
            # Salvamento
            self.save_reports(reports)
            
            logger.info("Pipeline executado com sucesso!")
            return {
                "status": "success", 
                "message": "Pipeline executado com sucesso",
                "records_processed": len(transformed_data)
            }
            
        except Exception as e:
            logger.error(f"Erro no pipeline: {e}")
            return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    pipeline = RegulatoryDataPipeline()
    result = pipeline.run_pipeline()
    print(result)
