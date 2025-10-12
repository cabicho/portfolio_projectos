import pandas as pd
import asyncio
from datetime import datetime
from src.config.database import get_async_connection

class DataSourcesVerification:
    """Sistema de verificação das fontes de dados SST Moçambique"""
    
    async def verify_all_sources(self) -> dict:
        print("🔍 VERIFICANDO FONTES DE DADOS SST MOÇAMBIQUE")
        print("=" * 60)
        
        report = {'timestamp': datetime.now().isoformat(), 'sources': {}}
        
        report['sources']['oms'] = await self.verify_oms_data()
        report['sources']['world_bank'] = await self.verify_world_bank_data()
        report['sources']['national'] = await self.verify_national_data()
        
        # Resumo
        active_sources = sum(1 for s in report['sources'].values() if s['total_records'] > 0)
        total_records = sum(s['total_records'] for s in report['sources'].values())
        
        report['summary'] = {
            'total_sources': len(report['sources']),
            'active_sources': active_sources,
            'total_records': total_records,
            'overall_status': '✅ EXCELENTE' if active_sources >= 2 else '⚠️  REGULAR' if active_sources == 1 else '❌ CRÍTICO'
        }
        
        # Exibir relatório
        print(f"\n📊 RESUMO:")
        print(f"   Fontes ativas: {active_sources}/{len(report['sources'])}")
        print(f"   Total registros: {total_records}")
        print(f"   Status: {report['summary']['overall_status']}")
        
        for name, data in report['sources'].items():
            print(f"\n🔹 {name.upper()}: {data['status']}")
            print(f"   Registros: {data['total_records']}")
            print(f"   Tipo: {data['source_type']}")
        
        return report
    
    async def verify_oms_data(self) -> dict:
        try:
            conn = await get_async_connection()
            result = await conn.fetch('SELECT COUNT(*) as count FROM who_data')
            count = result[0]['count'] if result else 0
            await conn.close()
            
            return {
                'status': "✅ ATIVA" if count > 0 else "❌ INATIVA",
                'total_records': count,
                'source_type': 'OMS - Organização Mundial da Saúde',
                'data_quality': 'Alta' if count > 5 else 'Média'
            }
        except Exception as e:
            return {'status': f"❌ ERRO: {str(e)}", 'total_records': 0, 'source_type': 'OMS', 'data_quality': 'Baixa'}
    
    async def verify_world_bank_data(self) -> dict:
        try:
            conn = await get_async_connection()
            result = await conn.fetch('SELECT COUNT(*) as count FROM world_bank_data')
            count = result[0]['count'] if result else 0
            await conn.close()
            
            return {
                'status': "✅ ATIVA" if count > 0 else "❌ INATIVA",
                'total_records': count,
                'source_type': 'Banco Mundial',
                'data_quality': 'Alta' if count > 5 else 'Média'
            }
        except Exception as e:
            return {'status': f"❌ ERRO: {str(e)}", 'total_records': 0, 'source_type': 'Banco Mundial', 'data_quality': 'Baixa'}
    
    async def verify_national_data(self) -> dict:
        try:
            conn = await get_async_connection()
            result1 = await conn.fetch('SELECT COUNT(*) as count FROM risk_assessment')
            result2 = await conn.fetch('SELECT COUNT(*) as count FROM occupational_diseases')
            count = (result1[0]['count'] if result1 else 0) + (result2[0]['count'] if result2 else 0)
            await conn.close()
            
            return {
                'status': "✅ ATIVA" if count > 0 else "❌ INATIVA",
                'total_records': count,
                'source_type': 'Dados Nacionais Moçambique',
                'data_quality': 'Alta' if count > 10 else 'Média'
            }
        except Exception as e:
            return {'status': f"❌ ERRO: {str(e)}", 'total_records': 0, 'source_type': 'Dados Nacionais', 'data_quality': 'Baixa'}
