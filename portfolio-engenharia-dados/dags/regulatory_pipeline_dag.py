from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# Adicionar scripts ao path
sys.path.append('/opt/airflow/scripts')

try:
    from data_pipeline import RegulatoryDataPipeline
except ImportError:
    # Fallback para desenvolvimento
    sys.path.append('/app/scripts')
    from data_pipeline import RegulatoryDataPipeline

default_args = {
    'owner': 'engenharia_dados',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

def run_regulatory_pipeline():
    """Executa o pipeline de dados regulamentares"""
    pipeline = RegulatoryDataPipeline()
    result = pipeline.run_pipeline()
    print(f"Pipeline result: {result}")
    return result

with DAG(
    'regulatory_reports_pipeline',
    default_args=default_args,
    description='Pipeline de dados para relatórios regulamentares',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['regulatory', 'reports', 'data_engineering']
) as dag:

    run_pipeline_task = PythonOperator(
        task_id='run_regulatory_pipeline',
        python_callable=run_regulatory_pipeline
    )

    run_pipeline_task
