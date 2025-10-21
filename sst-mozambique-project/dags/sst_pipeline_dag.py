from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import sys
import os

# Adicionar scripts ao path
sys.path.insert(0, '/opt/airflow/scripts')

default_args = {
    'owner': 'sst-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5)
}

def run_sst_pipeline():
    """Executa o pipeline SST completo"""
    from scripts.extraction.sst_data_pipeline import SSTDataPipeline
    pipeline = SSTDataPipeline()
    result = pipeline.execute_pipeline()
    
    if not result or result.get('status') != 'success':
        raise Exception('Pipeline SST falhou')

def data_quality_check():
    """Executa verificações de qualidade dos dados"""
    import json
    import pandas as pd
    
    try:
        # Verificar se os arquivos foram gerados
        required_files = [
            'data_sources/raw/full_extraction.json',
            'data_sources/processed/kpis_dashboard.json'
        ]
        
        for file_path in required_files:
            if not os.path.exists(file_path):
                raise Exception(f'Arquivo {file_path} não encontrado')
        
        # Verificar qualidade básica dos dados
        with open('data_sources/processed/kpis_dashboard.json', 'r') as f:
            kpis = json.load(f)
        
        # Validar KPIs essenciais
        essential_kpis = ['total_accidents', 'fatal_accidents', 'total_days_lost']
        for kpi in essential_kpis:
            if kpi not in kpis:
                raise Exception(f'KPI essencial faltando: {kpi}')
        
        print("✅ Verificação de qualidade concluída com sucesso")
        
    except Exception as e:
        print(f"❌ Falha na verificação de qualidade: {e}")
        raise

def generate_report():
    """Gera relatório de execução"""
    import json
    from datetime import datetime
    
    try:
        with open('data_sources/processed/kpis_dashboard.json', 'r') as f:
            kpis = json.load(f)
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_accidents': kpis.get('total_accidents', 0),
            'fatal_accidents': kpis.get('fatal_accidents', 0),
            'total_days_lost': kpis.get('total_days_lost', 0),
            'accidents_by_sector': kpis.get('accidents_by_sector', {}),
            'status': 'SUCCESS'
        }
        
        # Salvar relatório
        os.makedirs('data_sources/processed/reports', exist_ok=True)
        report_file = f"data_sources/processed/reports/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📊 Relatório gerado: {report_file}")
        
    except Exception as e:
        print(f"❌ Erro ao gerar relatório: {e}")
        raise

with DAG(
    'sst_mozambique_pipeline',
    default_args=default_args,
    description='Pipeline de dados SST Moçambique - Coleta, processamento e análise',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['sst', 'mozambique', 'data-pipeline']
) as dag:
    
    start = DummyOperator(task_id='start')
    
    extract_transform_load = PythonOperator(
        task_id='extract_transform_load_data',
        python_callable=run_sst_pipeline
    )
    
    quality_check = PythonOperator(
        task_id='data_quality_check',
        python_callable=data_quality_check
    )
    
    generate_report_task = PythonOperator(
        task_id='generate_daily_report',
        python_callable=generate_report
    )
    
    end = DummyOperator(task_id='end')
    
    start >> extract_transform_load >> quality_check >> generate_report_task >> end
