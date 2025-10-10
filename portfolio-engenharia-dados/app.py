from flask import Flask, jsonify, request, render_template
import pandas as pd
import os
import sys

# Adicionar scripts ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

try:
    from data_pipeline import RegulatoryDataPipeline
except ImportError as e:
    print(f"Erro ao importar pipeline: {e}")
    # Fallback para desenvolvimento
    RegulatoryDataPipeline = None

app = Flask(__name__)

# Inicializar pipeline apenas se importado com sucesso
if RegulatoryDataPipeline:
    pipeline = RegulatoryDataPipeline()
else:
    pipeline = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/run-pipeline', methods=['POST'])
def run_pipeline():
    """Endpoint para executar o pipeline"""
    if not pipeline:
        return jsonify({'status': 'error', 'message': 'Pipeline não disponível'})
    
    try:
        result = pipeline.run_pipeline()
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/reports', methods=['GET'])
def get_reports():
    """Endpoint para listar relatórios"""
    try:
        reports = []
        report_path = 'data/regulatory_reports'
        
        if os.path.exists(report_path):
            report_files = os.listdir(report_path)
            for file in report_files:
                if file.endswith(('.csv', '.json')):
                    reports.append({
                        'name': file,
                        'type': 'csv' if file.endswith('.csv') else 'json',
                        'path': f'{report_path}/{file}'
                    })
        
        return jsonify({'reports': reports})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/ml-insights', methods=['GET'])
def get_ml_insights():
    """Endpoint para insights de ML"""
    if not pipeline:
        return jsonify({'error': 'Pipeline não disponível'})
    
    try:
        dw_data, excel_data = pipeline.extract_from_multiple_sources()
        transformed_data = pipeline.transform_data(dw_data, excel_data)
        reports = pipeline.generate_regulatory_reports(transformed_data)
        
        return jsonify({
            'ml_insights': reports['ml_insights'],
            'compliance_summary': reports['compliance_report'].to_dict()
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/data-sources', methods=['GET'])
def get_data_sources():
    """Endpoint para informações das fontes de dados"""
    if not pipeline:
        return jsonify({'error': 'Pipeline não disponível'})
    
    try:
        # Simular fontes de dados para demo
        data_sources = [
            {'name': 'Data Warehouse', 'type': 'PostgreSQL', 'status': 'Ativo'},
            {'name': 'Arquivos Excel', 'type': 'Planilhas', 'status': 'Ativo'},
            {'name': 'SharePoint', 'type': 'Documentos', 'status': 'Ativo'}
        ]
        
        return jsonify({
            'data_sources': data_sources,
            'total_sources': len(data_sources)
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check da aplicação"""
    status = 'healthy' if pipeline else 'degraded'
    return jsonify({
        'status': status, 
        'service': 'Regulatory Data API',
        'pipeline_available': pipeline is not None
    })

# Criar diretórios necessários
os.makedirs('data/regulatory_reports', exist_ok=True)
os.makedirs('templates', exist_ok=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
