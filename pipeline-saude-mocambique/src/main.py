#portfolio_projectos/pipeline-saude-mocambique/src/main.py
import pandas as pd
from extract.data_sources import MozambiqueDataExtractor
from transform.data_cleaning import DataTransformer
from load.database_loader import DatabaseLoader
from config.database import create_tables
import os
from datetime import datetime
import json
import asyncio

async def main():
    print("🚀 Iniciando Pipeline de Dados - Moçambique")
    
    # Verificar variável de ambiente
    if not os.getenv('DATABASE_URL'):
        print("❌ DATABASE_URL não configurada")
        return
    
    # Criar tabelas
    print("🗄️ Configurando banco de dados...")
    await create_tables()
    
    # Inicializar componentes
    extractor = MozambiqueDataExtractor()
    transformer = DataTransformer()
    loader = DatabaseLoader()
    
    # Extração
    print("📥 Extraindo dados...")
    who_data = extractor.extract_who_data()
    diseases_data = extractor.extract_occupational_diseases()
    exposure_data = extractor.extract_environmental_exposure()
    world_bank_data = extractor.extract_world_bank_data()  # ADICIONE ESTA LINHA
    
    print(f"✅ Dados OMS: {len(who_data)} registros")
    print(f"✅ Dados Doenças: {len(diseases_data)} registros") 
    print(f"✅ Dados Exposição: {len(exposure_data)} registros")
    
    # Transformação
    print("🔄 Transformando dados...")
    who_clean = transformer.clean_occupational_data(who_data)
    diseases_clean = transformer.clean_occupational_data(diseases_data)
    exposure_clean = transformer.clean_occupational_data(exposure_data)
    
    # Cálculos
    health_indicators = transformer.calculate_health_indicators(diseases_clean, exposure_clean)
    risk_assessment = transformer.create_risk_assessment(diseases_clean, exposure_clean)
    
    # Carregar no banco
    print("💾 Carregando no PostgreSQL...")
    await loader.load_who_data(who_clean)
    await loader.load_occupational_diseases(diseases_clean)
    await loader.load_risk_assessment(risk_assessment)
    await loader.load_world_bank_data(world_bank_data)  # ADICIONE ESTA LINHA
    
    # Salvar localmente
    print("💿 Salvando arquivos locais...")
    os.makedirs('data/processed', exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    risk_assessment.to_csv(f'data/processed/risk_assessment_{timestamp}.csv', index=False)
    
    # Relatório
    quality_report = {
        'timestamp': timestamp,
        'data_sources': {
            'who': len(who_clean),
            'occupational_diseases': len(diseases_clean),
            'environmental_exposure': len(exposure_clean),
            'risk_assessment': len(risk_assessment)
        },
        'database_loaded': True
    }
    
    with open(f'data/processed/quality_report_{timestamp}.json', 'w') as f:
        json.dump(quality_report, f, indent=2)
    
    print("🎉 Pipeline executado com sucesso!")
    print(f"📊 Resumo: {quality_report}")

if __name__ == "__main__":
    asyncio.run(main())
