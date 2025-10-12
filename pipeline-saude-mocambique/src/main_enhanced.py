import pandas as pd
import asyncio
from extract.data_sources import MozambiqueDataExtractor
from extract.excel_sharepoint import ExcelSharePointExtractor
from transform.data_cleaning import DataTransformer
from load.database_loader import DatabaseLoader
from analytics.ml_predictive import HealthPredictiveAnalytics
from config.database import create_tables
import os
import json
from datetime import datetime

async def enhanced_pipeline():
    """Pipeline completo com ML e múltiplas fontes"""
    print("🚀 Iniciando Pipeline Avançado - Moçambique")
    
    if not os.getenv('DATABASE_URL'):
        print("❌ DATABASE_URL não configurada")
        return
    
    # Criar tabelas
    print("🗄️ Configurando banco de dados...")
    await create_tables()
    
    # Inicializar componentes
    extractor = MozambiqueDataExtractor()
    excel_extractor = ExcelSharePointExtractor()
    transformer = DataTransformer()
    loader = DatabaseLoader()
    ml_analytics = HealthPredictiveAnalytics()
    
    # EXTRAÇÃO - Múltiplas fontes
    print("📥 Extraindo dados de múltiplas fontes...")
    
    # 1. Fontes públicas
    who_data = extractor.extract_who_data()
    diseases_data = extractor.extract_occupational_diseases() 
    exposure_data = extractor.extract_environmental_exposure()
    
    # 2. Fontes locais (Excel/CSV)
    local_data_dir = 'data/raw'
    if os.path.exists(local_data_dir):
        excel_data = excel_extractor.extract_excel_files(local_data_dir)
        csv_data = excel_extractor.extract_csv_files(local_data_dir)
        print(f"✅ Dados locais: {len(excel_data)} Excel + {len(csv_data)} CSV")
    
    print(f"✅ Dados OMS: {len(who_data)} registros")
    print(f"✅ Dados Doenças: {len(diseases_data)} registros") 
    print(f"✅ Dados Exposição: {len(exposure_data)} registros")
    
    # TRANSFORMAÇÃO
    print("🔄 Transformando e enriquecendo dados...")
    who_clean = transformer.clean_occupational_data(who_data)
    diseases_clean = transformer.clean_occupational_data(diseases_data)
    exposure_clean = transformer.clean_occupational_data(exposure_data)
    
    # Cálculos de indicadores
    health_indicators = transformer.calculate_health_indicators(diseases_clean, exposure_clean)
    risk_assessment = transformer.create_risk_assessment(diseases_clean, exposure_clean)
    
    # MACHINE LEARNING
    print("🤖 Aplicando Machine Learning...")
    
    # 1. Clustering de províncias
    risk_assessment_ml = ml_analytics.cluster_provinces(risk_assessment)
    
    # 2. Detecção de anomalias
    risk_assessment_ml = ml_analytics.anomaly_detection(risk_assessment_ml)
    
    # 3. Previsão de tendências (se dados históricos disponíveis)
    if len(diseases_clean) > 3:
        risk_forecast = ml_analytics.predict_risk_evolution(risk_assessment_ml)
        print("✅ Previsões de risco geradas")
    
    # CARGA
    print("💾 Carregando dados no Data Warehouse...")
    await loader.load_who_data(who_clean)
    await loader.load_occupational_diseases(diseases_clean)
    await loader.load_risk_assessment(risk_assessment_ml)
    
    # Salvar modelos ML
    ml_analytics.save_models('models')
    
    # RELATÓRIO FINAL
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    report = {
        'timestamp': timestamp,
        'data_sources': {
            'who': len(who_clean),
            'occupational_diseases': len(diseases_clean),
            'environmental_exposure': len(exposure_clean),
            'risk_assessment': len(risk_assessment_ml),
            'ml_clusters': risk_assessment_ml['cluster_nome'].value_counts().to_dict(),
            'anomalies': len(risk_assessment_ml[risk_assessment_ml['anomalia'] == 'Anomalia'])
        },
        'pipeline_status': 'completed',
        'ml_applied': True
    }
    
    os.makedirs('data/processed', exist_ok=True)
    with open(f'data/processed/pipeline_report_{timestamp}.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    risk_assessment_ml.to_csv(f'data/processed/risk_assessment_enhanced_{timestamp}.csv', index=False)
    
    print("🎉 Pipeline avançado executado com sucesso!")
    print(f"📊 Relatório: {report}")

if __name__ == "__main__":
    asyncio.run(enhanced_pipeline())
